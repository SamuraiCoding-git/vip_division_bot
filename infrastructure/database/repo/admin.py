from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
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

    async def create_admin(self, id: int) -> Optional[Admin]:
        """
        Creates a new admin record.
        :param id: The ID of the admin to be created.
        :return: The created Admin object, or None if insertion failed.
        """
        try:
            insert_stmt = (
                insert(Admin)
                .values(id=id)
                .returning(Admin)  # Return the created object
            )

            result = await self.session.execute(insert_stmt)
            await self.session.commit()
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            await self.session.rollback()  # Rollback on error
            raise Exception(f"Error creating admin: {e}")

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
