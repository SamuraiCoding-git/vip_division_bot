import hashlib
import hmac
import json
import uuid
from typing import Mapping

import pyqrcode
import requests

def generate_payment_link(client_id, order_id, products, secret_key, linktoform):
    """
    Генерирует ссылку для оплаты на основе переданных данных заказа и товаров.

    :param client_id: str, ID клиента
    :param order_id: str, ID заказа
    :param products: list, список товаров (каждый товар - это словарь с полями name, price, quantity, sku)
    :param secret_key: str, секретный ключ для подписи
    :param linktoform: str, базовый URL формы оплаты
    :return: str, ссылка для оплаты
    """

    text = (f"Спасибо за покупку подписки “VipDivision” за {products[0]['price']}.Чтобы получить доступ перейдите по ссылке https://t.me/VipDivision_bot")

    # Подготовка данных
    data = {
        "client_id": client_id,
        "order_id": order_id,
        "products": products,
        "do": "link",
        "sys": "vipdivision",
        "paid_content": text
    }

    # Генерация подписи
    signature = generate_signature(data, secret_key)
    data["sign"] = signature

    # Упрощение данных для строки запроса
    flat_data = flatten_data(data)

    # Формирование строки запроса
    query_string = "&".join(f"{key}={value}" for key, value in flat_data.items())
    full_url = f"{linktoform}?{query_string}"
    print(full_url)

    # Отправка GET-запроса
    response = requests.get(full_url)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Ошибка при запросе: {response.status_code}, {response.text}")


def generate_signature(data, secret_key):
    # Преобразование вложенных структур в строковый формат
    # Уплощение данных
    flat_data = flatten_data(data)

    # Сортировка параметров по ключам
    sorted_items = sorted(flat_data.items())
    sign_string = "&".join(f"{key}={value}" for key, value in sorted_items) + secret_key

    # Генерация SHA256 подписи
    return hashlib.sha256(sign_string.encode('utf-8')).hexdigest()


# Упрощение данных для строки запроса
def flatten_data(data):
    def flatten(data, parent_key=""):
        items = []
        for key, value in data.items():
            new_key = f"{parent_key}[{key}]" if parent_key else key
            if isinstance(value, dict):
                items.extend(flatten(value, new_key).items())
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    items.extend(flatten(item, f"{new_key}[{i}]").items())
            else:
                items.append((new_key, str(value)))
        return dict(items)

    return flatten(data)


def _sort(data):
    """Recursively sort the dictionary."""
    if isinstance(data, Mapping):
        return {k: _sort(v) for k, v in sorted(data.items())}
    elif isinstance(data, list):
        return [_sort(v) for v in sorted(data)]
    else:
        return data


def create(data, key, algo='sha256'):
    """Create an HMAC signature."""
    if algo not in hashlib.algorithms_available:
        return False

    # Ensure data is a dictionary
    if not isinstance(data, (dict, list)):
        data = [data]

    # Convert all values to strings
    def stringify(item):
        if isinstance(item, dict):
            return {k: stringify(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [stringify(i) for i in item]
        else:
            return str(item)

    data = stringify(data)

    # Sort the data
    data = _sort(data)

    # Encode as JSON
    json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

    # Create the HMAC signature
    signature = hmac.new(key.encode('utf-8'), json_data.encode('utf-8'), getattr(hashlib, algo))

    return signature.hexdigest()


def process_payment(binding_id, client_id, sys, secret_key, api_url, order_sum):
    print("process_payment")
    data = {
        "binding_id": binding_id,
        "client_id": client_id,
        "sys": sys,
        'order_sum': order_sum
    }
    # Генерация подписи
    signature = create(data, secret_key)
    data["signature"] = signature

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(api_url + "/rest/payment/do", headers=headers, data=data)
        response_data = response.json()
        print(response_data)
        return response_data
    except Exception as e:
        print(e)
        return {"success": False, "error": str(e)}

def generate_qr_code(link: str):
    unique_filename = f"qr_code_{uuid.uuid4().hex}.png"

    # Create the QR code
    qr_code = pyqrcode.create(link)

    # Save the QR code as a PNG file
    qr_code.png(unique_filename, scale=10)

    return unique_filename

# Пример использования
# secret_key = "d9d0503a2e263c392aa3397614c342113ac8998446913247d238398dcab1091c"
# api_url = "https://vipdivision.payform.ru/rest/payment/do"
# binding_id = "406a979714f390e058a8c3511837e0cc"
# client_id = "422999166"
# sys = "vipdivision"

# result = process_payment(binding_id, client_id, sys, secret_key, api_url)
# print(result)
