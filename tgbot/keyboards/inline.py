from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from infrastructure.database.models import Admin
from tgbot.keyboards.callback_data import OfferConsentCallbackData, BackCallbackData, TariffsCallbackData, \
    GuidesCallbackData, PaginationCallbackData, ReadingCallbackData, AdminsListCallbackData, DeleteAdminCallbackData, \
    SettingsCallbackData, BlacklistCallbackData


def offer_consent_keyboard(extended=True, deeplink=None):
    buttons = [
        [
            InlineKeyboardButton(
                text="✔️ ДА, СОГЛАСЕН",
                callback_data=OfferConsentCallbackData(answer=True, deeplink=deeplink).pack()
            )
        ]
    ]

    if extended:
        buttons.append([
            InlineKeyboardButton(
                text="✖️ НЕТ, НЕ СОГЛАСЕН",
                callback_data=OfferConsentCallbackData(answer=False, deeplink=deeplink).pack()
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def greeting_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="🔥 ПОДРОБНЕЕ ПРО КЛУБ", callback_data="about_club"),
        ],
        [
            InlineKeyboardButton(text="✔️ ТАРИФЫ", callback_data="tariffs"),
        ],
        [
            InlineKeyboardButton(text="💎 ПОДДЕРЖКА", url="https://t.me/vipdivision"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard

def menu_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="🔺 ЧТО ТАКОЕ VIP DIVISION", callback_data="about_vip_division"),
        ],
        [
            InlineKeyboardButton(text="🏆 БИОГРАФИЯ", callback_data="biography"),
        ],
        [
            InlineKeyboardButton(text="⚡ МОЯ ПОДПИСКА", callback_data="my_subscription"),
        ],
        [
            InlineKeyboardButton(text="✔️ ТАРИФЫ", callback_data="tariffs"),
        ],
        # [
        #     InlineKeyboardButton(text="🎮 ИГРА", callback_data="game"),
        # ],
        [
            InlineKeyboardButton(text="👥 ОТЗЫВЫ", callback_data="reviews"),
            InlineKeyboardButton(text="📚 ЭКСПЕРТЫ", callback_data="experts"),
        ],
        [
            InlineKeyboardButton(text="❓ ВОПРОСЫ", callback_data="questions"),
            InlineKeyboardButton(text="📝 ГАЙДЫ", callback_data="guide"),
        ],
        [
            InlineKeyboardButton(text="💎 ПОДДЕРЖКА", url="https://t.me/vipdivision"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard

def vip_division_keyboard(state):
    buttons = [
        [
            InlineKeyboardButton(text="💬 КАК РАБОТАЕТ ЧАТ?", callback_data="how_chat_works"),
        ],
        [
            InlineKeyboardButton(text="✅ ВСТУПИТЬ В СООБЩЕСТВО", callback_data="tariffs"),
        ],
        [
            InlineKeyboardButton(text="НАЗАД ↩", callback_data=BackCallbackData(state=state).pack()),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


def access_payment_keyboard(state: str):
    buttons = [
        [
            InlineKeyboardButton(text="💸 ОПЛАТИТЬ ДОСТУП", callback_data="tariffs"),
        ],
        [
            InlineKeyboardButton(text="НАЗАД ↩", callback_data=BackCallbackData(state=state).pack()),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def story_keyboard(state: str):
    buttons = [
        [
            InlineKeyboardButton(text="✔️ ЧИТАТЬ ИСТОРИЮ", url="https://telegra.ph/YA-NEKRASIVYJ-U-MENYA-NET-DENEG-MNE-NE-POVEZLO-KOMU-YA-NUZHEN-MOYA-ISTORIYA-12-07"),
        ],
        [
            InlineKeyboardButton(text="НАЗАД ↩", callback_data=BackCallbackData(state=state).pack()),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def subscription_keyboard(state: str, plans):
    builder = InlineKeyboardBuilder()

    for plan in plans:
        builder.add(InlineKeyboardButton(text=plan.name, callback_data=TariffsCallbackData(id=plan.id).pack()))

    builder.add(InlineKeyboardButton(text="НАЗАД ↩", callback_data=BackCallbackData(state=state).pack()))

    builder.adjust(1)

    return builder.as_markup()

def reviews_payment_keyboard(state: str):
    buttons = [
        [
            InlineKeyboardButton(
                text="👉🏽 ЧИТАТЬ ОТЗЫВЫ", url="https://t.me/castingdirectorotzyv"
            ),
        ],
        [
            InlineKeyboardButton(
                text="💳 ОПЛАТИТЬ ДОСТУП", callback_data="tariffs"
            ),
        ],
        [
            InlineKeyboardButton(
                text="НАЗАД ↩", callback_data=BackCallbackData(state=state).pack()
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def experts_keyboard(state: str):
    buttons = [
        [
            InlineKeyboardButton(text="ВРАЧ", url="https://telegra.ph/VRACH-PRIVATKI---ANAR-11-13"),
            InlineKeyboardButton(text="СПОРТ", url="https://telegra.ph/RUZI--SPORT-PRIVATKI-12-07"),
            InlineKeyboardButton(text="СТИЛИСТ", url="https://telegra.ph/STILIST-PRIVATKI---RODOS-11-13"),
        ],
        [
            InlineKeyboardButton(text="💳 ОПЛАТИТЬ ДОСТУП", callback_data="tariffs"),
        ],
        [
            InlineKeyboardButton(text="НАЗАД ↩", callback_data=BackCallbackData(state=state).pack()),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def access_keyboard(state: str):
    buttons = [
        [
            InlineKeyboardButton(text="ИЗУЧИТЬ ✅", url="https://telegra.ph/CHto-poleznogo-est-v-tvoem-zakrytom-soobshchestve-11-04"),
        ],
        [
            InlineKeyboardButton(text="💸 ДОСТУП ЗА 41 РУБ/ДЕНЬ", callback_data="tariffs"),
        ],
        [
            InlineKeyboardButton(text="НАЗАД ↩", callback_data=BackCallbackData(state=state).pack()),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def assistant_keyboard(state: str):
    buttons = [
        [
            InlineKeyboardButton(text="НАПИСАТЬ АССИСТЕНТУ", url="https://t.me/vipdivision"),
        ],
        [
            InlineKeyboardButton(text="В МЕНЮ ↩", callback_data=BackCallbackData(state=state).pack()),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def my_subscription_keyboard(state: str, is_sub=False, chat_link=None, channel_link=None, is_recurrent=False):
    if is_sub:
        text = "❌ Отменить продление" if is_recurrent else "✅ ВКЛЮЧИТЬ продление"
        buttons = [
            [
                InlineKeyboardButton(text="🔺ВСТУПИТЬ В КАНАЛ", url=channel_link),
            ],
            [
                InlineKeyboardButton(text="🔺ВСТУПИТЬ В ЧАТ", url=chat_link),

            ],
            [
                InlineKeyboardButton(text=text, callback_data="toggle_recurrence")
            ],
            [
                InlineKeyboardButton(text="НАЗАД ↩", callback_data=BackCallbackData(state=state).pack()),
            ],
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(text="✔️ ТАРИФЫ", callback_data="tariffs"),
            ],
            [
                InlineKeyboardButton(text="НАЗАД ↩", callback_data=BackCallbackData(state=state).pack()),
            ],
        ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def guide_keyboard(state: str):
    buttons = [
        [
            InlineKeyboardButton(text="Гайд по перепискам", callback_data=GuidesCallbackData(guide="texting").pack()),
        ],
        [
            InlineKeyboardButton(text="Гайд по соблазнению", callback_data=GuidesCallbackData(guide="seduction").pack()),
        ],
        [
            InlineKeyboardButton(text="НАЗАД ↩", callback_data=BackCallbackData(state=state).pack()),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def communication_base_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                text="База для общения",
                url="https://t.me/c/1699879031/1061"
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_guide_keyboard(text):
    buttons = [
        [
            InlineKeyboardButton(
                text=text,
                callback_data="get_guide"
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def pagination_keyboard(current_page):
    buttons = [InlineKeyboardButton(
        text="←",  # Left arrow
        callback_data=PaginationCallbackData(page=current_page - 1).pack(),
    ), InlineKeyboardButton(
        text=f"{current_page} / 2",  # Page display
        callback_data="ignore",
    ), InlineKeyboardButton(
        text="→",  # Right arrow
        callback_data=PaginationCallbackData(page=current_page + 1).pack(),
    )]

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def read_keyboard(text, link, state, extended=False):
    buttons = [
        [
            InlineKeyboardButton(
                text=text,
                callback_data=ReadingCallbackData(link=link, state=state).pack()
            ),
        ],
    ]

    if extended:
        buttons.append([
            InlineKeyboardButton(
                text="Научиться также 👌🏻",
                callback_data="get_guide"
            ),
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard

def guides_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                text="Разбор удачной переписки с СЗ",
                callback_data="successful_texting"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Гайд по Соблазнению",
                callback_data="get_guide"
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def pay_keyboard(payment_link, state):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💳 ПЕРЕЙТИ К ОПЛАТЕ",
                web_app=WebAppInfo(url=payment_link)  # Укажите ваш URL
            )
        ],
        [
            InlineKeyboardButton(
                text="ОПЛАТИТЬ КРИПТОЙ USDT (TRC 20)",
                callback_data="pay_crypto"
            )
        ],
        [
            InlineKeyboardButton(
                text="НАЗАД ↩",
                callback_data=BackCallbackData(state=state).pack()
            )
        ]
    ])

    return keyboard

def crypto_pay_link(state):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="НАЗАД ↩",
                callback_data=BackCallbackData(state=state).pack()
            )
        ]
    ])
    return keyboard

def crypto_pay_check_keyboard(state):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Я ОПЛАТИЛ ✅",
                callback_data="check_crypto_pay"
            )
        ],
        [
            InlineKeyboardButton(
                text="НАЗАД ↩",
                callback_data=BackCallbackData(state=state).pack()
            )
        ]
    ])
    return keyboard

def join_resources_keyboard(channel_invite_link, chat_invite_link, is_recurrent):
    buttons = [
        [
            InlineKeyboardButton(text="🔺 ВСТУПИТЬ В КАНАЛ", url=channel_invite_link)
        ],
        [
            InlineKeyboardButton(text="🔺 ВСТУПИТЬ В ЧАТ", url=chat_invite_link)
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def instruction_keyboard():
    buttons = [
        InlineKeyboardButton(text="1️⃣ Изучить для начала", url="https://telegra.ph/S-chego-nachat-chitat-privatnyj-kanal-12-23")
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard

def ready_to_change_keyboard():
    buttons = [
        InlineKeyboardButton(text="✅ Я готов и хочу изменений", callback_data="ready_to_change")
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def community_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                text="💯Отзывы", url="https://t.me/castingdirectorotzyv"
                                 )
        ],
        [
            InlineKeyboardButton(
                text="❓ ВОПРОСЫ", callback_data="questions"
            )
        ],
        [
            InlineKeyboardButton(
                text="➡️ Доступ за 46 руб/месяц", callback_data="tariffs"
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def generate_keyboard(button_text):
    buttons = [
        InlineKeyboardButton(text=button_text, callback_data="tariffs")
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard

def podcast_channel_keyboard():
    buttons = [
        InlineKeyboardButton(text="Смотреть подкаст", url="https://youtu.be/I1bn-3Y5A_Y")
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard

def admin_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Добавить админа", callback_data="add_admin"),
            InlineKeyboardButton(text="Cписок админов", callback_data="admin_list")
        ],
        [
            InlineKeyboardButton(text="Настройки", callback_data="admin_settings")
        ],
        [
            InlineKeyboardButton(text="Статус пользователя", switch_inline_query_current_chat="")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def user_status_keyboard(data):
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{'Разблокировать' if data['is_blocked'] else 'Заблокировать'} пользователя",
                callback_data=BlacklistCallbackData(
                                id=data['id'],
                                is_blocked=data['is_blocked']).pack()
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def admins_list_keyboard(admins_list: list[Admin]):
    keyboard = InlineKeyboardBuilder()

    for admin in admins_list:
        keyboard.add(InlineKeyboardButton(text=f"{admin.id}",
                                          callback_data=AdminsListCallbackData(id=admin.id).pack()))

    keyboard.adjust(1)
    return keyboard.as_markup()

def settings_keyboard(settings: dict, state: str):
    keyboard = InlineKeyboardBuilder()
    for setting in settings.values():
        title = setting['title']
        status_icon = '✅' if setting['value'] else '❌'
        callback_data = SettingsCallbackData(id=setting['id'], value=setting['value']).pack()
        keyboard.button(
            text=f"{title} {status_icon}",
            callback_data=callback_data
        )
    keyboard.add(InlineKeyboardButton(text="НАЗАД ↩", callback_data=BackCallbackData(state=state).pack()))
    keyboard.adjust(1)
    return keyboard.as_markup()



def admin_delete_keyboard(id, state):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Удалить", callback_data=DeleteAdminCallbackData(id=id).pack())
        ],
        [
            InlineKeyboardButton(text="НАЗАД ↩", callback_data=BackCallbackData(state=state).pack())
        ]
    ])
    return keyboard