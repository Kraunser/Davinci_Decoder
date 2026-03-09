"""
GERADOR DE TESTE AES - VOCÊ CRIA SUA PRÓPRIA CIFRA!

Use este script para criar seus próprios textos cifrados AES
com senhas que VOCÊ escolhe. Depois teste no DaVinci Decoder.
"""
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
import base64

print("="*70)
print("🔐 GERADOR DE TESTE AES - FAÇA SEU PRÓPRIO TESTE!")
print("="*70)

# PERSONALIZE AQUI:
# ==================
plaintext = input("\n📝 Digite o texto que você quer cifrar: ").strip()
password = input("🔑 Digite a senha que você quer usar: ").strip()

# Escolha o algoritmo
print("\n📋 Escolha o algoritmo:")
print("   1. AES-128-ECB")
print("   2. AES-192-ECB")
print("   3. AES-256-ECB")
print("   4. AES-128-CBC")
print("   5. AES-192-CBC")
print("   6. AES-256-CBC")

choice = input("\nEscolha (1-6): ").strip()

# Mapeamento
algorithms = {
    '1': ('AES-128-ECB', 16, AES.MODE_ECB),
    '2': ('AES-192-ECB', 24, AES.MODE_ECB),
    '3': ('AES-256-ECB', 32, AES.MODE_ECB),
    '4': ('AES-128-CBC', 16, AES.MODE_CBC),
    '5': ('AES-192-CBC', 24, AES.MODE_CBC),
    '6': ('AES-256-CBC', 32, AES.MODE_CBC),
}

if choice not in algorithms:
    print("❌ Escolha inválida!")
    exit(1)

algo_name, key_len, mode = algorithms[choice]

print(f"\n🔧 Cifrando com {algo_name}...")

# Derivar chave
# Testando múltiplos métodos de derivação
methods = {
    'PBKDF2-1000': PBKDF2(password.encode(), b'', dkLen=key_len, count=1000, hmac_hash_module=SHA256),
    'PBKDF2-1': PBKDF2(password.encode(), b'', dkLen=key_len, count=1, hmac_hash_module=SHA256),
    'SHA256-truncated': SHA256.new(password.encode()).digest()[:key_len],
    'Password-padded': password.encode().ljust(key_len, b'\x00')[:key_len],
}

print(f"\n📊 Testando {len(methods)} métodos de derivação de chave:")

for method_name, key in methods.items():
    try:
        # Cifrar
        if mode == AES.MODE_CBC:
            iv = b'\x00' * 16  # IV zeros para simplicidade
            cipher = AES.new(key, mode, iv)
        else:
            cipher = AES.new(key, mode)
        
        ciphertext_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        ciphertext_b64 = base64.b64encode(ciphertext_bytes).decode('utf-8')
        
        print(f"\n✅ {method_name}:")
        print(f"   Ciphertext: {ciphertext_b64}")
        print(f"\n   🧪 TESTE NO DAVINCI DECODER:")
        print(f"   1. Cole o ciphertext acima")
        print(f"   2. Wordlist: {password}")
        print(f"   3. Clique Auto-Detect")
        print(f"   4. Deve decifrar: {plaintext}")
        
    except Exception as e:
        print(f"❌ {method_name}: Erro - {e}")

print("\n" + "="*70)
print("💡 INSTRUÇÕES:")
print("="*70)
print("""
1. Copie UM dos ciphertexts acima
2. Abra http://localhost:5000
3. Cole o ciphertext
4. Adicione a senha no Wordlist
5. Clique "Auto-Detect & Decrypt"
6. DEVE encontrar seu texto original!

Isso prova que o sistema é genérico e funciona com
QUALQUER texto e QUALQUER senha! 🎯
""")
print("="*70)
