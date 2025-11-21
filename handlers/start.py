from aiogram import Router, types
from aiogram.filters import Command
from keyboards.keyboard import main_menu_keyboard

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "🏔️ Добро пожаловать в Ride Forecast Bot!\n"
        "Я помогу тебе подготовиться к поездке на сноуборде.",
        reply_markup=main_menu_keyboard()
    )