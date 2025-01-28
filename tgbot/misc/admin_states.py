from aiogram.fsm.state import StatesGroup, State

class AdminStates(StatesGroup):
    admin_id = State()
    add_days = State()
    mailing_message = State()
