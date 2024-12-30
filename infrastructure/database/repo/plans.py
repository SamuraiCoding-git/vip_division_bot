from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

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

    async def get_all_plans(self) -> List[Plan]:
        """
        Retrieves all plans from the database.
        :return: A list of Plan objects.
        """
        query = select(Plan)
        result = await self.session.execute(query)
        return result.scalars().all()
