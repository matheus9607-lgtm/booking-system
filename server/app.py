import os
import json
from datetime import datetime
import werkzeug.utils
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

# Initialize database structure on startup
from init_db import init_database
try:
    init_database()
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")

app = Flask(__name__, static_folder='static')

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://marcos-lima-booking.vercel.app",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://192.168.100.10:8000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Database Configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///booking.db')
USE_POSTGRES = DATABASE_URL.startswith('postgresql://')

def get_db_connection():
    """Get database connection based on environment"""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        conn = sqlite3.connect('booking.db')
        conn.row_factory = sqlite3.Row
        return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- ROUTES ---

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = werkzeug.utils.secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_url = f'/static/uploads/{filename}'
        return jsonify({'url': file_url}), 200
    return jsonify({'error': 'File type not allowed'}), 400

# 1. Rooms
@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM rooms')
    rooms = cursor.fetchall()
    conn.close()
    
    rooms_list = []
    for room in rooms:
        # Handle dict (Postgres) vs Row (SQLite)
        r = dict(room)
        rooms_list.append({
            'id': r['id'],
            'name': r['name'],
            'price': r['price'],
            'size': r['size'],
            'features': r['features'].split(',') if r['features'] else [],
            'image': r['image']
        })
    return jsonify(rooms_list)

@app.route('/api/rooms', methods=['POST'])
def add_room():
    data = request.json
    features_str = ','.join(data.get('features', []))
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        cursor.execute(
            'INSERT INTO rooms (name, price, size, features, image) VALUES (%s, %s, %s, %s, %s) RETURNING id',
            (data['name'], data['price'], data['size'], features_str, data['image'])
        )
        new_id = cursor.fetchone()['id']
    else:
        cursor.execute(
            'INSERT INTO rooms (name, price, size, features, image) VALUES (?, ?, ?, ?, ?)',
            (data['name'], data['price'], data['size'], features_str, data['image'])
        )
        new_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return jsonify({'id': new_id, 'message': 'Room created'}), 201

