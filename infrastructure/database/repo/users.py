from typing import Optional, List

from sqlalchemy import select, update, literal, and_, not_, func, text, cast, DateTime
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models import User, Order
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

    async def get_eligible_orders(
        self,
        plan_id: int = 1,
        start_date_range: tuple[str, str] = ("2024-12-12", "2024-12-16"),
    ) -> List[Order]:
        """
        Fetch eligible orders based on the provided conditions:
        - Plan ID is 1.
        - Start date is at least 30 days old but within the specified range.
        - The order is paid.
        - No other recent orders exist for the same user with the same plan.

        :param plan_id: The plan ID to filter orders. Default is 1.
        :param start_date_range: A tuple containing the start and end dates as strings in 'YYYY-MM-DD' format.
        :return: A list of eligible orders.
        """
        # Convert date strings to datetime.date objects
        start_date_start = datetime.strptime(start_date_range[0], "%Y-%m-%d")
        start_date_end = datetime.strptime(start_date_range[1], "%Y-%m-%d")

        # Define the interval as a text literal
        thirty_days_ago_interval = text("now() - interval '30 days'")

        # Subquery for recent orders
        recent_orders_subquery = (
            select(literal(1))
            .where(
                and_(
                    Order.user_id == Order.user_id,
                    Order.plan_id == plan_id,
                    Order.start_date > thirty_days_ago_interval,
                    Order.is_paid == True,
                )
            )
            .exists()
        )

        # Main query for eligible orders
        query = (
            select(Order)
            .where(
                and_(
                    Order.plan_id == plan_id,
                    Order.start_date <= thirty_days_ago_interval,
                    Order.start_date.between(start_date_start, start_date_end),
                    Order.is_paid == True,
                    not_(recent_orders_subquery),
                )
            )
        )

        # Execute the query
        result = await self.session.execute(query)

        # Return the list of eligible orders
        return result.scalars().all()
