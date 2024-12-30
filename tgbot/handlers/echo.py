from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hcode

echo_router = Router()

@echo_router.message(F.text)
async def bot_echo_all(message: types.Message, state: FSMContext):
    text = ("Я ещё не знаю как ответить на эту команду 👾",)
    await message.answer("\n".join(text))
