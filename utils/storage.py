import json
from pathlib import Path

DATA_PATH = Path("data/user_state.json")


def load_user_state():
    """Загрузка состояния пользователей с обработкой ошибок"""
    try:
        if DATA_PATH.exists():
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:  # Если файл пустой
                    return {}
                return json.loads(content)
        return {}
    except (json.JSONDecodeError, Exception) as e:
        print(f"⚠️ Ошибка загрузки user_state.json: {e}")
        print("Создаем новый файл...")
        return {}


def save_user_state(user_state):
    """Сохранение состояния пользователей"""
    try:
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(user_state, f, ensure_ascii=False, indent=2)
        print("💾 Состояние сохранено успешно")
    except Exception as e:
        print(f"❌ Ошибка сохранения user_state.json: {e}")


def initialize_storage():
    """Инициализация хранилища при первом запуске"""
    if not DATA_PATH.exists():
        save_user_state({})
        print("📁 Файл user_state.json создан")