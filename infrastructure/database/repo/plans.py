from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from infrastructure.database.models.plans import Plan
from infrastructure.database.repo.base import BaseRepo


class PlanRepo(BaseRepo):
    async def get_or_create_plan(
        self,
        name: str,
        original_price: float,
        discounted_price: float,
        duration: str,
    ) -> Optional[Plan]:
        """
        Creates or updates a plan in the database and returns the plan object.
        :param name: The name of the plan.
        :param original_price: The original price of the plan.
        :param discounted_price: The discounted price of the plan.
        :param duration: The duration of the plan.
        :return: Plan object, None if there was an error while making a transaction.
        """

        insert_stmt = (
            insert(Plan)
            .values(
                name=name,
                original_price=original_price,
                discounted_price=discounted_price,
                duration=duration,
            )
            .on_conflict_do_update(
                index_elements=[Plan.name],
                set_=dict(
                    original_price=original_price,
                    discounted_price=discounted_price,
                    duration=duration,
                ),
            )
            .returning(Plan)
        )
        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()

    async def select_plan(self, plan_id: int) -> Optional[Plan]:
        """
        Retrieves a plan by its ID.
        :param plan_id: The ID of the plan.
        :return: Plan object, or None if not found.
        """
        query = select(Plan).filter(Plan.id == plan_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def select_plan_sum(self, sum: int) -> Optional[Plan]:
        """
        Retrieves a plan by its ID.
        :param plan_id: The ID of the plan.
        :return: Plan object, or None if not found.
        """
        query = select(Plan).filter(Plan.discounted_price == sum)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_plans(self) -> List[Plan]:
        """
        Retrieves all plans from the database.
        :return: A list of Plan objects.
        """
        query = select(Plan).order_by(Plan.id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_plans_by_discounted_price(self, price: float) -> Plan:
        """
        Retrieves all plans with a discounted price equal to the specified amount.
        :param price: Discounted price to filter plans.
        :return: A list of Plan objects.
        """
        try:
            query = select(Plan).filter(Plan.discounted_price == price).order_by(Plan.discounted_price)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching plans with discounted price == {price}: {e}")
