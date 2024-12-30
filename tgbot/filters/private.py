from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message


class IsPrivateFilter(BaseFilter):
    is_private: bool = True

    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        if isinstance(obj, Message):
            return False if obj.from_user.id != 422999166 else True
            # return (obj.chat.type == "private") == self.is_private
        elif isinstance(obj, CallbackQuery):
            return False if obj.message.chat.id != 422999166 else True
            # return (obj.message.chat.type == "private") == self.is_private
        return False