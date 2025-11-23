import sqlite3
import os

DB_NAME = 'booking.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Rooms Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            size INTEGER,
            features TEXT,
            image TEXT
        )
    ''')

    # Bookings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            date TEXT NOT NULL,
            time_range TEXT NOT NULL,
            total TEXT NOT NULL,
            created_at TEXT NOT NULL,
            slots_json TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    ''')

    # Blocked Slots Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL
        )
    ''')

    # Settings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    
    # Initialize default settings if not exists
    cursor.execute('SELECT * FROM settings WHERE key = ?', ('startTime',))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO settings (key, value) VALUES (?, ?)', ('startTime', '08:00'))
        
    cursor.execute('SELECT * FROM settings WHERE key = ?', ('endTime',))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO settings (key, value) VALUES (?, ?)', ('endTime', '22:00'))
        
    cursor.execute('SELECT * FROM settings WHERE key = ?', ('workDays',))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO settings (key, value) VALUES (?, ?)', ('workDays', '["1","2","3","4","5"]'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
