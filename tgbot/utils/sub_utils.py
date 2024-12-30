from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.order import Order


async def send_notification(bot: Bot, user_id: int, message: str):
    await bot.send_message(user_id, message)

async def process_recurring_payment(order: Order):
    pass

# Function to check subscriptions
async def check_subscriptions(session: AsyncSession, bot: Bot):
    """
    Check active subscriptions and send notifications or process recurring payments.
    """
    result = await session.execute(
        select(Order).filter(Order.status == "active")
    )
    orders = result.scalars().all()

    for order in orders:
        days_remaining = order.get_days_remaining()
        if days_remaining == 3:
            # Notify about expiration in 3 days
            await send_notification(order.user_id, "Your subscription will expire in 3 days.")
        elif days_remaining == 1:
            # Notify about expiration in 1 day
            await send_notification(order.user_id, "Your subscription will expire tomorrow.")
        elif days_remaining == 0:
            # Process recurring payment or mark subscription as expired
            try:
                await process_recurring_payment(order)
                print(f"Recurring payment successful for order {order.order_id}")
            except Exception as e:
                print(f"Failed to process recurring payment for order {order.order_id}: {e}")
                order.status = "expired"
                await send_notification(order.user_id, "Your subscription has expired.")

        await session.commit()