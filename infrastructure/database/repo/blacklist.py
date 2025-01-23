from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from infrastructure.database.models import User
from infrastructure.database.models.blacklist import Blacklist
from infrastructure.database.repo.base import BaseRepo


class BlacklistRepo(BaseRepo):
    async def add_to_blacklist(self, user_id: int) -> bool:
        """
        Adds a user to the blacklist.

        :param user_id: User's ID
        :return: True if the user was successfully added, False otherwise
        """
        try:
            # Check if the user exists
            user_query = select(User).filter_by(id=user_id)
            user = (await self.session.execute(user_query)).scalar_one_or_none()
            if not user:
                return False

            # Check if the user is already in the blacklist
            if await self.is_blocked(user_id):
                return False

            # Add user to the blacklist
            blacklist_entry = Blacklist(user_id=user.id)
            self.session.add(blacklist_entry)
            await self.session.commit()
            return True
        except SQLAlchemyError:
            await self.session.rollback()
            return False

    async def remove_from_blacklist(self, user_id: int) -> bool:
        """
        Removes a user from the blacklist.

        :param user_id: User's ID
        :return: True if the user was successfully removed, False otherwise
        """
        try:
            # Check if the user is in the blacklist
            blacklist_query = select(Blacklist).filter_by(user_id=user_id)
            blacklist_entry = (await self.session.execute(blacklist_query)).scalar_one_or_none()
            if not blacklist_entry:
                return False

            # Remove user from the blacklist
            delete_stmt = delete(Blacklist).where(Blacklist.user_id == user_id)
            await self.session.execute(delete_stmt)
            await self.session.commit()
            return True
        except SQLAlchemyError:
            await self.session.rollback()
            return False

    async def is_blocked(self, user_id: int) -> bool:
        """
        Checks if a user is in the blacklist.

        :param user_id: User's ID
        :return: True if the user is in the blacklist, False otherwise
        """
        try:
            blacklist_query = select(Blacklist).filter_by(user_id=user_id)
            blacklist_entry = (await self.session.execute(blacklist_query)).scalar_one_or_none()
            return blacklist_entry is not None
        except SQLAlchemyError:
            return False

    async def get_blacklist(self):
        """
        Retrieves all users in the blacklist.

        :return: List of blacklist entries
        """
        try:
            query = select(Blacklist)
            result = (await self.session.execute(query)).scalars().all()
            return result
        except SQLAlchemyError:
            return []
