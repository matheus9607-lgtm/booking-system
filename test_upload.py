import requests

# URL do servidor backend
url = 'http://localhost:5000/api/upload'

# Caminho para uma imagem de teste (mude para uma imagem real no seu computador)
# Por exemplo: 'C:\\Users\\mathe\\Pictures\\test.jpg'
image_path = input("Cole o caminho completo de uma imagem para testar: ")

print(f"\nTestando upload de: {image_path}")
print("="*50)

try:
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✅ SUCESSO! Upload funcionou!")
        print(f"URL da imagem: {response.json()['url']}")
    else:
        print("\n❌ ERRO no upload")
        
except FileNotFoundError:
    print("\n❌ ERRO: Arquivo não encontrado. Verifique o caminho.")
except Exception as e:
    print(f"\n❌ ERRO: {e}")
