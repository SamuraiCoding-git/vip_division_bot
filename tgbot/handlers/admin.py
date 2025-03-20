import re
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.exc import IntegrityError
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent


from main import config
from tgbot.config import Config, load_config
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.callback_data import AdminsListCallbackData, DeleteAdminCallbackData, \
    SettingsCallbackData, BlacklistCallbackData, AddDaysCallbackData
from tgbot.keyboards.inline import admin_keyboard, admins_list_keyboard, admin_delete_keyboard, settings_keyboard, \
    user_status_keyboard
from tgbot.misc.admin_states import AdminStates
from tgbot.utils.admin_utils import get_readable_subscription_end_date
from tgbot.utils.db_utils import get_repo
from tgbot.utils.message_utils import delete_messages

admin_router = Router()
admin_router.message.filter(AdminFilter())
admin_router.callback_query.filter(AdminFilter())

from aiogram.types import Message

@admin_router.message(Command("admin"))
async def admin_start(message: Message, state: FSMContext, bot: Bot, config: Config):
    repo = await get_repo(config)
    users = await repo.users.count_users()
    subscriptions = await repo.subscriptions.count_unique_subscription_users()
    exp_subs = await repo.subscriptions.get_expired_users()
    text = (
        f"Всего пользователей: {users}\n",
        f"Купившие подписку: {subscriptions}\n",
        f"Некупившие подписку: {users - subscriptions}\n",
        f"Непродлившие подписку: {len(exp_subs)}"
    )
    sent_message = await message.answer("\n".join(text), reply_markup=admin_keyboard())
    await delete_messages(bot, message.from_user.id, state, [sent_message.message_id])

@admin_router.message(F.text.startswith("User Details:"))
async def handle_message(message: Message):
    await message.delete()
    if message.text.startswith("User Details:"):
        try:
            lines = message.text.split("\n")
            user_id_line = next((line for line in lines if line.startswith("ID:")), None)

            if not user_id_line:
                await message.answer("User ID not found in the message.")
                return

            user_id = int(user_id_line.split(":")[1].strip())

            config = load_config(".env")
            repo = await get_repo(config)

            user = await repo.users.select_user(user_id)
            if user:
                is_blocked = await repo.blacklist.is_blocked(user.id)
                payments_number = await repo.payments.count_payments(user.id)
                days = await repo.subscriptions.get_combined_active_subscription_days(user.id)
                subscription_end_date = get_readable_subscription_end_date(days)
                is_admin = await repo.admins.is_admin(user_id)
                data = {
                    "id": user.id,
                    "is_blocked": is_blocked
                }
                await message.answer("Пользователь:\n"
                                     f"Имя: {user.full_name}\n"
                                     f"ID: {user.id}\n"
                                     f"Username: {user.username}\n"
                                     f"Админ: {'да' if is_admin else 'нет'}\n"
                                     f"Количество платежей: {payments_number}\n"
                                     f"Дата окончания подписки: {subscription_end_date} ({days})",
                                     reply_markup=user_status_keyboard(data))
            else:
                await message.answer("User not found.")
        except ValueError:
            await message.answer("Invalid User ID format.")
        except Exception as e:
            await message.answer("Failed to process the message. Please try again.")
            print(f"Error handling message: {e}")


@admin_router.callback_query(AddDaysCallbackData.filter())
async def add_days(call: CallbackQuery, state: FSMContext, callback_data: AddDaysCallbackData):
    await state.set_state(AdminStates.add_days)
    await state.update_data(add_days_user_id=callback_data.id)
    sent_message = await call.message.answer("Отправь количество дней продления или дату:\n\n"
                                             "<b>Формат:</b>\n"
                                             "<i>+10 (Чтобы продлить на 10 дней)\n\n"
                                             "2025-06-19 (Чтобы продлить подписку до 19 июня 2025 года)</i>")
    await delete_messages(call.bot, call.message.chat.id, state, [sent_message.message_id])

