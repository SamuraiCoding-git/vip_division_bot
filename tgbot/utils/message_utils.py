import asyncio

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto

from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_session_pool
from tgbot.config import Config
from tgbot.keyboards.inline import offer_consent_keyboard, get_guide_keyboard, communication_base_keyboard, \
    pagination_keyboard, read_keyboard, guides_keyboard, ready_to_change_keyboard, community_keyboard, \
    want_too_keyboard, together_keyboard, transformation_keyboard, choose_tariff_keyboard


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

async def handle_seduction_deeplink(call: CallbackQuery, state: FSMContext, config: Config):
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

    text = config.text.texting_guide_caption
    animation = config.media.guide_animation
    await call.message.answer_video(animation, caption=text)
    await asyncio.sleep(3600)

    text = (
        "Я знаю, о чем ты сейчас думаешь. Мне это знакомо.\n\n"
        "Прочитал, вроде понял, но но с чего начать? / <b>жирный шрифт</b>\n\n"
        "— Или не знаешь как проработать заниженную самооценку, неуверенность в себе, застенчивость\n"
        "— Чувствуешь, что проживаешь жизнь в пустую. Полное разочарование в себе, ощущение что я проиграл везде где только можно\n"
        "— Слишком вежливый и услужливый (<b>СЛАВНЫЙ ПАРЕНЬ</b>). Как это исправить?\n"
        "— Апатия, депрессия, уныние, негативное мышление\n"
        "— Страдаешь по бывшей, не можешь ее забыть\n\n"
        "Да твои проблемы в пост даже не запихнуть, не <b>ЗАБЕАЛА</b> ли эта ситуация?\n\n"
        "<b>КОГДА ТЫ УЖЕ НАЧНЕШЬ ЕБАТЬ ЭТУ ЖИЗНЬ?</b>\n\n"
        "Готов ли ты?"
    )
    await call.message.answer(text, reply_markup=ready_to_change_keyboard())

    data = await state.get_data()
    if not data.get("ready_to_change_clicked"):
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
    await asyncio.sleep(300)

    media_group = [
        InputMediaPhoto(media=config.media.pagination_photos[0]),
        InputMediaPhoto(media=config.media.pagination_photos[1])
    ]

    await call.message.answer_media_group(media_group, reply_markup=want_too_keyboard())
    await asyncio.sleep(86400)

    session_pool = await create_session_pool(config.db)

    async with session_pool() as session:
        repo = RequestsRepo(session)
        user = await repo.users.select_user(call.message.chat.id)
    if not user.plan_id:
        photo = "AgACAgIAAxkBAALwWWd7s7x8kF_R3kR6nVG6tFFH9-iCAAJw7zEbBr3ZSw-xsFIugK0sAQADAgADeAADNgQ"
        text = (
            "Ну что, как сидится на мягком диване?\n\n"
            "Сколько женщин ты в этом месяце насадил? Ноль, одну и то жирную?\n\n"
            "<b>О ТАКОЙ СЧАСТЛИВОЙ ЖИЗНИ ТЫ МЕЧТАЕШЬ?</b>\n\n"
            "Или все таки ты хочешь уже понять какого это, когда к тебе домой едут девушки, которые тебе нравятся? / <b>жирный шрифт</b>\n\n"
            "Может ты хочешь понять какого это, когда тебя уважают в обществе? / / <b>жирный шрифт</b>\n\n"
            "Может ты наконец хочешь приходить в ресторан и не думать сколько ты потратил, путешествовать и соблазнить иностранок? / <b>жирный шрифт</b>\n\n"
            "У тебя есть риск, что это все останется только мечтами, все о чем ты грезил и представлял...\n\n"
            "Я даю тебе еще один шанс поменять свою жизнь, как бы высокомерно это не звучало. Даю ссылку на знания, которые 100% приведут тебя к твоей жизни мечты легко и быстро!\n\n"
            "С нами уже 1400 счастливчиков, которые уже на шаг впереди тебя, а ты что? Обратно на диван, братик? / <b>жирный шрифт</b>\n\n"
            "Решать тебе"
        )
        await call.message.answer_photo(photo, caption=text, reply_markup=together_keyboard())

        photo_1 = config.media.pagination_photos[2]

        await call.message.answer_photo(photo_1, reply_markup=pagination_keyboard(1))
        await asyncio.sleep(86400)

        user = await repo.users.select_user(call.message.chat.id)
        if not user.plan_id:
            photo = "AgACAgIAAxkBAALEoGdy0moCPAW26FOcBhDgms9Ha56YAAKp6TEbOoaJSx-kJg3As9GDAQADAgADeQADNgQ"
            text = (
                "⁉️ Не пора бы и тебе, уже сделать главную трансформацию в своей жизни?"
            )
            await call.message.answer_photo(photo, text, reply_markup=transformation_keyboard())

        await asyncio.sleep(21600)
        user = await repo.users.select_user(call.message.chat.id)
        if not user.plan_id:
            media_group = [
                InputMediaPhoto(media="AgACAgIAAxkBAALElWdy0mrJWR5Ka193eWKfnHx3dw8vAAKc6TEbOoaJS4VMu5npPoh8AQADAgADeQADNgQ"),
                InputMediaPhoto(media="AgACAgIAAxkBAALEk2dy0mp2roojzlk292HUudC8xrAiAAKe6TEbOoaJSwEMtc7BpeqCAQADAgADeQADNgQ"),
                InputMediaPhoto(media="AgACAgIAAxkBAALEnmdy0mopLLTnyePeeEHE6kyneRx9AAKn6TEbOoaJS_3sDQoZC0iCAQADAgADeQADNgQ")
            ]
            await call.message.answer_media_group(media_group)
            text = (
                "У тебя прямо сейчас есть всемирная база знаний на любую тему, а ты сидишь и сливаешь свою жизнь в унитаз, смотришь рилсы.\n\n"
                "<b>Ты не имеешь права пиздеть, что все вокруг виноваты и тебе не повезло быть богатым, пока ты заходишь в ебаный инстаграм, вместо чтения литературы и накачки себя знаниями.</b>\n\n"
                "<b>Выбирай тариф, читай посты и общайся с парнями, после выходи, если будешь готов.</b>\n\n"
                "1 месяц и ты многое для себя поймешь.\n\n"
                "Твой выбор?"
            )
            await call.message.answer(text, reply_markup=choose_tariff_keyboard())


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
