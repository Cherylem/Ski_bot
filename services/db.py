import sqlite3
from pathlib import Path

DB_PATH = Path("weather.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Включаем WAL для параллельного чтения/записи
    cur.execute("PRAGMA journal_mode=WAL;")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS weather (
        resort TEXT,
        elevation INTEGER,
        timestamp TEXT,
        temp REAL,
        wind REAL,
        humidity REAL,
        pressure REAL,
        precipitation REAL,
        wind_dir REAL,
        condition TEXT,
        PRIMARY KEY (resort, elevation)
    )
    """)

    conn.commit()
    conn.close()