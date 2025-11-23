import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_database_url():
    """Get database URL from environment or use default PostgreSQL"""
    return os.environ.get('DATABASE_URL', 'sqlite:///booking.db')

def init_database():
    """Initialize the database with all required tables"""
    
    database_url = get_database_url()
    
    # Check if using PostgreSQL or SQLite
    if database_url.startswith('postgresql://'):
        init_postgresql(database_url)
    else:
        init_sqlite()

def init_postgresql(database_url):
    """Initialize PostgreSQL database"""
    print(f"Initializing PostgreSQL database...")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Create rooms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id SERIAL PRIMARY KEY,
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
                id SERIAL PRIMARY KEY,
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
                id SERIAL PRIMARY KEY,
                roomId TEXT NOT NULL,
                date TEXT NOT NULL,
                startTime TEXT NOT NULL,
                endTime TEXT NOT NULL
            )
        ''')
        
        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id SERIAL PRIMARY KEY,
                startTime TEXT DEFAULT '08:00',
                endTime TEXT DEFAULT '22:00',
                workDays TEXT DEFAULT '1,2,3,4,5,6'
            )
        ''')
        
        # Create custom_pricing table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_pricing (
                id SERIAL PRIMARY KEY,
                roomId TEXT NOT NULL,
                startDate TEXT NOT NULL,
                endDate TEXT NOT NULL,
                priceModifier REAL NOT NULL,
                description TEXT
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
            
            for room in sample_rooms:
                cursor.execute('''
                    INSERT INTO rooms (name, price, size, features, image)
                    VALUES (%s, %s, %s, %s, %s)
                ''', room)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ PostgreSQL database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing PostgreSQL: {e}")
        raise

def init_sqlite():
    """Initialize SQLite database (fallback)"""
    import sqlite3
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'booking.db')
    print(f"Initializing SQLite database at: {db_path}")
    
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
    
    # Create custom_pricing table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_pricing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roomId TEXT NOT NULL,
            startDate TEXT NOT NULL,
            endDate TEXT NOT NULL,
            priceModifier REAL NOT NULL,
            description TEXT
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
    
    print("✅ SQLite database initialized successfully!")

if __name__ == '__main__':
    init_database()
