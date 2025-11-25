# services/weather_service.py
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import requests
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pytz
from services.weather_plot import make_weather_plot
from services.resorts_list import RESORTS

# Используем абсолютные пути
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "weather.db"
PLOTS_DIR = BASE_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

API_URL = "https://api.open-meteo.com/v1/forecast"

# Курорты с координатами и часовым поясом


# RESORTS = {
#     "sheregesh": {"lat": 52.9235, "lon": 87.9576, "name": "Шерегеш", "elevations": [850], "timezone": "Asia/Novosibirsk"},
#     "elbrus": {"lat": 43.2837, "lon": 42.4408, "name": "Эльбрус", "elevations": [2300], "timezone": "Europe/Moscow"},
#     "rosa": {"lat": 43.6673, "lon": 40.3176, "name": "Роза Хутор", "elevations": [1170], "timezone": "Europe/Moscow"},
#     "dombay": {"lat": 43.5361, "lon": 41.5772, "name": "Домбай", "elevations": [1600], "timezone": "Europe/Moscow"},
# }

logging.basicConfig(level=logging.INFO)
MAX_MESSAGE_LENGTH = 4000  # Telegram limit

# -------------------------
# Работа с базой данных
# -------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS weather (
        resort TEXT,
        elevation INTEGER,
        timestamp TEXT,
        temp REAL,
        wind REAL,
        wind_dir REAL,
        precipitation REAL,
        condition TEXT,
        PRIMARY KEY (resort, elevation, timestamp)
    )
    """)
    conn.commit()
    conn.close()

def save_weather(resort: str, elevation: int, timestamp: str, temp: float,
                 wind: float, wind_dir: float, precipitation: float, condition: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO weather
    (resort, elevation, timestamp, temp, wind, wind_dir, precipitation, condition)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (resort, elevation, timestamp, temp, wind, wind_dir, precipitation, condition))
    conn.commit()
    conn.close()

def get_latest_weather(resort: str, hours: int = 24):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT * FROM weather 
        WHERE resort=? 
        ORDER BY timestamp ASC
        LIMIT ?
        """, (resort, hours))
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"❌ Ошибка при получении данных для {resort}: {e}")
        return []

def clear_weather(resort: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM weather WHERE resort=?", (resort,))
    conn.commit()
    conn.close()

# -------------------------
# Создание графиков погоды
# -------------------------
def create_weather_plots():
    """Создает/обновляет графики для всех курортов"""
    print("📊 Создание графиков для всех курортов...")
    
    for resort_id in RESORTS.keys():
        try:
            rows = get_latest_weather(resort_id)
            if not rows:
                print(f"⚠️ Нет данных для создания графика {resort_id}")
                continue

            # Формируем данные для графика
            hours = [
                datetime.fromisoformat(row["timestamp"]).strftime("%H:%M")
                for row in rows
            ]
            temps = [row["temp"] for row in rows]
            winds = [row["wind"] for row in rows]
            prec = [row["precipitation"] for row in rows]

            # Создаем график
            output_path = PLOTS_DIR / f"{resort_id}_weather.png"
            
            make_weather_plot(
                hours=hours,
                temps=temps,
                wind_speeds=winds,
                precipitation=prec,
                resort_name=RESORTS[resort_id]["name"],
                elevation=rows[0]["elevation"],
                output_path=str(output_path)
            )
            
            print(f"✅ График создан: {output_path}")
            
        except Exception as e:
            print(f"❌ Ошибка создания графика для {resort_id}: {e}")

# -------------------------
# Получение данных с API
# -------------------------
def fetch_weather(resort: str, lat: float, lon: float, elevations: list, timezone: str):
    try:
        # удаляем старые данные
        clear_weather(resort)

        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,precipitation,weathercode,windspeed_10m,winddirection_10m",
            "timezone": timezone
        }
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # текущий час в таймзоне курорта
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        now_str = now.strftime("%Y-%m-%dT%H:00")  # округляем до часа

        # находим индекс ближайшего часа в данных
        start_index = next(i for i, t in enumerate(data["hourly"]["time"]) if t >= now_str)

        for elevation in elevations:
            for i in range(start_index, start_index + 24):
                if i >= len(data["hourly"]["time"]):
                    break
                timestamp = data["hourly"]["time"][i]
                temp = data["hourly"]["temperature_2m"][i]
                wind = data["hourly"]["windspeed_10m"][i]
                wind_dir = data["hourly"]["winddirection_10m"][i]
                precipitation = data["hourly"]["precipitation"][i]
                condition = str(data["hourly"]["weathercode"][i])
                save_weather(resort, elevation, timestamp, temp, wind, wind_dir, precipitation, condition)

        logging.info(f"✅ Прогноз обновлен для {resort}")
        
    except Exception as e:
        logging.error(f"❌ Не удалось обновить прогноз {resort}: {e}")

def update_all_resorts():
    """Обновляет данные и графики для всех курортов"""
    print("🔄 Обновление данных для всех курортов...")
    for code, info in RESORTS.items():
        fetch_weather(code, info["lat"], info["lon"], info["elevations"], info["timezone"])
    
    # После обновления данных создаем графики
    create_weather_plots()

# -------------------------
# Планировщик обновления
# -------------------------
scheduler = AsyncIOScheduler()

def start_scheduler():
    update_all_resorts()  # обновляем сразу при старте (данные + графики)
    scheduler.add_job(update_all_resorts, 'interval', hours=1)  # потом каждый час
    scheduler.start()
    logging.info("[Scheduler] Прогноз и графики обновляются каждый час")

# -------------------------
# Форматирование данных для бота
# -------------------------
def format_weather_text(resort: str) -> str:
    rows = get_latest_weather(resort)
    if not rows:
        return "Прогноз недоступен ❌"

    # Берём высоту из первой записи (все записи на одной высоте)
    elevation = rows[0]['elevation']

    all_precipitation = sum(row['precipitation'] for row in rows)
    text = f"🌤️ Прогноз погоды для {RESORTS[resort]['name']} (высота {elevation} м) на ближайшие 24 часа:\n🌧️ Осадки на ближайшие сутки: {all_precipitation/10:.1f} см\n\n"
    
    # Показываем только ключевые часы (каждые 3 часа)
    for i, row in enumerate(rows):
        if i % 3 == 0:  # Каждые 3 часа
            dt = datetime.fromisoformat(row['timestamp'])
            formatted_time = dt.strftime("%H:%M")
            text += (f"⏰ {formatted_time}->🌡️ {row['temp']}°C | 💨 {row['wind']} м/с | 🌧️ {row['precipitation']} мм\n")
        
    return text

def weather_keyboard(resort: str) -> InlineKeyboardMarkup:
    """Теперь просто проверяет наличие графика и возвращает клавиатуру"""
    plot_path = PLOTS_DIR / f"{resort}_weather.png"
    
    if not plot_path.exists():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📊 График готовится...", callback_data="none")],
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_resorts")]
            ]
        )
    
    # Если график существует - показываем кнопку
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📈 График погоды", callback_data=f"weather_plot:{resort}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_resorts")]
        ]
    )

# ==========================
# Инициализация базы при старте
# ==========================
init_db()