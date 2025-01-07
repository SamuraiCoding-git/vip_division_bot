import re
from datetime import datetime, timedelta

import time
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo, FSInputFile

from infrastructure.api.app import config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_session_pool
from main import create_invite_link
from tgbot.config import Config
from tgbot.filters.private import IsPrivateFilter
from tgbot.keyboards.callback_data import OfferConsentCallbackData, BackCallbackData, GuidesCallbackData, \
    PaginationCallbackData, ReadingCallbackData, TariffsCallbackData
from tgbot.keyboards.inline import offer_consent_keyboard, greeting_keyboard, menu_keyboard, vip_division_keyboard, \
    access_payment_keyboard, story_keyboard, subscription_keyboard, reviews_payment_keyboard, experts_keyboard, \
    assistant_keyboard, access_keyboard, my_subscription_keyboard, guide_keyboard, pagination_keyboard, guides_keyboard, \
    pay_keyboard, crypto_pay_link, crypto_pay_check_keyboard, join_resources_keyboard, instruction_keyboard, \
    community_keyboard
from tgbot.misc.states import UsdtTransaction
from tgbot.utils.message_utils import delete_messages, handle_deeplink, send_consent_request, handle_seduction_deeplink
from tgbot.utils.payment_utils import generate_payment_link, generate_qr_code
from tgbot.utils.sub_utils import get_transaction_confirmations

user_router = Router()

user_router.message.filter(IsPrivateFilter())
user_router.callback_query.filter(IsPrivateFilter())

@user_router.message(F.content_type.in_({"photo", "video", "animation", "document", "video_note", "voice"}))
async def send_media(message: Message, state: FSMContext):
    if message.from_user.id != 422999166:
        return
    data = await state.get_data()
    message_ids = data.get("message_ids", [])
    message_ids.append(message.message_id)
    await state.update_data(message_ids=message_ids)

    content_type_to_attr = {
        "photo": message.photo[-1].file_id if message.photo else None,
        "video": message.video.file_id if message.video else None,
        "animation": message.animation.file_id if message.animation else None,
        "document": message.document.file_id if message.document else None,
        "video_note": message.video_note.file_id if message.video_note else None,
        "voice": message.voice.file_id if message.voice else None,
    }

    file_id = content_type_to_attr.get(message.content_type)

    if file_id:
        sent_message = await message.reply(file_id)
        message_ids.append(sent_message.message_id)
        await state.update_data(message_ids=message_ids)


@user_router.callback_query(F.data == "read_article")
async def read_article(call: CallbackQuery, state: FSMContext, config: Config):
    text = config.text.read_article_part_1
    text_part_2 = config.text.read_article_part_2
    await state.update_data(read_clicked=True)
    await call.message.answer(text)
    await call.message.answer(text_part_2, reply_markup=guides_keyboard())



@user_router.message(CommandStart(deep_link=True))
async def user_deeplink(message: Message, command: CommandObject, config: Config):
    text = config.text.mailing_consent_message
    await message.answer(text, reply_markup=offer_consent_keyboard(deeplink=command.args), disable_web_page_preview=True)


