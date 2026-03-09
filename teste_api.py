"""
Teste direto da API
"""
import requests
import json

print("🧪 TESTE DA API")
print("="*70)

url = "http://localhost:5000/api/auto-detect"

data = {
    "ciphertext": "SGVsbG8gV29ybGQh",
    "wordlist": [],
    "max_results": 5
}

print(f"\n📤 Enviando POST para {url}")
print(f"📝 Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data, timeout=10)
    
    print(f"\n📥 Status: {response.status_code}")
    print(f"📄 Response:")
    print(json.dumps(response.json(), indent=2))
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
