from aiogram.fsm.state import StatesGroup, State


class UsdtTransaction(StatesGroup):
    hash = State()
