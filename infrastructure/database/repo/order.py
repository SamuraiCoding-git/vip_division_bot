from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models import Order, User


class OrderRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(
        self,
        user_id: int,
        plan_id: int,
        total_price: float,
        is_paid: bool = False,
    ) -> Optional[Order]:
        """
        Creates a new order in the database and returns the order object.
        :param user_id: The ID of the user making the order.
        :param plan_id: The ID of the plan being ordered.
        :param total_price: The total price of the order.
        :param is_paid: The payment status of the order (default is False).
        :return: The created Order object or None if the creation fails.
        """
        order = Order(
            user_id=user_id,
            plan_id=plan_id,
            total_price=total_price,
            is_paid=is_paid,
        )
        self.session.add(order)
        await self.session.commit()
        return order

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
        Retrieves an order by its ID.
        :param order_id: The ID of the order.
        :return: The Order object or None if not found.
        """
        result = await self.session.execute(select(Order).filter(Order.id == order_id))
        return result.scalar_one_or_none()

    async def get_orders_by_user_id(self, user_id: int) -> List[Order]:
        """
        Retrieves all orders for a specific user.
        :param user_id: The ID of the user.
        :return: A list of Order objects.
        """
        result = await self.session.execute(select(Order).filter(Order.user_id == user_id))
        return result.scalars().all()

    async def update_order_payment_status(self, order_id: int, is_paid: bool) -> Optional[Order]:
        """
        Updates the payment status of an order.
        :param order_id: The ID of the order to update.
        :param is_paid: The new payment status of the order.
        :return: The updated Order object or None if not found.
        """
        result = await self.session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(is_paid=is_paid)
            .returning(Order)
        )
        await self.session.commit()
        return result.scalar_one_or_none()

    async def get_paid_orders(self) -> List[Order]:
        """
        Retrieves all paid orders.
        :return: A list of paid Order objects.
        """
        result = await self.session.execute(select(Order).filter(Order.is_paid == True))
        return result.scalars().all()

    async def get_unpaid_orders(self) -> List[Order]:
        """
        Retrieves all unpaid orders.
        :return: A list of unpaid Order objects.
        """
        result = await self.session.execute(select(Order).filter(Order.is_paid == False))
        return result.scalars().all()

    async def get_latest_paid_order_by_user(self, user_id: int) -> Optional[Order]:
        """
        Retrieves the latest paid order for a specific user based on the start_date.
        :param user_id: The ID of the user.
        :return: The latest paid Order object for the user, or None if no such orders exist.
        """
        result = await self.session.execute(
            select(Order)
            .filter(Order.id == user_id, Order.is_paid == True)
            .order_by(Order.start_date.desc())
        )
        return result.scalar_one_or_none()

    async def get_user_by_order_id(self, order_id: int) -> Optional[User]:
        """
        Retrieves the User associated with a given order_id.
        :param order_id: The ID of the order.
        :return: The User object associated with the order or None if not found.
        """
        result = await self.session.execute(
            select(User).join(Order).filter(Order.id == order_id)
        )
        return result.scalar_one_or_none()

