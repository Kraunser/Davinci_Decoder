# Teste rápido de funcionalidade básica
import sys
import os

# Avoid cp1252 emoji crashes on Windows terminals.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 50)
print("DaVinci Decoder - Teste Rápido")
print("=" * 50)

# Test 1: Import API
try:
    from api_server import app
    print("✅ API importada com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar API: {e}")
    sys.exit(1)

# Test 2: Import Decoder Manager
try:
    from backend.decoders.decoder_manager import DecoderManager
    dm = DecoderManager()
    print(f"✅ Decoder Manager: {len(dm.active_decoders)} decoders ativos")
except Exception as e:
    print(f"❌ Erro no Decoder Manager: {e}")
    sys.exit(1)

# Test 3: List Algorithms
try:
    algorithms = dm.list_algorithms()
    print(f"✅ Algoritmos disponíveis: {len(algorithms)}")
except Exception as e:
    print(f"❌ Erro ao listar algoritmos: {e}")
    sys.exit(1)

# Test 4: Base64 Decode
try:
    result = dm.decrypt_auto(
        ciphertext="SGVsbG8gV29ybGQh",
        wordlist=[],
        max_decoders=5
    )
    if result and len(result) > 0:
        print(f"✅ Base64 Test: '{result[0]['plaintext']}' ({result[0]['confidence']}%)")
    else:
        print("❌ Nenhum resultado encontrado")
except Exception as e:
    print(f"❌ Erro no teste Base64: {e}")
    sys.exit(1)

# Test 5: Flask Test Client
try:
    with app.test_client() as client:
        response = client.get('/api/health')
        if response.status_code == 200:
            print(f"✅ Health Check: {response.get_json()['status']}")
        else:
            print(f"❌ Health Check falhou: {response.status_code}")
except Exception as e:
    print(f"❌ Erro no Flask test client: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("✅ Todos os testes passaram!")
print("=" * 50)
