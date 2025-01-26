from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.config import Config
from tgbot.filters.private import IsPrivateFilter
from tgbot.keyboards.callback_data import OfferConsentCallbackData
from tgbot.keyboards.inline import offer_consent_keyboard, greeting_keyboard, generate_keyboard
from tgbot.misc.states import Suggestion
from tgbot.utils.db_utils import get_repo
from tgbot.utils.message_utils import delete_messages, handle_deeplink, send_consent_request

start_router = Router()

start_router.message.filter(IsPrivateFilter())
start_router.callback_query.filter(IsPrivateFilter())


@start_router.message(CommandStart(deep_link=True))
async def user_deeplink(message: Message, command: CommandObject, config: Config, state: FSMContext):
    if command.args == "9ae0a8989a14fb1263b255b24d8becf2":
        await state.update_data(payments_opened='True')
        await message.answer("Платежная ссылка активирована!", reply_markup=generate_keyboard("📊Выбрать тариф"))
        return
    elif command.args == 'ded_gs':
        photo = "AgACAgIAAxkBAAEBJHBnh3_9jUk_UjRzcdmW0oEyCmwazAAC8-MxG8VuQUgclQED-Tf_RgEAAwIAA3kAAzYE"

        text = (
            "Успей попасть на ведение к главному коучу за 1390\n\n"
            "В приватном канале Рома ДЕД (главный коуч) устраивает 7-ми дневный тренинг по полному раскрытию потенциала.\n\n"
            "Через него уже прошли 1000-чи учеников, и их результаты поражают.\n\n"
            "Слушай гс от Романа с вводными на неделю и присоединяйся к тренингу."
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Слушать ГС от Деда 🔥", callback_data="ded_gs")
            ]
        ])
        await message.answer_photo(photo, caption=text, reply_markup=keyboard)
        return
    elif command.args == "suggestion":
        await message.answer("Напишите вопрос, и мы ответим в ближайшее время.")
        await state.set_state(Suggestion.message)
    text = config.text.mailing_consent_message
    await message.answer(text, reply_markup=offer_consent_keyboard(deeplink=command.args), disable_web_page_preview=True)


@start_router.message(CommandStart())
async def user_start(message: Message, config: Config, state: FSMContext):
    message_ids = []
    repo = await get_repo(config)

    user = await repo.users.select_user(message.from_user.id)
    await repo.users.get_or_create_user(
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username
    )

    if user:
        caption = config.text.start_message
        photo = config.media.welcome_photo_id
        sent_message = await message.answer_photo(photo, caption, reply_markup=greeting_keyboard())
        message_ids.append(sent_message.message_id)
    else:
        text = config.text.offer_consent_message
        sent_message = await message.answer(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=offer_consent_keyboard()
        )
        message_ids.append(sent_message.message_id)

    await delete_messages(message.bot, message.chat.id, state, message_ids)


@start_router.callback_query(OfferConsentCallbackData.filter())
async def offer_consent(call: CallbackQuery, callback_data: OfferConsentCallbackData, config: Config,
                        state: FSMContext):
    await delete_messages(bot=call.bot, chat_id=call.message.chat.id, state=state)

    if callback_data.answer:
        repo = await get_repo(config)
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
