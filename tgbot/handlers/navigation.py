from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, InputMediaVideo, Message

from tgbot.config import Config
from tgbot.filters.private import IsPrivateFilter
from tgbot.keyboards.callback_data import BackCallbackData, PaginationCallbackData
from tgbot.keyboards.inline import menu_keyboard, vip_division_keyboard, subscription_keyboard, access_payment_keyboard, \
    story_keyboard, assistant_keyboard, access_keyboard, experts_keyboard, reviews_payment_keyboard, pagination_keyboard
from tgbot.utils.db_utils import get_repo
from tgbot.utils.message_utils import delete_messages

navigation_router = Router()

navigation_router.message.filter(IsPrivateFilter())
navigation_router.callback_query.filter(IsPrivateFilter())

@navigation_router.callback_query(F.data == "about_club")
async def about_club(call: CallbackQuery, state: FSMContext, config: Config):
    message_ids = []

    photo = config.media.about_club_photo_id
    sent_message = await call.message.answer_photo(photo, reply_markup=menu_keyboard())
    message_ids.append(sent_message.message_id)
    await call.bot.pin_chat_message(call.message.chat.id, sent_message.message_id)

    await delete_messages(call.bot, call.message.chat.id, state, message_ids)


@navigation_router.message(F.text == "/vipdivision")
@navigation_router.callback_query(F.data == "about_vip_division")
async def about_vip_division(event, state: FSMContext, config: Config):
    chat_id = event.message.chat.id if isinstance(event, CallbackQuery) else event.chat.id

    media_group = [
        InputMediaPhoto(media=config.media.vip_division_photos[0]),
        InputMediaVideo(media=config.media.vip_division_photos[1]),
    ]
    sent_media = await event.bot.send_media_group(chat_id=chat_id, media=media_group)
    message_ids = [msg.message_id for msg in sent_media]

    caption = config.text.vip_division_caption

    sent_caption = await event.bot.send_message(chat_id=chat_id, text=caption, reply_markup=vip_division_keyboard("menu"))
    message_ids.append(sent_caption.message_id)

    await delete_messages(event.bot, chat_id, state, message_ids)


@navigation_router.callback_query(F.data == "how_chat_works")
async def how_chat_works(call: CallbackQuery, state: FSMContext, config: Config):
    message_ids = []

    text = config.text.chat_caption
    sent = await call.message.answer(text, reply_markup=access_payment_keyboard("how_chat_works"))
    message_ids.append(sent.message_id)

    await delete_messages(call.bot, call.message.chat.id, state, message_ids)


@navigation_router.message(F.text == "/biography")
@navigation_router.callback_query(F.data == "biography")
async def biography(event, state: FSMContext, config: Config):
    chat_id = event.message.chat.id if isinstance(event, CallbackQuery) else event.chat.id
    caption = config.text.biography_message
    photo = config.media.biography_photo_id

    message_ids = []

    sent_photo = await event.bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=caption,
        reply_markup=story_keyboard("menu")
    )

    message_ids.append(sent_photo.message_id)

    await delete_messages(event.bot, chat_id, state, message_ids)


@navigation_router.callback_query(F.data == "questions")
async def questions(call: CallbackQuery, state: FSMContext, config: Config):
    text = config.text.questions_caption
    photo = config.media.questions_photo
    sent_message = await call.message.answer_photo(photo, caption=text, reply_markup=access_keyboard("menu"))
    await state.update_data(message_ids=[sent_message.message_id])

    await delete_messages(call.bot, call.message.chat.id, state, [sent_message.message_id])

@navigation_router.message(F.text == '/support')
async def support(message: Message, state: FSMContext):
    text = "<b>Личный ассистент Кастинг Директора</b>"
    sent_message = await message.answer(text, reply_markup=assistant_keyboard("menu"))

    await delete_messages(message.bot, message.from_user.id, state, [sent_message.message_id])


@navigation_router.message(F.text == "/experts")
@navigation_router.callback_query(F.data == "experts")
async def experts(event, state: FSMContext, config: Config):
    chat_id = event.message.chat.id if isinstance(event, CallbackQuery) else event.chat.id

    text = config.text.experts_caption

    sent_message = await event.bot.send_message(chat_id, text, reply_markup=experts_keyboard("menu"))
    await delete_messages(event.bot, chat_id, state, [sent_message.message_id])

@navigation_router.callback_query(F.data == "reviews")
async def reviews(call: CallbackQuery, state: FSMContext, config: Config):
    media_group = [
        InputMediaPhoto(media=config.media.reviews_photos[0]),
        InputMediaPhoto(media=config.media.reviews_photos[1]),
    ]

    sent_media = await call.message.answer_media_group(media=media_group)

    message_ids = [msg.message_id for msg in sent_media]

    caption = config.text.reviews_caption

    sent_caption = await call.message.answer(text=caption, reply_markup=reviews_payment_keyboard("menu"))
    message_ids.append(sent_caption.message_id)

    await delete_messages(call.bot, call.message.chat.id, state, message_ids)

@navigation_router.callback_query(BackCallbackData.filter())
async def filter_callback_query(call: CallbackQuery, callback_data: BackCallbackData, state: FSMContext, config: Config):
    await delete_messages(bot=call.bot, chat_id=call.message.chat.id, state=state)

    if callback_data.state == "menu":
        photo = config.media.about_club_photo_id
        new_message = await call.message.answer_photo(photo, reply_markup=menu_keyboard())
        await call.bot.pin_chat_message(call.message.chat.id, new_message.message_id)
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
        repo = await get_repo(config)
        plans = await repo.plans.get_all_plans()

        text = config.text.tariffs_message
        sent_message = await call.bot.send_message(chat_id=call.message.chat.id, text=text,
                                              reply_markup=subscription_keyboard("menu", plans))
        await state.update_data(message_ids=[sent_message.message_id])


@navigation_router.callback_query(PaginationCallbackData.filter())
async def handle_pagination(call: CallbackQuery, callback_data: PaginationCallbackData, config: Config):
    current_page = callback_data.page

    total_pages = 2

    if current_page < 1:
        current_page = total_pages
    elif current_page > total_pages:
        current_page = 1

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

    keyboard = pagination_keyboard(current_page)

    await call.message.edit_media(
        media=photos[str(current_page)],
        reply_markup=keyboard,
    )
