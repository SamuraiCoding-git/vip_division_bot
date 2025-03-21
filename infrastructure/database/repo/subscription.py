from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from infrastructure.database.models import Subscription, Payment
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

    async def get_subscription_by_user_id(self, user_id: int) -> Optional[Subscription]:
        """
        Retrieves a subscription by user ID.
        :param user_id: The ID of the user.
        :return: Subscription object, or None if not found.
        """
        try:
            stmt = select(Subscription).where(Subscription.user_id == user_id)
            result = await self.session.execute(stmt)
            subscription = result.scalars().first()
            return subscription
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching subscription for user ID {user_id}: {e}")

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

    async def toggle_all_user_subscriptions(self, user_id: int) -> bool:
        """
        Toggles the is_recurrent value for all active subscriptions of a specific user
        and returns a single boolean by combining all updated values with the 'and' operator.
        :param user_id: The ID of the user whose active subscriptions will be toggled.
        :return: True if all updated subscriptions are recurrent, False otherwise.
        """
        try:
            # Query to get all active subscriptions for the given user
            query = select(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.status == "active"
            )
            result = await self.session.execute(query)
            subscriptions = result.scalars().all()

            if not subscriptions:
                raise ValueError(f"No active subscriptions found for user ID {user_id}.")

            combined_is_recurrent = True
            for subscription in subscriptions:
                # Toggle the is_recurrent value
                subscription.is_recurrent = not subscription.is_recurrent
                combined_is_recurrent = combined_is_recurrent and subscription.is_recurrent

            # Commit the changes to the database
            await self.session.commit()

            return combined_is_recurrent
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Error toggling is_recurrent for all active subscriptions of user ID {user_id}: {e}")
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

    async def is_recurrent(self, user_id: int) -> bool:
        """
        Checks if all active subscriptions for a specific user have 'is_recurrent = True'.
        :param user_id: The ID of the user.
        :return: True if all active subscriptions for the user are recurrent, False otherwise.
        """
        try:
            # Query to get all 'is_recurrent' values for active subscriptions of the user
            query = select(Subscription.is_recurrent).filter(
                Subscription.user_id == user_id,
                Subscription.status == "active"
            )
            result = await self.session.execute(query)
            is_recurrent_values = result.scalars().all()

            if not is_recurrent_values:
                # No active subscriptions found
                return False

            # Check if all 'is_recurrent' values are True
            return all(is_recurrent_values)
        except SQLAlchemyError as e:
            raise Exception(
                f"Error checking if all active subscriptions for user {user_id} are recurrent or not: {e}")

    async def extend_subscription(
        self,
        user_id: int,
        extension: str
    ) -> Optional[Subscription]:
        """
        Extends the last active subscription by either adding days (e.g., "+10") or setting a new end date ("YYYY-MM-DD").
        :param user_id: The ID of the user whose subscription will be updated.
        :param extension: Either a string representing days to add (e.g., "+10") or a specific date ("YYYY-MM-DD").
        :return: The updated Subscription object, or None if no active subscription is found.
        """
        try:
            # Determine whether `extension` is days or a specific date
            if extension.startswith("+"):  # Adding days (e.g., "+10")
                days = int(extension[1:])
                until_date = None
            else:  # Specific date (e.g., "2025-01-31")
                until_date = datetime.strptime(extension, "%Y-%m-%d")
                days = None

            # Query to get the last active subscription sorted by start_date
            query = (
                select(Subscription)
                .filter(
                    Subscription.user_id == user_id,
                    Subscription.status == "active"
                )
                .order_by(Subscription.start_date.desc())
            )
            result = await self.session.execute(query)
            last_subscription = result.scalars().first()

            if not last_subscription:
                return None  # No active subscription found

            # Update the end date
            if days is not None:
                last_subscription.end_date += timedelta(days=days)
            elif until_date is not None:
                if until_date <= last_subscription.end_date:
                    raise ValueError("New end date must be later than the current end date.")
                last_subscription.end_date = until_date

            # Commit the changes
            await self.session.commit()
            return last_subscription
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Error extending subscription for user {user_id} with extension {extension}: {e}")
        except ValueError as e:
            raise Exception(f"Invalid extension value: {e}")

    async def get_recurrent_subscriptions(self):
        # Query to get all subscriptions with is_recurrent == True, their associated Payment.binding_id,
        # and ensuring Payment.binding_id is not None
        stmt = (
            select(Subscription, Payment.binding_id)  # Select Subscription and Payment.binding_id
            .outerjoin(Payment, Subscription.id == Payment.subscription_id)  # Left join to get the Payment data
            .where(Subscription.is_recurrent == True,
                   Subscription.end_date < datetime.now(),
                   Payment.binding_id.isnot(None))  # Filter for recurrent subscriptions where binding_id is not None
        )

        # Execute the query asynchronously
        result = await self.session.execute(stmt)

        # Fetch all results, returning a list of tuples (Subscription, binding_id)
        subscriptions_with_payments = result.fetchall()

        # Create a list of Subscription objects and add the binding_id as an attribute
        subscriptions = []
        for subscription, binding_id in subscriptions_with_payments:
            subscription.binding_id = binding_id  # Dynamically attach the binding_id to the Subscription object
            subscriptions.append(subscription)

        return subscriptions

    async def get_latest_active_subscription(self, user_id: int) -> Optional[Subscription]:
        """
        Retrieves the latest active subscription for a given user based on the highest end_date.
        :param user_id: The ID of the user.
        :return: The latest active Subscription object, or None if no active subscription is found.
        """
        try:
            query = (
                select(Subscription)
                .filter(
                    Subscription.user_id == user_id,
                    Subscription.status == "active"
                )
                .order_by(Subscription.end_date.desc())
                .limit(1)
            )
            result = await self.session.execute(query)
            return result.scalars().first()
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching latest active subscription for user {user_id}: {e}")

    async def expire_subscription(self, subscription_id: int) -> bool:
        """
        Marks a subscription as expired by setting 'is_recurrent' to False and 'status' to 'expired'.
        :param subscription_id: The ID of the subscription to update.
        :return: True if the update was successful, False if the subscription was not found.
        """
        try:
            subscription = await self.session.get(Subscription, subscription_id)
            if not subscription:
                return False

            subscription.is_recurrent = False
            subscription.status = "expired"

            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Error expiring subscription with ID {subscription_id}: {e}")

    async def extend_subscription_by_id(self, subscription_id: int, days: int) -> Optional[Subscription]:
        """
        Extends a subscription by adding a specified number of days.
        :param subscription_id: The ID of the subscription to update.
        :param days: The number of days to add to the subscription.
        :return: The updated Subscription object, or None if the subscription is not found.
        """
        try:
            # Fetch the subscription by ID
            subscription = await self.session.get(Subscription, subscription_id)
            if not subscription:
                return None  # Subscription not found

            # Ensure the subscription has a valid end date
            if not subscription.end_date:
                raise ValueError(f"Subscription {subscription_id} does not have an end_date set.")

            # Extend the subscription by the given number of days
            subscription.end_date = datetime.now() + timedelta(days=days)
            subscription.status = "active"

            # Commit changes to the database
            await self.session.commit()
            return subscription
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Error extending subscription with ID {subscription_id}: {e}")
        except ValueError as e:
            raise Exception(f"Invalid operation: {e}")

    async def count_unique_subscription_users(self) -> int:
        query = select(func.count(func.distinct(Subscription.user_id)))
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_expired_users(self) -> List[int]:
        """
        Retrieves user IDs of all non-recurrent subscriptions that have expired.
        :return: List of user IDs.
        """
        try:
            query = (
                select(Subscription.user_id)
                .where(
                    Subscription.is_recurrent == False,
                    Subscription.end_date < datetime.utcnow()
                )
                .distinct()
            )
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching non-recurrent expired users: {e}")

    async def get_subscription_count_by_plan(self) -> dict:
        """
        Retrieves the count of subscriptions for each plan_id (from 1 to 4).
        :return: A dictionary where keys are plan_ids, and values are the subscription count.
        """
        try:
            # Запрос для подсчёта подписок по каждому plan_id
            query = select(Subscription.plan_id, func.count(Subscription.id).label('subscription_count')) \
                .where(Subscription.plan_id.in_([1, 2, 3, 4]), Subscription.status == "active") \
                .group_by(Subscription.plan_id)

            result = await self.session.execute(query)
            plan_distribution = result.fetchall()

            # Формируем словарь для каждого plan_id и его соответствующего количества подписок
            distribution = {plan_id: count for plan_id, count in plan_distribution}

            # Добавляем в словарь plan_id, если они не были найдены в базе (если подписок по какому-то плану нет)
            for plan_id in [1, 2, 3, 4]:
                if plan_id not in distribution:
                    distribution[plan_id] = 0

            return distribution
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching subscription count by plan: {e}")

