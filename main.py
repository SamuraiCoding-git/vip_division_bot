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

    # Create the worker instance
    worker_instance = worker()

    # Define worker arguments
    argv = [
        "worker",  # Celery worker command
        "-A", "main",  # Replace 'main' with the name of your script (without .py)
        "--loglevel=info",  # Log level
        "--concurrency=1",  # Adjust concurrency based on your needs
    ]

    # Run the worker with the specified arguments
    worker_instance.run(argv=argv)


async def handle_request(request):
    return web.json_response({'message': 'success'}, status=200)


# Define the aiohttp app
app = web.Application()
app.router.add_post('/', handle_request)


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
    import uvicorn

    # Start Celery worker in a separate process
    celery_process = Process(target=start_celery_worker)
    celery_process.start()

    # Start the ASGI server with aiohttp
    uvicorn.run(ASGIWrapper(app), host='0.0.0.0', port=5000)

    # Ensure the Celery worker terminates gracefully
    celery_process.join()
