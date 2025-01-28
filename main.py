import hashlib
import hmac
import json
from datetime import datetime, timedelta
import requests
from aiohttp import web
from celery import Celery
from multiprocessing import Process
from tgbot.config import load_config
from tgbot.utils.db_utils import get_repo

# Redis and Celery configuration
REDIS_URL = "redis://:B7dG39pFzKvXrQwL5M2N8T1C4J6Y9H3P7Xv5RfQK2W8L9Z3TpVJ@92.119.114.185:6379/0"
celery = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

SECRET_KEY = 'd9d0503a2e263c392aa3397614c342113ac8998446913247d238398dcab1091c'
TELEGRAM_BOT_TOKEN = '7926443493:AAF2mhVZivQttPdVjO4VC5HQK2RLHfAnUu8'
PRIVATE_CHANNEL_ID = '-1001677058959'
PRIVATE_CHAT_ID = '-1002008772427'
config = load_config(".env")

PHOTO_ID_DICT = {
    1: config.media.check_crypto_pay_photos[0],
    2: config.media.check_crypto_pay_photos[1],
    3: config.media.check_crypto_pay_photos[2],
    4: config.media.check_crypto_pay_photos[3]
}

VIDEO_FILE_ID = config.media.check_crypto_pay_video


def start_celery_worker():
    """Start the Celery worker process."""
    from celery.bin.worker import worker
    worker_instance = worker()
    argv = [
        "worker",  # Command
        "--loglevel=info",  # Log level
        "--concurrency=1"   # Adjust concurrency as needed
    ]
    worker_instance.run(argv=argv)


def create_hmac(data, key, algo='sha256'):
    try:
        data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        encoded_key = key.encode('utf-8')
        encoded_data = data.encode('utf-8')
        return hmac.new(encoded_key, encoded_data, getattr(hashlib, algo)).hexdigest()
    except Exception as e:
        print(f"Error in HMAC creation: {e}")
        return None


def send_telegram_message(method, chat_id, media_id, caption, buttons=None):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
        payload = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": "HTML",
        }

        if method == "sendPhoto":
            payload["photo"] = media_id
        elif method == "sendVideo":
            payload["video"] = media_id

        if buttons:
            payload["reply_markup"] = json.dumps({"inline_keyboard": buttons})

        response = requests.post(url, json=payload)
        if not response.ok:
            print(f"Failed to send message: {response.text}")
        return response.ok
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


def send_telegram_text_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def create_invite_link(target_chat_id):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/createChatInviteLink"
        payload = {
            "chat_id": target_chat_id,
            "member_limit": 1
        }
        response = requests.post(url, json=payload)
        if response.ok:
            return response.json().get('result', {}).get('invite_link')
        print(f"Failed to create invite link: {response.text}")
        return None
    except Exception as e:
        print(f"Error creating invite link: {e}")
        return None


def unban_user_from_chat_or_channel(chat_id, user_id):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/unbanChatMember"
        payload = {
            "chat_id": chat_id,
            "user_id": user_id
        }
        response = requests.post(url, json=payload)
        if response.ok:
            print(f"User {user_id} unbanned successfully from chat {chat_id}.")
        else:
            print(f"Failed to unban user {user_id} from chat {chat_id}: {response.text}")
        return response.ok
    except Exception as e:
        print(f"Error unbanning user {user_id} from chat {chat_id}: {e}")
        return False


@celery.task
def send_video_notification(chat_id, user_full_name):
    try:
        import time
        time.sleep(1800)  # Delay for 1800 seconds
        caption_video = (
            f"{user_full_name}, приветствуем тебя, бро!\n\n"
            "Я заявляю с полной уверенностью, что знаю все, что ты хочешь получить в этой жизни.\n"
            "Я знаю как тебе это дать!\n\n"
            "<b>ТЫ ХОЧЕШЬ ТРЁХ ВЕЩЕЙ — ТРАХАТЬСЯ, ВЫЖИТЬ И БЫТЬ ЛУЧШЕ ОСТАЛЬНЫХ.</b>\n\n"
            "В закрепе канала ты найдёшь:\n"
            "1 — первый пост (начни с него)\n"
            "2 — навигацию по темам для удобства и поиска информации (в описании канала)\n"
            "3 — Не забудь вступить в ЧАТ для общения с парнями\n\n"
            "Переходи по кнопке ИНСТРУКЦИЯ для новичка и начинай собирать эту жизнь!"
        )
        buttons_video = [
            [{"text": "1️⃣ Изучить для начала", "url": "https://telegra.ph/S-chego-nachat-chitat-privatnyj-kanal-12-23"}]
        ]
        send_telegram_message("sendVideo", chat_id, VIDEO_FILE_ID, caption_video, buttons_video)
    except Exception as e:
        print(f"Error in send_video_notification: {e}")


async def handle_request(request):
    # Existing logic remains the same...
    pass


# Custom ASGI wrapper for aiohttp
class ASGIWrapper:
    def __init__(self, aiohttp_app):
        self.aiohttp_app = aiohttp_app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            raise NotImplementedError("Only HTTP connections are supported.")
        aiohttp_app = self.aiohttp_app

        async def asgi_receive():
            message = await receive()
            return message

        async def asgi_send(message):
            await send(message)

        await aiohttp_app(scope, asgi_receive, asgi_send)


if __name__ == '__main__':
    # Start Celery worker in a separate process
    celery_process = Process(target=start_celery_worker)
    celery_process.start()

    # Start the ASGI server
    uvicorn.run(ASGIWrapper(app), host='0.0.0.0', port=5000)

    # Wait for Celery process to finish
    celery_process.join()
