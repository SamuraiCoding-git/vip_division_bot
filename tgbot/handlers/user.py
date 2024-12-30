from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo

from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_session_pool
from tgbot.config import Config
from tgbot.filters.private import IsPrivateFilter
from tgbot.keyboards.callback_data import OfferConsentCallbackData, BackCallbackData, GuidesCallbackData, \
    PaginationCallbackData, ReadingCallbackData, TariffsCallbackData
from tgbot.keyboards.inline import offer_consent_keyboard, greeting_keyboard, menu_keyboard, vip_division_keyboard, \
    access_payment_keyboard, story_keyboard, subscription_keyboard, reviews_payment_keyboard, experts_keyboard, \
    assistant_keyboard, access_keyboard, my_subscription_keyboard, guide_keyboard, pagination_keyboard, guides_keyboard, \
    pay_keyboard
from tgbot.utils.message_utils import delete_messages, handle_deeplink, send_consent_request, handle_seduction_deeplink
from tgbot.utils.payment_utils import generate_payment_link

user_router = Router()

user_router.message.filter(IsPrivateFilter())
user_router.callback_query.filter(IsPrivateFilter())

@user_router.message(F.content_type.in_({"photo", "video", "animation", "document", "video_note"}))
async def send_media(message: Message, state: FSMContext):
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
    }

    file_id = content_type_to_attr.get(message.content_type)

    if file_id:
        sent_message = await message.reply(file_id)
        message_ids.append(sent_message.message_id)
        await state.update_data(message_ids=message_ids)


@user_router.callback_query(F.data == "read_article")
async def read_article(call: CallbackQuery, state: FSMContext):
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
    text_part_2 = ("Заебись? Конечно за*бись, представляю твое восхищенное лицо, особенно когда ты поймешь какой результат это дает!\n\n"
        "Это ты еще в привате не был, там ты сознание бы х*уй потерял, поэтому не заходи туда, если не готов.\n\n"
        "Пойми важное правило — ты должен показать ей небольшую дерзость в первом сообщении, "
        "в первых тем, что ты не поздороваешься, а значит ты её ставишь ниже себя на старте, "
        "следовательно у тебя наверняка есть еще варианты, и ей это понравится. Запомни — тебе не нужен её ответ, "
        "пиши дерзко, как последний х*й, чтобы дурачок как я когда-то не сделал!\n\n"
        "<b>Просто бери и делай как говорит Директор и получай результат!</b>"
    )
    await state.update_data(read_clicked=True)
    await call.message.answer(text)
    await call.message.answer(text_part_2, reply_markup=guides_keyboard())



@user_router.message(CommandStart(deep_link=True))
async def user_deeplink(message: Message, command: CommandObject):
    text = (
        "<b>Небольшая формальность</b> 👆\n\n"
        "Чтобы забрать файл, который изменит тебя, нажми на кнопку для "
        '<a href="https://docs.google.com/document/d/14V62s6TOVBT8uOB-4UVX6NcTJqsxmVdz5GZnzYQeRe0/edit?tab=t.0">'
        "согласия получения рекламных рассылок</a>.\n\n"
        "<b>P.S.</b> <i>Спама не будет, отправляю только нужное: тебя ждут дополнительные бонусы, фишки, "
        "видеоуроки и другие ценные материалы.</i>"
    )
    await message.answer(text, reply_markup=offer_consent_keyboard(deeplink=command.args), disable_web_page_preview=True)


