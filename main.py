import hashlib
import hmac
import json
from datetime import datetime, timedelta
import requests
from aiohttp import web
from multiprocessing import Process
from celery import Celery
from celery.bin.worker import worker
from tgbot.config import load_config
from tgbot.utils.db_utils import get_repo

# Redis и Celery конфигурация
REDIS_URL = "redis://:B7dG39pFzKvXrQwL5M2N8T1C4J6Y9H3P7Xv5RfQK2W8L9Z3TpVJ@92.119.114.185:6379/0"
celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

# Конфигурация приложения
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
    """Запускаем Celery Worker."""
    argv = [
        "worker",  # Команда запуска worker
        "-A", "main",  # Указываем модуль, где определён Celery (main.py)
        "--loglevel=info",  # Уровень логов
        "--concurrency=1",  # Количество потоков (можно увеличить)
    ]
    worker().run(argv=argv)


async def handle_request(request):
    """Обработчик HTTP-запросов."""
    return web.json_response({'message': 'success'}, status=200)


# Определяем приложение aiohttp
app = web.Application()
app.router.add_post('/', handle_request)


# Обёртка ASGI для aiohttp
class ASGIWrapper:
    def __init__(self, aiohttp_app):
        self.aiohttp_app = aiohttp_app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            raise NotImplementedError("Только HTTP-соединения поддерживаются.")
        aiohttp_app = self.aiohttp_app

        async def asgi_receive():
            message = await receive()
            return message

        async def asgi_send(message):
            await send(message)

        await aiohttp_app(scope, asgi_receive, asgi_send)


if __name__ == '__main__':
    import uvicorn

    # Запускаем Celery worker в отдельном процессе
    celery_process = Process(target=start_celery_worker)
    celery_process.start()

    # Запускаем сервер Uvicorn
    uvicorn.run(ASGIWrapper(app), host='0.0.0.0', port=5000)

    # Завершаем процесс Celery worker при остановке основного скрипта
    celery_process.join()
