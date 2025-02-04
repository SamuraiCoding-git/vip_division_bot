from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.config import Config
from tgbot.filters.private import IsPrivateFilter
from tgbot.keyboards.callback_data import OfferConsentCallbackData
from tgbot.keyboards.inline import offer_consent_keyboard, greeting_keyboard, generate_payment_keyboard
from tgbot.utils.db_utils import get_repo
from tgbot.utils.message_utils import delete_messages, handle_deeplink, send_consent_request, start_suggestion, \
    send_ded_gs_message, default_action, activate_payment

start_router = Router()

start_router.message.filter(IsPrivateFilter())
start_router.callback_query.filter(IsPrivateFilter())


@start_router.message(CommandStart(deep_link=True))
async def user_deeplink(message: Message, command: CommandObject, config: Config, state: FSMContext):
    deeplink_actions = {
        "9ae0a8989a14fb1263b255b24d8becf2": {
            "action": lambda: activate_payment(message, state),
        },
        "ded_gs": {
            "action": lambda: send_ded_gs_message(message),
        },
        "suggestion": {
            "action": lambda: start_suggestion(message, state),
        }
    }

    action_data = deeplink_actions.get(command.args)

    if action_data:
        await action_data["action"]()
    else:
        await default_action(message, command.args, config)

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
