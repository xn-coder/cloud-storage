from django.http import JsonResponse, HttpResponse, FileResponse, StreamingHttpResponse
from telethon.types import MessageMediaDocument, MessageMediaPhoto
from authentication.CustomSession import CustomSession
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from telethon.sync import TelegramClient
from asgiref.sync import sync_to_async, async_to_sync
from django.core.cache import cache
from telethon.types import Message
from django.conf import settings
from io import BytesIO
import mimetypes
import asyncio
import datetime
import base64
import json
import re
import os

async def home(request):
    phone = await sync_to_async(request.session.get)('phone')
    if phone and len(phone) > 10:
        client = TelegramClient(CustomSession(phone), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH, timeout=50)
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            await sync_to_async(request.session.__setitem__)('phone', "")
            return redirect("login")

        await client.disconnect()
        return render(request, 'index.html')
    else:
        return redirect("login")
    
async def get_media(request):
    phone = await sync_to_async(request.session.get)('phone')
    if request.method == 'POST' and phone and len(phone) > 10:
        client = TelegramClient(CustomSession(phone), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH, timeout=50)
        await client.connect()
        try:
            data = json.loads(request.body)
            offset_id = data['offset_id']
            messages = await client.get_messages('me', limit=50, offset_id=offset_id)
            
            media_files = []
            for message in messages:
                if isinstance(message, Message):
                    md = False
                    if message.message.startswith("xncoder") and "IMG" in message.message and message.media:
                        md = True
                        type = "image"
                        message_id = message.id
                        msg = message.message
                    elif message.message.startswith("xncoder") and "VID" in message.message and message.media:
                        md = True
                        type = "video"
                        message_id = message.id
                        msg = message.message
                    offset_id = message_id
                    
                    
                    
                    if md:
                        media_file = {
                            'type': type,
                            'message_id': message_id,
                            'message':msg
                        }
                        media_files.append(media_file)
                        
            await client.disconnect()
            return JsonResponse({'status': 'success', 'media_files': media_files, 'offset_id': offset_id})
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def progress_callback(current, total):
    print('Uploaded', current, 'out of', total,
          'bytes: {:.2%}'.format(current / total))