@user_router.callback_query(F.data == "get_guide")
async def get_guide(call: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(guide_clicked=True)
    await handle_seduction_deeplink(call)



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
    photos = {
        "1": InputMediaPhoto(media="AgACAgIAAxkBAALEnmdy0mopLLTnyePeeEHE6kyneRx9AAKn6TEbOoaJS_3sDQoZC0iCAQADAgADeQADNgQ"),
        "2": InputMediaPhoto(media="AgACAgIAAxkBAALEn2dy0mopt4VsyRZwqGT1T1f06onlAAKo6TEbOoaJS14XDq9LF5aBAQADAgADeQADNgQ")
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

    await delete_messages(bot=message.bot, chat_id=message.chat.id, state=state)

    if user:
        caption = (
            "<b>Приветствую в клубе \"VIP DIVISION\"</b> — <i>закрытое сообщество мужчин, "
            "которым не все равно на себя и свою жизнь. Именно там происходит максимально "
            "эффективное развитие себя по всем фронтам.</i>\n\n"
            "<i>Место обретения уверенности, веры в себя и поддержки со стороны мужчин, которые уже ВНЕ КОНКУРЕНЦИИ.</i>\n\n"
            "<b>🔎 Подробная информация по клубу доступна по кнопке ниже, переходи и изучай, или сразу оплачивай доступ</b>\n\n"
            "Ты на верном пути. Действуй!"
        )
        photo = "AgACAgIAAxkBAALEnWdy0mpGliziww9ozZWVnD1AXjDZAAKm6TEbOoaJS6osN8zKvnYYAQADAgADeQADNgQ"
        sent_message = await message.answer_photo(photo, caption, reply_markup=greeting_keyboard())
        await state.update_data(message_ids=[sent_message.message_id])
    else:
        text = (
            "<i>Продолжая использовать бот, вы даете </i>"
            '<a href="https://docs.google.com/document/d/14V62s6TOVBT8uOB-4UVX6NcTJqsxmVdz5GZnzYQeRe0/edit?tab=t.0">'
            "согласие на получение рекламных рассылок</a> и "
            '<a href="https://docs.google.com/document/d/10i9OLsAMYRiNaLuCZwBTE8w9gHCetNgj-AZU_lweodE/edit?usp=drive_link">'
            "согласие оферту по оказанию консультационных услуг</a>.\n"
            '<i>Подробнее</i> <a href="https://docs.google.com/document/d/188a7jAnvl-iB9DKyiVtzJqzm6QfS6oZiezEjfuT9n0w/edit?usp=drive_link">'
            "тут</a>"
        )
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
            caption = (
                "<b>Приветствую в клубе \"VIP DIVISION\"</b> — <i>закрытое сообщество мужчин, которым не все равно на себя и свою жизнь."
                " Именно там происходит максимально эффективное развитие себя по всем фронтам.</i>\n\n"
                "<i>Место обретения уверенности, веры в себя и поддержки со стороны мужчин, которые уже ВНЕ КОНКУРЕНЦИИ.</i>\n\n"
                "<b>🔎 Подробная информация по клубу доступна по кнопке ниже, переходи и изучай, или сразу оплачивай доступ</b>\n\n"
                "Ты на верном пути. Действуй!"
            )
            photo = "AgACAgIAAxkBAANeZ25tpU_auagRV6XRAnUyvbCW1BcAAj3mMRsF63FL1GuyRcTcVmQBAAMCAAN5AAM2BA"
            sent_message = await call.message.answer_photo(photo, caption, reply_markup=greeting_keyboard())
            await state.update_data(message_ids=[sent_message.message_id])
        else:
            await handle_deeplink(call, callback_data.deeplink, state)
    else:
        await send_consent_request(call, state)


@user_router.callback_query(F.data == "about_club")
async def about_club(call: CallbackQuery, bot: Bot, state: FSMContext):
    await delete_messages(bot=call.bot, chat_id=call.message.chat.id, state=state)

    photo = "AgACAgIAAxkBAALEjmdy0mrTJ-bx2nlZDWMhqBbBV8jKAAKX6TEbOoaJSzj3KXBj1mmtAQADAgADeQADNgQ"
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
        InputMediaPhoto(media="AgACAgIAAxkBAAIs-WdVrJiz3J4cVEHjerodiRRYH6bXAAJq5DEbTXapSuHtzkxwLB-WAQADAgADeQADNgQ"),
        InputMediaVideo(media="BAACAgIAAxkBAAIs-mdVrJgeZZ3gDm-tkwUOcmkUjmtpAALlWAACTXapSn9ubO3gLOtANgQ"),
    ]
    sent_media = await bot.send_media_group(chat_id=chat_id, media=media_group)
    message_ids = [msg.message_id for msg in sent_media]

    caption = (
        "<b>ПРИВАТНЫЙ КАНАЛ СОСТОИТ ИЗ 2 ВЕЩЕЙ:</b> \n\n"
        "<b>1. ЗНАНИЯ</b>, это считай учебник для любого мужчины, который собирается получить от жизни ВСЕ!!! "
        "Бесплатный канал, это начальная школа. Приватка — это магистратура. \n\n"
        "Что в себя включает? \n\n"
        "<b>— СОБЛАЗНЕНИЕ ТЕОРИЯ/ ПРАКТИКА.</b>\n"
        "Психология и работа мозга женщины, как появляется влечение, свидания и что на них говорить, секс. "
        "Вопрос с девушками/ сексом навсегда будет закрыт. \n\n"
        "<b>— ОТНОШЕНИЯ</b>\n"
        "Здесь про выбор пригодной девушки для семьи, как вести себя так, чтобы страсть не пропадала, "
        "про распределение ролей, воспитание детей и просто о счастливой семейной жизни.\n\n"
        "<b>— МУЖЕСТВЕННОСТЬ. ДЕНЬГИ. УСПЕХ. ХАРИЗМА</b>\n"
        "Здесь ты прокачиваешь свою личность на весь свой потенциал, сначала уничтожаешь ограничивающие убеждения, "
        "закладываешь новые, разжигаешь любовь к себе и миру, и на этой энергии, становишься ЕБЫРЕМ ПРИВАТКИ. \n\n"
        "<b>— ПСИХОЛОГИЯ И НЛП</b>\n"
        "Познаешь все тайны психологии человека, не только женщины, но и мужчин, общественных масс, чтобы позиционировать "
        "себя должным образом и становишься мужчиной ВЫСОКОЙ ЦЕННОСТИ и вооружаешься всеми видами манипуляций, "
        "а также техниками НЛП. \n\n"
        "<b>— ТЕЛО. ЗДОРОВЬЕ. СПОРТ</b>\n"
        "Приводишь в порядок свое здоровье, тело, соц. сети — это истинное проявление заботы и любви о себе в первую очередь. "
        "Составишь программу тренировок или похудения. Так же получаешь знания о своей гормональной системе и избавляешься "
        "от всей вредной хуйни по типу алкоголя, сигарет. \n\n"
        "<b>— СТИЛЬ. УХОД ЗА СОБОЙ</b>\n"
        "Создаешь свой утонченный стиль, подбираешь духи, приводишь в порядок свою привлекательность и до конца жизни выглядишь "
        "пиздато, данная информация экономит огромные деньги, ведь грамотно подбираешь себе гардероб/духи/средства ухода.\n\n"
        "<b>— ПРЯМЫЕ ЭФИРЫ</b>\n"
        "Ко всему сказанному, делюсь своим жизненным опытом, как преодолевал препятствия и откуда брал веру в свои силы. "
        "Регулярно проводятся эфиры с разбором подписчиков, чтобы вытащить/развить человека конкретно в его ситуации. \n\n"
        "✅ Более 1000 постов в свободном доступе"
    )

    sent_caption = await bot.send_message(chat_id=chat_id, text=caption, reply_markup=vip_division_keyboard("menu"))
    message_ids.append(sent_caption.message_id)

    await state.update_data(message_ids=message_ids)


@user_router.callback_query(F.data == "how_chat_works")
async def how_chat_works(call: CallbackQuery, state: FSMContext):
    await delete_messages(bot=call.bot, chat_id=call.message.chat.id, state=state)

    message_ids = []

    text = (
        "<b>ЧАТ</b> \n\n"
        "Знания это заебись, но чат это место их применения и поддержки. \n\n"
        "Сгусток тестостероново-дружной атмосферы, где люди достигшие результатов помогут вам с вопросами, "
        "дадут дельные советы в любой сфере жизни. \n\n"
        "Здесь же ты отрабатываешь навыки общения все что предложено в постах, НА ГЛАЗАХ МЕНЯЕШЬ СВОЮ СТАРУЮ ПРОШИВКУ, "
        "получаешь поддержку, заводишь друзей/ братьев/ партнеров для бизнеса. \n\n"
        "Так же в чате ты можешь лично мне задать вопрос. \n\n"
        "В нем ты можешь делиться всем, что происходит в жизни или в чем ищешь развитие, да и просто зарядиться бешенной энергией "
        "и посмеяться, обсудить такие темы, как: книги, спорт, заработок, да все что угодно, никого еще стороной не обошли, "
        "и не бросили в беде. \n\n"
        "<b>Сообщество которое мотивирует друг друга своими результатами, это мужчины объединенных общей целью ВЫЕБАТЬ ЭТУ ЖИЗНЬ, "
        "тут рады всем кто стремится к развитию.</b>"
    )
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

    caption = (
        "<b>Я НЕКРАСИВЫЙ, У МЕНЯ НЕТ ДЕНЕГ, МНЕ НЕ ПОВЕЗЛО, КОМУ Я НУЖЕН? МОЯ ИСТОРИЯ</b> \n\n"
        "Как же сука часто Я в последнее время вижу все эти сообщения от многих из вас, "
        "и как же Я узнаю в этом себя лет так 13-14 назад.\n\n"
        "Парни, вот прям один в один была у меня такая же хуйня в голове."
    )

    photo = "AgACAgIAAxkBAALEj2dy0mpBgWOxySzS5SO6WSsrds-hAAKY6TEbOoaJS4HJDjOaq7oCAQADAgADeQADNgQ"

    # Send the photo with caption and a keyboard for navigation
    sent_photo = await bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=caption,
        reply_markup=story_keyboard("menu")
    )
    await state.update_data(message_ids=[sent_photo.message_id])

