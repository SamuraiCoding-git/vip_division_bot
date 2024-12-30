import asyncio

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto

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


async def handle_texting_deeplink(call: CallbackQuery, state: FSMContext):
    photo_1 = "AgACAgIAAxkBAALEmGdy0mpEkPwMF_CwHEJdLh0GG6zLAAKh6TEbOoaJS8XT479tCd6FAQADAgADeAADNgQ"
    caption_1 = (
        "Привет, на связи Евгений,\n"
        "Кастинг Директор<a href='https://t.me/+e393pjYbFfpkYzUy'>🚨</a>\n\n"
        "Этот бот выдаст тебе ГАЙД, где я рассказал, как быть вне конкуренции на СЗ (сайты знакомств):\n\n"
        "1) Первая часть гайда про оформление анкеты, какие должны быть фотографии и описание, чтобы цеплять девушек\n\n"
        "2) Вторая часть гайда про фишки переписки: о чем разговаривать, чтобы не было скучно, какие темы создают влечение и как создавать грамотный флирт.\n\n"
        "И еще больше полезной информации тебя уже ждет в гайде, который бот отправит в ближайшее время."
    )
    await call.message.answer_photo(photo_1, caption_1)
    await asyncio.sleep(60)

    texting_guide_file_id = "BQACAgIAAxkBAALFHGdy1deNck8Csc3p6RZaflKPy8clAAIhZwACho5wS17kLtlN_gO0NgQ"
    file_caption = "Улучшить навыки общения в мессенджерах за 9 минут"
    await call.message.answer_document(texting_guide_file_id)
    await call.message.answer(file_caption)
    await asyncio.sleep(1800)

    caption = (
        "<b>Благодаря гайду ты сможешь:</b>\n\n"
        "1. Создать анкету, которая будет собирать много лайков\n\n"
        "2. Перестанешь вести скучные разговоры и проводить девушкам допросы\n\n"
        "3. Поймешь, как создавать интерес к тебе с помощью переписки\n\n"
        "4. Сможешь легко выстраивать диалог и приглашать девушек на свидания или к себе домой\n\n"
        "5. Перестанешь страдать от общения, и начнешь получать удовольствие\n\n"
        "<b>Если хочешь узнать, как легко выводить девушек на свидания, раскачивать их по эмоциям в переписке и после сразу пригласить домой, то читай ГАЙД</b>"
    )
    animation = "CgACAgIAAxkBAALEpmdy0mqjnV514046tn6z4TXT_oPYAAKrWAACOoaJS4LAN_TnVprUNgQ"
    await call.message.answer_animation(animation, caption=caption)
    await asyncio.sleep(3600)

    text = (
        "Ты должен знать эту базу, если хочешь быть востребованным не только на сайте знакомств, но и в переписках с любой девушкой:\n\n"
        "— понижение ее значимости\n"
        "— почему надо иметь требования к женщине\n"
        "— как не переборщить с фишками\n\n"
        "На канале я все рассказал, переходи: "
        "<a href='https://t.me/c/1699879031/1061'>База для общения</a>"
    )
    await call.message.answer(text, reply_markup=communication_base_keyboard())
    await asyncio.sleep(43200)

    caption_2 = (
        "Какой с*ка ЖАЛКИЙ диалог.\n\n"
        "Мужчина – миллионер, стелится как ебаный влюбленный слабохарактерный раб. Вот этот позор ждет каждого, кто невнимательно читает мой канал.\n\n"
        "Разберем его ошибки:\n\n"
        "1. Предлагает перевести деньги.\n"
        "Он понимает, что кроме денег ему предложить нечего, он обычно всех покупает. Но если ты ничего из себя не представляешь, то твои деньги тебя не спасут, все равно всем будет на тебя пох*й.\n\n"
        "2. Я уже со счета сбился сколько он сообщений ей написал, а в ответ них*я, и он видя это продолжает х*ярить...\n\n"
        "3. Сделал предложение позавтракать, она проигнорила, предложил пообедать – игнор, он дальше х*ярит предложение поужинать.\n\n"
        "Что о таком мужчине можно сказать? Одинокий нах*й и никому не нужный, навязчивый, с низкой ценностью.\n\n"
        "4. Берет и звонит, тем еще больше опускает свою ценность на дно, а дальше еще и оправдывается зачем звонил.\n\n"
        "Конечно же после такого девушка его слила.\n\n"
        "Если бы он только подписался на мой канал... я не говорю уже о приватке."
    )
    photo_2 = "AgACAgIAAxkBAALEl2dy0mrdqr7qdgQ3Bh6_Mz4uhGqQAAKi6TEbOoaJS37mc-VD8qapAQADAgADeQADNgQ"
    await call.message.answer_photo(photo_2, caption_2)
    await asyncio.sleep(1800)

    media_group = [
        InputMediaPhoto(media="AgACAgIAAxkBAALEmmdy0mraYsGaEPe_rF0re5IIUgRkAAKj6TEbOoaJS39kCBNbPnjxAQADAgADeQADNgQ"),
        InputMediaPhoto(media="AgACAgIAAxkBAALEnGdy0mpNjIHeKkRfLWkMHY9zwTzrAAKk6TEbOoaJS1p7XOKw9mQ7AQADAgADeQADNgQ"),
        InputMediaPhoto(media="AgACAgIAAxkBAALEm2dy0mqiN1694y5tYn-leUqo9pNnAAKl6TEbOoaJSw0nZU08y18jAQADAgADeQADNgQ")
    ]
    media_group_caption = (
        "А здесь чувствуете разницу, когда не вам надо, а ей надо?\n\n"
        "Нужно уметь управлять вниманием любого человека, особенно женщин. Знать психологию воздействия."
        " Надо понимать, когда брать паузу, выдерживать дистанцию, чтобы после в тебе нуждались еще сильнее.\n\n"
        "Так работает дофаминовая система, и работает это со всеми.\n\n"
        "Тогда вы будете получать все, что хотите, и не будете соглашаться на меньшее.\n\n"
        "Запомните — УПРАВЛЯЕТЕ ВЫ, А НЕ ВАМИ\n\n"
        "🔴 Забирай еще 1 бесплатный гайд:\n"
        "Как влюбить в себя женщин. Техники.\n\n"
        "Это элементарная база, которую я собирал годами. От меня лично ты можешь узнать:\n\n"
        "— Основные принципы как не оказаться во френдзоне\n"
        "— Женские манипуляции\n"
        "— Как найти ту самую\n"
        "— Почему важно разжигать огонь в отношениях, и как это делать\n"
        "— Психологию женщин и как работает их мозг\n"
        "— Так же, как формируется женское влечение.\n\n"
        "В конце раскрою два качества: одно отталкивает девушек (проблема 90% парней) и второе притягивает, как куколда к непригодке.\n\n"
        "Других вариантов у тебя нет! Читай:"
    )
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
        text = (
            "<b>НАПИШИ ЕЙ ЭТО И ПОЛУЧИ ЕЕ ИНТЕРЕС</b>\n\n"
            "Каждый из вас сидит на сайтах знакомств и большая часть безрезультатно, потому что пишет скучную банальную или "
            "чересчур креативную по*бень, которая не цепляет ее интерес.\n\n"
            "Как пишут все?\n"
            "— Привет, как дела?\n"
            "— Привет, что здесь ищешь?\n"
            "— Привет, что делаешь?\n"
            "— Привет, давай познакомимся?\n\n"
            "<i>Нах*й твой привет, джентльмен бл*ть?</i>\n\n"
            "Здороваются в первом сообщении куколды и девственники, а подписчики Директора пишут сразу по сути:\n\n"
            "— Ну как тут охота на хороших мальчиков?\n"
            "— Ну че ты тут, рассказывай, сколько уже дурачков отшила за сегодня?\n"
            "— Решил в кое-то веки написать первый, надеюсь ты не извращенка\n"
            "— Ну и когда тебя дома ждать? Опять на сайтах знакомств сидит, дети скучают по матери!\n\n"
        )
        text_part_2 = (
            "Заебись? Конечно за*бись, представляю твое восхищенное лицо, особенно когда ты поймешь какой результат это дает!\n\n"
            "Это ты еще в привате не был, там ты сознание бы х*уй потерял, поэтому не заходи туда, если не готов.\n\n"
            "Пойми важное правило — ты должен показать ей небольшую дерзость в первом сообщении, "
            "в первых тем, что ты не поздороваешься, а значит ты её ставишь ниже себя на старте, "
            "следовательно у тебя наверняка есть еще варианты, и ей это понравится. Запомни — тебе не нужен её ответ, "
            "пиши дерзко, как последний х*й, чтобы дурачок как я когда-то не сделал!\n\n"
            "<b>Просто бери и делай как говорит Директор и получай результат!</b>"
            )
        await call.message.answer(text)
        await call.message.answer(text_part_2, reply_markup=guides_keyboard())

    data = await state.get_data()
    if not data.get("successful_texting_clicked"):
        caption = "Разбор переписки от ученика, объясняю какие фишки использовал"
        photo = "AgACAgIAAxkBAALElmdy0mpPLYect2H8vAnptPnXVxXUAAKf6TEbOoaJS2OiYXkXxsTdAQADAgADeQADNgQ"
        await call.message.answer_photo(photo, caption=caption, reply_markup=read_keyboard("Читать", "https://t.me/c/1699879031/1651", "reading_1651_2_clicked"))
    await asyncio.sleep(86400)

    data = await state.get_data()
    if not data.get("reading_1651_2_clicked"):
        text = (
            "привет, как дела?\n\n"
            "Более скучного и вялого начала диалога я не знаю, если только, расскажи о себе.\n\n"
            "<b>Большинство из вас:</b>\n"
            "1. Не знают, что писать\n"
            "2. Не могут вести себя легко в переписках\n"
            "3. Возвышают девушку\n"
            "4. Боятся игнора и отказов\n"
            "5. Пишут скучно и нудно\n\n"
            "Только практика и наличие рядом примера, как правильно писать, могут сделать из тебя "
            "харизматичного и интересного собеседника.\n\n"
            "Нам всем хватает официальности и стеснения на работе/учебе, а юмор, абсурд и подьёбы – "
            "это то, что расслабляет и объединяет людей.\n\n"
            "Девушки хотят легкости и игры, хотят окунуться в детство, и да, они тоже какают, "
            "прими это как факт, и не стесняйся обострять, не стесняйся быть несерьезным.\n\n"
            "Умение общаться в переписке – это <b>БАЗА 21 века.</b>\n\n"
            "Встретил на улице девчонку или в компании, на работе, в любом другом месте, итог один. "
            "Вы расходитесь и единственное, что вам остается – держать связь онлайн.\n\n"
            "Как ни крути, тебе 99% не хватит смелости и навыка произвести впечатление сразу, "
            "поэтому переписка – это твоё оружие, где ты или потерпишь неудачу или подсадишь её "
            "на общение с тобой.\n\n"
            "<b>Ниже лови кейс парня из приватки:</b>"
        )
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

