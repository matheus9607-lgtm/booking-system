import requests
import json
from datetime import datetime

# API URL
API_URL = "http://localhost:5000/api"

# Criar uma reserva de teste
booking_data = {
    "room": "Sala A",
    "customerName": "João Teste",
    "customerPhone": "(11) 98765-4321",
    "date": "2025-01-15",
    "timeRange": "14:00 - 16:00",
    "total": 300.00,
    "createdAt": datetime.now().isoformat(),
    "slots": [
        {"date": "2025-01-15", "time": "14:00"},
        {"date": "2025-01-15", "time": "15:00"}
    ]
}

print("Criando reserva de teste...")
print("="*50)

try:
    response = requests.post(f"{API_URL}/bookings", json=booking_data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"SUCESSO! Reserva criada com ID: {result.get('id')}")
        print(f"\nDados da reserva:")
        print(f"- Cliente: {booking_data['customerName']}")
        print(f"- Telefone: {booking_data['customerPhone']}")
        print(f"- Data: {booking_data['date']}")
        print(f"- Horario: {booking_data['timeRange']}")
        print(f"- Total: R$ {booking_data['total']:.2f}")
        print(f"\nStatus inicial: PENDING (pendente)")
    else:
        print(f"ERRO ao criar reserva: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"ERRO: {e}")