@user_router.message(F.text == "/payment")
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

    text = (
        "<b>ЭТО САМОЕ ЛУЧШЕЕ что есть в интернете и один только вопрос, сколько стоит?</b>\n\n"
        "<b>46 ₽ в день или 1390 в месяц</b>\n\n"
        "<b>НИ ОДНОГО ПЛОХОГО ОТЗЫВА, это можно считать выдумкой, но это ФАКТ, люди меняют свою жизнь на 180 градусов уже за неделю чтения.</b>\n\n"
        "<b>3 месяца — <s>4.190</s> 3790 рублей (10% скидка)</b>\n"
        "<b>6 месяца — <s>7.790</s> 6590 рублей (15% скидка)</b>\n"
        "<b>9 месяцев — <s>12.510</s> 9990 рублей (20% скидка)</b>\n\n"
        "<b>Выбирай удобный тариф и начинай работу.</b>"
    )
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
        InputMediaPhoto(media="AgACAgIAAxkBAALFAAFnctQiwkDfyOam9nRQiAMkqU2NoAACregxG93mmUvFJ7sd1rpbFQEAAwIAA3kAAzYE"),
        InputMediaPhoto(media="AgACAgIAAxkBAALFAWdy1CKA8eaokd8r3z345LgVtrWHAAKu6DEb3eaZS1uc7B_6ru-UAQADAgADeQADNgQ"),
    ]

    sent_media = await call.message.answer_media_group(media=media_group)

    message_ids = [msg.message_id for msg in sent_media]

    caption = (
        "Тысячи мужчин уже <b>ЖИВУТ ЖИЗНЬ</b>, к которой ты стремишься и не сказать, что они были богатыми или харизматичными.\n\n"
        "Большая часть из них была:\n"
        "— закомплексованные\n"
        "— неуверенные в себе\n"
        "— безэнергичные\n\n"
        "Главное кем в итоге они стали. Ознакомься с историями мужчин."
    )

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

    text = (
        "<b>Специально для тебя есть 2 эксперта:</b>\n\n"
        "Анар - знает все об уходе за кожей, здоровье, диетах, гормональной системы и всего что касается ЗОЖ!\n\n"
        "Родион - истинный мастер в мире стилистики и профессионал с харизмой!"
    )

    sent_message = await bot.send_message(chat_id, text, reply_markup=experts_keyboard("menu"))
    await state.update_data(message_ids=[sent_message.message_id])