@user_router.callback_query(F.data == "get_guide")
async def get_guide(call: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(guide_clicked=True)
    await handle_seduction_deeplink(call, state, config)



@user_router.callback_query(PaginationCallbackData.filter())
async def handle_pagination(call: CallbackQuery, callback_data: PaginationCallbackData):
    # Get the current page from the callback data
    current_page = callback_data.page

    # Total number of pages
    total_pages = 2

    # Wrap around logic
    if current_page < 1:
        current_page = total_pages
    elif current_page > total_pages:
        current_page = 1

    # Define the media for each page
    if call.message.video.file_id in config.media.pagination_photos[:2]:
        photos = {
            "1": InputMediaPhoto(media=config.media.pagination_photos[0]),
            "2": InputMediaPhoto(media=config.media.pagination_photos[1])
        }
    else:
        photos = {
            "1": InputMediaPhoto(media=config.media.pagination_photos[2]),
            "2": InputMediaPhoto(media=config.media.pagination_photos[3])
        }
    # Generate the pagination keyboard
    keyboard = pagination_keyboard(current_page)

    # Edit the message with the new content and keyboard
    await call.message.edit_media(
        media=photos[str(current_page)],
        reply_markup=keyboard,
    )



@user_router.message(CommandStart())
async def user_start(message: Message, config: Config, state: FSMContext):
    session_pool = await create_session_pool(config.db)

    async with session_pool() as session:
        repo = RequestsRepo(session)
        user = await repo.users.select_user(message.from_user.id)
        await repo.users.get_or_create_user(
            message.from_user.id,
            message.from_user.full_name,
            message.from_user.username
        )

    await delete_messages(bot=message.bot, chat_id=message.chat.id, state=state)

    if user:
        caption = config.text.start_message
        photo = config.media.welcome_photo_id
        sent_message = await message.answer_photo(photo, caption, reply_markup=greeting_keyboard())
        await state.update_data(message_ids=[sent_message.message_id])
    else:
        text = config.text.offer_consent_message
        sent_message = await message.answer(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=offer_consent_keyboard()
        )
        await state.update_data(message_ids=[sent_message.message_id])


@user_router.callback_query(OfferConsentCallbackData.filter())
async def offer_consent(call: CallbackQuery, callback_data: OfferConsentCallbackData, config: Config,
                        state: FSMContext):
    await delete_messages(bot=call.bot, chat_id=call.message.chat.id, state=state)

    if callback_data.answer:
        session_pool = await create_session_pool(config.db)

        async with session_pool() as session:
            repo = RequestsRepo(session)
            await repo.users.get_or_create_user(
                call.message.chat.id,
                call.message.chat.full_name,
                call.message.chat.username
            )

        if not callback_data.deeplink:
            caption = config.text.start_message
            photo = config.media.welcome_photo_id
            sent_message = await call.message.answer_photo(photo, caption, reply_markup=greeting_keyboard())
            await state.update_data(message_ids=[sent_message.message_id])
        else:
            await handle_deeplink(call, config, callback_data.deeplink, state)
    else:
        await send_consent_request(call, state)

@user_router.callback_query(F.data == "about_club")
async def about_club(call: CallbackQuery, bot: Bot, state: FSMContext):
    await delete_messages(bot=call.bot, chat_id=call.message.chat.id, state=state)

    photo = config.media.about_club_photo_id
    sent_message = await call.message.answer_photo(photo, reply_markup=menu_keyboard())
    await bot.pin_chat_message(call.message.chat.id, sent_message.message_id)
    await state.update_data(message_ids=[sent_message.message_id])


@user_router.message(F.text == "/vipdivision")
@user_router.callback_query(F.data == "about_vip_division")
async def about_vip_division(event, bot: Bot, state: FSMContext):
    if isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
        await delete_messages(bot=bot, chat_id=chat_id, state=state)
    elif isinstance(event, Message):
        chat_id = event.chat.id

    media_group = [
        InputMediaPhoto(media=config.media.vip_division_photos[0]),
        InputMediaVideo(media=config.media.vip_division_photos[1]),
    ]
    sent_media = await bot.send_media_group(chat_id=chat_id, media=media_group)
    message_ids = [msg.message_id for msg in sent_media]

    caption = config.text.vip_division_caption

    sent_caption = await bot.send_message(chat_id=chat_id, text=caption, reply_markup=vip_division_keyboard("menu"))
    message_ids.append(sent_caption.message_id)

    await state.update_data(message_ids=message_ids)


@user_router.callback_query(F.data == "how_chat_works")
async def how_chat_works(call: CallbackQuery, state: FSMContext):
    await delete_messages(bot=call.bot, chat_id=call.message.chat.id, state=state)

    message_ids = []

    text = config.text.chat_caption
    sent = await call.message.answer(text, reply_markup=access_payment_keyboard("how_chat_works"))
    message_ids.append(sent.message_id)

    await state.update_data(message_ids=message_ids)

@user_router.message(F.text == "/biography")
@user_router.callback_query(F.data == "biography")
async def biography(event, state: FSMContext, bot: Bot):
    # Determine the type of event (message or callback query)
    if isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
    elif isinstance(event, Message):
        chat_id = event.chat.id
    await delete_messages(bot=event.bot, chat_id=chat_id, state=state)

    caption = config.text.biography_message

    photo = config.media.biography_photo_id

    # Send the photo with caption and a keyboard for navigation
    sent_photo = await bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=caption,
        reply_markup=story_keyboard("menu")
    )
    await state.update_data(message_ids=[sent_photo.message_id])

