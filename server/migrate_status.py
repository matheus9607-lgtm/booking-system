import sqlite3

# Script to add status column to existing bookings
conn = sqlite3.connect('booking.db')
cursor = conn.cursor()

try:
    # Try to add the status column
    cursor.execute('ALTER TABLE bookings ADD COLUMN status TEXT DEFAULT "pending"')
    print("Status column added successfully!")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Status column already exists!")
    else:
        print(f"Error: {e}")

# Update all existing bookings to 'pending' status
cursor.execute('UPDATE bookings SET status = "pending" WHERE status IS NULL')
conn.commit()

print(f"Updated {cursor.rowcount} bookings to pending status")

conn.close()
print("\nDatabase migration completed!")
