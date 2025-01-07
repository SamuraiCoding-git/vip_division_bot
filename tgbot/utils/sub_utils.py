from datetime import datetime, timedelta

import requests
from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.order import Order
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_session_pool
from tgbot.config import Config
from tgbot.utils.payment_utils import process_payment


async def send_notification(bot: Bot, user_id: int, message: str):
    await bot.send_message(user_id, "Подписка успешно")


async def check_subscriptions(session: AsyncSession, bot: Bot, config: Config):
    session_pool = await create_session_pool(config.db)

    async with session_pool() as session:
        repo = RequestsRepo(session)
    orders = await repo.orders.get_paid_orders()

    for order in orders:
        plan = await repo.plans.select_plan(order.plan_id)
        try:
            duration_days = int(order.plan.duration)  # Ensure duration is an integer
        except ValueError:
            print(f"Invalid plan duration for order {order.id}: {order.plan.duration}")
            continue

        # Calculate days remaining until the subscription ends
        now = datetime.utcnow()
        end_date = order.start_date + timedelta(days=duration_days)
        days_remaining = (end_date - now).days

        if days_remaining <= 0:
            # Process recurring payment or mark subscription as expired
            try:
                await process_payment(
                    order.binding_id,
                    order.user_id,
                    config.misc.sys,
                    config.payment.token,
                    config.misc.payment_form_url,
                    order.total_price
                )
                print(f"Recurring payment successful for order {order.id}")
            except Exception as e:
                print(f"Failed to process recurring payment for order {order.id}: {e}")
                order.is_paid = False
                await send_notification(order.user_id, "Your subscription has expired.")

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

        if response.status_code != 200:
            return f"Ошибка при получении данных о транзакции: HTTP {response.status_code}"

        transaction_data = response.json()

        print(transaction_data)

        if 'to_address' not in transaction_data:
            return "Поле 'toAddress' отсутствует в данных транзакции."

        if 'confirmed' not in transaction_data:
            return "Поле 'confirmed' отсутствует в данных транзакции."

        if not transaction_data.get('confirmed', False):
            return "Транзакция не подтверждена."

        if transaction_data.get('to_address') != tron_wallet:
            return "Адрес получателя не совпадает с ожидаемым."

        if usd_price > normalize_usdt_price(transaction_data):
            return "Сумма транзакции меньше ожидаемой."

        return "Транзакция успешно подтверждена."

    except requests.RequestException as e:
        return f"Ошибка запроса к API: {str(e)}"

    except ValueError:
        return "Ошибка при обработке ответа от API. Возможно, неверный формат JSON."

    except Exception as e:
        return f"Неизвестная ошибка: {str(e)}"
