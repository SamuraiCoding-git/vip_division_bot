from typing import Optional, Dict

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from infrastructure.database.models import Setting
from infrastructure.database.repo.base import BaseRepo


class SettingRepo(BaseRepo):
    async def get_setting(self) -> Optional[Setting]:
        """
        Retrieves the Setting object. Assumes there is only one row in the table.
        :return: Setting object, or None if not found.
        """
        try:
            query = select(Setting).limit(1)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching setting: {e}")

    async def update_payment_status(self, is_active: bool, id: int) -> Optional[Setting]:
        """
        Updates the payment status in the Setting table.
        :param is_active: New payment status.
        :param id: The ID of the setting to update.
        :return: Updated Setting object, or None if the update fails.
        """
        try:
            setting = await self.session.get(Setting, id)
            if not setting:
                raise Exception(f"Setting with id {id} not found.")

            setting.value = is_active
            await self.session.commit()
            return setting
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error updating payment status: {e}")

    async def delete_setting(self) -> bool:
        """
        Deletes the Setting row from the database. Assumes only one row exists.
        :return: True if deletion was successful, False otherwise.
        """
        try:
            setting = await self.get_setting()
            if not setting:
                return False

            await self.session.delete(setting)
            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Error deleting setting: {e}")

    async def get_all_settings_as_dict(self) -> Dict[int, Dict[str, Optional[bool]]]:
        """
        Retrieves all settings as a dictionary with id as key and all properties as a nested dictionary.
        :return: Dictionary with ids as keys and their properties as nested dictionaries.
        """
        try:
            setting = await self.get_setting()
            if not setting:
                return {}

            return {setting.id: {column.name: getattr(setting, column.name) for column in Setting.__table__.columns}}
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching all settings as dictionary: {e}")
