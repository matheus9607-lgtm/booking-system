import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def test_api():
    print("Testing API...")
    
    # 1. Get Rooms (should be empty initially)
    try:
        res = requests.get(f'{BASE_URL}/rooms')
        print(f"GET /rooms: {res.status_code}")
        print(res.json())
    except Exception as e:
        print(f"Error connecting: {e}")
        return

    # 2. Add a Room
    new_room = {
        "name": "Test Room",
        "price": 100.0,
        "size": 50,
        "features": ["Wifi", "AC"],
        "image": "http://example.com/img.jpg"
    }
    res = requests.post(f'{BASE_URL}/rooms', json=new_room)
    print(f"POST /rooms: {res.status_code}")
    print(res.json())

    # 3. Get Rooms again
    res = requests.get(f'{BASE_URL}/rooms')
    print(f"GET /rooms: {res.status_code}")
    print(res.json())

if __name__ == '__main__':
    test_api()