# @user_router.message()
# async def message_mailing(message: Message, config: Config, bot: Bot):
#     if message.from_user.id != 422999166:
#         return
#     session_pool = await create_session_pool(config.db)
#     async with session_pool() as session:
#         repo = RequestsRepo(session)
#     users = await repo.orders.get_users_with_unpaid_orders()
#
#     media_group = [
#         InputMediaPhoto(media="AgACAgIAAxkBAAL3SGd9UE3wfsGlDfEwNWhcgnuICwTxAAKc5TEb1ZfwS5mYI_pSCptZAQADAgADeAADNgQ"),
#         InputMediaPhoto(media="AgACAgIAAxkBAAL3R2d9UE1EYeBhPXFvQGBkWna2yXcnAAKb5TEb1ZfwS0agxuDpiNZzAQADAgADeQADNgQ"),
#         InputMediaPhoto(media="AgACAgIAAxkBAAL3Smd9UE3kyz-lk6HssIYs6yJ-RcNpAAKd5TEb1ZfwS-K_RG3NedvvAQADAgADeAADNgQ"),
#         InputMediaPhoto(media="AgACAgIAAxkBAAL3Rmd9UE3GKs6c6cRJIimssYktbBDAAAKa5TEb1ZfwS_ltPR5mcvEqAQADAgADeAADNgQ"),
#         InputMediaPhoto(media="AgACAgIAAxkBAAL3SWd9UE3RPnWOeKknSGUQZZ_CarbDAAKe5TEb1ZfwS3T7_fqc1lXAAQADAgADeQADNgQ")
#     ]
#
#     await message.answer("Рассылка началась.")
#
#
#     for user in users:
#         if user in [821892126, 886105115]:
#             continue
#         try:
#             await bot.forward_message(chat_id=user, from_chat_id=message.chat.id, message_id=message.message_id)
#         except:
#             pass
#         time.sleep(0.06)
#     await message.answer("Рассылка завершена")

@user_router.message(F.text == "/payment")
@user_router.callback_query(F.data == "view_tariffs")
@user_router.callback_query(F.data == "tariffs")

async def tariffs(event, state: FSMContext, bot: Bot, config: Config):
    if isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
    elif isinstance(event, Message):
        chat_id = event.chat.id
    await delete_messages(bot=bot, chat_id=chat_id, state=state)

    session_pool = await create_session_pool(config.db)

    async with session_pool() as session:
        repo = RequestsRepo(session)
        plans = await repo.plans.get_all_plans()

    text = config.text.tariffs_message
    sent_message = await bot.send_message(chat_id=chat_id, text=text, reply_markup=subscription_keyboard("menu", plans))
    await state.update_data(message_ids=[sent_message.message_id])

@user_router.callback_query(ReadingCallbackData.filter())
async def successful_texting(call: CallbackQuery, state: FSMContext, callback_data: ReadingCallbackData):
    await call.message.answer(callback_data.link)
    if callback_data.state:
        await state.update_data(
            {callback_data.state: True}
        )


@user_router.callback_query(F.data == "reviews")
async def reviews(call: CallbackQuery, state: FSMContext, bot: Bot):
    await delete_messages(bot=bot, chat_id=call.message.chat.id, state=state)

    media_group = [
        InputMediaPhoto(media=config.media.reviews_photos[0]),
        InputMediaPhoto(media=config.media.reviews_photos[1]),
    ]

    sent_media = await call.message.answer_media_group(media=media_group)

    message_ids = [msg.message_id for msg in sent_media]

    caption = config.text.reviews_caption

    sent_caption = await call.message.answer(text=caption, reply_markup=reviews_payment_keyboard("menu"))
    message_ids.append(sent_caption.message_id)

    await state.update_data(message_ids=message_ids)

@user_router.message(F.text == "/experts")
@user_router.callback_query(F.data == "experts")
async def experts(event, state: FSMContext, bot: Bot):
    if isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
    elif isinstance(event, Message):
        chat_id = event.chat.id
    await delete_messages(bot=bot, chat_id=chat_id, state=state)

    text = config.text.experts_caption

    sent_message = await bot.send_message(chat_id, text, reply_markup=experts_keyboard("menu"))
    await state.update_data(message_ids=[sent_message.message_id])

@user_router.callback_query(F.data == "questions")
async def questions(call: CallbackQuery, state: FSMContext, bot: Bot, config: Config):
    await delete_messages(bot=bot, chat_id=call.message.chat.id, state=state)

    text = config.text.questions_caption
    photo = config.media.questions_photo
    sent_message = await call.message.answer_photo(photo, caption=text, reply_markup=access_keyboard("menu"))
    await state.update_data(message_ids=[sent_message.message_id])

