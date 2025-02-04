import hashlib
import hmac
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import requests
from aiohttp import web

from tgbot.config import load_config
from tgbot.utils.db_utils import get_repo

# Конфигурация
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

# Пул потоков для фоновых задач
executor = ThreadPoolExecutor(max_workers=5)

def create_hmac(data, key, algo='sha256'):
    """Создание HMAC."""
    try:
        data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        encoded_key = key.encode('utf-8')
        encoded_data = data.encode('utf-8')
        return hmac.new(encoded_key, encoded_data, getattr(hashlib, algo)).hexdigest()
    except Exception as e:
        print(f"Error in HMAC creation: {e}")
        return None

def send_telegram_message(method, chat_id, media_id=None, caption=None, buttons=None):
    """Отправка сообщения в Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
        payload = {
            "chat_id": chat_id,
            "parse_mode": "HTML",
        }
        if caption:
            payload["caption"] = caption
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
    """Отправка текстового сообщения в Telegram."""
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
    """Создание ссылки-приглашения."""
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

def is_user_admin(chat_id, user_id):
    """Проверяет, является ли пользователь администратором чата"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChatMember"
        payload = {"chat_id": chat_id, "user_id": user_id}
        response = requests.post(url, json=payload)
        if response.ok:
            result = response.json().get("result", {})
            status = result.get("status")
            return status in ["administrator", "creator"]
        print(f"Failed to get chat member info: {response.text}")
        return False
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False

def unban_user_from_chat_or_channel(chat_id, user_id):
    """Разблокировка пользователя в чате/канале, если он не является администратором"""
    if is_user_admin(chat_id, user_id):
        print(f"User {user_id} is an administrator in chat {chat_id}. Skipping unban.")
        return True

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/unbanChatMember"
        payload = {"chat_id": chat_id, "user_id": user_id}
        response = requests.post(url, json=payload)
        if response.ok:
            print(f"User {user_id} unbanned successfully from chat {chat_id}.")
            return True
        else:
            print(f"Failed to unban user {user_id} from chat {chat_id}: {response.text}")
            return False
    except Exception as e:
        print(f"Error unbanning user {user_id} from chat {chat_id}: {e}")
        return False
def send_video_notification(chat_id, user_full_name):
    """Фоновая задача для отправки видео."""
    try:
        import time
        time.sleep(1800)  # Имитация долгой задачи (30 минут)
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
    """Обработчик HTTP-запросов."""
    try:
        form_data = await request.post()
        repo = await get_repo(config)

        user = await repo.users.select_user(int(form_data['client_id']))
        if not user:
            return web.json_response({'error': 'User not found'}, status=404)

        chat_id = user.id

        payment = await repo.payments.get_payment_by_id(int(form_data['order_num']))
        if not payment:
            return web.json_response({'error': 'Payment not found'}, status=404)

        subscription = await repo.subscriptions.get_subscription_by_id(payment.subscription_id)
        if not subscription:
            return web.json_response({'error': 'Payment not found'}, status=404)

        subscription = await repo.subscriptions.update_subscription(
            subscription_id=payment.subscription_id,
            status="active",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=subscription.plan_id)
        )
        payment = await repo.payments.update_payment(
            payment_id=int(form_data['order_num']),
            amount=int(float(form_data['sum'])),
            currency="RUB",
            payment_method="card_ru",
            is_successful=True,
            binding_id=form_data['binding_id']
        )

        photo_id = PHOTO_ID_DICT.get(payment.subscription.plan_id)
        if not photo_id:
            return web.json_response({'error': 'Invalid plan ID'}, status=400)

        channel_invite_link = create_invite_link(PRIVATE_CHANNEL_ID)
        chat_invite_link = create_invite_link(PRIVATE_CHAT_ID)

        if not channel_invite_link or not chat_invite_link:
            return web.json_response({'error': 'Failed to create invite links'}, status=500)

        if subscription.gifted_by:
            gifter = await repo.users.select_user(int(subscription.gifted_by))
            caption_photo = (f"✅ Подписка на канал подарена {gifter.full_name}!\n"
                             "Перeходи по кнопкам ниже:")
            gifter_text = "Подписка успешно подарена!"
            await send_telegram_text_message(chat_id, gifter_text)
        else:
            caption_photo = ("✅ Подписка на канал успешно оформлена!\n"
                             "Перeходи по кнопкам ниже:")
        buttons_photo = [
            [{"text": "🔺 ВСТУПИТЬ В КАНАЛ", "url": channel_invite_link}],
            [{"text": "🔺 ВСТУПИТЬ В ЧАТ", "url": chat_invite_link}]
        ]

        # Отправляем фото уведомление
        if not send_telegram_message("sendPhoto", chat_id, photo_id, caption_photo, buttons_photo):
            return web.json_response({'error': 'Failed to send photo notification'}, status=500)

        # Запускаем фоновую задачу
        executor.submit(send_video_notification, chat_id, user.full_name)

        # Разблокируем пользователя в чате и канале
        if not unban_user_from_chat_or_channel(PRIVATE_CHANNEL_ID, chat_id):
            return web.json_response({'error': 'Failed to unban user from private channel'}, status=500)
        if not unban_user_from_chat_or_channel(PRIVATE_CHAT_ID, chat_id):
            return web.json_response({'error': 'Failed to unban user from private chat'}, status=500)

        return web.json_response({'message': 'success'}, status=200)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return web.json_response({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)


app = web.Application()
app.router.add_post('/', handle_request)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)
