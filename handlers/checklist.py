from aiogram import Router, types
from keyboards.keyboard import categories_keyboard, items_keyboard, main_menu_keyboard
from utils.storage import save_user_state

router = Router()

# Пример базового шаблона списка
BASE_CATEGORIES = {
    "Одежда для катания 🏂": {
        "🧥 Куртка": False,
        "👖 Брюки": False,
        "🩳 Термобелье верх (2 шт)": False,
        "🩳 Термобелье низ": False,
        "🧣 Флисовая кофта": False,
        "🧥 Тонкие утепленные куртка и шорты": False,
        "🧥 Пуховый свитер, пуховые шорты": False,
        "🧤 Варежки, перчатки (1 пара запасных)": False,
        "🧣 Бафф/балаклава/подшлемник": False,
        "🧦 Носки горнолыжные (2 пары)": False,
    },
    "Одежда apres-ski ☕": {
        "🧤 Перчатки": False,
        "🧢 Шапка": False,
        "👟 Повседневная обувь": False,
        "👖 Повседневные брюки": False,
        "👕 Кофта": False,
        "🩲 Сменное нижнее белье": False,
        "👕 Футболки": False,
        "🧦 Носки (3-4 пары)": False,
        "👚 Одежда в номер/дом": False,
        "🥿 Домашняя обувь («пуховые тапки»)": False,
        "👙 Купальник/плавки": False,
        "🩴 Резиновые шлепки в душ/баню/бассейн": False,
    },
    "Снаряжение для катания 🏔": {
        "🏂 Сноуборд": False,
        "🥾 Сноубордические ботинки": False,
        "🔗 Сноубордические крепления": False,
        "⛑️ Шлем": False,
        "🕶️ Маска (2 шт)": False,
        "🛡️ Защита тела": False,
        "🎒 Рюкзак": False,
    },
    "Лавинное снаряжение ⚠️": {
        "📟 Биппер": False,
        "📏 Щуп": False,
        "⛏️ Лопата": False,
        "🎒 Лавинный рюкзак": False,
    },
    "Багаж 🧳": {
        "🛡️ Чехол для сноуборда": False,
        "🎒 Сумка для ботинок": False,
        "👜 Сумка на колесах/баул": False,
        "🎁 Стретч пленка": False,
        "🎒 Компактный рюкзак": False,
        "🧤 Гермомешок для запасных перчаток и шапки": False,
        "📦 Гермомешок для электроники и документов": False,
    },
    "Здоровье и гигиена 🩺": {
        "💊 Аптечка": False,
        "🧴 Средства гигиены": False,
        "💄 Бальзам для губ": False,
        "🧴 Солнцезащитный крем": False,
        "🧻 Салфетки влажные/сухие": False,
        "🧻 Туалетная бумага": False,
        "🧳 Нессесер": False,
        "🧺 Полотенце": False,
    },
    "Электроника 📱": {
        "📱 Смартфон": False,
        "⌚ Часы": False,
        "📻 Рации": False,
        "🔋 Пауэрбанк": False,
        "📷 Экшен-камера": False,
        "📸 Фотоаппарат": False,
        "🔌 Зарядные устройства": False,
        "🔌 Переходники/тройники": False,
        "🎧 Проводные наушники": False,
    },
    "Полезные аксессуары 🛠️": {
        "🕶️ Солнцезащитные очки": False,
        "👢 Сушилка для ботинок": False,
        "🔧 Отвертка/мультитул": False,
        "📱 Гермочехол для телефона": False,
        "📂 Гермочехол для документов": False,
        "💻 Мягкий кейс для электроники": False,
        "☕ Термос": False,
        "🥤 Фляга": False,
        "🥡 Пакеты zip-lock для еды": False,
        "🛌 Спасательное одеяло": False,
        "🔥 Каталитическая грелка/грелки": False,
        "🧵 Швейный набор": False,
        "🛠️ Ремнабор": False,
        "🔧 Отвертка": False,
    },
    "Документы 📄": {
        "🪪 Паспорт, водительские права": False,
        "🧾 Страховой полис": False,
        "💰 Кошелек, деньги": False,
    },
}

def init_user(user_state, user_id):
    """Инициализация состояния пользователя"""
    user_id_str = str(user_id)
    if user_id_str not in user_state:
        user_state[user_id_str] = {
            "level": "main", 
            "categories": BASE_CATEGORIES.copy()
        }
    return user_state[user_id_str]

