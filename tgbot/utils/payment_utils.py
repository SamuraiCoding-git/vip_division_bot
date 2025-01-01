import hashlib
import uuid

import pyqrcode
import requests
import matplotlib.pyplot as plt
from PIL import Image


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
    # Подготовка данных
    data = {
        "client_id": client_id,
        "order_id": order_id,
        "products": products,
        "do": "link",
        "sys": "vipdivision",
    }

    # Функция для генерации подписи
    def generate_signature(data, secret_key):
        # Преобразование вложенных структур в строковый формат
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

        # Уплощение данных
        flat_data = flatten(data)

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
    """
    Генерация SHA256 подписи на основе данных и секретного ключа.
    :param data: dict, данные для подписи
    :param secret_key: str, секретный ключ
    :return: str, подпись
    """
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

    flat_data = flatten(data)
    sorted_items = sorted(flat_data.items())
    sign_string = "&".join(f"{key}={value}" for key, value in sorted_items) + secret_key
    return hashlib.sha256(sign_string.encode('utf-8')).hexdigest()

def process_payment(binding_id, client_id, sys, secret_key, api_url):
    """
    Выполняет оплату по токену через API платежной формы.

    :param binding_id: str, платежный токен
    :param client_id: str, уникальный идентификатор пользователя
    :param sys: str, код системы
    :param secret_key: str, секретный ключ для подписи
    :param api_url: str, URL API платежной формы
    :return: dict, результат запроса
    """
    data = {
        "binding_id": binding_id,
        "client_id": client_id,
        "sys": sys
    }

    # Генерация подписи
    signature = generate_signature(data, secret_key)
    data["signature"] = signature

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response_data = response.json()
        return response_data
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def generate_qr_code(link: str):
    unique_filename = f"qr_code_{uuid.uuid4().hex}.png"

    # Create the QR code
    qr_code = pyqrcode.create(link)

    # Save the QR code as a PNG file
    qr_code.png(unique_filename, scale=10)

    return unique_filename

# # Пример использования
# secret_key = "your_secret_key_for_token_payment"
# api_url = "https://producer.payform.ru/rest/payment/do"
# binding_id = "example_token"
# client_id = "unique_client_id"
# sys = "yoursystem"
#
# result = process_payment(binding_id, client_id, sys, secret_key, api_url)
# print(result)
