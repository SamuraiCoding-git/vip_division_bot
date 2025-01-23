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

    async def create_subscription(self, subscription: Subscription) -> Subscription:
        """
        Creates a new subscription record.
        :param subscription: The Subscription object to insert.
        :return: The created Subscription object.
        """
        try:
            self.session.add(subscription)
            await self.session.commit()
            return subscription
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Error creating subscription: {e}")

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
