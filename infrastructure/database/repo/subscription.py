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
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_recurrent: bool = False,
        is_gifted: bool = False,
        gifted_by: Optional[int] = None,
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
                status=status,
                start_date=start_date,
                end_date=end_date,
                is_recurrent=is_recurrent,
                is_gifted=is_gifted,
                gifted_by=gifted_by
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
    ) -> Subscription:
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

    async def get_combined_active_subscription_days(self, user_id: int) -> Optional[int]:
        """
        Retrieves the combined number of days remaining for all active subscriptions of a user.
        :param user_id: The ID of the user.
        :return: The total days of active subscriptions, or None if no active subscriptions exist.
        """
        try:
            query = select(Subscription).filter(Subscription.user_id == user_id, Subscription.status == "active")
            result = await self.session.execute(query)
            active_subscriptions = result.scalars().all()

            if not active_subscriptions:
                return None

            total_days = 0
            for subscription in active_subscriptions:
                if subscription.end_date and subscription.start_date:
                    days_remaining = (subscription.end_date - subscription.start_date).days
                    total_days += days_remaining

            return total_days
        except SQLAlchemyError as e:
            raise Exception(f"Error calculating combined active subscription days for user {user_id}: {e}")

    async def toggle_is_recurrent(self, subscription_id: int) -> bool:
        """
        Toggles the is_recurrent value of a subscription.
        :param subscription_id: The ID of the subscription.
        :return: The updated is_recurrent value.
        """
        try:
            subscription = await self.session.get(Subscription, subscription_id)
            if not subscription:
                raise ValueError(f"Subscription with ID {subscription_id} not found.")

            subscription.is_recurrent = not subscription.is_recurrent
            await self.session.commit()

            return subscription.is_recurrent
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Error toggling is_recurrent for subscription ID {subscription_id}: {e}")
        except ValueError as e:
            raise Exception(f"Validation error: {e}")

    async def toggle_all_user_subscriptions(self, user_id: int) -> List[bool]:
        """
        Toggles the is_recurrent value for all subscriptions of a specific user.
        :param user_id: The ID of the user whose subscriptions will be toggled.
        :return: A list of updated is_recurrent values for the user's subscriptions.
        """
        try:
            query = select(Subscription).filter(Subscription.user_id == user_id)
            result = await self.session.execute(query)
            subscriptions = result.scalars().all()

            if not subscriptions:
                raise ValueError(f"No subscriptions found for user ID {user_id}.")

            updated_values = []
            for subscription in subscriptions:
                subscription.is_recurrent = not subscription.is_recurrent
                updated_values.append(subscription.is_recurrent)

            await self.session.commit()

            return updated_values
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Error toggling is_recurrent for all subscriptions of user ID {user_id}: {e}")
        except ValueError as e:
            raise Exception(f"Validation error: {e}")

    async def print_subscriptions(self, subscriptions: List[Subscription], delimiter: str = " | ") -> str:
        """
        Prints all properties of the provided subscriptions with a specified delimiter.
        :param subscriptions: List of Subscription objects to print.
        :param delimiter: The delimiter to separate the properties.
        :return: A formatted string of subscriptions' details.
        """
        output = []
        for subscription in subscriptions:
            properties = [
                f"ID: {subscription.id}",
                f"User ID: {subscription.user_id}",
                f"Plan ID: {subscription.plan_id}",
                f"Status: {subscription.status}",
                f"Start Date: {subscription.start_date}",
                f"End Date: {subscription.end_date}",
                f"Is Recurrent: {subscription.is_recurrent}",
                f"Is Gifted: {subscription.is_gifted}",
                f"Gifted By: {subscription.gifted_by}"
            ]
            output.append(delimiter.join(properties))
        return "\n".join(output)
