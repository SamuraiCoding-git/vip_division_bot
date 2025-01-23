from typing import Optional, List
from sqlalchemy import select
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

    async def create_payment(self, payment: Payment) -> Payment:
        """
        Creates a new payment record.
        :param payment: The Payment object to insert.
        :return: The created Payment object.
        """
        try:
            self.session.add(payment)
            await self.session.commit()
            return payment
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Error creating payment: {e}")

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
