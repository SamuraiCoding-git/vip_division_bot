import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.config import Config
from tgbot.keyboards.inline import crypto_pay_check_keyboard, subscription_keyboard
from tgbot.misc.states import UsdtTransaction
from tgbot.utils.db_utils import get_repo
from tgbot.utils.message_utils import delete_messages

payment_router = Router()

@payment_router.message(UsdtTransaction.hash)
async def usdt_transaction_hash(message: Message, state: FSMContext):
    hash_text = message.text.strip()

    tron_hash_pattern = r'^[a-f0-9]{64}$'

    if re.match(tron_hash_pattern, hash_text):
        sent_message = await message.answer(
            "После подтверждения транзакции 20 блоками - нажми на кнопку.",
                 reply_markup=crypto_pay_check_keyboard("tariffs"))
    else:
        sent_message = await message.answer(
            "Неверный хэш транзакции Tron.\n"
            "Отправьте ещё раз")
        await state.update_data(message_ids=[sent_message.message_id])
        return
    await state.update_data(hash=hash_text)
    await state.clear()
    await delete_messages(message.bot, message.from_user.id, state, [sent_message.message_id])


@payment_router.message(F.text == "/payment")
@payment_router.callback_query(F.data == "tariffs")
async def tariffs(event, state: FSMContext, config: Config):
    chat_id = event.message.chat.id if isinstance(event, CallbackQuery) else event.chat.id

    message_ids = []

    repo = await get_repo(config)
    plans = await repo.plans.get_all_plans()

    text = config.text.tariffs_message
    sent_message = await event.bot.send_message(chat_id=chat_id, text=text, reply_markup=subscription_keyboard("menu", plans))

    message_ids.append(sent_message.message_id)

    await delete_messages(event.bot, chat_id, state, message_ids)
