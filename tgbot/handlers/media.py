from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.config import Config
from tgbot.filters.private import IsPrivateFilter
from tgbot.keyboards.callback_data import GuidesCallbackData

media_router = Router()

media_router.message.filter(IsPrivateFilter())
media_router.callback_query.filter(IsPrivateFilter())

@media_router.message(F.content_type.in_({"photo", "video", "animation", "document", "video_note", "voice"}))
async def handle_media(message: Message, state: FSMContext):
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


@media_router.callback_query(GuidesCallbackData.filter())
async def guides(call: CallbackQuery, callback_data: GuidesCallbackData, config: Config):
    guides = {
        "texting": config.media.guides_texting_file_id,
        "seduction": config.media.guides_seduction_file_id,
    }

    selected_guide = callback_data.guide
    file_id = guides.get(selected_guide)

    if file_id:
        await call.message.answer_document(file_id)
    else:
        await call.message.answer("Гайд не найден.")
