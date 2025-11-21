from pathlib import Path
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.keyboard import main_menu_keyboard
from services.weather_service import format_weather_text, weather_keyboard, RESORTS, PLOTS_DIR

router = Router()

# Словарь для хранения message_id отправленных графиков
user_graph_messages = {}

# =======================
# Клавиатура выбора курортов
# =======================
def resorts_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🏔️ Шерегеш", callback_data="resort_sheregesh")],
        [InlineKeyboardButton(text="⛰️ Эльбрус", callback_data="resort_elbrus")],
        [InlineKeyboardButton(text="🏂 Роза Хутор", callback_data="resort_rosa")],
        [InlineKeyboardButton(text="🎿 Домбай", callback_data="resort_dombay")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# =======================
# Меню курортов
# =======================
@router.callback_query(lambda c: c.data == "main_resorts")
async def show_resorts(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🎿 Выбери курорт для получения информации:",
        reply_markup=resorts_keyboard()
    )

# =======================
# Информация о конкретном курорте
# =======================
@router.callback_query(lambda c: c.data.startswith("resort_"))
async def show_resort_info(callback: types.CallbackQuery):
    resort_id = callback.data.replace("resort_", "")

    resort_info = {
        "sheregesh": {
            "name": "🏔️ Шерегеш",
            "description": "📍 Кемеровская область\n📏 Высота: 1270м\n🎿 Трасс: 35\n❄️ Сезон: ноябрь-апрель\n\nЛучший курорт для фрирайда!",
            "weather": "weather_sheregesh"
        },
        "elbrus": {
            "name": "⛰️ Эльбрус",
            "description": "📍 Кабардино-Балкария\n📏 Высота: 3847м\n🎿 Трасс: 11\n❄️ Сезон: декабрь-апрель\n\nСамый высокогорный курорт России!",
            "weather": "weather_elbrus"
        },
        "rosa": {
            "name": "🏂 Роза Хутор",
            "description": "📍 Сочи\n📏 Высота: 2320м\n🎿 Трасс: 102\n❄️ Сезон: декабрь-апрель\n\nКрупнейший курорт России!",
            "weather": "weather_rosa"
        },
        "dombay": {
            "name": "🎿 Домбай",
            "description": "📍 Карачаево-Черкесия\n📏 Высота: 3168м\n🎿 Трасс: 12\n❄️ Сезон: декабрь-апрель\n\nЖемчужина Кавказа!",
            "weather": "weather_dombay"
        }
    }

    resort = resort_info.get(resort_id)
    if not resort:
        await callback.answer("❌ Курорт не найден")
        return

    resort_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌤️ Погода", callback_data=resort["weather"])],
        [InlineKeyboardButton(text="📞 Контакты", callback_data=f"contacts_{resort_id}")],
        [InlineKeyboardButton(text="⬅️ Назад к курортам", callback_data="main_resorts")]
    ])

    await callback.message.edit_text(
        f"{resort['name']}\n\n{resort['description']}",
        reply_markup=resort_kb
    )

# =======================
# Погода на весь день
# =======================
@router.callback_query(lambda c: c.data.startswith("weather_") and not c.data.startswith("weather_plot:"))
async def weather_handler(callback: types.CallbackQuery):
    resort_id = callback.data.replace("weather_", "")
    text = format_weather_text(resort_id)
    kb = weather_keyboard(resort_id)
    await callback.message.edit_text(text, reply_markup=kb)

# =======================
# Контакты (заглушка)
# =======================
@router.callback_query(lambda c: c.data.startswith("contacts_"))
async def contacts_handler(callback: types.CallbackQuery):
    await callback.answer("📞 Контакты скоро будут доступны!")

# =======================
# Назад в главное меню
# =======================
@router.callback_query(lambda c: c.data == "main_menu")
async def back_to_main_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🏠 Главное меню:",
        reply_markup=main_menu_keyboard()
    )

# =======================
# Отправка готового графика
# =======================
@router.callback_query(lambda c: c.data.startswith("weather_plot:"))
async def send_weather_plot(callback: types.CallbackQuery):
    try:
        resort_id = callback.data.split(":")[1]
        plot_path = PLOTS_DIR / f"{resort_id}_weather.png"
        
        print(f"🖼️ [send_weather_plot] Пытаемся отправить график для {resort_id}")
        print(f"🖼️ [send_weather_plot] Путь: {plot_path}")
        print(f"🖼️ [send_weather_plot] Файл существует: {plot_path.exists()}")

        if not plot_path.exists():
            print(f"❌ [send_weather_plot] График не найден по пути: {plot_path}")
            await callback.answer("График ещё не готов ❌")
            return

        # Отправляем готовый график
        photo = types.FSInputFile(plot_path)
        sent_message = await callback.message.answer_photo(
            photo, 
            caption=f"📈 Погода на 24 часа: {RESORTS[resort_id]['name']}"
        )
        
        # Сохраняем message_id отправленного графика
        user_id = callback.from_user.id
        user_graph_messages[user_id] = sent_message.message_id
        print(f"✅ [send_weather_plot] График успешно отправлен для {resort_id}, message_id: {sent_message.message_id}")
        
        # Отправляем клавиатуру с кнопкой "Удалить график и назад"
        delete_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад к курортам", callback_data="delete_graph_and_back")]
        ])
        
        # Редактируем исходное сообщение с прогнозом, добавляя кнопку удаления
        await callback.message.edit_reply_markup(reply_markup=delete_kb)
        await callback.answer("📊 График отправлен!")
        
    except Exception as e:
        print(f"❌ Ошибка при отправке графика: {e}")
        import traceback
        print(f"❌ Детали ошибки: {traceback.format_exc()}")
        await callback.answer("Ошибка при отправке графика ❌")

# =======================
# Удаление графика и возврат назад
# =======================
@router.callback_query(lambda c: c.data == "delete_graph_and_back")
async def delete_graph_and_back(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        
        # Проверяем, есть ли сохраненный график для пользователя
        if user_id in user_graph_messages:
            graph_message_id = user_graph_messages[user_id]
            
            # Пытаемся удалить сообщение с графиком
            try:
                await callback.bot.delete_message(callback.message.chat.id, graph_message_id)
                print(f"✅ График с message_id {graph_message_id} удален")
            except Exception as e:
                print(f"⚠️ Не удалось удалить график: {e}")
            
            # Удаляем запись из словаря
            del user_graph_messages[user_id]
        
        # Возвращаем пользователя к меню курортов
        await callback.message.edit_text(
            "🎿 Выбери курорт для получения информации:",
            reply_markup=resorts_keyboard()
        )
        await callback.answer("🗑️ График удален")
        
    except Exception as e:
        print(f"❌ Ошибка при удалении графика: {e}")
        await callback.answer("Ошибка при удалении графика ❌")