from fastapi import FastAPI, UploadFile, HTTPException, Form, File, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from telethon import TelegramClient, errors
from telethon.types import Message
import logging
import io
import datetime
import base64
from telethon.sessions import StringSession

api_id = YOUR_API_ID
api_hash = "YOUR_API_HASH"

app = FastAPI()
client = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_client(session_string=None, reset=False):
    global client
    if client is None or session_string or reset:
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
    return client

def progress_callback(current, total):
    print('Uploaded', current, 'out of', total,
          'bytes: {:.2%}'.format(current / total))

@app.get("/")
async def root():
    return {"Message": "Welcome to Cloud stoarge"}

@app.post("/sign-in/")
async def sign_in(phone_number: str = Form(...)):
    try:
        client = get_client()
        await client.connect()
        if not await client.is_user_authorized():
            phone_code = await client.send_code_request(phone_number)
            await client.disconnect()
            return {"message": "Code sent to your phone number", "phone_code": phone_code.phone_code_hash}
        await client.disconnect()
        return {"message": "Already signed in", "session_string": client.session.save()}
    except errors.FloodWaitError as e:
        raise HTTPException(status_code=429, detail=f"Too many requests. Please wait for {e.seconds} seconds.")
    except errors.PhoneNumberFloodError:
        raise HTTPException(status_code=429, detail="Too many attempts. Please try again later.")
    except errors.PhoneNumberBannedError:
        raise HTTPException(status_code=403, detail="This phone number is banned.")
    except errors.PhoneNumberInvalidError:
        raise HTTPException(status_code=400, detail="The phone number is invalid.")
    except Exception as e:
        logger.error(f"Error during sign-in: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-code/")
async def verify_code(phone_number: str = Form(...), code: str = Form(...), phone_code_hash: str = Form(...), password: str = Form(None), session_string: str = Form(None)):
    try:
        client = get_client(session_string)
        await client.connect()
        if not await client.is_user_authorized():
            try:
                await client.sign_in(phone_number, code, phone_code_hash=phone_code_hash)
            except errors.SessionPasswordNeededError:
                if password is None:
                    await client.disconnect()
                    return {"message": "2FA enabled. Please provide the password"}
                await client.sign_in(password=password)
            session_string = client.session.save()
            await client.disconnect()
            return {"message": "Signed in successfully", "session_string": session_string}
        await client.disconnect()
        return {"message": "Already signed in", "session_string": client.session.save()}
    except Exception as e:
        logger.error(f"Error during code verification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logout/")
async def logout(session_string: str = Form(None)):
    try:
        client = get_client(session_string)
        await client.connect()
        if await client.is_user_authorized():
            await client.log_out()
            await client.disconnect()
            get_client(reset=True)
            return {"message": "Logout successfully"}
        await client.disconnect()
        get_client(reset=True)
        return {"message": "Already signed in"}
    except Exception as e:
        logger.error(f"Error during code verification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/")
async def upload_files(file: UploadFile = File(...), session_string: str = Form(...)):
    try:
        client = get_client(session_string)
        await client.connect()
        
        media_files = None
        
        file_bytes = await file.read()
        file_stream = io.BytesIO(file_bytes)
        file_stream.name = file.filename
        fileType = file.headers['content-type'].split("/")[1]
        msg = "XNCODER-P-"+fileType.upper()+"-"+str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    
        message = await client.send_file(
            'me', 
            file_stream, 
            progress_callback=progress_callback, 
            part_size_kb=1024, 
            part_size=20000000, 
            parallel=16, 
            caption=msg
        )

        if fileType in ['jpeg', 'jpg', 'png']:
            media_files = {
                'type': "image",
                'id': message.id,
                'message': message.message
            }
        elif fileType in ['mp4', 'mov', 'vid']:
            media_files = {
                'type': "video",
                'id': message.id,
                'message': message.message
            }
                
        await client.disconnect()
        return JSONResponse({'status': 'success', 'file': media_files})
    except Exception as e:
        logger.error(f"Error during file upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{id}")
