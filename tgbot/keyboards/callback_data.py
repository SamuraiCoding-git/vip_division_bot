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
