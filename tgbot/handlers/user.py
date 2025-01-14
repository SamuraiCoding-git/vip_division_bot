from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from infrastructure.api.app import config
from tgbot.config import Config
from tgbot.filters.private import IsPrivateFilter
from tgbot.keyboards.callback_data import ReadingCallbackData
from tgbot.keyboards.inline import guide_keyboard, guides_keyboard, \
    community_keyboard
from tgbot.utils.message_utils import delete_messages, handle_seduction_deeplink

user_router = Router()

user_router.message.filter(IsPrivateFilter())
user_router.callback_query.filter(IsPrivateFilter())


@user_router.callback_query(F.data == "read_article")
async def read_article(call: CallbackQuery, state: FSMContext, config: Config):
    text = config.text.read_article_part_1
    text_part_2 = config.text.read_article_part_2
    await state.update_data(read_clicked=True)
    await call.message.answer(text)
    await call.message.answer(text_part_2, reply_markup=guides_keyboard())


@user_router.callback_query(F.data == "get_guide")
async def get_guide(call: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(guide_clicked=True)
    await handle_seduction_deeplink(call, state, config)


@user_router.callback_query(ReadingCallbackData.filter())
async def successful_texting(call: CallbackQuery, state: FSMContext, callback_data: ReadingCallbackData):
    await call.message.answer(callback_data.link)
    if callback_data.state:
        await state.update_data(
            {callback_data.state: True}
        )

@user_router.callback_query(F.data == "guide")
async def guide(call: CallbackQuery, state: FSMContext, bot: Bot, config: Config):
    await delete_messages(bot=bot, chat_id=call.message.chat.id, state=state)

    caption = config.text.guide_caption
    animation = config.media.guide_animation

    sent_message = await call.message.answer_animation(animation, caption=caption, reply_markup=guide_keyboard("menu"))
    await state.update_data(message_ids=[sent_message.message_id])


@user_router.callback_query(F.data == "ready_to_change")
async def ready_to_change(call: CallbackQuery, state: FSMContext):
    await state.update_data(ready_to_change_clicked=True)
    text = config.text.ready_to_change_text
    photo = config.media.ready_to_change_photo
    await call.message.answer_photo(photo, text, reply_markup=community_keyboard())
