from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler) -> None:
        super().__init__()
        self.scheduler = scheduler

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        try:
            data["scheduler"] = self.scheduler
            return await handler(event, data)
        except Exception as e:
            raise
