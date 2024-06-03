from telethon.errors import SessionPasswordNeededError
from django.shortcuts import render, redirect
from telethon.sync import TelegramClient
from asgiref.sync import sync_to_async
from django.conf import settings
from .CustomSession import CustomSession


async def login(request):
    phone = await sync_to_async(request.session.get)('phone')
    if request.method == 'POST':
        country = request.POST.get('country')
        phone = request.POST.get('phone')
        otp = request.POST.get('otp')
        passwd = request.POST.get('passwd')
        
        if len(phone) > 10:
            client = TelegramClient(CustomSession(phone), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH, timeout=50)
            await client.connect()
            
            if not await client.is_user_authorized():
                if len(otp) == 0:
                    result = await client.send_code_request(phone)
                    await sync_to_async(request.session.__setitem__)('phone_hash', result.phone_code_hash)
                    return render(request, 'login.html', {'code':country, 'phone': phone})
                
                elif len(otp) > 0 and len(passwd) == 0:
                    phone_hash = await sync_to_async(request.session.get)('phone_hash')
                    try:
                        await client.sign_in(phone=phone, code=otp, phone_code_hash=phone_hash)
                        await sync_to_async(request.session.__setitem__)('phone', phone)
                        await client.disconnect()
                        return redirect("home")
                    except SessionPasswordNeededError:
                        return render(request, 'login.html', {'code':country, 'phone': phone, 'otp': otp, 'F2A':True})
                    except Exception as e:
                        print("Error:", e)
                        return render(request, 'login.html', {'code':country, 'phone': phone, 'error': e})
                    
                elif len(passwd) > 0:
                    await client.sign_in(password=passwd)
                    await sync_to_async(request.session.__setitem__)('phone', phone)
                    await client.disconnect()
                    return redirect("home")
        return render(request, 'login.html', {'code':country, 'phone': phone})
    elif phone and len(phone) > 10:
        client = TelegramClient(phone, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH, timeout=20)
        await client.connect()
        if await client.is_user_authorized():
            return redirect("home")
        else:
            return render(request, 'login.html')
        
    else:
        return render(request, 'login.html')
    
async def logout(request):
    phone = await sync_to_async(request.session.get)('phone')
    if phone and len(phone) > 10:
        client = TelegramClient(CustomSession(phone), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH, timeout=50)
        await client.connect()
        await client.log_out()
        await client.disconnect()
    await sync_to_async(request.session.__setitem__)('phone', "")
    return redirect("login")

