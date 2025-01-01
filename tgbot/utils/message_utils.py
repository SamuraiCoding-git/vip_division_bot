import asyncio

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto

from tgbot.config import Config
from tgbot.keyboards.inline import offer_consent_keyboard, get_guide_keyboard, communication_base_keyboard, \
    pagination_keyboard, read_keyboard, guides_keyboard


async def delete_messages(bot: Bot, chat_id: int, state: FSMContext):
    data = await state.get_data()
    message_ids = data.get("message_ids", [])

    for message_id in message_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            print(f"Failed to delete message {message_id}: {e}")

    await state.update_data(message_ids=[])

async def handle_deeplink(call: CallbackQuery, deeplink: str, state):
    deeplink_handlers = {
        "texting": handle_texting_deeplink,
        "seduction": handle_seduction_deeplink,
    }

    handler = deeplink_handlers.get(deeplink)
    if handler:
        await handler(call, state)
    else:
        await call.message.answer("Неизвестный диплинк. Попробуйте ещё раз.")


async def handle_texting_deeplink(call: CallbackQuery, state: FSMContext, config: Config):
    photo_1 = config.media.photo_1
    caption_1 = config.text.texting_guide_intro
    await call.message.answer_photo(photo_1, caption_1)
    await asyncio.sleep(60)

    texting_guide_file_id = config.media.texting_guide_file_id
    file_caption = config.text.texting_guide_caption
    await call.message.answer_document(texting_guide_file_id)
    await call.message.answer(file_caption)
    await asyncio.sleep(1800)

    caption = config.text.texting_guide_advantages
    animation = config.media.texting_guide_animation
    await call.message.answer_animation(animation, caption=caption)
    await asyncio.sleep(3600)

    text = config.text.texting_guide_base
    await call.message.answer(text, reply_markup=communication_base_keyboard())
    await asyncio.sleep(43200)

    caption_2 = config.text.dialogue_analysis_text
    photo_2 = config.media.photo_2
    await call.message.answer_photo(photo_2, caption_2)
    await asyncio.sleep(1800)

    media_group = [
        InputMediaPhoto(media=config.media.media_group_photos[0]),
        InputMediaPhoto(media=config.media.media_group_photos[1]),
        InputMediaPhoto(media=config.media.media_group_photos[2])
    ]
    media_group_caption = config.text.media_group_caption
    await call.message.answer_media_group(media_group)
    await call.message.answer(media_group_caption, reply_markup=get_guide_keyboard("✅ Забрать ГАЙД"))

    data = await state.get_data()
    if not data.get("guide_clicked"):
        text = (
            "Как писать так, чтобы девочка понимала, что перед ней не просто очередной славный ухажер, "
            "а опытный и востребованный альфа, с ох*енным чувством юмора.\n\n"
            "<b>Забирай пост и мои примеры смс.</b>"
        )
        await call.message.answer(text, reply_markup=read_keyboard("Читать", "https://t.me/c/1699879031/1651", "reading_1651_1_clicked"))
    await asyncio.sleep(600)

    data = await state.get_data()
    if not data.get("reading_1651_1_clicked"):
        text = config.text.read_article_part_1
        text_part_2 = config.text.read_article_part_2
        await call.message.answer(text)
        await call.message.answer(text_part_2, reply_markup=guides_keyboard())

    data = await state.get_data()
    if not data.get("successful_texting_clicked"):
        caption = "Разбор переписки от ученика, объясняю какие фишки использовал"
        photo = config.media.reading_1651_photo
        await call.message.answer_photo(photo, caption=caption, reply_markup=read_keyboard("Читать", "https://t.me/c/1699879031/1651", "reading_1651_2_clicked"))
    await asyncio.sleep(86400)

    data = await state.get_data()
    if not data.get("reading_1651_2_clicked"):
        text = config.text.performance_text
        await call.message.answer(text, reply_markup=read_keyboard("Читать переписку", "https://t.me/c/1699879031/1735", "reading_1735_1_clicked"))
        await asyncio.sleep(900)

    data = await state.get_data()
    if not data.get("reading_1735_1_clicked"):
        caption = (
            "Познакомился с девчонкой, всё по приватке, показал ценность, по началу "
            "выёбывалась и гнула пальцы.\n\n"
            "Спустя два дня общения готова снять дом с Басcиком, что бы я 🤴🏻 отдыхнул 😄"
        )
        photo = "AgACAgIAAxkBAALEkmdy0movAzjNmJEvUQEozr3PPE-KAAKb6TEbOoaJS0SeGzCpreeMAQADAgADeQADNgQ"
        await call.message.answer_photo(photo, caption=caption,
                                        reply_markup=read_keyboard("Читать", "https://t.me/c/1699879031/1735",
                                                                   "reading_1735_2_clicked", True))
        await asyncio.sleep(1800)

    data = await state.get_data()
    if not data.get("reading_1735_2_clicked"):
        text = (
            "С девушкой нужно сохранять баланс под*ебов и душевности, "
            "нужно также показывать им, что ты человек, который проявляет заботу и готов защищать близких. "
            "В бесплатном гайде по соблазнению я уже все рассказал, не ленись читать. "
            "Это должен знать каждый мужчина!"
        )
        await call.message.answer(text, reply_markup=get_guide_keyboard("Читать ГАЙД ✅"))

async def handle_seduction_deeplink(call: CallbackQuery, config: Config):
    video_note = config.media.video_note
    video_file = config.media.video_file
    try:
        await call.message.answer_video_note(video_note)
    except Exception as e:
        await call.message.answer_video(video_file)
    await asyncio.sleep(60)

    text = (
        "То, что ты сейчас прочитаешь — полностью поменяет твое мышление, наслаждайся 🤝\n\n"
        "<b>Время чтения:</b> 11 минут"
    )
    file = config.media.guides_seduction_file_id
    await call.message.answer_document(file)
    await call.message.answer(text)
    await asyncio.sleep(300)

    photo_1 = config.media.pagination_photos[0]

    # "AgACAgIAAxkBAAICGmdxSVyiWahM-a-rS3NAk0rYqVpDAALQ5TEbJ2-RSwwAAZtOAeeXDQEAAwIAA3kAAzYE"
    await call.message.answer_photo(photo_1, reply_markup=pagination_keyboard(1))
    await asyncio.sleep(1500)

    text = config.text.texting_guide_advantages
    animation = config.media.guide_animation
    await call.message.answer_video(animation, caption=text)
    await asyncio.sleep(3600)




async def send_consent_request(call: CallbackQuery, state: FSMContext):
    text = (
        "Для того, чтобы продолжить использовать БОТ и получить информацию, необходимо дать "
        "<a href=\"https://docs.google.com/document/d/14V62s6TOVBT8uOB-4UVX6NcTJqsxmVdz5GZnzYQeRe0/edit?tab=t.0\">согласие на получение рекламных рассылок</a> и "
        "<a href=\"https://docs.google.com/document/d/10i9OLsAMYRiNaLuCZwBTE8w9gHCetNgj-AZU_lweodE/edit?usp=drive_link\">согласие оферту по оказанию консультационных услуг</a>. "
        "<i>Подробнее</i> <a href=\"https://docs.google.com/document/d/188a7jAnvl-iB9DKyiVtzJqzm6QfS6oZiezEjfuT9n0w/edit?usp=drive_link\">тут</a>"
    )
    sent_message = await call.message.answer(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=offer_consent_keyboard(False)
    )
    await state.update_data(message_ids=[sent_message.message_id])