@user_router.message(F.text == '/support')
async def support(message: Message, state: FSMContext, bot: Bot):
    await delete_messages(bot=bot, chat_id=message.from_user.id, state=state)

    text = "<b>Личный ассистент Кастинг Директора</b>"
    sent_message = await message.answer(text, reply_markup=assistant_keyboard("menu"))
    await state.update_data(message_ids=[sent_message.message_id])


@user_router.message(F.text == '/subscription')
@user_router.callback_query(F.data == "my_subscription")
async def my_subscription(event, state: FSMContext, bot: Bot, config: Config):
    if isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
    elif isinstance(event, Message):
        chat_id = event.chat.id

    # Delete previous messages
    await delete_messages(bot=bot, chat_id=chat_id, state=state)

    # Create a database session and handle the logic
    session_pool = await create_session_pool(config.db)
    async with session_pool() as session:
        repo = RequestsRepo(session)
        order = await repo.orders.get_latest_paid_order_by_user(chat_id)

        if order:
            plan = await repo.plans.select_plan(order.plan_id)
            try:
                # Calculate days remaining
                duration_days = plan.duration  # Extract duration as integer
                end_date = order.start_date + timedelta(days=duration_days)
                days_remaining = max((end_date - datetime.utcnow()).days, 0)
            except ValueError:
                days_remaining = 0
        else:
            days_remaining = 0
        # Prepare the message text based on subscription status
        if days_remaining > 0:
            text = config.text.payment_success_message.replace("{days_remaining}", str(days_remaining))
            sent_message = await bot.send_message(chat_id=chat_id, text=text,
                                                  reply_markup=my_subscription_keyboard(state="menu",
                                                                                        is_sub=True,
                                                                                        chat_link=create_invite_link(config.misc.private_chat_id),
                                                                                        channel_link=create_invite_link(config.misc.private_channel_id)))
        else:
            text = config.text.payment_inactive_message

        # Send the message
            sent_message = await bot.send_message(chat_id=chat_id, text=text, reply_markup=my_subscription_keyboard(state="menu"))
    # Update state with the message ID for tracking
    await state.update_data(message_ids=[sent_message.message_id])


@user_router.callback_query(TariffsCallbackData.filter())
async def sub_tariffs(call: CallbackQuery, state: FSMContext, bot: Bot, callback_data: TariffsCallbackData, config: Config):
    await delete_messages(bot=bot, chat_id=call.message.chat.id, state=state)
    session_pool = await create_session_pool(config.db)
    async with session_pool() as session:
        repo = RequestsRepo(session)
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
    await state.update_data(message_ids=[sent_message.message_id])

@user_router.callback_query(F.data == "guide")
async def guide(call: CallbackQuery, state: FSMContext, bot: Bot, config: Config):
    await delete_messages(bot=bot, chat_id=call.message.chat.id, state=state)

    caption = config.text.guide_caption
    animation = config.media.guide_animation

    sent_message = await call.message.answer_animation(animation, caption=caption, reply_markup=guide_keyboard("menu"))
    await state.update_data(message_ids=[sent_message.message_id])


@user_router.callback_query(GuidesCallbackData.filter())
async def guides(call: CallbackQuery, state: FSMContext, bot: Bot, callback_data: GuidesCallbackData, config: Config):
    guides = {
        "texting": config.media.guides_texting_file_id,  # Гайд по перепискам
        "seduction": config.media.guides_seduction_file_id,  # Гайд по соблазнению
    }

    # Get the selected guide
    selected_guide = callback_data.guide
    file_id = guides.get(selected_guide)

    if file_id:
        # Send the guide as a document
        await call.message.answer_document(file_id)
    else:
        # Send an error message if the guide is not found
        await call.message.answer("Гайд не найден.")


@user_router.callback_query(F.data == "pay_crypto")
async def pay_crypto_handler(call: CallbackQuery, state: FSMContext, bot: Bot, config: Config):
    await delete_messages(bot, chat_id=call.message.chat.id, state=state)

    data = await state.get_data()
    usd_price = int(data.get("usd_price"))
    trust_wallet_link = f"tron:{config.misc.tron_wallet}?amount={usd_price}"
    path = generate_qr_code(trust_wallet_link)
    qr_code_png = FSInputFile(path)

    caption = (f"Адрес: {config.misc.tron_wallet}\n"
               f"Стоимость: {usd_price}$\n\n"
               f"Отправьте хэш транзакции:")

    sent_message = await call.message.answer_photo(qr_code_png, caption=caption, reply_markup=crypto_pay_link('tariffs'), parse_mode='HTML')
    await state.set_state(UsdtTransaction.hash )
    await state.update_data(message_ids=[sent_message.message_id])