async def upload(request):
    phone = await sync_to_async(request.session.get)('phone')
    if phone and len(phone) > 10:
        client = TelegramClient(CustomSession(phone), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH, timeout=50)
        if request.method == 'POST':
            await client.connect()
            
            files = []
            for file in request.FILES.getlist('files'):
                if file.content_type.startswith("image"):
                   message = await client.send_file('me', file, part_size_kb=512, part_size=10000000, parallel=8, progress_callback=progress_callback, caption="xncoder-IMG"+str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")))
                   files.append({
                    'type': "image",
                    'message_id': message.id,
                    'message': message.message
                   })
                elif file.content_type.startswith("video"):
                    message = await client.send_file('me', file, progress_callback=progress_callback, caption="xncoder-VID"+str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")))
                    files.append({
                        'type': "video",
                        'message_id': message.id,
                        'message': message.message
                    })

            await client.disconnect()
            return JsonResponse({'status': 'success', 'files': files})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

async def media(request):
    phone = await sync_to_async(request.session.get)('phone')
    if request.method == 'POST' and phone and len(phone) > 10:
        client = TelegramClient(CustomSession(phone), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH, timeout=50)
        await client.connect()
        try:
            data = json.loads(request.body)
            cache_key = f"media_{data['type']}_{data['message_id']}"
            cached_media = cache.get(cache_key)
            
            if cached_media:
                await client.disconnect()
                return JsonResponse({'status': 'success', **cached_media})

            if data['type'] == "image":
                message = await client.get_messages("me", ids=int(data['message_id']))
                buffer = BytesIO()
                await message.download_media(file=buffer)
                await client.disconnect()
                buffer.seek(0)
                base64_media = base64.b64encode(buffer.read()).decode('utf-8')
                media_data = {
                    'type': 'image',
                    'src': f'data:image/jpeg;base64,{base64_media}',
                    'message': message.message
                }
                cache.set(cache_key, media_data, timeout=60*60)  # Cache for 1 hour
                return JsonResponse({'status': 'success', **media_data})
            elif data['type'] == "video":
                message = await client.get_messages("me", ids=int(data['message_id']))
                if "video/mp4" in message.media.document.mime_type and message.media.document.thumbs:
                    thumb = message.media.document.thumbs[-1]
                    thumb_io = BytesIO()
                    await message.download_media(thumb=thumb, file=thumb_io)
                    await client.disconnect()
                    thumb_io.seek(0)
                    base64_thumb = base64.b64encode(thumb_io.read()).decode('utf-8')
                    duration_seconds = message.media.document.attributes[0].duration
                    minutes, seconds = divmod(int(duration_seconds), 60)
                    duration_formatted = f"{minutes:02}:{seconds:02}"
                    media_data = {
                        'type': 'video',
                        'src': f"data:image/jpeg;base64,{base64_thumb}",
                        'duration': duration_formatted,
                        'message': message.message
                    }
                    cache.set(cache_key, media_data, timeout=60*60)  # Cache for 1 hour
                    return JsonResponse({'status': 'success', **media_data})
            else:
                await client.disconnect()
                return JsonResponse({'status': 'error', 'message': 'Invalid type'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

async def fetch_video(request):
    phone = await sync_to_async(request.session.get)('phone')
    if request.method == 'POST' and phone and len(phone) > 10:
        client = TelegramClient(CustomSession(phone), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH, timeout=50)
        await client.connect()
        data = json.loads(request.body)

        try:
            message = await client.get_messages('me', ids=int(data['video_id']))
            if not message or not message.media:
                return JsonResponse({'status': 'error', 'message': 'Video not found'})

            video_file = BytesIO()
            await message.download_media(file=video_file)
            video_file.seek(0)
            await client.disconnect()

            video_path = f'videos/{data["video_id"]}.mp4'
            default_storage.save(video_path, ContentFile(video_file.read()))

            video_url = default_storage.url(video_path)
            
            print(video_url)

            return JsonResponse({'status': 'success', 'video_url': video_url})
        except Exception as e:
            await client.disconnect()
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def stream_video(request, video_id):
    video_path = os.path.join(settings.MEDIA_ROOT, f'videos/{video_id}.mp4')
    if not os.path.exists(video_path):
        return HttpResponse(status=404)

    range_header = request.headers.get('Range', '').strip()
    range_match = re.match(r'bytes=(\d+)-(\d+)?', range_header)
    size = os.path.getsize(video_path)
    content_type, _ = mimetypes.guess_type(video_path)

    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        length = last_byte - first_byte + 1
        response = FileResponse(open(video_path, 'rb'), content_type=content_type)
        response['Content-Length'] = str(length)
        response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{size}'
        response.status_code = 206
    else:
        response = FileResponse(open(video_path, 'rb'), content_type=content_type)
        response['Content-Length'] = str(size)
        response.status_code = 200

    return response

async def download_media(request):
    phone = await sync_to_async(request.session.get)('phone')
    if request.method == 'POST' and phone and len(phone) > 10:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        TELETHON_SESSION_DIR = os.path.join(BASE_DIR, 'telethon_sessions')
        if not os.path.exists(TELETHON_SESSION_DIR):
            os.makedirs(TELETHON_SESSION_DIR)
        client = TelegramClient(CustomSession(phone), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH, timeout=50)
        await client.connect()
        data = json.loads(request.body)

        try:
            message = await client.get_messages('me', ids=int(data['message_id']))
            if message.media:
                if message.media.photo:
                    file_extension = 'jpg'
                elif message.media.document:
                    mime_type = message.media.document.mime_type
                    file_extension = mimetypes.guess_extension(mime_type).lstrip('.')
                else:
                    file_extension = 'bin'
                    
                print(file_extension)
                    
                response = HttpResponse(content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment;filename={message.message}.{file_extension}'

                async for chunk in client.iter_download(message.media):
                    response.write(chunk)
                    response.flush()

                await client.disconnect()
                return response
            else:
                await client.disconnect()
                return JsonResponse({'error': 'Media not found'}, status=404)
        except Exception as e:
            await client.disconnect()
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