@user_router.callback_query(F.data == "questions")
async def questions(call: CallbackQuery, state: FSMContext, bot: Bot):
    await delete_messages(bot=bot, chat_id=call.message.chat.id, state=state)

    text = (
        "<b>В голове много вопросов? Подойдет ли тебе мой клуб?</b> "
        "<b>Что нового найдешь для себя?</b>\n\n"
        "Специально для тебя собрал статью из часто задаваемых вопросов.\n\n"
        "Изучай 🤝"
    )
    photo = "AgACAgIAAxkBAALEjWdy0mrMCpokNVNmsSDM_LA4yUGcAAKU6TEbOoaJS2R_fx-NCCulAQADAgADeQADNgQ"
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

    session_pool = await create_session_pool(config.db)
    async with session_pool() as session:
        repo = RequestsRepo(session)  # Pass the session to the repository
        order = await repo.orders.get_latest_paid_order_by_user(chat_id)

    if order and order.get_days_remaining() > 0:
        # Active subscription exists
        days_remaining = order.get_days_remaining()
        text = (
            f"У тебя активная подписка! 🎉\n\n"
            f"Осталось дней: {days_remaining} дней.\n"
        )
    else:
        text = (
            "У тебя нет активных подписок ⌛\n\n"
            "Ознакомьтесь с тарифами, нажав на соответствующую кнопку"
        )

    # Send the message
    sent_message = await bot.send_message(chat_id=chat_id, text=text, reply_markup=my_subscription_keyboard("menu"))

    # Update state with the message ID for tracking
    await state.update_data(message_ids=[sent_message.message_id])


