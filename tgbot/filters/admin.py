from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from tgbot.config import Config
from tgbot.utils.db_utils import get_repo


class AdminFilter(BaseFilter):
    is_admin: bool = True

    @staticmethod
    async def get_admin_ids(config: Config):
        repo = await get_repo(config)
        return [i.id for i in await repo.admins.get_all_admins()]

    async def __call__(self, obj: Message | CallbackQuery, config: Config) -> bool:
        user_id = None
        if isinstance(obj, Message):
            user_id = obj.from_user.id
        elif isinstance(obj, CallbackQuery):
            user_id = obj.message.chat.id

        if user_id is None:
            return False

        return (user_id in await self.get_admin_ids(config)) == self.is_admin
