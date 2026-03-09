"""
Gerador de Teste para AES-192-CBC
Cria ciphertext válido + senha para testar o DaVinci Decoder
"""
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
import base64

# Mensagem e senha
plaintext = "Teste do DaVinci Decoder com AES-192!"
password = "minhaSenha123"

print("="*70)
print("TESTE AES-192-CBC - DaVinci Decoder".center(70))
print("="*70)

# Derivar chave de 24 bytes (AES-192)
key = PBKDF2(password, b'', dkLen=24, count=100)

# IV de 16 bytes
iv = b'1234567890123456'

# Cifrar
cipher = AES.new(key, AES.MODE_CBC, iv)
ciphertext_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))

# Combinar IV + ciphertext
full_ciphertext = iv + ciphertext_bytes
ciphertext_b64 = base64.b64encode(full_ciphertext).decode()

print(f"\n📝 PLAINTEXT:")
print(f"   {plaintext}")
print(f"\n🔑 SENHA (cole na Wordlist):")
print(f"   {password}")
print(f"\n🔒 CIPHERTEXT (cole no campo Ciphertext):")
print(f"   {ciphertext_b64}")
print(f"\n📊 INFORMAÇÕES:")
print(f"   Algoritmo: AES-192-CBC")
print(f"   Tamanho da chave: 24 bytes (192 bits)")
print(f"   IV: Primeiros 16 bytes do ciphertext")
print(f"   Derivação: PBKDF2 com 100 iterações")

print(f"\n📋 PASSOS PARA TESTAR:")
print(f"   1. Copie o CIPHERTEXT acima")
print(f"   2. Cole no campo 'Ciphertext' da interface")
print(f"   3. Cole '{password}' no campo 'Wordlist'")
print(f"   4. Clique em 'Auto-Detect & Decrypt'")

print(f"\n✅ RESULTADO ESPERADO:")
print(f"   Algoritmo: AES-192-CBC ou AES-192-ECB")
print(f"   Plaintext: {plaintext}")
print(f"   Confiança: 80-95%")
print(f"   Senha usada: {password}")

print("="*70)

# Salvar em arquivo para facilitar
with open('teste_aes192.txt', 'w', encoding='utf-8') as f:
    f.write(f"CIPHERTEXT:\n{ciphertext_b64}\n\n")
    f.write(f"SENHA:\n{password}\n\n")
    f.write(f"PLAINTEXT ESPERADO:\n{plaintext}\n")

print(f"\n💾 Dados salvos em: teste_aes192.txt")
print("="*70)
