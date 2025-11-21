import asyncio
from aiogram import Bot, Dispatcher, BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message, CallbackQuery

from config import BOT_TOKEN
from handlers.start import router as start_router
from handlers.resorts import router as resorts_router
from handlers.checklist import router as checklist_router
from utils.storage import load_user_state, initialize_storage
from services.weather_service import init_db, start_scheduler

# =========================
# Middleware для состояния пользователей
# =========================
class UserStateMiddleware(BaseMiddleware):
    def __init__(self, user_state: dict):
        super().__init__()
        self.user_state = user_state

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        data['user_state'] = self.user_state
        return await handler(event, data)

# =========================
# Основная функция
# =========================
async def main():
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN not found!")
        print("Please create .env file with BOT_TOKEN=your_bot_token")
        return

    # Инициализация
    initialize_storage()
    user_state = load_user_state()
    print(f"📊 Загружено пользователей: {len(user_state)}")

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Middleware
    dp.update.outer_middleware(UserStateMiddleware(user_state))

    # Роутеры
    dp.include_router(start_router)
    dp.include_router(checklist_router)
    dp.include_router(resorts_router)

    # Инициализация базы погоды и планировщика
    init_db()
    start_scheduler()  # автообновление каждые 15 минут

    print("🤖 Bot started successfully!")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Bot stopped with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())