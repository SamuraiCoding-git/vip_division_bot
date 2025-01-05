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

def normalize_usdt_price(transaction_data):
    """
    Normalizes the USDT price from the transaction data.
    :param transaction_data: The transaction data containing 'trc20TransferInfo'.
    :return: Normalized USDT price as a float.
    """
    try:
        trc20_info = transaction_data.get('trc20TransferInfo', [{}])[0]  # Get the first transfer info
        amount_str = trc20_info.get('amount_str', '0')
        decimals = trc20_info.get('decimals', 6)  # Default to 6 decimals if not provided
        normalized_amount = float(amount_str) / (10 ** decimals)
        return normalized_amount
    except (KeyError, IndexError, ValueError) as e:
        print(f"Error normalizing USDT price: {e}")
        return None

def get_transaction_confirmations(tx_hash, usd_price, tron_wallet):
    try:
        response = requests.get(f"https://apilist.tronscanapi.com/api/transaction-info?hash={tx_hash}")
        transaction_data = response.json()

        if transaction_data.get('toAddress') == tron_wallet and transaction_data.get("confirmed", False):
            return usd_price <= normalize_usdt_price(transaction_data)

        return False

    except Exception:
        return False
