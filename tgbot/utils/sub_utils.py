from datetime import datetime, timedelta

import requests
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_session_pool
from tgbot.config import Config
from tgbot.utils.payment_utils import process_payment


async def check_subscriptions(bot: Bot, config: Config):
    session_pool = await create_session_pool(config.db)

    async with session_pool() as session:
        repo = RequestsRepo(session)
        subscriptions = await repo.subscriptions.get_active_recurrent_subscriptions()
        now = datetime.utcnow()

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Моя подписка ✅", callback_data="my_subscription")]
        ])

        for subscription in subscriptions:
            payment = await repo.payments.get_latest_successful_payment(subscription.user_id)
            days_remaining = (subscription.end_date - now).days
            if subscription.id == 178:
                print(True)
            if days_remaining <= 0:
                print(days_remaining)
            else:
                pass

            if days_remaining <= 0:
                try:
                    await process_payment(
                        payment.binding_id,
                        subscription.user_id,
                        config.misc.sys,
                        config.payment.token,
                        config.misc.payment_form_url,
                        subscription.plan.discounted_price
                    )
                    await bot.send_message(subscription.user_id, "✅ Ваша подписка успешно продлена!",
                                           reply_markup=keyboard)

                except Exception as e:
                    print(f"❌ Ошибка продления подписки {subscription.id}: {e}")
                    subscription.is_recurrent = False
                    subscription.status = "expired"
                    await session.commit()

                    await send_failed_renewal_notification(bot, subscription.user_id)

                    await ban_user_from_channel_and_chat(bot, subscription.user_id, config)


async def send_failed_renewal_notification(bot: Bot, user_id: int):
    text = (
        "Удален из канала\n\n"
        "❌ <b>Продление подписки не удалось.</b>"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться в канал ↩️", callback_data="tariffs")],
        [InlineKeyboardButton(text="🤝🏽 Написать в поддержку", url="https://t.me/vipdivision")]
    ])

    await bot.send_message(user_id, text, reply_markup=keyboard, parse_mode="HTML")


async def ban_user_from_channel_and_chat(bot: Bot, user_id: int, config: Config):
    try:

        await bot.ban_chat_member(chat_id=config.misc.private_channel_id, user_id=user_id)
        await bot.ban_chat_member(chat_id=config.misc.private_chat_id, user_id=user_id)

        print(f"✅ Пользователь {user_id} забанен в канале {config.misc.private_channel_id} и чате {config.misc.private_chat_id}.")
    except Exception as e:
        print(f"❌ Ошибка при бане пользователя {user_id}: {e}")

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

        if 'confirmed' not in transaction_data:
            return "Поле 'confirmed' отсутствует в данных транзакции."

        if not transaction_data.get('confirmed', False):
            return "Транзакция не подтверждена."

        if transaction_data['tokenTransferInfo']['to_address'] != tron_wallet:
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
