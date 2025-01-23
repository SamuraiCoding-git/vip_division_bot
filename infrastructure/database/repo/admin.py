from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from infrastructure.database.models import User
from infrastructure.database.models.admin import Admin
from infrastructure.database.repo.base import BaseRepo


class AdminRepo(BaseRepo):
    async def _get_admin_by_id(self, admin_id: int) -> Optional[Admin]:
        """
        Helper method to fetch an admin by its ID.
        :param admin_id: The ID of the admin.
        :return: Admin object, or None if not found.
        """
        query = select(Admin).filter(Admin.id == admin_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create_admin(
            self,
            id: int
    ) -> Optional[Admin]:
        try:
            admin = await self.session.get(Admin, id)
            if admin:
                return admin

            admin = Admin(id=id)
            self.session.add(admin)

            await self.session.commit()
            return admin
        except Exception as e:
            await self.session.rollback()
            print(f"Error in get_or_create_admin: {e}")
            return None

    async def select_admin(self, admin_id: int) -> Optional[Admin]:
        """
        Retrieves an admin by its ID.
        :param admin_id: The ID of the admin.
        :return: Admin object, or None if not found.
        """
        try:
            admin = await self._get_admin_by_id(admin_id)
            return admin
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching admin by id {admin_id}: {e}")

    async def get_all_admins(self) -> List[Admin]:
        """
        Retrieves all admins from the database.
        :return: A list of Admin objects.
        """
        try:
            query = select(Admin).order_by(Admin.id)
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching all admins: {e}")

    async def get_all_admins_user_objects(self) -> List[Tuple[Admin, User]]:
        """
        Retrieves all Admin objects along with their associated User objects.
        :return: A list of tuples (Admin, User).
        """
        try:
            query = select(Admin).options(joinedload(Admin.user)).order_by(Admin.id)
            result = await self.session.execute(query)
            admins = result.scalars().all()
            return [(admin, admin.user) for admin in admins]
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching all admins with user objects: {e}")

    async def delete_admin(self, admin_id: int) -> bool:
        """
        Deletes an admin from the database.
        :param admin_id: The ID of the admin to be deleted.
        :return: True if deletion was successful, False otherwise.
        """
        try:
            admin = await self._get_admin_by_id(admin_id)
            if not admin:
                return False

            await self.session.delete(admin)
            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()  # Rollback on error
            raise Exception(f"Error deleting admin {admin_id}: {e}")
