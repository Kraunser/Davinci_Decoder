"""
Teste específico AES-192-ECB com senha 'mana'
"""
import sys
sys.path.insert(0, 'backend')

ciphertext = "C0bK1HadIqsf2mt3gFvbeU-5NAYN1OIidqPAzors7zexrX6CFuqpLmZFkXQ7gs0zTGU1IM6uCacJYhyfLGvaYAw"
password = "mana"

print("="*70)
print("🧪 TESTE AES-192-ECB COM SENHA 'mana'")
print("="*70)

print(f"\n📝 Ciphertext: {ciphertext[:50]}...")
print(f"🔑 Senha: {password}")

# Teste 1: Decodificar Base64
print("\n1️⃣ Decodificando Base64:")
import base64
try:
    # Normalizar Base64 URL-safe
    normalized = ciphertext.replace('-', '+').replace('_', '/')
    while len(normalized) % 4 != 0:
        normalized += '='
    
    data = base64.b64decode(normalized)
    print(f"   ✅ Tamanho dos dados: {len(data)} bytes")
    print(f"   ✅ Hex: {data.hex()[:50]}...")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 2: Derivar chave de 192 bits (24 bytes)
print("\n2️⃣ Derivando chave AES-192:")
try:
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto.Hash import SHA256
    
    # Tentar várias derivações
    methods = [
        ("PBKDF2-SHA256-1000", lambda: PBKDF2(password, b'', dkLen=24, count=1000, hmac_hash_module=SHA256)),
        ("PBKDF2-SHA256-1", lambda: PBKDF2(password, b'', dkLen=24, count=1, hmac_hash_module=SHA256)),
        ("Password direto (24 bytes)", lambda: password.encode('utf-8').ljust(24, b'\x00')[:24]),
        ("SHA256 truncado", lambda: SHA256.new(password.encode('utf-8')).digest()[:24]),
    ]
    
    for name, key_func in methods:
        key = key_func()
        print(f"   • {name}: {key.hex()[:40]}...")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 3: Tentar decifrar com AES-192-ECB
print("\n3️⃣ Tentando decifrar AES-192-ECB:")
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    
    for name, key_func in methods:
        try:
            key = key_func()
            cipher = AES.new(key, AES.MODE_ECB)
            plaintext_bytes = unpad(cipher.decrypt(data), AES.block_size)
            plaintext = plaintext_bytes.decode('utf-8', errors='ignore')
            
            # Calcular confiança
            printable = sum(1 for c in plaintext if 32 <= ord(c) <= 126 or c in '\n\r\t')
            confidence = (printable / len(plaintext)) * 100 if plaintext else 0
            
            if confidence > 40:
                print(f"\n   ✅ SUCESSO com {name}!")
                print(f"   📄 Plaintext: {plaintext}")
                print(f"   📊 Confiança: {confidence:.1f}%")
                break
        except Exception as e:
            print(f"   ❌ {name}: {str(e)[:50]}")
    
except Exception as e:
    print(f"   ❌ Erro geral: {e}")

# Teste 4: Verificar se AES-192-ECB está nos decoders
print("\n4️⃣ Verificando decoders AES:")
try:
    from decoders import decoder_manager
    
    aes_decoders = [d for d in decoder_manager.decoders if 'aes' in d.get_algorithm_name().lower()]
    print(f"   Total de decoders AES: {len(aes_decoders)}")
    
    for d in aes_decoders:
        if '192' in d.get_algorithm_name():
            print(f"   ✅ {d.get_algorithm_name()}")
            
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "="*70)
