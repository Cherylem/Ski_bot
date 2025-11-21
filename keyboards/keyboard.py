from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    """Главное меню как inline-клавиатура под сообщением"""
    buttons = [
        [InlineKeyboardButton(text="📋 Чеклист", callback_data="main_checklist")],
        [InlineKeyboardButton(text="⛰️ Курорты", callback_data="main_resorts")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="main_settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def categories_keyboard(user_data):
    """Клавиатура категорий с прогрессом"""
    categories = user_data["categories"]
    buttons = []
    
    # Используем индексы вместо названий для callback_data
    category_names = list(categories.keys())
    
    for index, category_name in enumerate(category_names):
        category = categories[category_name]
        # Подсчет выполненных пунктов
        checked_count = sum(1 for item in category.values() if item)
        total_count = len(category)
        
        buttons.append([InlineKeyboardButton(
            text=f"{category_name} ({checked_count}/{total_count})",
            callback_data=f"cat_{index}"
        )])
    
    #кнопки управления
    buttons.append([InlineKeyboardButton(text="🔄 Сбросить всё", callback_data="reset_all")])
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def items_keyboard(category_index, category_name, items):
    """Клавиатура элементов конкретной категории"""
    buttons = []
    
    # Используем индексы для элементов
    item_names = list(items.keys())
    
    for item_index, (item_name, checked) in enumerate(items.items()):
        status = "✅" if checked else "❌"
        buttons.append([InlineKeyboardButton(
            text=f"{status} {item_name}",
            callback_data=f"item_{category_index}_{item_index}"
        )])
    
    # Кнопки навигации
    buttons.append([InlineKeyboardButton(text="⬅️ Назад к категориям", callback_data="back_to_categories")])
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)