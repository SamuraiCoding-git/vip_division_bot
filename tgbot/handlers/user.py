import asyncio

import time

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message

from infrastructure.api.app import config
from tgbot.config import Config
from tgbot.filters.private import IsPrivateFilter
from tgbot.keyboards.callback_data import ReadingCallbackData
from tgbot.keyboards.inline import guide_keyboard, guides_keyboard, \
    community_keyboard, generate_payment_keyboard
from tgbot.utils.db_utils import get_repo
from tgbot.utils.message_utils import delete_messages, handle_seduction_deeplink

user_router = Router()

user_router.message.filter(IsPrivateFilter())
user_router.callback_query.filter(IsPrivateFilter())


# @user_router.message()
# async def message_mailing(message: Message, config: Config, bot: Bot):
#     if message.from_user.id != 422999166:
#         return
#
#     users = list(
#         {6496782, 8048021, 30638565, 34020866, 59032490, 74025481, 85664088, 159838509, 166057510, 181380512, 212735411,
#          224795506, 226319498, 238783404, 243656913, 244357708, 253407407, 267978087, 270032975, 277621870, 285969221,
#          292763292, 299659518})
#
#     text = (
#         "Удален из канала.\n\n"
#         "<b>Не советую тебе жить взаймы и искать выгоду, ничего не отдавая взамен.</b>\n\n"
#         "Кнопка - Вернуться в канал ↩️"
#     )
#
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [
#             InlineKeyboardButton(text="Вернуться в канал ↩️", callback_data="tariffs")
#         ]
#     ])
#
#     await message.answer("Рассылка началась.")
#
#     for user in users:
#         if user in [821892126, 886105115, 5755603332]:
#             continue
#
#         try:
#             await bot.send_message(chat_id=user, text=text, reply_markup=keyboard)
#         except Exception as e:
#             print(f"Ошибка при отправке пользователю {user}: {e}")
#         time.sleep(0.03)
#
#     await message.answer("Рассылка завершена")

@user_router.callback_query(F.data == "ded_gs")
async def ded_gs(call: CallbackQuery, config: Config):
    voice = 'AwACAgIAAx0CY_XjjwACCYpnhng17q2-MTUCFZeba9Vl0QHnowACG2oAAt_sOEiCPufGmhSDTzYE'

    caption = (
        "<b>#неделясдедом 1/7</b>\n"
        "Вводный подкаст от @spacerom\n\n"
        "— Поздравление от деда с наступлением Нового года\n\n"
        "— Плохие по приватке те, кто неудобен, не соглашается с малым, выбирает себя и не боится конфликта.\n\n"
        "— Обращение к новичкам\n\n"
        "— Что будет на этой неделе?\n\n"
        "Внуки, активность необходима.\n"
        "1) Реакции\n"
        "2) Комментарии\n"
        "3) Задавайте вопросы и пишите запросы"
    )

    await call.message.answer_voice(voice=voice, caption=caption, reply_markup=generate_payment_keyboard("Купить доступ на месяц ✅"))

    await asyncio.sleep(300)

    repo = await get_repo(config)

    user = await repo.users.select_user(call.message.chat.id)

    if user.plan_id:
        photo = "AgACAgIAAxkBAAEBJF9nh38xldRlYK7FPIEvKz8WfLKexgAC7uMxG8VuQUhFxnU-PrVg3gEAAwIAA20AAzYE"

        text = (
            "Учиться у лучшего, чтобы быть лучше!\n\n"
            "Открыл продажи приватки, чтобы вы успели на неделю с Дедом.\n\n"
            "Забирай место и не упускай такую возможность за 1390 👇🏽"
        )

        await call.message.answer_photo(photo=photo, caption=text, reply_markup=generate_payment_keyboard("Купить доступ на месяц ✅"))





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
