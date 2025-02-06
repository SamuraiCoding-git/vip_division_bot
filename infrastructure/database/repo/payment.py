from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from infrastructure.database.models import Payment
from infrastructure.database.repo.base import BaseRepo


class PaymentRepo(BaseRepo):
    async def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """
        Retrieves a payment by its ID.
        :param payment_id: The ID of the payment.
        :return: Payment object, or None if not found.
        """
        try:
            payment = await self.session.get(Payment, payment_id)
            return payment
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching payment with ID {payment_id}: {e}")

    async def get_all_payments(self) -> List[Payment]:
        """
        Retrieves all payments.
        :return: A list of Payment objects.
        """
        try:
            query = select(Payment).order_by(Payment.created_at.desc())
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching all payments: {e}")

    async def create_payment(
        self,
        user_id: int,
        subscription_id: int
    ) -> "Payment":
        """
        Creates a new payment record with mandatory fields.

        :param user_id: ID of the user making the payment.
        :param subscription_id: ID of the associated subscription.
        :return: The created Payment object.
        """
        try:
            # Ensure required fields are provided
            if not user_id or not subscription_id:
                raise ValueError("User ID and Subscription ID are required to create a payment.")

            # Create a new Payment object with minimal required fields
            payment = Payment(
                user_id=user_id,
                subscription_id=subscription_id
            )

            # Add and commit the payment to the database
            self.session.add(payment)
            await self.session.commit()

            return payment
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Database error creating payment: {e}")
        except ValueError as e:
            raise Exception(f"Validation error: {e}")
    async def update_payment(
        self,
        payment_id: int,
        amount: Optional[int] = None,
        currency: Optional[str] = None,
        payment_method: Optional[str] = None,
        is_successful: Optional[bool] = None,
        hash: Optional[str] = None,
        binding_id: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> "Payment":
        """
        Updates an existing payment record with optional fields.

        :param payment_id: ID of the payment to update.
        :param amount: Updated payment amount.
        :param currency: Updated currency code.
        :param payment_method: Updated payment method.
        :param is_successful: Updated payment success status.
        :param hash: Updated hash for payment identification.
        :param subscription_id: Updated subscription ID associated with the payment.
        :return: The updated Payment object.
        """
        try:
            # Fetch the payment record
            payment = await self.session.get(Payment, payment_id)
            if not payment:
                raise ValueError(f"Payment with ID {payment_id} does not exist.")

            # Update fields if provided
            if amount is not None:
                payment.amount = amount
            if currency is not None:
                payment.currency = currency
            if payment_method is not None:
                payment.payment_method = payment_method
            if is_successful is not None:
                payment.is_successful = is_successful
            if hash is not None:
                payment.hash = hash
            if binding_id is not None:
                payment.binding_id = binding_id
            if phone_number is not None:
                payment.phone_number = phone_number

            # Commit the changes
            await self.session.commit()

            return payment
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Database error updating payment: {e}")
        except ValueError as e:
            raise Exception(f"Validation error: {e}")

    async def delete_payment(self, payment_id: int) -> bool:
        """
        Deletes a payment by its ID.
        :param payment_id: The ID of the payment to delete.
        :return: True if successful, False otherwise.
        """
        try:
            payment = await self.get_payment_by_id(payment_id)
            if not payment:
                return False
            await self.session.delete(payment)
            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Error deleting payment with ID {payment_id}: {e}")

    async def is_unique_payment_hash(self, hash: str) -> bool:
        """
        Checks if there is already a payment with the given hash.
        :param hash: The hash to check for uniqueness.
        :return: True if no payment with the same hash exists, False otherwise.
        """
        result = await self.session.execute(select(Payment).filter(Payment.hash == hash))
        existing_payment = result.scalar_one_or_none()
        return existing_payment is None

    async def count_payments(self, user_id) -> int:
        """
        Counts the total number of payments in the database.
        :return: The total count of payments.
        """
        try:
            query = select(func.count(Payment.id)).filter(Payment.user_id == user_id, Payment.is_successful == True)
            result = await self.session.execute(query)
            total_count = result.scalar_one()
            return total_count
        except SQLAlchemyError as e:
            raise Exception(f"Error counting payments: {e}")

