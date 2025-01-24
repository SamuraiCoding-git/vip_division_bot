from datetime import datetime
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from infrastructure.database.models import Subscription
from infrastructure.database.repo.base import BaseRepo


class SubscriptionRepo(BaseRepo):
    async def get_subscription_by_id(self, subscription_id: int) -> Optional[Subscription]:
        """
        Retrieves a subscription by its ID.
        :param subscription_id: The ID of the subscription.
        :return: Subscription object, or None if not found.
        """
        try:
            subscription = await self.session.get(Subscription, subscription_id)
            return subscription
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching subscription with ID {subscription_id}: {e}")

    async def get_all_subscriptions(self) -> List[Subscription]:
        """
        Retrieves all subscriptions.
        :return: A list of Subscription objects.
        """
        try:
            query = select(Subscription).order_by(Subscription.start_date.desc())
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching all subscriptions: {e}")

    async def create_subscription(
        self,
        user_id: int,
        plan_id: int,
        gifted_by: int,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_recurrent: bool = False,
        is_gifted: bool = False
    ) -> "Subscription":
        """
        Creates a new subscription with mandatory and optional parameters.
        :param user_id: ID of the user.
        :param plan_id: ID of the plan.
        :param gifted_by: ID of the user who gifted the subscription.
        :param status: Status of the subscription.
        :param start_date: Start date of the subscription.
        :param end_date: End date of the subscription.
        :param is_recurrent: Indicates if the subscription is recurrent.
        :param is_gifted: Indicates if the subscription is gifted.
        :return: The created Subscription object.
        """
        try:
            subscription = Subscription(
                user_id=user_id,
                plan_id=plan_id,
                gifted_by=gifted_by,
                status=status,
                start_date=start_date,
                end_date=end_date,
                is_recurrent=is_recurrent,
                is_gifted=is_gifted
            )
            self.session.add(subscription)
            await self.session.commit()
            return subscription
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Error creating subscription: {e}")

    async def update_subscription(
        self,
        subscription_id: int,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_recurrent: Optional[bool] = None,
        is_gifted: Optional[bool] = None
    ) -> "Subscription":
        """
        Updates an existing subscription with optional parameters.
        :param subscription_id: ID of the subscription to update.
        :param status: New status of the subscription.
        :param start_date: New start date of the subscription.
        :param end_date: New end date of the subscription.
        :param is_recurrent: Indicates if the subscription is recurrent.
        :param is_gifted: Indicates if the subscription is gifted.
        :return: The updated Subscription object.
        """
        try:
            subscription = await self.session.get(Subscription, subscription_id)
            if not subscription:
                raise ValueError(f"Subscription with ID {subscription_id} not found.")

            if status is not None:
                subscription.status = status
            if start_date is not None:
                subscription.start_date = start_date
            if end_date is not None:
                subscription.end_date = end_date
            if is_recurrent is not None:
                subscription.is_recurrent = is_recurrent
            if is_gifted is not None:
                subscription.is_gifted = is_gifted

            await self.session.commit()
            return subscription
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Error updating subscription with ID {subscription_id}: {e}")

    async def delete_subscription(self, subscription_id: int) -> bool:
        """
        Deletes a subscription by its ID.
        :param subscription_id: The ID of the subscription to delete.
        :return: True if successful, False otherwise.
        """
        try:
            subscription = await self.get_subscription_by_id(subscription_id)
            if not subscription:
                return False
            await self.session.delete(subscription)
            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Error deleting subscription with ID {subscription_id}: {e}")