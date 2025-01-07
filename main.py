import json
import hmac
import hashlib
import requests
from flask import Flask, request, jsonify

from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_session_pool
from tgbot.config import load_config

app = Flask(__name__)

SECRET_KEY = 'd9d0503a2e263c392aa3397614c342113ac8998446913247d238398dcab1091c'
TELEGRAM_BOT_TOKEN = '7926443493:AAF2mhVZivQttPdVjO4VC5HQK2RLHfAnUu8'
PRIVATE_CHANNEL_ID = '-1001677058959'  # Replace with your private channel's ID
PRIVATE_CHAT_ID = '-1002008772427'  # Replace with your private chat's ID
config = load_config(".env")

# Define photo IDs for each plan
PHOTO_ID_DICT = {
    1: "AgACAgIAAxkBAALEjGdy0mrDQWi18wFpYoZq9NVA2TqjAAKV6TEbOoaJS4n3s7ggUnRgAQADAgADeQADNgQ",  # Replace with actual photo_id for plan 1
    2: "AgACAgIAAxkBAALEimdy0mogvij5Ftf2H8gl35umq8q3AAKS6TEbOoaJSyo0D53HGSccAQADAgADeQADNgQ",
    3: "AgACAgIAAxkBAALVIGdz6Q6rehB64Lr3d9PdSyHCntiHAAKy5jEb3eahS01IU1EPEcbzAQADAgADeQADNgQ",# Replace with actual photo_id for plan 2
    4: "AgACAgIAAxkBAALEi2dy0mq9sEozgl_G_TSMMQTr6Xv4AAKT6TEbOoaJS3CNhv-ILUFiAQADAgADeQADNgQ"   # Replace with actual photo_id for plan 3
}


def create_hmac(data, key, algo='sha256'):
    try:
        data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        encoded_key = key.encode('utf-8')
        encoded_data = data.encode('utf-8')
        return hmac.new(encoded_key, encoded_data, getattr(hashlib, algo)).hexdigest()
    except Exception as e:
        return None


def verify_hmac(data, key, sign, algo='sha256'):
    calculated_sign = create_hmac(data, key, algo)
    return calculated_sign and calculated_sign.lower() == sign.lower()


def send_telegram_photo(chat_id, photo_id, caption, buttons=None):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": photo_id,
            "caption": caption,
            "parse_mode": "HTML"  # Optional: For formatting the message
        }
        if buttons:
            payload["reply_markup"] = json.dumps({"inline_keyboard": buttons})

        response = requests.post(url, json=payload)
        return response.ok
    except Exception as e:
        print(f"Failed to send photo: {e}")
        return False


def send_telegram_video(chat_id, video_id, caption, buttons=None):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
        payload = {
            "chat_id": chat_id,
            "video": video_id,
            "caption": caption,
            "parse_mode": "HTML"  # Optional: For formatting the message
        }
        if buttons:
            payload["reply_markup"] = json.dumps({"inline_keyboard": buttons})

        response = requests.post(url, json=payload)
        if not response.ok:
            print(f"Failed to send video: {response.text}")
        return response.ok
    except Exception as e:
        print(f"Failed to send video: {e}")
        return False


def create_invite_link(target_chat_id):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/createChatInviteLink"
        payload = {
            "chat_id": target_chat_id,
            "member_limit": 1  # Allow only one person to join
        }
        response = requests.post(url, json=payload)
        if response.ok:
            return response.json().get('result', {}).get('invite_link')
        else:
            print(f"Failed to create invite link: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating invite link: {e}")
        return None


@app.route('/', methods=['POST'])
async def process_request():
    try:
        # Извлечение данных из формы
        form_data = request.form
        form_dict = form_data.to_dict()

        if form_dict['payment_status'] == 'success' and form_dict['payment_init'] == 'api':
            return jsonify({'message': 'success'}), 200

        # Создание пула сессий базы данных
        session_pool = await create_session_pool(config.db)

        async with session_pool() as session:
            repo = RequestsRepo(session)
            # Получение информации о пользователе и заказе
            user = await repo.users.select_user(int(form_dict['client_id']))
            chat_id = user.id
            if not chat_id:
                raise ValueError('User chat ID not provided')

        # Проверка корректности плана подписки
        order = await repo.orders.get_order_by_id(int(form_dict['order_num']))
        await repo.orders.update_order_payment_status(int(form_dict['order_num']), True, form_dict['binding_id'])
        plan_id = order.plan_id
        await repo.users.update_plan_id(chat_id, int(plan_id))
        if plan_id not in PHOTO_ID_DICT:
            raise ValueError('Invalid plan_id provided')

        # Получение photo_id для указанного плана
        photo_id = PHOTO_ID_DICT[plan_id]

        # Генерация ссылок-приглашений
        channel_invite_link = create_invite_link(PRIVATE_CHANNEL_ID)
        chat_invite_link = create_invite_link(PRIVATE_CHAT_ID)

        # Проверка успешности создания ссылок
        if not channel_invite_link or not chat_invite_link:
            raise ValueError('Failed to create invite links')

        # Отправка фото с кнопками
        caption = "✅ Подписка на канал успешно оформлена!\nПерeходи по кнопкам ниже:"
        buttons = [
            [
                {"text": "🔺 ВСТУПИТЬ В КАНАЛ", "url": channel_invite_link}
            ],
            [
                {"text": "🔺 ВСТУПИТЬ В ЧАТ", "url": chat_invite_link}
            ]
        ]
        if not send_telegram_photo(chat_id, photo_id, caption, buttons):
            raise ValueError('Failed to send notification to user')

        VIDEO_FILE_ID = "BAACAgIAAxkBAALmHGd4rRnMKnmvZnp2ziGvf9VqZZsUAAJcXQACQzDJS1VissnlL4f0NgQ"

        caption = (
            f"{user.full_name}, приветствуем тебя, бро, ты попал в лучшее мужское комьюнити 🤝\n\n"
            "Я заявляю с полной уверенностью, что знаю все, что ты хочешь получить в этой жизни.\n"
            "Я знаю как тебе это дать!\n\n"
            "<b>ТЫ ХОЧЕШЬ ТРЁХ ВЕЩЕЙ — ТРАХАТЬСЯ, ВЫЖИТЬ И БЫТЬ ЛУЧШЕ ОСТАЛЬНЫХ.</b>\n\n"
            "В закрепе канала ты найдёшь:\n"
            "1 — первый пост (начни с него)\n"
            "2 — навигацию по темам для удобства и поиска информации (в описании канала)\n"
            "3 — Не забудь вступить в ЧАТ для общения с парнями\n\n"
            "Переходи по кнопке ИНСТРУКЦИЯ для новичка и начинай собирать эту жизнь!"
        )

        buttons = [
            [
                {"text": "1️⃣ Изучить для начала", "url": "https://telegra.ph/S-chego-nachat-chitat-privatnyj-kanal-12-23"}
            ]
        ]

        if not send_telegram_video(chat_id, VIDEO_FILE_ID, caption, buttons):
            raise ValueError('Failed to send video to user')
        # Успешный ответ
        return jsonify({'message': 'success'}), 200

    except ValueError as e:
        # Обработка ошибок валидации
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        # Общая обработка неожиданных ошибок
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
