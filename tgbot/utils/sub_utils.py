from datetime import datetime, timedelta

import requests
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
        select(Order).filter(Order.is_paid == True)
    )
    orders = result.scalars().all()

    for order in orders:
        # Convert duration to integer if it's stored as a string
        try:
            duration_days = int(order.plan.duration)  # Ensure duration is an integer
        except ValueError:
            print(f"Invalid plan duration for order {order.id}: {order.plan.duration}")
            continue

        # Calculate days remaining until the subscription ends
        now = datetime.utcnow()
        end_date = order.start_date + timedelta(days=duration_days)
        days_remaining = (end_date - now).days

        if days_remaining == 3:
            # Notify about expiration in 3 days
            await send_notification(order.user_id, "Your subscription will expire in 3 days.")
        elif days_remaining == 1:
            # Notify about expiration in 1 day
            await send_notification(order.user_id, "Your subscription will expire tomorrow.")
        elif days_remaining <= 0:
            # Process recurring payment or mark subscription as expired
            try:
                await process_recurring_payment(order)
                print(f"Recurring payment successful for order {order.id}")
            except Exception as e:
                print(f"Failed to process recurring payment for order {order.id}: {e}")
                order.status = "expired"
                await send_notification(order.user_id, "Your subscription has expired.")

        # Commit changes to the database after processing each order
        await session.commit()

def get_transaction_confirmations(tx_hash):
    tronscan_api_url = "https://apilist.tronscanapi.com/api/transaction-info"

    try:
        response = requests.get(f"{tronscan_api_url}?hash={tx_hash}")
        response.raise_for_status()  # Raise an HTTPError for bad responses
        transaction_data = response.json()
        print(transaction_data)

        if "confirmed" in transaction_data:
            return transaction_data["confirmed"]
        else:
            return f"Transaction data not available for {tx_hash}."

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"