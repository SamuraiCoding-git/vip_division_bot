import asyncio
from datetime import timedelta, datetime

from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from infrastructure.database.models import Payment
from main import create_invite_link
from tgbot.config import Config
from tgbot.filters.private import IsPrivateFilter
from tgbot.keyboards.callback_data import TariffsCallbackData
from tgbot.keyboards.inline import my_subscription_keyboard, crypto_pay_link, \
    instruction_keyboard, join_resources_keyboard, pay_keyboard
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
    # user = await repo.users.select_user(call.message.chat.id)
    # reference_date = datetime(2025, 1, 10)

    # data = await state.get_data()
    # payments_opened = data.get('payments_opened')
    #
    # if payments_opened != 'True' and user.created_at > reference_date:
    #     text = ("Приватный канал закрыт.\n\n"
    #             "Но можешь насладиться подкастом")
    #     photo = "AgACAgIAAxkBAAEBGrpnf455RP6B5uNFzd3G5oqw1YuZTgACLuoxGzT-AAFIhutJCNi8w8IBAAMCAAN5AAM2BA"
    #     await call.message.answer_photo(photo=photo, caption=text, reply_markup=podcast_channel_keyboard())
    #     return
    plan = await repo.plans.select_plan(callback_data.id)
    subscription = await repo.subscriptions.create_subscription(
        user_id=call.message.chat.id,
        plan_id=callback_data.id,
        is_recurrent=True,
        is_gifted=False,
        status="pending"
    )
    payment = await repo.payments.create_payment(
        call.message.chat.id,
        subscription.id)

    if plan.original_price != plan.discounted_price:
        discount_percentage = int((1 - plan.discounted_price / plan.original_price) * 100)
        price_text = f"<b>Стоимость:</b> <s>{plan.original_price} ₽</s> {plan.discounted_price} ₽ (скидка {discount_percentage if discount_percentage > 10 else 10}%)\n"
    else:
        price_text = f"<b>Стоимость:</b> {plan.original_price} ₽\n"

    text = config.text.tariff_caption.replace("{plan.name}", plan.name).replace("{price_text}", price_text).replace("{plan.name[:-2]}", str(plan.name[:-2]))

    await state.update_data(usd_price=plan.usd_price)
    await state.update_data(plan_id=plan.id)
    await state.update_data(payment_id=payment.id)

    product = [
        {
            "quantity": 1,
            "name": plan.name[:-2],
            "price": int(plan.discounted_price),
            "sku": plan.id
        }
    ]

    link = generate_payment_link(str(call.message.chat.id), payment.id, product, config.payment.token, config.misc.payment_form_url)

    sent_message = await call.message.answer(text, reply_markup=pay_keyboard(link, "tariffs"))

    await delete_messages(bot, call.message.chat.id, state, [sent_message.message_id])


@subscription_router.message(F.text == '/subscription')
@subscription_router.callback_query(F.data == "my_subscription")
async def my_subscription(event, state: FSMContext, bot: Bot, config: Config):
    chat_id = event.message.chat.id if isinstance(event, CallbackQuery) else event.chat.id

    message_ids = []
    repo = await get_repo(config)

    subscription_days = await repo.subscriptions.get_combined_active_subscription_days(chat_id)

    subscriptions_status = await repo.subscriptions.is_recurrent(chat_id)

    if subscription_days > 0:
        text = config.text.payment_success_message.replace("{days_remaining}", str(subscription_days))
        sent_message = await bot.send_message(chat_id=chat_id, text=text,
                                              reply_markup=my_subscription_keyboard(state="menu",
                                                                                    is_sub=True,
                                                                                    chat_link=create_invite_link(config.misc.private_chat_id),
                                                                                    channel_link=create_invite_link(config.misc.private_channel_id),
                                                                                    is_recurrent=subscriptions_status))
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


@subscription_router.callback_query(F.data == "toggle_recurrence")
async def toggle_recurrence(call: CallbackQuery, config: Config):
    repo = await get_repo(config)

    subscription = await repo.subscriptions.toggle_all_user_subscriptions(call.message.chat.id)

    await call.answer(f"Успешно {'включено' if subscription else 'отключено'} продление", show_alert=True)

    await call.message.edit_reply_markup(reply_markup=my_subscription_keyboard(state="menu",
                                                                               is_sub=True,
                                                                               chat_link=create_invite_link(config.misc.private_chat_id),
                                                                               channel_link=create_invite_link(config.misc.private_channel_id),
                                                                               is_recurrent=subscription))

@subscription_router.callback_query(F.data == "check_crypto_pay")
async def check_crypto_pay(call: CallbackQuery, state: FSMContext, bot: Bot, config: Config):
    repo = await get_repo(config)
    data = await state.get_data()
    hash = data.get("hash")
    usd_price = data.get("usd_price")
    is_unique_hash = await repo.payments.is_unique_payment_hash(hash)
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
        payment = await repo.payments.get_payment_by_id(int(data['payment_id']))

        subscription = await repo.subscriptions.get_subscription_by_id(payment.subscription_id)
        await repo.payments.update_payment(
            payment_id=int(data['payment_id']),
            amount=usd_price,
            currency="RUB",
            payment_method="card_ru",
            is_successful=True
        )
        await repo.subscriptions.update_subscription(
            subscription_id=payment.subscription_id,
            status="active",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=subscription.plan_id)
        )
        await call.message.answer_photo(
            photo=PHOTO_ID_DICT[int(data['plan_id'])],
            caption=caption,
            reply_markup=join_resources_keyboard(
                create_invite_link(config.misc.private_channel_id),
                create_invite_link(config.misc.private_chat_id),
            )
        )
        VIDEO_FILE_ID = config.media.check_crypto_pay_video

        caption = config.text.check_crypto_pay_text.replace("{full_name}", call.message.chat.full_name)
        await asyncio.sleep(1800)
        await call.message.answer_video(VIDEO_FILE_ID, caption=caption, reply_markup=instruction_keyboard())
    else:
        await call.answer(result, show_alert=True)

    await delete_messages(bot, call.message.chat.id, state)