@app.route('/api/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    data = request.json
    features_str = ','.join(data.get('features', []))
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'UPDATE rooms SET name=%s, price=%s, size=%s, features=%s, image=%s WHERE id=%s' if USE_POSTGRES else \
            'UPDATE rooms SET name=?, price=?, size=?, features=?, image=? WHERE id=?'
            
    cursor.execute(query, (data['name'], data['price'], data['size'], features_str, data['image'], room_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Room updated'})

@app.route('/api/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'DELETE FROM rooms WHERE id = %s' if USE_POSTGRES else 'DELETE FROM rooms WHERE id = ?'
    cursor.execute(query, (room_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Room deleted'})

# 2. Bookings
@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings')
    bookings = cursor.fetchall()
    conn.close()
    
    bookings_list = []
    for b in bookings:
        b = dict(b)
        bookings_list.append({
            'id': b['id'],
            'room': b['room'] if 'room' in b else b.get('room_name', 'Unknown'), # Handle potential column name diffs
            'customerName': b['customerName'] if 'customerName' in b else b.get('customer_name', ''),
            'customerPhone': b['customerPhone'] if 'customerPhone' in b else b.get('customer_phone', ''),
            'date': b['date'],
            'timeRange': b['timeRange'] if 'timeRange' in b else b.get('time_range', ''),
            'total': b['total'],
            'createdAt': b['createdAt'] if 'createdAt' in b else b.get('created_at', ''),
            'slots': json.loads(b['slots']) if 'slots' in b else json.loads(b.get('slots_json', '[]')),
            'status': b.get('status', 'pending')
        })
    return jsonify(bookings_list)

@app.route('/api/bookings', methods=['POST'])
def add_booking():
    data = request.json
    slots_json = json.dumps(data['slots'])
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        cursor.execute('''
            INSERT INTO bookings (room, customerName, customerPhone, date, timeRange, total, createdAt, slots, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        ''', (data['room'], data['customerName'], data['customerPhone'], data['date'], data['timeRange'], data['total'], data['createdAt'], slots_json, 'pending'))
        new_id = cursor.fetchone()['id']
    else:
        cursor.execute('''
            INSERT INTO bookings (room, customerName, customerPhone, date, timeRange, total, createdAt, slots, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['room'], data['customerName'], data['customerPhone'], data['date'], data['timeRange'], data['total'], data['createdAt'], slots_json, 'pending'))
        new_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return jsonify({'id': new_id, 'message': 'Booking created'}), 201

@app.route('/api/bookings/<int:booking_id>/approve', methods=['PUT'])
def approve_booking(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'UPDATE bookings SET status = %s WHERE id = %s' if USE_POSTGRES else 'UPDATE bookings SET status = ? WHERE id = ?'
    cursor.execute(query, ('approved', booking_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Booking approved'})

@app.route('/api/bookings/<int:booking_id>/reject', methods=['PUT'])
def reject_booking(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'UPDATE bookings SET status = %s WHERE id = %s' if USE_POSTGRES else 'UPDATE bookings SET status = ? WHERE id = ?'
    cursor.execute(query, ('rejected', booking_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Booking rejected'})

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'DELETE FROM bookings WHERE id = %s' if USE_POSTGRES else 'DELETE FROM bookings WHERE id = ?'
    cursor.execute(query, (booking_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Booking deleted'})

# 3. Blocked Slots
@app.route('/api/blocked-slots', methods=['GET'])
def get_blocked_slots():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blocked_slots')
    slots = cursor.fetchall()
    conn.close()
    
    blocked_map = {}
    for slot in slots:
        s = dict(slot)
        rid = str(s['roomId'] if 'roomId' in s else s.get('room_id'))
        if rid not in blocked_map:
            blocked_map[rid] = []
        blocked_map[rid].append({
            'id': s['id'],
            'date': s['date'],
            'startTime': s['startTime'] if 'startTime' in s else s.get('start_time'),
            'endTime': s['endTime'] if 'endTime' in s else s.get('end_time')
        })
    return jsonify(blocked_map)

@app.route('/api/blocked-slots', methods=['POST'])
def add_blocked_slot():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        cursor.execute(
            'INSERT INTO blocked_slots (roomId, date, startTime, endTime) VALUES (%s, %s, %s, %s)',
            (data['roomId'], data['date'], data['startTime'], data['endTime'])
        )
    else:
        cursor.execute(
            'INSERT INTO blocked_slots (roomId, date, startTime, endTime) VALUES (?, ?, ?, ?)',
            (data['roomId'], data['date'], data['startTime'], data['endTime'])
        )
        
    conn.commit()
    conn.close()
    return jsonify({'message': 'Slot blocked'}), 201

@app.route('/api/blocked-slots/<int:room_id>/<int:slot_index>', methods=['DELETE'])
def delete_blocked_slot(room_id, slot_index):
    # Logic to find slot by index (temporary fix for frontend logic)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT id FROM blocked_slots WHERE roomId = %s' if USE_POSTGRES else 'SELECT id FROM blocked_slots WHERE roomId = ?'
    cursor.execute(query, (str(room_id),))
    rows = cursor.fetchall()
    
    if 0 <= slot_index < len(rows):
        slot_db_id = rows[slot_index]['id'] if USE_POSTGRES else rows[slot_index][0] # Postgres dict vs SQLite row/tuple
        if USE_POSTGRES:
             slot_db_id = rows[slot_index]['id']
        else:
             slot_db_id = rows[slot_index]['id']
             
        del_query = 'DELETE FROM blocked_slots WHERE id = %s' if USE_POSTGRES else 'DELETE FROM blocked_slots WHERE id = ?'
        cursor.execute(del_query, (slot_db_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Slot unblocked'})
    
    conn.close()
    return jsonify({'error': 'Slot not found'}), 404

# 4. Settings
@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'GET':
            cursor.execute('SELECT * FROM settings LIMIT 1')
            settings = cursor.fetchone()
            conn.close()
            
            if settings:
                s = dict(settings)
                return jsonify({
                    'startTime': s['startTime'],
                    'endTime': s['endTime'],
                    'workDays': s['workDays']
                })
            else:
                return jsonify({
                    'startTime': '08:00',
                    'endTime': '22:00',
                    'workDays': '1,2,3,4,5,6'
                })
        
        elif request.method == 'POST':
            data = request.json
            work_days = ','.join(map(str, data.get('workDays', [])))
            
            cursor.execute('SELECT COUNT(*) FROM settings')
            count_result = cursor.fetchone()
            # Postgres returns dict, SQLite returns Row/tuple
            count = count_result['count'] if USE_POSTGRES else count_result[0]
            
            if count > 0:
                query = 'UPDATE settings SET startTime=%s, endTime=%s, workDays=%s WHERE id=1' if USE_POSTGRES else \
                        'UPDATE settings SET startTime=?, endTime=?, workDays=? WHERE id=1'
                cursor.execute(query, (data.get('startTime'), data.get('endTime'), work_days))
            else:
                query = 'INSERT INTO settings (startTime, endTime, workDays) VALUES (%s, %s, %s)' if USE_POSTGRES else \
                        'INSERT INTO settings (startTime, endTime, workDays) VALUES (?, ?, ?)'
                cursor.execute(query, (data.get('startTime'), data.get('endTime'), work_days))
            
            conn.commit()
            conn.close()
            return jsonify({'message': 'Settings updated successfully'})
            
    except Exception as e:
        print(f"Error in settings: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
