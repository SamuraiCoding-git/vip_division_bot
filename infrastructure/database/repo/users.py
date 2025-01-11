from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models import User
from infrastructure.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    async def get_or_create_user(
        self,
        id: int,
        full_name: str,
        username: Optional[str] = None,
        plan_id: Optional[int] = None,
    ) -> Optional[User]:
        """
        Creates or updates a new user in the database and returns the user object.
        :param id: The user's ID.
        :param full_name: The user's full name.
        :param username: The user's username. It's an optional parameter.
        :param plan_id: The ID of the plan the user has purchased. It's an optional parameter.
        :return: User object, None if there was an error while making a transaction.
        """

        insert_stmt = (
            insert(User)
            .values(
                id=id,
                username=username,
                full_name=full_name,
                plan_id=plan_id,
            )
            .on_conflict_do_update(
                index_elements=[User.id],
                set_=dict(
                    username=username,
                    full_name=full_name,
                    plan_id=plan_id,
                ),
            )
            .returning(User)
        )
        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()

    async def select_user(self, user_id: int) -> Optional[User]:
        query = select(User).filter(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_plan_id(self, user_id: int, new_plan_id: int) -> User:
        # Create the update statement
        update_stmt = (
            update(User)
            .where(User.id == user_id)
            .values(plan_id=new_plan_id)
            .returning(User)
        )

        # Execute the update
        result = await self.session.execute(update_stmt)

        # Commit the transaction
        await self.session.commit()

        # Return the updated user object
        return result.scalar_one()

    async def update_recurrence(self, user_id: int, is_recurrent: bool) -> User:
        # Create the update statement
        update_stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_recurrent=is_recurrent)
            .returning(User)
        )

        # Execute the update
        result = await self.session.execute(update_stmt)

        # Commit the transaction
        await self.session.commit()

        # Return the updated user object
        return result.scalar_one()