async def handle_seduction_deeplink(call: CallbackQuery):
    video_note = "DQACAgIAAxkBAALFMmdy1yiqV26OxKRS689nWuZykp5NAAJYXAAC4HlJScA_p-RezxqdNgQ"
    video_file = "BAACAgIAAxkBAALFNGdy10tETN0LaTdEOJvzoJoWFNNeAAKaZgAC3eaZS_HiXTOiSdAjNgQ"
    try:
        await call.message.answer_video_note(video_note)
    except Exception as e:
        await call.message.answer_video(video_file)
    await asyncio.sleep(60)

    text = (
        "То, что ты сейчас прочитаешь — полностью поменяет твое мышление, наслаждайся 🤝\n\n"
        "<b>Время чтения:</b> 11 минут"
    )
    file = "BQACAgIAAxkBAALFHWdy1ddGT-0fTMob9D3yWwJfIfRFAAKiVwACCqjBSUlYSd1AZvJdNgQ"
    await call.message.answer_document(file)
    await call.message.answer(text)
    await asyncio.sleep(300)

    photo_1 = "AgACAgIAAxkBAALEnmdy0mopLLTnyePeeEHE6kyneRx9AAKn6TEbOoaJS_3sDQoZC0iCAQADAgADeQADNgQ"

    # "AgACAgIAAxkBAAICGmdxSVyiWahM-a-rS3NAk0rYqVpDAALQ5TEbJ2-RSwwAAZtOAeeXDQEAAwIAA3kAAzYE"
    await call.message.answer_photo(photo_1, reply_markup=pagination_keyboard(1))
    await asyncio.sleep(1500)

    text = (
        "<b>Благодаря гайду ты сможешь:</b>\n\n"
        "1. Создать анкету, которая будет собирать много лайков\n\n"
        "2. Перестанешь вести скучные разговоры и проводить девушкам допросы\n\n"
        "3. Поймешь, как создавать интерес к тебе с помощью переписки\n\n"
        "4. Сможешь легко выстраивать диалог и приглашать девушек на свидания или к себе домой\n\n"
        "5. Перестанешь страдать от общения, и начнешь получать удовольствие\n\n"
        "<b>Если хочешь узнать, как легко выводить девушек на свидания, раскачивать их по эмоциям в переписке и после сразу пригласить домой, то читай ГАЙД</b>"
    )
    animation = "BAACAgIAAxkBAAID5GdUP1HOorIbqY-v_jImDf0OZP-nAAJ7YAACDq9BSe1TKBaZWCL-NgQ"
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