@user_router.callback_query(TariffsCallbackData.filter())
async def sub_tariffs(call: CallbackQuery, state: FSMContext, bot: Bot, callback_data: TariffsCallbackData, config: Config):
    session_pool = await create_session_pool(config.db)
    async with session_pool() as session:
        repo = RequestsRepo(session)
        plan = await repo.plans.select_plan(callback_data.id)
        order = await repo.orders.create_order(call.message.chat.id,
                                               callback_data.id,
                                               plan.original_price)

    if plan.discounted_price != plan.original_price:
        discount_percentage = int((1 - plan.discounted_price / plan.original_price) * 100)
        price_text = f"<b>Стоимость:</b> <s>{plan.original_price} ₽</s> {plan.discounted_price} ₽ (скидка {discount_percentage if discount_percentage < 10 else 10}%)\n"
    else:
        price_text = f"<b>Стоимость:</b> {plan.original_price} ₽\n"

    text = (
        f"<b>Тариф: {plan.name}</b>\n"
        f"{price_text}"
        f"<b>Срок действия: {plan.name[:-2]}</b> \n\n"
        "Ты получаешь доступ:\n\n"
        "— <u>CASTING DIRECTOR VIP</u>\n"
        "канал со всеми материалами по темам: соблазнение, финансы, стиль, спорт, здоровье, отношения, мужественность, секс\n"
        "— <u>VIP DIVISION</u>\n"
        "чат с единомышленниками 24/7\n"
    )

    product = [
        {
            "quantity": 1,
            "name": plan.name[:-2],
            "price": int(plan.original_price),
            "sku": plan.id
        }
    ]

    linktoform = "https://vipdivision.payform.ru/"

    link = generate_payment_link(str(call.message.chat.id), order.id, product, config.payment.token, linktoform)

    await call.message.answer(text, reply_markup=pay_keyboard(link, "tariffs"))

