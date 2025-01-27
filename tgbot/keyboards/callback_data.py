from typing import Optional

from aiogram.filters.callback_data import CallbackData


class OfferConsentCallbackData(CallbackData, prefix="offer_consent"):
    answer: bool
    deeplink: Optional[str]

class BackCallbackData(CallbackData, prefix="vip_division"):
    state: str

class TariffsCallbackData(CallbackData, prefix="tariffs"):
    id: int

class GuidesCallbackData(CallbackData, prefix="guide"):
    guide: str

class PaginationCallbackData(CallbackData, prefix="pagination"):
    page: int

class ReadingCallbackData(CallbackData, prefix="reading"):
    link: str
    state: Optional[str]

class AdminsListCallbackData(CallbackData, prefix="admins_list"):
    id: int

class DeleteAdminCallbackData(CallbackData, prefix="delete_admins"):
    id: int

class SettingsCallbackData(CallbackData, prefix="settings"):
    id: int
    value: bool

class BlacklistCallbackData(CallbackData, prefix="blacklist"):
    id: int
    is_blocked: bool

class AddDaysCallbackData(CallbackData, prefix="add_days"):
    id: int