@user_router.message(UsdtTransaction.hash)
async def usdt_transaction_hash(message: Message, state: FSMContext, bot: Bot):
    await delete_messages(bot, chat_id=message.chat.id, state=state)
    hash_text = message.text.strip()

    tron_hash_pattern = r'^[a-f0-9]{64}$'

    if re.match(tron_hash_pattern, hash_text):
        sent_message = await message.answer(
            "После подтверждения транзакции 20 блоками - нажми на кнопку.",
                 reply_markup=crypto_pay_check_keyboard("tariffs"))
    else:
        sent_message = await message.answer(
            "Неверный хэш транзакции Tron."
            "Отправьте ещё раз")
        await state.update_data(message_ids=[sent_message.message_id])
        return
    await state.update_data(hash=hash_text)
    await state.update_data(message_ids=[sent_message.message_id])


@user_router.callback_query(F.data == "check_crypto_pay")
async def check_crypto_pay(call: CallbackQuery, state: FSMContext, bot: Bot, config: Config):
    await delete_messages(bot=bot, chat_id=call.message.chat.id, state=state)
    session_pool = await create_session_pool(config.db)
    async with session_pool() as session:
        repo = RequestsRepo(session)
    data = await state.get_data()
    hash = data.get("hash")
    usd_price = data.get("usd_price")
    is_unique_hash = await repo.orders.is_unique_order_hash(hash)
    if not is_unique_hash:
        await call.answer("Уже есть заказ с таким хэшем", show_alert=True)
    result = get_transaction_confirmations(hash, usd_price, config.misc.tron_wallet)
    print()
    if result:
        caption = "✅ Подписка на канал успешно оформлена!\nПерeходи по кнопкам ниже:"
        PHOTO_ID_DICT = {
            1: "AgACAgIAAxkBAALEjGdy0mrDQWi18wFpYoZq9NVA2TqjAAKV6TEbOoaJS4n3s7ggUnRgAQADAgADeQADNgQ",
            2: "AgACAgIAAxkBAALEimdy0mogvij5Ftf2H8gl35umq8q3AAKS6TEbOoaJSyo0D53HGSccAQADAgADeQADNgQ",
            3: "AgACAgIAAxkBAALVIGdz6Q6rehB64Lr3d9PdSyHCntiHAAKy5jEb3eahS01IU1EPEcbzAQADAgADeQADNgQ",
            4: "AgACAgIAAxkBAALEi2dy0mq9sEozgl_G_TSMMQTr6Xv4AAKT6TEbOoaJS3CNhv-ILUFiAQADAgADeQADNgQ"
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
                                  ))
        VIDEO_FILE_ID = "BAACAgIAAxkBAALmHGd4rRnMKnmvZnp2ziGvf9VqZZsUAAJcXQACQzDJS1VissnlL4f0NgQ"

        caption = (
            f"{call.message.chat.full_name}, приветствуем тебя, бро, ты попал в лучшее мужское комьюнити 🤝\n\n"
            "Я заявляю с полной уверенностью, что знаю все, что ты хочешь получить в этой жизни.\n"
            "Я знаю как тебе это дать!\n\n"
            "<b>ТЫ ХОЧЕШЬ ТРЁХ ВЕЩЕЙ — ТРАХАТЬСЯ, ВЫЖИТЬ И БЫТЬ ЛУЧШЕ ОСТАЛЬНЫХ.</b>\n\n"
            "В закрепе канала ты найдёшь:\n"
            "1 — первый пост (начни с него)\n"
            "2 — навигацию по темам для удобства и поиска информации (в описании канала)\n"
            "3 — Не забудь вступить в ЧАТ для общения с парнями\n\n"
            "Переходи по кнопке ИНСТРУКЦИЯ для новичка и начинай собирать эту жизнь!"
        )
        await call.message.answer_video(VIDEO_FILE_ID, caption=caption, reply_markup=instruction_keyboard())
    else:
        await call.answer("Транзакция ещё не подтверждена!", show_alert=True)


