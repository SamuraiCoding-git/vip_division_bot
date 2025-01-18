import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from infrastructure.database.setup import create_session_pool
from schedulers.base import setup_scheduler
from tgbot.config import load_config, Config
from tgbot.handlers import routers_list
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.database import DatabaseMiddleware
from tgbot.middlewares.scheduler import SchedulerMiddleware
from tgbot.services import broadcaster



from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from tgbot.utils.db_utils import get_repo


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="payment", description="✅ Тарифы"),
        BotCommand(command="start", description="🔄 Перезапустить бота"),
        BotCommand(command="vipdivision", description="🔺 Что такое VIP DIVISION"),
        BotCommand(command="support", description="💎 Поддержка"),
        BotCommand(command="play", description="🎮 Игра"),
        BotCommand(command="subscription", description="⚡ Моя подписка"),
        BotCommand(command="biography", description="🏆 Биография"),
    ]
    await bot.delete_my_commands()
    await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Бот был запущен")


def register_global_middlewares(dp: Dispatcher, config: Config, scheduler, session_pool=None):
    """
    Register global middlewares for the given dispatcher.
    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param dp: The dispatcher instance.
    :type dp: Dispatcher
    :param config: The configuration object from the loaded configuration.
    :param session_pool: Optional session pool object for the database using SQLAlchemy.
    :return: None
    """
    middleware_types = [
        ConfigMiddleware(config),
        SchedulerMiddleware(scheduler),
        DatabaseMiddleware(session_pool),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)

async def get_admin_ids(config: Config):
    repo = await get_repo(config)
    return [i.id for i in await repo.admins.get_all_admins()]

def setup_logging():
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(config):
    """
    Return storage based on the provided configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Storage: The storage object based on the configuration.

    """
    import logging

    if config.tg_bot.use_redis:
        logging.info("Using Redis as FSM storage")
        try:
            # Debug Redis configuration
            logging.info(f"Redis DSN: {config.redis.dsn()}")
            logging.info(f"Redis Host: {config.redis.redis_host}")
            logging.info(f"Redis Port: {config.redis.redis_port}")
            logging.info(f"Redis Password: {config.redis.redis_pass}")

            # Ensure critical parameters are set
            if not config.redis.redis_host or not config.redis.redis_port:
                raise ValueError("Redis configuration is incomplete.")

            # Attempt to create RedisStorage
            storage = RedisStorage.from_url(
                config.redis.dsn(),
                key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
            )
            # Check Redis connection
            logging.info("Redis connection established successfully")
            return storage

        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")
            raise

    else:
        logging.info("Using MemoryStorage as FSM storage")
        return MemoryStorage()

async def main():
    setup_logging()

    config = load_config(".env")
    storage = get_storage(config)

    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher(storage=storage)
    dp.include_routers(*routers_list)
    session_pool = await create_session_pool(config.db, echo=False)
    admin_ids = await get_admin_ids(config)

    scheduler = setup_scheduler(bot, config, storage, session_pool)

    register_global_middlewares(dp, config, scheduler, session_pool)

    await create_session_pool(config.db)
    await set_bot_commands(bot)
    await on_startup(bot, admin_ids)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот был выключен!")
