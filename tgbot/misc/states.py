from aiogram.fsm.state import StatesGroup, State


class UsdtTransaction(StatesGroup):
    hash = State()

class SubscriptionGift(StatesGroup):
    receiver = State()

class Suggestion(StatesGroup):
    message = State()
