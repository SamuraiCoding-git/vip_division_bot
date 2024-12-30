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
    2: "AgACAgIAAxkBAALEimdy0mogvij5Ftf2H8gl35umq8q3AAKS6TEbOoaJSyo0D53HGSccAQADAgADeQADNgQ",  # Replace with actual photo_id for plan 2
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


def create_invite_link(target_chat_id, expire_in=3600):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/createChatInviteLink"
        payload = {
            "chat_id": target_chat_id,
            "expire_date": expire_in,  # Expire after specified seconds
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
    form_data = request.form

    # Convert form data to a dictionary
    form_dict = form_data.to_dict()

    try:
        # Extract headers
        headers = request.headers

        # Ensure signature is provided
        if 'Sign' not in headers:
            raise ValueError('Signature not found in headers')

        # Verify the HMAC signature
        if not verify_hmac(request.json, SECRET_KEY, headers['Sign']):
            raise ValueError('Signature is incorrect')

        # Create a database session pool
        session_pool = await create_session_pool(config.db)

        async with session_pool() as session:
            repo = RequestsRepo(session)
            # Extract chat ID from the request
            user = await repo.orders.get_user_by_order_id(int(form_dict['order_id']))
            order = await repo.orders.get_order_by_id(int(form_dict['order_id']))
            chat_id = user.id
            if not chat_id:
                raise ValueError('User chat ID not provided')

        # Determine the plan_id
        plan_id = order.plan_id
        if plan_id not in PHOTO_ID_DICT:
            raise ValueError('Invalid plan_id provided')

        # Get the photo_id for the specified plan_id
        photo_id = PHOTO_ID_DICT[plan_id]

        # Generate invite links for the private channel and chat
        channel_invite_link = create_invite_link(PRIVATE_CHANNEL_ID)
        chat_invite_link = create_invite_link(PRIVATE_CHAT_ID)

        # Ensure invite links were successfully created
        if not channel_invite_link or not chat_invite_link:
            raise ValueError('Failed to create invite links')

        # Compose and send the photo message with buttons
        caption = "✅ Подписка на канал успешно оформлена!\nПерeходи по кнопкам ниже:"
        buttons = [
            [
                {"text": "🔺 ВСТУПИТЬ В КАНАЛ", "url": channel_invite_link},
                {"text": "🔺 ВСТУПИТЬ В ЧАТ", "url": chat_invite_link}
            ]
        ]
        if not send_telegram_photo(chat_id, photo_id, caption, buttons):
            raise ValueError('Failed to send notification to user')

        # Return success response
        return jsonify({'message': 'success'}), 200

    except ValueError as e:
        # Handle validation and processing errors
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        # Catch-all for any unexpected errors
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