@user_router.callback_query(F.data == "guide")
async def guide(call: CallbackQuery, state: FSMContext, bot: Bot):
    await delete_messages(bot=bot, chat_id=call.message.chat.id, state=state)

    caption = (
        "<b>Благодаря гайдам ты сможешь:</b>\n\n"
        "1 — Трахать тех девушек, которые были для тебя ранее недоступны ( НИТАКУСИ )\n\n"
        "2 — Найдешь ТУ САМУЮ девушку для отношений\n\n"
        "3 — Будешь выстраивать отношения где ТЫ будешь главными, ТЕБЯ будет любить и уважать девушка.\n\n"
        "4 — Научишься любить и уважать СЕБЯ без исключений\n\n"
        "5 — Избавишься от страхов и ограничивающих убеждений\n\n"
        "<b>Также ты найдешь примеры фраз, как заставить девушку тебя добиваться, конкретные модели поведения, чтобы не потерять авторитет.</b>\n\n"
        "Если хочешь узнать, как уже закрыть вопрос с девушками, чтобы они сами просили их выебать, а ты уже думал надо тебе или нет, то будь на связи и читай ГАЙДЫ."
    )

    animation = "BAACAgIAAxkBAAID5GdUP1HOorIbqY-v_jImDf0OZP-nAAJ7YAACDq9BSe1TKBaZWCL-NgQ"

    sent_message = await call.message.answer_animation(animation, caption=caption, reply_markup=guide_keyboard("menu"))
    await state.update_data(message_ids=[sent_message.message_id])