@user_router.callback_query(F.data == "ready_to_change")
async def ready_to_change(call: CallbackQuery, state: FSMContext):
    await state.update_data(ready_to_change_clicked=True)
    text = (
        "Именно здесь произойдет максимально эффективное развитие тебя по всем фронтам.\n\n"
        "Закрытое сообщество мужчин, которым не похуй на себя и свою жизнь — <b>VIP DIVISION</b>\n\n"
        "<b>СООБЩЕСТВО СОСТОИТ ИЗ:</b>\n\n"
        "📚<b>ЗНАНИЯ</b> — практическое руководство для любого мужчины, который собирается получить от жизни ВСЁ!!!\n\n"
        "Что в себя включает?\n\n"
        "1) <b>СОБЛАЗНЕНИЕ. Теория/практика</b>\n"
        "— здесь про психологию и работу мозга женщины, секс, как появляется влечение, свидания и что на них говорить, + фишки (манипуляции) на общения вживую и по переписке\n\n"
        "2) <b>ОТНОШЕНИЯ. Найти/сохранить</b>\n"
        "— здесь про выбор пригодной девушки для семьи, как вести себя так, чтобы страсть не пропадала, про распределение ролей, воспитание детей и просто о счастливой семейной жизни.\n\n"
        "3) <b>МУЖЕСТВЕННОСТЬ. ДЕНЬГИ. УСПЕХ. ХАРИЗМА. МЫШЛЕНИЕ.</b>\n"
        "— здесь ты прокачиваешь свою личность на весь свой потенциал. Сначала уничтожаешь ограничивающие убеждения, закладываешь новые сильные мысли, разжигаешь любовь к себе и миру, и на этой энергии становишься <b>ЕБЫРЕМ ПРИВАТКИ</b>.\n\n"
        "💭<b>ЧАТ</b>\n"
        "Знания это хорошо, но чат это место их применения и поддержки.\n\n"
        "Сгусток тестостеронового-дружной атмосферы, где люди достигшие результатов помогут вам с вопросами, дадут дельные советы в любой сфере жизни.\n\n"
        "Мужчины объединённых общей целью ВЫЕБАТЬ ЭТУ ЖИЗНЬ, тут рады всем, кто стремится к развитию — вот что тебе нужно.\n\n"
        "Ты уже понял, что <b>ЭТО САМОЕ ЛУЧШЕЕ</b>, что есть в интернете и один только вопрос, сколько стоит?\n\n"
        "46 ₽ в день / <b>жирный шрифт</b>\n"
        "или 1390 в месяц / <b>жирный шрифт</b>\n\n"
        "<b>НИ ОДНОГО ПЛОХОГО ОТЗЫВА</b>\n"
        "Это можно считать выдумкой, но это ФАКТ, люди меняют свою жизнь на 180 градусов уже за неделю чтения."
    )
    photo = "AgACAgIAAxkBAALwSmd7rbeai71JkaICHNAtxB6n2CE4AAJb7zEbBr3ZS4VZXoog8qcCAQADAgADeQADNgQ"
    await call.message.answer_photo(photo, text, reply_markup=community_keyboard())


@user_router.callback_query(BackCallbackData.filter())
async def filter_callback_query(call: CallbackQuery, callback_data: BackCallbackData, bot: Bot, state: FSMContext, config: Config):
    await delete_messages(bot=call.bot, chat_id=call.message.chat.id, state=state)

    if callback_data.state == "menu":
        photo = config.media.about_club_photo_id
        new_message = await call.message.answer_photo(photo, reply_markup=menu_keyboard())
        await bot.pin_chat_message(call.message.chat.id, new_message.message_id)
        await state.update_data(message_ids=[new_message.message_id])
    elif callback_data.state == "how_chat_works":
        media_group = [
            InputMediaPhoto(media=config.media.vip_division_photos[0]),
            InputMediaVideo(media=config.media.vip_division_photos[1]),
        ]
        sent_media = await call.message.answer_media_group(media_group)
        message_ids = [msg.message_id for msg in sent_media]

        caption = config.text.vip_division_caption

        sent_caption = await call.message.answer(caption, reply_markup=vip_division_keyboard("menu"))
        message_ids.append(sent_caption.message_id)
        await state.update_data(message_ids=message_ids)
    elif callback_data.state == "tariffs":
        session_pool = await create_session_pool(config.db)

        async with session_pool() as session:
            repo = RequestsRepo(session)
            plans = await repo.plans.get_all_plans()

        text = config.text.tariffs_message
        sent_message = await bot.send_message(chat_id=call.message.chat.id, text=text,
                                              reply_markup=subscription_keyboard("menu", plans))
        await state.update_data(message_ids=[sent_message.message_id])
