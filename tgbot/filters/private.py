from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message


class IsPrivateFilter(BaseFilter):
    is_private: bool = True

    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        if isinstance(obj, Message):
            return (obj.chat.type == "private") == self.is_private
        elif isinstance(obj, CallbackQuery):
            return (obj.message.chat.type == "private") == self.is_private
        return False