@user_router.callback_query(GuidesCallbackData.filter())
async def guides(call: CallbackQuery, state: FSMContext, bot: Bot, callback_data: GuidesCallbackData):
    guides = {
        "texting": "BQACAgIAAxkBAALFHGdy1deNck8Csc3p6RZaflKPy8clAAIhZwACho5wS17kLtlN_gO0NgQ",  # Гайд по перепискам
        "seduction": "BQACAgIAAxkBAALFHWdy1ddGT-0fTMob9D3yWwJfIfRFAAKiVwACCqjBSUlYSd1AZvJdNgQ",  # Гайд по соблазнению
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


@user_router.callback_query(BackCallbackData.filter())
async def filter_callback_query(call: CallbackQuery, callback_data: BackCallbackData, bot: Bot, state: FSMContext, config: Config):
    await delete_messages(bot=call.bot, chat_id=call.message.chat.id, state=state)

    if callback_data.state == "menu":
        photo = "AgACAgIAAxkBAALEjmdy0mrTJ-bx2nlZDWMhqBbBV8jKAAKX6TEbOoaJSzj3KXBj1mmtAQADAgADeQADNgQ"
        new_message = await call.message.answer_photo(photo, reply_markup=menu_keyboard())
        await bot.pin_chat_message(call.message.chat.id, new_message.message_id)
        await state.update_data(message_ids=[new_message.message_id])
    elif callback_data.state == "how_chat_works":
        media_group = [
            InputMediaPhoto(media="AgACAgIAAxkBAAIs-WdVrJiz3J4cVEHjerodiRRYH6bXAAJq5DEbTXapSuHtzkxwLB-WAQADAgADeQADNgQ"),
            InputMediaVideo(media="BAACAgIAAxkBAAIs-mdVrJgeZZ3gDm-tkwUOcmkUjmtpAALlWAACTXapSn9ubO3gLOtANgQ"),
        ]
        sent_media = await call.message.answer_media_group(media_group)
        message_ids = [msg.message_id for msg in sent_media]

        caption = (
            "<b>ПРИВАТНЫЙ КАНАЛ СОСТОИТ ИЗ 2 ВЕЩЕЙ:</b> \n\n"
            "<b>1. ЗНАНИЯ</b>, это считай учебник для любого мужчины, который собирается получить от жизни ВСЕ!!! "
            "Бесплатный канал, это начальная школа. Приватка — это магистратура. \n\n"
            "Что в себя включает? \n\n"
            "<b>— СОБЛАЗНЕНИЕ ТЕОРИЯ/ ПРАКТИКА.</b>\n"
            "Психология и работа мозга женщины, как появляется влечение, свидания и что на них говорить, секс. "
            "Вопрос с девушками/ сексом навсегда будет закрыт. \n\n"
            "<b>— ОТНОШЕНИЯ</b>\n"
            "Здесь про выбор пригодной девушки для семьи, как вести себя так, чтобы страсть не пропадала, "
            "про распределение ролей, воспитание детей и просто о счастливой семейной жизни.\n\n"
            "<b>— МУЖЕСТВЕННОСТЬ. ДЕНЬГИ. УСПЕХ. ХАРИЗМА</b>\n"
            "Здесь ты прокачиваешь свою личность на весь свой потенциал, сначала уничтожаешь ограничивающие убеждения, "
            "закладываешь новые, разжигаешь любовь к себе и миру, и на этой энергии, становишься ЕБЫРЕМ ПРИВАТКИ. \n\n"
            "<b>— ПСИХОЛОГИЯ И НЛП</b>\n"
            "Познаешь все тайны психологии человека, не только женщины, но и мужчин, общественных масс, чтобы позиционировать "
            "себя должным образом и становишься мужчиной ВЫСОКОЙ ЦЕННОСТИ и вооружаешься всеми видами манипуляций, "
            "а также техниками НЛП. \n\n"
            "<b>— ТЕЛО. ЗДОРОВЬЕ. СПОРТ</b>\n"
            "Приводишь в порядок свое здоровье, тело, соц. сети — это истинное проявление заботы и любви о себе в первую очередь. "
            "Составишь программу тренировок или похудения. Так же получаешь знания о своей гормональной системе и избавляешься "
            "от всей вредной хуйни по типу алкоголя, сигарет. \n\n"
            "<b>— СТИЛЬ. УХОД ЗА СОБОЙ</b>\n"
            "Создаешь свой утонченный стиль, подбираешь духи, приводишь в порядок свою привлекательность и до конца жизни выглядишь "
            "пиздато, данная информация экономит огромные деньги, ведь грамотно подбираешь себе гардероб/духи/средства ухода.\n\n"
            "<b>— ПРЯМЫЕ ЭФИРЫ</b>\n"
            "Ко всему сказанному, делюсь своим жизненным опытом, как преодолевал препятствия и откуда брал веру в свои силы. "
            "Регулярно проводятся эфиры с разбором подписчиков, чтобы вытащить/развить человека конкретно в его ситуации. \n\n"
            "✅ Более 1000 постов в свободном доступе"
        )

        sent_caption = await call.message.answer(caption, reply_markup=vip_division_keyboard("menu"))
        message_ids.append(sent_caption.message_id)
        await state.update_data(message_ids=message_ids)
    elif callback_data.state == "tariffs":
        session_pool = await create_session_pool(config.db)

        async with session_pool() as session:
            repo = RequestsRepo(session)
            plans = await repo.plans.get_all_plans()

        text = (
            "<b>ЭТО САМОЕ ЛУЧШЕЕ что есть в интернете и один только вопрос, сколько стоит?</b>\n\n"
            "<b>46 ₽ в день или 1390 в месяц</b>\n\n"
            "<b>НИ ОДНОГО ПЛОХОГО ОТЗЫВА, это можно считать выдумкой, но это ФАКТ, люди меняют свою жизнь на 180 градусов уже за неделю чтения.</b>\n\n"
            "<b>3 месяца — <s>4.190</s> 3790 рублей (10% скидка)</b>\n"
            "<b>9 месяцев — <s>12.510</s> 9990 рублей (20% скидка)</b>\n\n"
            "<b>Выбирай удобный тариф и начинай работу.</b>"
        )
        sent_message = await bot.send_message(chat_id=call.message.chat.id, text=text,
                                              reply_markup=subscription_keyboard("menu", plans))
        await state.update_data(message_ids=[sent_message.message_id])
