import sqlite3
import os

def init_database():
    """Initialize the database with all required tables"""
    
    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'booking.db')
    
    print(f"Initializing database at: {db_path}")
    
    # Connect to database (creates file if doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create rooms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            size INTEGER NOT NULL,
            features TEXT NOT NULL,
            image TEXT
        )
    ''')
    
    # Create bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT NOT NULL,
            customerName TEXT NOT NULL,
            customerPhone TEXT NOT NULL,
            date TEXT NOT NULL,
            timeRange TEXT NOT NULL,
            total REAL NOT NULL,
            createdAt TEXT NOT NULL,
            slots TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Create blocked_slots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roomId TEXT NOT NULL,
            date TEXT NOT NULL,
            startTime TEXT NOT NULL,
            endTime TEXT NOT NULL
        )
    ''')
    
    # Create settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            startTime TEXT DEFAULT '08:00',
            endTime TEXT DEFAULT '22:00',
            workDays TEXT DEFAULT '1,2,3,4,5,6'
        )
    ''')
    
    # Insert default settings if not exists
    cursor.execute('SELECT COUNT(*) FROM settings')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO settings (startTime, endTime, workDays)
            VALUES ('08:00', '22:00', '1,2,3,4,5,6')
        ''')
    
    # Insert sample rooms if table is empty
    cursor.execute('SELECT COUNT(*) FROM rooms')
    if cursor.fetchone()[0] == 0:
        sample_rooms = [
            ('Sala A', 150.00, 30, 'Luz Natural, Ciclorama, Pé Direito Alto', 
             'https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2069&auto=format&fit=crop'),
            ('Sala B', 120.00, 25, 'Isolamento Acústico, Equipamento de Som', 
             'https://images.unsplash.com/photo-1497366811353-6870744d04b2?q=80&w=2069&auto=format&fit=crop'),
        ]
        
        cursor.executemany('''
            INSERT INTO rooms (name, price, size, features, image)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_rooms)
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully!")
    print(f"   - Tables created: rooms, bookings, blocked_slots, settings")
    print(f"   - Sample rooms added (if database was empty)")

if __name__ == '__main__':
    init_database()
