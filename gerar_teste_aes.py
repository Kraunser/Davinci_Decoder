"""
Teste de AES - Gerador de Ciphertext
Cria um texto cifrado com AES para testar o sistema
"""
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
import base64

# Configuração
plaintext = "Esta é uma mensagem secreta cifrada com AES-256!"
password = "senha123"

# Derivar chave de 32 bytes (AES-256)
key = PBKDF2(password, b'', dkLen=32, count=100)

# Gerar IV (16 bytes)
iv = b'0123456789abcdef'  # IV fixo para teste

# Cifrar com AES-256-CBC
cipher = AES.new(key, AES.MODE_CBC, iv)
ciphertext_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))

# Combinar IV + ciphertext e codificar em Base64
full_ciphertext = iv + ciphertext_bytes
ciphertext_b64 = base64.b64encode(full_ciphertext).decode()

print("="*70)
print("TESTE DE AES-256-CBC".center(70))
print("="*70)
print(f"\n📝 Plaintext original:")
print(f"   {plaintext}")
print(f"\n🔑 Senha:")
print(f"   {password}")
print(f"\n🔒 Ciphertext (Base64):")
print(f"   {ciphertext_b64}")
print(f"\n📋 Para testar:")
print(f"   1. Cole o ciphertext acima no campo 'Ciphertext'")
print(f"   2. Cole '{password}' (sem aspas) no campo 'Wordlist'")
print(f"   3. Clique em 'Auto-Detect'")
print(f"\n✅ Resultado esperado:")
print(f"   Algoritmo: AES-256-CBC")
print(f"   Plaintext: {plaintext}")
print(f"   Confiança: >80%")
print("="*70)
