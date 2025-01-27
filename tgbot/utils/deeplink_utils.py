import hmac
import hashlib
import json
import base64

def generate_signature(data: dict, secret_key: str) -> str:
    json_data = json.dumps(data, separators=(",", ":"), sort_keys=True)
    return hmac.new(secret_key.encode(), json_data.encode(), hashlib.sha256).hexdigest()

def create_deep_link(bot_username: str, action: str, params: dict, secret_key: str) -> str:
    data = {"action": action, "params": params}
    signature = generate_signature(data, secret_key)
    encoded_data = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    return f"https://t.me/{bot_username}?start={encoded_data}&signature={signature}"

def verify_deep_link(encoded_data: str, signature: str, secret_key: str) -> bool:
    try:
        decoded_data = json.loads(base64.urlsafe_b64decode(encoded_data.encode()).decode())
        expected_signature = generate_signature(decoded_data, secret_key)
        return hmac.compare_digest(expected_signature, signature)
    except Exception:
        return False

def base62_encode(num: int) -> str:
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(chars)
    encoded = []
    while num > 0:
        num, rem = divmod(num, base)
        encoded.append(chars[rem])
    return ''.join(reversed(encoded))

def base62_decode(encoded: str) -> int:
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(chars)
    decoded = 0
    for char in encoded:
        decoded = decoded * base + chars.index(char)
    return decoded


# Пример использования
secret_key = "863a1ad48740fb3ed13650052a7d9beb6cf41a25e33fa1c118a6001fcf7cead8"
bot_username = "VipDivision_bot"
action = "gift"
params = {"plan_id": 123, "user_id": 456}

# Создание диплинка
deep_link = create_deep_link(bot_username, action, params, secret_key)
print("Сгенерированный диплинк:", deep_link)

# Расшифровка и верификация диплинка
encoded_data, signature = deep_link.split("?start=")[1].split("&signature=")
is_valid = verify_deep_link(encoded_data, signature, secret_key)
print("Диплинк валиден:", is_valid)
