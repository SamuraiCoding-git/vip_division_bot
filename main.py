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


def send_telegram_message(chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        response = requests.post(url, json=payload)
        return response.ok
    except Exception as e:
        print(f"Failed to send message: {e}")
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
    print("YES")
    try:
        # Extract headers
        headers = request.headers

        # Validate the request body
        if not request.json:
            raise ValueError('Request body is empty')

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
            chat_id = await repo.orders.get_user_by_order_id(request.json['order_id'])
            if not chat_id:
                raise ValueError('User chat ID not provided')

        # Generate invite links for the private channel and chat
        channel_invite_link = create_invite_link(PRIVATE_CHANNEL_ID)
        chat_invite_link = create_invite_link(PRIVATE_CHAT_ID)

        # Ensure invite links were successfully created
        if not channel_invite_link or not chat_invite_link:
            raise ValueError('Failed to create invite links')

        # Compose and send the notification message
        message = (
            f"Your payment was successful! 🎉\n\n"
            f"Join our private channel: {channel_invite_link}\n"
            f"Join our private chat: {chat_invite_link}"
        )
        if not send_telegram_message(chat_id, message):
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
