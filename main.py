import json
import hmac
import hashlib
import requests
from flask import Flask, request, jsonify
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_session_pool
from tgbot.config import load_config
from tgbot.utils.db_utils import get_repo

app = Flask(__name__)

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


@app.route('/', methods=['POST'])
async def process_request():
    try:
        form_data = request.form.to_dict()

        if form_data.get('payment_status') != 'success' and form_data.get('payment_init') != 'api':
            return jsonify({'message': 'Invalid payment status or initiation method'}), 400

        repo = await get_repo(config)
        user = await repo.users.select_user(int(form_data['client_id']))
        if not user:
            return jsonify({'error': 'User not found'}), 404

        chat_id = user.id
        order = await repo.orders.get_order_by_id(int(form_data['order_num']))

        if not order:
            return jsonify({'error': 'Order not found'}), 404

        await repo.orders.update_order_payment_status(order.id, True, form_data.get('binding_id'))
        await repo.users.update_plan_id(chat_id, order.plan_id)

        photo_id = PHOTO_ID_DICT.get(order.plan_id)
        if not photo_id:
            return jsonify({'error': 'Invalid plan ID'}), 400

        channel_invite_link = create_invite_link(PRIVATE_CHANNEL_ID)
        chat_invite_link = create_invite_link(PRIVATE_CHAT_ID)

        if not channel_invite_link or not chat_invite_link:
            return jsonify({'error': 'Failed to create invite links'}), 500

        caption_photo = "✅ Подписка на канал успешно оформлена!\nПерeходи по кнопкам ниже:"
        buttons_photo = [
            [{"text": "🔺 ВСТУПИТЬ В КАНАЛ", "url": channel_invite_link}],
            [{"text": "🔺 ВСТУПИТЬ В ЧАТ", "url": chat_invite_link}]
        ]
        if not send_telegram_message("sendPhoto", chat_id, photo_id, caption_photo, buttons_photo):
            return jsonify({'error': 'Failed to send photo notification'}), 500

        caption_video = (
            f"{user.full_name}, приветствуем тебя, бро!\n\n"
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
        if not send_telegram_message("sendVideo", chat_id, VIDEO_FILE_ID, caption_video, buttons_video):
            return jsonify({'error': 'Failed to send video notification'}), 500

        return jsonify({'message': 'success'}), 200

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