# Обработчик для кнопки "Чеклист" в главном меню
@router.callback_query(lambda c: c.data == "main_checklist")
async def open_main_checklist(callback: types.CallbackQuery, user_state: dict):
    """Обработчик кнопки чеклиста из главного меню"""
    user_data = init_user(user_state, callback.from_user.id)
    await callback.message.edit_text(
        "🎒 Выбери категорию:",
        reply_markup=categories_keyboard(user_data)
    )

@router.callback_query(lambda c: c.data.startswith("cat_"))
async def open_category(callback: types.CallbackQuery, user_state: dict):
    """Открытие конкретной категории по индексу"""
    try:
        user_data = init_user(user_state, callback.from_user.id)
        
        # Извлекаем индекс категории
        category_index = int(callback.data.replace("cat_", ""))
        
        # Получаем название категории и элементы по индексу
        category_names = list(user_data["categories"].keys())
        
        if category_index < 0 or category_index >= len(category_names):
            await callback.answer("❌ Категория не найдена")
            return
            
        category_name = category_names[category_index]
        items = user_data["categories"][category_name]

        await callback.message.edit_text(
            f"📦 Категория: {category_name}",
            reply_markup=items_keyboard(category_index, category_name, items)
        )
    except (ValueError, IndexError) as e:
        print(f"❌ Ошибка в open_category: {e}")
        await callback.answer("❌ Ошибка при открытии категории")

@router.callback_query(lambda c: c.data.startswith("item_"))
async def toggle_item(callback: types.CallbackQuery, user_state: dict):
    """Переключение состояния элемента по индексам"""
    try:
        # Разбираем callback_data: item_категория_элемент
        parts = callback.data.split("_")
        if len(parts) != 3:
            await callback.answer("❌ Неверный формат данных")
            return
            
        category_index = int(parts[1])
        item_index = int(parts[2])
        
        user_data = init_user(user_state, callback.from_user.id)
        
        # Получаем категорию и элемент по индексам
        category_names = list(user_data["categories"].keys())
        
        if category_index < 0 or category_index >= len(category_names):
            await callback.answer("❌ Категория не найдена")
            return
            
        category_name = category_names[category_index]
        category_items = user_data["categories"][category_name]
        item_names = list(category_items.keys())
        
        if item_index < 0 or item_index >= len(item_names):
            await callback.answer("❌ Элемент не найден")
            return
            
        item_name = item_names[item_index]
        
        # Переключаем состояние
        current = category_items[item_name]
        category_items[item_name] = not current
        
        # Сохраняем состояние
        save_user_state(user_state)
        
        # Обновляем клавиатуру
        await callback.message.edit_reply_markup(
            reply_markup=items_keyboard(category_index, category_name, category_items)
        )
        
        await callback.answer("✅ Изменения сохранены")
        
    except Exception as e:
        print(f"❌ Ошибка в toggle_item: {e}")
        await callback.answer("❌ Произошла ошибка")

@router.callback_query(lambda c: c.data == "back_to_categories")
async def back_to_categories(callback: types.CallbackQuery, user_state: dict):
    """Возврат к списку категорий"""
    user_data = init_user(user_state, callback.from_user.id)
    await callback.message.edit_text(
        "🎒 Выбери категорию:",
        reply_markup=categories_keyboard(user_data)
    )

@router.callback_query(lambda c: c.data == "reset_all")
async def reset_all(callback: types.CallbackQuery, user_state: dict):
    """Сброс всех чекбоксов"""
    user_data = init_user(user_state, callback.from_user.id)
    
    for category in user_data["categories"].values():
        for item in category:
            category[item] = False
    
    save_user_state(user_state)

    await callback.message.edit_text(
        "♻️ Всё сброшено!\n\n🎒 Выбери категорию:",
        reply_markup=categories_keyboard(user_data)
    )

@router.callback_query(lambda c: c.data == "main_menu")
async def to_main_menu(callback: types.CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text(
        "🏠 Главное меню:", 
        reply_markup=main_menu_keyboard()
    )

# Заглушки для других кнопок главного меню

@router.callback_query(lambda c: c.data == "main_settings")
async def settings_handler(callback: types.CallbackQuery):
    await callback.answer(
        "⚙️ Настройки скоро будут доступны!",
        reply_markup=main_menu_keyboard()
    )



