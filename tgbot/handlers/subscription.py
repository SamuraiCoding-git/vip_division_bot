from datetime import timedelta, datetime

from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from main import create_invite_link
from tgbot.config import Config
from tgbot.filters.private import IsPrivateFilter
from tgbot.keyboards.callback_data import TariffsCallbackData
from tgbot.keyboards.inline import my_subscription_keyboard, crypto_pay_link, \
    instruction_keyboard, join_resources_keyboard, podcast_channel_keyboard, pay_keyboard
from tgbot.misc.states import UsdtTransaction
from tgbot.utils.db_utils import get_repo
from tgbot.utils.message_utils import delete_messages
from tgbot.utils.payment_utils import generate_qr_code, generate_payment_link
from tgbot.utils.sub_utils import get_transaction_confirmations

subscription_router = Router()

subscription_router.message.filter(IsPrivateFilter())
subscription_router.callback_query.filter(IsPrivateFilter())

@subscription_router.callback_query(TariffsCallbackData.filter())
async def sub_tariffs(call: CallbackQuery, state: FSMContext, bot: Bot, callback_data: TariffsCallbackData, config: Config):
    repo = await get_repo(config)
    user = await repo.users.select_user(call.message.chat.id)
    reference_date = datetime(2025, 1, 10)
    if user.created_at > reference_date:
        text = ("Приватный канал закрыт.\n\n"
                "Но можешь насладиться подкастом")
        photo = "AgACAgIAAxkBAAEBGrpnf455RP6B5uNFzd3G5oqw1YuZTgACLuoxGzT-AAFIhutJCNi8w8IBAAMCAAN5AAM2BA"
        await call.message.answer_photo(photo=photo, caption=text, reply_markup=podcast_channel_keyboard())
        return
    plan = await repo.plans.select_plan(callback_data.id)
    order = await repo.orders.create_order(call.message.chat.id,
                                           callback_data.id,
                                           plan.original_price)

    if plan.discounted_price != plan.original_price:
        discount_percentage = int((1 - plan.discounted_price / plan.original_price) * 100)
        price_text = f"<b>Стоимость:</b> <s>{plan.discounted_price} ₽</s> {plan.original_price} ₽ (скидка {discount_percentage if discount_percentage < 10 else 10}%)\n"
    else:
        price_text = f"<b>Стоимость:</b> {plan.original_price} ₽\n"


    text = config.text.tariff_caption.replace("{plan.name}", plan.name).replace("{price_text}", price_text).replace("{plan.name[:-2]}", str(plan.name[:-2]))

    await state.update_data(usd_price=plan.usd_price)
    await state.update_data(plan_id=plan.id)
    await state.update_data(order_id=order.id)

    product = [
        {
            "quantity": 1,
            "name": plan.name[:-2],
            "price": int(plan.original_price),
            "sku": plan.id
        }
    ]

    link = generate_payment_link(str(call.message.chat.id), order.id, product, config.payment.token, config.misc.payment_form_url)

    sent_message = await call.message.answer(text, reply_markup=pay_keyboard(link, "tariffs"))

    await delete_messages(bot, call.message.chat.id, state, [sent_message.message_id])



@subscription_router.message(F.text == '/subscription')
@subscription_router.callback_query(F.data == "my_subscription")
async def my_subscription(event, state: FSMContext, bot: Bot, config: Config):
    chat_id = event.message.chat.id if isinstance(event, CallbackQuery) else event.chat.id

    message_ids = []
    repo = await get_repo(config)

    order = await repo.orders.get_latest_paid_order_by_user(chat_id)

    if order:
        plan = await repo.plans.select_plan(order.plan_id)
        try:
            duration_days = plan.duration
            end_date = order.start_date + timedelta(days=duration_days)
            days_remaining = max((end_date - datetime.utcnow()).days, 0)
        except ValueError:
            days_remaining = 0
    else:
        days_remaining = 0

    if days_remaining > 0:
        text = config.text.payment_success_message.replace("{days_remaining}", str(days_remaining))
        sent_message = await bot.send_message(chat_id=chat_id, text=text,
                                              reply_markup=my_subscription_keyboard(state="menu",
                                                                                    is_sub=True,
                                                                                    chat_link=create_invite_link(config.misc.private_chat_id),
                                                                                    channel_link=create_invite_link(config.misc.private_channel_id)))
    else:
        text = config.text.payment_inactive_message
        sent_message = await bot.send_message(chat_id=chat_id, text=text, reply_markup=my_subscription_keyboard(state="menu"))

    message_ids.append(sent_message.message_id)

    await delete_messages(event.bot, chat_id, state, message_ids)


@subscription_router.callback_query(F.data == "pay_crypto")
async def pay_crypto_handler(call: CallbackQuery, state: FSMContext, bot: Bot, config: Config):
    data = await state.get_data()
    usd_price = int(data.get("usd_price"))
    trust_wallet_link = f"tron:{config.misc.tron_wallet}?amount={usd_price}"
    path = generate_qr_code(trust_wallet_link)
    qr_code_png = FSInputFile(path)
    message_ids = []

    caption = (f"Адрес: {config.misc.tron_wallet}\n"
               f"Стоимость: {usd_price}$\n\n"
               f"Отправьте хэш транзакции:")

    sent_message = await call.message.answer_photo(qr_code_png,
                                                   caption=caption,
                                                   reply_markup=crypto_pay_link('tariffs'),
                                                   parse_mode='HTML')
    message_ids.append(sent_message.message_id)
    await state.set_state(UsdtTransaction.hash)

    await delete_messages(bot, call.message.chat.id, state, message_ids)


@subscription_router.callback_query(F.data == "check_crypto_pay")
async def check_crypto_pay(call: CallbackQuery, state: FSMContext, bot: Bot, config: Config):
    repo = await get_repo(config)
    data = await state.get_data()
    hash = data.get("hash")
    usd_price = data.get("usd_price")
    is_unique_hash = await repo.orders.is_unique_order_hash(hash)
    if not is_unique_hash:
        await call.answer("Уже есть заказ с таким хэшем", show_alert=True)
        return

    result = get_transaction_confirmations(hash, usd_price, config.misc.tron_wallet)

    if result == "Транзакция успешно подтверждена.":
        caption = "✅ Подписка на канал успешно оформлена!\nПерeходи по кнопкам ниже:"
        PHOTO_ID_DICT = {
            1: config.media.check_crypto_pay_photos[0],
            2: config.media.check_crypto_pay_photos[1],
            3: config.media.check_crypto_pay_photos[2],
            4: config.media.check_crypto_pay_photos[3]
        }
        await state.clear()
        await repo.users.update_plan_id(call.message.chat.id, int(data['plan_id']))
        await repo.orders.update_order_payment_status(int(data['order_id']), True, hash=hash)
        await call.message.answer_photo(
            photo=PHOTO_ID_DICT[int(data['plan_id'])],
            caption=caption,
            reply_markup=join_resources_keyboard(
                create_invite_link(config.misc.private_channel_id),
                create_invite_link(config.misc.private_chat_id)
            )
        )
        VIDEO_FILE_ID = config.media.check_crypto_pay_video

        caption = config.text.check_crypto_pay_text.replace("{full_name}", call.message.chat.full_name)
        await call.message.answer_video(VIDEO_FILE_ID, caption=caption, reply_markup=instruction_keyboard())
    else:
        await call.answer(result, show_alert=True)

    await delete_messages(bot, call.message.chat.id, state)