async def download_file(id: str, session_string: str, request: Request):
    try:
        client = get_client(session_string)
        await client.connect()
        message = await client.get_messages('me', ids=int(id))
        if not message.media:
            raise HTTPException(status_code=404, detail="File not found")

        file_size = message.file.size

        range_header = request.headers.get('Range')
        if range_header:
            range_start, range_end = range_header.replace('bytes=', '').split('-')
            range_start = int(range_start)
            range_end = int(range_end) if range_end else file_size - 1
            length = range_end - range_start + 1
            print(message.file.name)

            async def iterfile():
                async for chunk in client.iter_download(message.media, offset=range_start, limit=length):
                    yield bytes(chunk)

            headers = {
                'Content-Range': f'bytes {range_start}-{range_end}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(length),
                'Content-Disposition': f'attachment; filename={message.file.name}'
            }
            return StreamingResponse(iterfile(), status_code=206, headers=headers)
        else:
            async def iterfile():
                async for chunk in client.iter_download(message.media):
                    yield bytes(chunk)

            headers = {
                'Content-Length': str(file_size),
                'Content-Disposition': f'attachment; filename={message.file.name}'
            }
            return StreamingResponse(iterfile(), headers=headers)
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/remove/")
async def remove(id: str, session_string:str):
    try:
        client = get_client(session_string)
        await client.connect()
        await client.delete_messages('me', message_ids=int(id))
        await client.disconnect()
        return {"message": "File removed successfully"}
    except Exception as e:
        logger.error(f"Error removing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/media/")
async def media(id: str, type: str, session_string: str):
    try:
        client = get_client(session_string)
        await client.connect()
        message = await client.get_messages('me', ids=int(id))
        if not message.media:
            raise HTTPException(status_code=404, detail="Media not found")
        
        buffer = io.BytesIO()
        
        if type == "image":
            await message.download_media(file=buffer)
            buffer.seek(0)
            base64_media = base64.b64encode(buffer.read()).decode('utf-8')
            media_data = {
                'type': 'image',
                'src': f'data:image/jpeg;base64,{base64_media}',
                'message': message.message
            }
            await client.disconnect()
            return JSONResponse({'status': 'success', **media_data})
        elif type == "video":
            if "video/mp4" in message.media.document.mime_type and message.media.document.thumbs:
                thumb = message.media.document.thumbs[-1]
                print(thumb)
                await message.download_media(thumb=thumb, file=buffer)
                buffer.seek(0)
                base64_thumb = base64.b64encode(buffer.read()).decode('utf-8')
                duration_seconds = message.media.document.attributes[0].duration
                minutes, seconds = divmod(int(duration_seconds), 60)
                duration_formatted = f"{minutes:02}:{seconds:02}"
                media_data = {
                    'type': 'video',
                    'src': f"data:image/jpeg;base64,{base64_thumb}",
                    'duration': duration_formatted,
                    'message': message.message
                }
                await client.disconnect()
                return JSONResponse({'status': 'success', **media_data})
    except Exception as e:
        logger.error(f"Error serving media: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stream/{id}")
async def stream_video(id: str, session_string: str, request: Request):
    try:
        client = get_client(session_string)
        await client.connect()
        message = await client.get_messages('me', ids=int(id))
        if not message.media:
            raise HTTPException(status_code=404, detail="File not found")

        file_size = message.file.size

        range_header = request.headers.get('Range')
        if range_header:
            range_start, range_end = range_header.replace('bytes=', '').split('-')
            range_start = int(range_start)
            range_end = int(range_end) if range_end else file_size - 1
            length = range_end - range_start + 1

            async def iterfile():
                async for chunk in client.iter_download(message.media, offset=range_start, limit=length):
                    yield bytes(chunk)

            headers = {
                'Content-Range': f'bytes {range_start}-{range_end}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(length),
                'Content-Type': 'video/mp4'
            }
            return StreamingResponse(iterfile(), status_code=206, headers=headers)
        else:
            async def iterfile():
                async for chunk in client.iter_download(message.media):
                    yield bytes(chunk)

            headers = {
                'Content-Length': str(file_size),
                'Content-Type': 'video/mp4'
            }
            return StreamingResponse(iterfile(), headers=headers)
    except Exception as e:
        logger.error(f"Error streaming video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-files/")
async def list_files(session_string: str, offset: int = 0):
    try:
        client = get_client(session_string)
        await client.connect()
        messages = await client.get_messages('me', offset_id=offset, limit=20)
        media_files = []
        offset_id = None
        for message in messages:
            if isinstance(message, Message):
                md = False
                message_id = None
                if message.message.startswith("XNCODER") and message.message[10:message.message.find("-", 10+1)] in ["JPEG", "JPG", "PNG"] and message.media:
                    md = True
                    type = "image"
                    message_id = message.id
                    msg = message.message
                elif message.message.startswith("XNCODER") and message.message[10:message.message.find("-", 10+1)] in ["VID", "MOV", "MP4"]  and message.media:
                    md = True
                    type = "video"
                    message_id = message.id
                    msg = message.message
                offset_id = message_id
                
                if md and message_id is not None:  # Check if message_id is set
                    media_file = {
                        'type': type,
                        'id': message_id,
                        'message': msg
                    }
                    media_files.append(media_file)
        await client.disconnect()
        return {"files": media_files, "offset_id": offset_id}
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
