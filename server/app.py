import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import werkzeug.utils

# Initialize database on startup
from init_db import init_database
init_database()

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('booking.db')
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# --- Routes ---

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = werkzeug.utils.secure_filename(file.filename)
        # Add timestamp to prevent duplicates
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Return the URL relative to the server root
        file_url = f'/static/uploads/{filename}'
        return jsonify({'url': file_url}), 200
    return jsonify({'error': 'File type not allowed'}), 400

# 1. Rooms
@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    rooms = query_db('SELECT * FROM rooms')
    rooms_list = []
    for room in rooms:
        rooms_list.append({
            'id': room['id'],
            'name': room['name'],
            'price': room['price'],
            'size': room['size'],
            'features': room['features'].split(',') if room['features'] else [],
            'image': room['image']
        })
    return jsonify(rooms_list)

@app.route('/api/rooms', methods=['POST'])
def add_room():
    data = request.json
    features_str = ','.join(data.get('features', []))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO rooms (name, price, size, features, image) VALUES (?, ?, ?, ?, ?)',
                (data['name'], data['price'], data['size'], features_str, data['image']))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    
    return jsonify({'id': new_id, 'message': 'Room created'}), 201

@app.route('/api/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    data = request.json
    features_str = ','.join(data.get('features', []))
    
    conn = get_db_connection()
    conn.execute('UPDATE rooms SET name=?, price=?, size=?, features=?, image=? WHERE id=?',
                 (data['name'], data['price'], data['size'], features_str, data['image'], room_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Room updated'})

@app.route('/api/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM rooms WHERE id = ?', (room_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Room deleted'})

# 2. Bookings
@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    bookings = query_db('SELECT * FROM bookings')
    bookings_list = []
    for b in bookings:
        bookings_list.append({
            'id': b['id'],
            'room': b['room_name'],
            'customerName': b['customer_name'],
            'customerPhone': b['customer_phone'],
            'date': b['date'],
            'timeRange': b['time_range'],
            'total': b['total'],
            'createdAt': b['created_at'],
            'slots': json.loads(b['slots_json']),
            'status': b['status'] if 'status' in b.keys() else 'pending'
        })
    return jsonify(bookings_list)

@app.route('/api/bookings', methods=['POST'])
def add_booking():
    data = request.json
    slots_json = json.dumps(data['slots'])
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO bookings (room_name, customer_name, customer_phone, date, time_range, total, created_at, slots_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['room'], data['customerName'], data['customerPhone'], data['date'], data['timeRange'], data['total'], data['createdAt'], slots_json))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    
    return jsonify({'id': new_id, 'message': 'Booking created'}), 201

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Booking deleted'})

# 3. Blocked Slots
@app.route('/api/blocked-slots', methods=['GET'])
def get_blocked_slots():
    slots = query_db('SELECT * FROM blocked_slots')
    # Group by room_id to match frontend structure: { roomId: [slots] }
    blocked_map = {}
    for slot in slots:
        rid = str(slot['room_id'])
        if rid not in blocked_map:
            blocked_map[rid] = []
        blocked_map[rid].append({
            'id': slot['id'],
            'date': slot['date'],
            'startTime': slot['start_time'],
            'endTime': slot['end_time']
        })
    return jsonify(blocked_map)

@app.route('/api/blocked-slots', methods=['POST'])
def add_blocked_slot():
    data = request.json
    room_id = data['roomId']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO blocked_slots (room_id, date, start_time, end_time) VALUES (?, ?, ?, ?)',
                (room_id, data['date'], data['startTime'], data['endTime']))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Slot blocked'}), 201

@app.route('/api/blocked-slots/<int:room_id>/<int:slot_index>', methods=['DELETE'])
def delete_blocked_slot(room_id, slot_index):
    # This is tricky because frontend sends index, but DB has IDs.
    # We need to fetch all slots for the room and delete the one at the index.
    # OR, better: update frontend to use IDs.
    # For now, let's try to find it by index.
    
    # Actually, let's just accept that we might need to change frontend logic to send ID.
    # But to keep changes minimal, let's fetch all for room, find the one at index, and delete it.
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM blocked_slots WHERE room_id = ?', (room_id,))
    rows = cur.fetchall()
    
    if 0 <= slot_index < len(rows):
        slot_db_id = rows[slot_index]['id']
        cur.execute('DELETE FROM blocked_slots WHERE id = ?', (slot_db_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Slot unblocked'})
    
    conn.close()
    return jsonify({'error': 'Slot not found'}), 404

# 4. Settings
@app.route('/api/settings', methods=['GET'])
def get_settings():
    rows = query_db('SELECT * FROM settings')
    settings = {}
    for row in rows:
        val = row['value']
        # Try to parse JSON if it looks like an array/object
        try:
            val = json.loads(val)
        except:
            pass
        settings[row['key']] = val
    return jsonify(settings)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json
    conn = get_db_connection()
    
    for key, value in data.items():
        val_str = json.dumps(value) if isinstance(value, (list, dict)) else str(value)
        # Upsert
        conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, val_str))
        
    conn.commit()
    conn.close()
    return jsonify({'message': 'Settings updated'})

# Booking Approval
@app.route('/api/bookings/<int:booking_id>/approve', methods=['PUT'])
def approve_booking(booking_id):
    conn = get_db_connection()
    conn.execute('UPDATE bookings SET status = ? WHERE id = ?', ('approved', booking_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Booking approved'})

@app.route('/api/bookings/<int:booking_id>/reject', methods=['PUT'])
def reject_booking(booking_id):
    conn = get_db_connection()
    conn.execute('UPDATE bookings SET status = ? WHERE id = ?', ('rejected', booking_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Booking rejected'})

# Settings endpoint
@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        conn = get_db_connection()
        settings = conn.execute('SELECT * FROM settings LIMIT 1').fetchone()
        conn.close()
        
        if settings:
            return jsonify({
                'startTime': settings['startTime'],
                'endTime': settings['endTime'],
                'workDays': settings['workDays']
            })
        else:
            # Return defaults if no settings found
            return jsonify({
                'startTime': '08:00',
                'endTime': '22:00',
                'workDays': '1,2,3,4,5,6'
            })
    
    elif request.method == 'POST':
        data = request.json
        conn = get_db_connection()
        
        # Convert workDays array to comma-separated string
        work_days = ','.join(map(str, data.get('workDays', [])))
        
        # Check if settings exist
        existing = conn.execute('SELECT COUNT(*) FROM settings').fetchone()[0]
        
        if existing > 0:
            # Update existing settings
            conn.execute('''
                UPDATE settings 
                SET startTime = ?, endTime = ?, workDays = ?
                WHERE id = 1
            ''', (data.get('startTime'), data.get('endTime'), work_days))
        else:
            # Insert new settings
            conn.execute('''
                INSERT INTO settings (startTime, endTime, workDays)
                VALUES (?, ?, ?)
            ''', (data.get('startTime'), data.get('endTime'), work_days))
        
        conn.commit()
        conn.close()
        return jsonify({'message': 'Settings updated successfully'})


if __name__ == '__main__':
    # Porta configurável para produção (Render, Railway, etc)
    port = int(os.environ.get('PORT', 5000))
    # Debug desligado em produção
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
