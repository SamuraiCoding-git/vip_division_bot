from aiogram.filters import BaseFilter
from aiogram.types import Message

from tgbot.config import Config
from tgbot.utils.db_utils import get_repo


class AdminFilter(BaseFilter):
    is_admin: bool = True

    @staticmethod
    async def get_admin_ids(config: Config):
        repo = await get_repo(config)
        return [i.id for i in await repo.admins.get_all_admins()]

    async def __call__(self, obj: Message, config: Config) -> bool:
        return (obj.from_user.id in await self.get_admin_ids(config)) == self.is_admin