@admin_router.message(AdminStates.add_days)
async def add_days_state(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    repo = await get_repo(config)

    user_id = int(data.get("add_days_user_id"))
    input_data = message.text.strip()

    try:
        if input_data.startswith("+") and input_data[1:].isdigit():
            days = int(input_data[1:])
            if days <= 0:
                raise ValueError("Количество дней должно быть больше 0.")
            await repo.subscriptions.extend_subscription(user_id, f"+{days}")
            await message.answer(f"Добавлено {days} дней пользователю с ID {user_id}.")

        elif re.match(r"^\d{4}-\d{2}-\d{2}$", input_data):
            date = datetime.strptime(input_data, "%Y-%m-%d")
            if date <= datetime.now():
                raise ValueError("Дата должна быть в будущем.")
            await repo.subscriptions.extend_subscription(user_id, date.strftime("%Y-%m-%d"))
            await message.answer(
                f"Установлена новая дата окончания подписки: {date.date()} для пользователя с ID {user_id}.")

        else:
            raise ValueError("Неверный формат. Введите '+N' для добавления дней или 'YYYY-MM-DD' для установки даты.")

    except ValueError as e:
        await message.answer(f"Ошибка: {e}")

    sent_message = await message.answer("Панель админа:", reply_markup=admin_keyboard())
    await delete_messages(message.bot, message.from_user.id, state, [sent_message.message_id])

@admin_router.callback_query(BlacklistCallbackData.filter())
async def blacklist_data(call: CallbackQuery, callback_data: BlacklistCallbackData, config: Config):
    repo = await get_repo(config)
    if callback_data.is_blocked:
        await repo.blacklist.remove_from_blacklist(callback_data.id)
    else:
        await repo.blacklist.add_to_blacklist(callback_data.id)
    data = {
        "id": callback_data.id,
        "is_blocked": not callback_data.is_blocked
    }
    await call.message.edit_reply_markup(reply_markup=user_status_keyboard(data))

@admin_router.callback_query(F.data == "add_admin")
async def add_admin_button(call: CallbackQuery, state: FSMContext, bot: Bot):
    sent_message = await call.message.answer("Отправьте ID админа: ")

    await state.set_state(AdminStates.admin_id)

    await delete_messages(bot, call.message.chat.id, state, [sent_message.message_id])

@admin_router.callback_query(F.data == "mailing")
async def mailing(call: CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.answer("Отправьте сообщение для рассылки:")
    await state.set_state(AdminStates.mailing_message)


@admin_router.message(
    (F.state == AdminStates.mailing_message) &
    F.content_type.in_([
        ContentType.PHOTO, ContentType.VIDEO, ContentType.DOCUMENT,
        ContentType.AUDIO, ContentType.VOICE, ContentType.STICKER, ContentType.TEXT
    ])
)

async def mailing_message(message: Message, state: FSMContext):
    data_to_save = {
        "file_id": None,
        "caption": message.caption if message.caption else None,
        "text": message.text if message.text else None,
    }

    if message.content_type == ContentType.PHOTO:
        data_to_save["file_id"] = message.photo[-1].file_id
    elif message.content_type == ContentType.VIDEO:
        data_to_save["file_id"] = message.video.file_id
    elif message.content_type == ContentType.DOCUMENT:
        data_to_save["file_id"] = message.document.file_id
    elif message.content_type == ContentType.AUDIO:
        data_to_save["file_id"] = message.audio.file_id
    elif message.content_type == ContentType.VOICE:
        data_to_save["file_id"] = message.voice.file_id
    elif message.content_type == ContentType.STICKER:
        data_to_save["file_id"] = message.sticker.file_id
    elif message.content_type == ContentType.TEXT:
        pass
    else:
        await message.reply("Тип контента не поддерживается.")
        return

    await state.update_data(mailing_data=data_to_save)

    await message.reply("Сообщение сохранено.\n"
                        "Настрой клавиатуру:")


@admin_router.message(AdminStates.admin_id)
async def admin_id_state(message: Message, config: Config, bot: Bot, state: FSMContext):
    message_ids = []

    repo = await get_repo(config)

    try:
        admin = await repo.admins.get_or_create_admin(int(message.text))

        if admin.id:
            message_ids.append(await message.answer("Админ успешно добавлен"))
            message_ids.append(await message.answer("Панель админа:", reply_markup=admin_keyboard()))
            await delete_messages(bot, message.from_user.id, state, [i.message_id for i in message_ids])
            await state.clear()
        else:
            message_ids.append(await message.answer("Произошла ошибка, отправьте ID ещё раз"))
    except IntegrityError:
        message_ids.append(await message.answer("Админа с таким ID ещё нет в базе\n"
                                                "Он должен нажать /start в боте\n"
                                                "После этого пришлите ID ещё раз"))
    except Exception as e:
        message_ids.append(await message.answer(f"Произошла ошибка: {e}"))


@admin_router.callback_query(F.data == "admin_list")
async def admin_list_state(call: CallbackQuery, state: FSMContext, bot: Bot, config: Config):
    repo = await get_repo(config)

    admins = await repo.admins.get_all_admins()

    sent_message = await call.message.answer("Список админов:",
                                             reply_markup=admins_list_keyboard(admins))

    await delete_messages(bot, call.message.chat.id, state, [sent_message.message_id])


@admin_router.callback_query(AdminsListCallbackData.filter())
async def admins_list_callback_data(call: CallbackQuery, state: FSMContext, callback_data: AdminsListCallbackData, config: Config):
    repo = await get_repo(config)

    admin = await repo.users.select_user(callback_data.id)
    sent_message = await call.message.answer("Инфо об админе:\n\n"
                                             f"Имя: {admin.full_name}\n"
                                             f"Юзернейм: @{admin.username}\n"
                                             f"ID: {admin.id}",
                                             reply_markup=admin_delete_keyboard(admin.id, "admin"))

    await delete_messages(call.bot, call.message.chat.id, state, [sent_message.message_id])


@admin_router.callback_query(DeleteAdminCallbackData.filter())
async def delete_admin_callback_data(call: CallbackQuery, state: FSMContext, callback_data: AdminsListCallbackData, config: Config):
    message_ids = []

    repo = await get_repo(config)
    await repo.admins.delete_admin(callback_data.id)

    message_ids.append(await call.message.answer("Админ успешно удалён!"))
    message_ids.append(await call.message.answer("Панель админа:", reply_markup=admin_keyboard()))
    await delete_messages(call.bot, call.message.chat.id, state, [i.message_id for i in message_ids])


@admin_router.callback_query(F.data == "admin_settings")
async def admin_settings(call: CallbackQuery, state: FSMContext):
    repo = await get_repo(config)
    settings = await repo.settings.get_all_settings_as_dict()
    sent_message = await call.message.answer("Настройки:", reply_markup=settings_keyboard(settings, "admin"))
    await delete_messages(call.bot, call.message.chat.id, state, [sent_message.message_id])


@admin_router.callback_query(SettingsCallbackData.filter())
async def settings_callback_data(call: CallbackQuery, callback_data: SettingsCallbackData):
    repo = await get_repo(config)
    await repo.settings.update_payment_status(not callback_data.value, callback_data.id)
    settings = await repo.settings.get_all_settings_as_dict()
    await call.message.edit_reply_markup(reply_markup=settings_keyboard(settings, "admin"))

@admin_router.inline_query()
async def user_inline_query(inline_query: InlineQuery):
    config = load_config(".env")
    repo = await get_repo(config)

    if inline_query.query != "":
        users = await repo.users.find_users_by_id_prefix(inline_query.query)
        users_json_list = [user.to_dict() for user in users]

        results = [
            InlineQueryResultArticle(
                id=str(user["id"]),
                title=user["full_name"],
                description=f"Username: {user.get('username', 'N/A')}",
                input_message_content=InputTextMessageContent(
                    message_text=f"User Details:\n"
                                 f"ID: {user['id']}\n"
                ),
            )
            for user in users_json_list
        ]

        await inline_query.answer(results, cache_time=1)
    else:
        await inline_query.answer([], cache_time=1)
