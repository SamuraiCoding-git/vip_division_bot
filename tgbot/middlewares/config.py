from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from tgbot.utils.db_utils import get_repo


class ConfigMiddleware(BaseMiddleware):
    def __init__(self, config) -> None:
        self.config = config

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        data["config"] = self.config
        repo = await get_repo(self.config)
        is_blocked = await repo.blacklist.is_blocked(event.from_user.id)
        if is_blocked:
            return
        return await handler(event, data)
