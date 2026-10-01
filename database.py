import sqlite3

DB_NAME = "notes.db"

def init_db():
    """Инициализация базы данных: создание таблиц и демо-данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Создаем таблицу категорий
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # 2. Создаем таблицу заметок со связью FOREIGN KEY (внешний ключ)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    """)
    
    # Наполняем базу базовыми категориями для теста, если таблица пустая
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO categories (name) VALUES (?)", [
            ("Учеба",),
            ("Работа",),
            ("Личное",)
        ])
        print("Базовые категории успешно добавлены в БД!")
        
    conn.commit()
    conn.close()

def get_db_connection():
    """Подключение к БД с поддержкой внешних ключей и словарей."""
    conn = sqlite3.connect(DB_NAME)
    # Обязательно включаем поддержку FOREIGN KEY в самом SQLite
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn
