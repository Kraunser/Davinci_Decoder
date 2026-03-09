"""
DaVinci Decoder - Script de Treinamento ML
Gera dados de treinamento e treina o modelo de classificação
"""
import sys
sys.path.insert(0, 'backend')

from ml_engine import CipherMLEngine, ML_AVAILABLE
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
import base64
import hashlib
import random
import string

def generate_training_data(samples_per_class: int = 50):
    """
    Gera dados de treinamento sintéticos para cada tipo de cifra
    
    Args:
        samples_per_class: Número de exemplos por classe
    
    Returns:
        Lista de (ciphertext, label)
    """
    print(f"📝 Gerando {samples_per_class} exemplos por classe...")
    
    training_data = []
    
    # ========== ENCODINGS ==========
    
    # Base64
    for _ in range(samples_per_class):
        plaintext = generate_random_text(random.randint(10, 100))
        ciphertext = base64.b64encode(plaintext.encode()).decode()
        training_data.append((ciphertext, 'Base64'))
    
    # Hexadecimal
    for _ in range(samples_per_class):
        plaintext = generate_random_text(random.randint(10, 100))
        ciphertext = plaintext.encode().hex()
        training_data.append((ciphertext, 'Hexadecimal'))
    
    # Binary
    for _ in range(samples_per_class):
        plaintext = generate_random_text(random.randint(5, 20))
        ciphertext = ' '.join(format(ord(c), '08b') for c in plaintext)
        training_data.append((ciphertext, 'Binary'))
    
    # URL Encoding
    for _ in range(samples_per_class):
        plaintext = generate_random_text(random.randint(10, 50), with_spaces=True)
        ciphertext = plaintext.replace(' ', '%20').replace('!', '%21')
        training_data.append((ciphertext, 'URL'))
    
    # Morse
    morse_dict = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..'
    }
    for _ in range(samples_per_class):
        plaintext = generate_random_text(random.randint(5, 20), only_alpha=True).upper()
        ciphertext = ' '.join(morse_dict.get(c, '') for c in plaintext if c in morse_dict)
        training_data.append((ciphertext, 'Morse'))
    
    # ========== CIFRAS CLÁSSICAS ==========
    
    # Caesar
    for _ in range(samples_per_class):
        plaintext = generate_random_text(random.randint(20, 100), with_spaces=True)
        shift = random.randint(1, 25)
        ciphertext = caesar_cipher(plaintext, shift)
        training_data.append((ciphertext, 'Caesar'))
    
    # ROT13
    for _ in range(samples_per_class):
        plaintext = generate_random_text(random.randint(20, 100), with_spaces=True)
        ciphertext = caesar_cipher(plaintext, 13)
        training_data.append((ciphertext, 'ROT13'))
    
    # Atbash
    for _ in range(samples_per_class):
        plaintext = generate_random_text(random.randint(20, 100), only_alpha=True)
        ciphertext = atbash_cipher(plaintext)
        training_data.append((ciphertext, 'Atbash'))
    
    # Reverse
    for _ in range(samples_per_class):
        plaintext = generate_random_text(random.randint(20, 100), with_spaces=True)
        ciphertext = plaintext[::-1]
        training_data.append((ciphertext, 'Reverse'))
    
    # ========== CIFRAS MODERNAS ==========
    
    # AES (Base64-encoded)
    for _ in range(samples_per_class):
        plaintext = generate_random_text(random.randint(16, 64))
        password = generate_random_text(8)
        
        key = PBKDF2(password, b'', dkLen=32, count=100)
        iv = bytes([random.randint(0, 255) for _ in range(16)])
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        ciphertext = base64.b64encode(iv + ciphertext_bytes).decode()
        
        training_data.append((ciphertext, 'AES'))
    
    # ========== HASHES ==========
    
    # MD5
    for _ in range(samples_per_class):
        plaintext = generate_random_text(random.randint(5, 20))
        ciphertext = hashlib.md5(plaintext.encode()).hexdigest()
        training_data.append((ciphertext, 'MD5'))
    
    # SHA1
    for _ in range(samples_per_class):
        plaintext = generate_random_text(random.randint(5, 20))
        ciphertext = hashlib.sha1(plaintext.encode()).hexdigest()
        training_data.append((ciphertext, 'SHA1'))
    
    # SHA256
    for _ in range(samples_per_class):
        plaintext = generate_random_text(random.randint(5, 20))
        ciphertext = hashlib.sha256(plaintext.encode()).hexdigest()
        training_data.append((ciphertext, 'SHA256'))
    
    print(f"✅ Gerados {len(training_data)} exemplos de treinamento")
    
    # Shuffle
    random.shuffle(training_data)
    
    return training_data


def generate_random_text(length: int, only_alpha: bool = False, with_spaces: bool = False) -> str:
    """Gera texto aleatório"""
    if only_alpha:
        chars = string.ascii_letters
    elif with_spaces:
        chars = string.ascii_letters + ' '
    else:
        chars = string.ascii_letters + string.digits
    
    text = ''.join(random.choice(chars) for _ in range(length))
    
    # Adicionar espaços aleatórios se with_spaces
    if with_spaces and length > 10:
        words = []
        pos = 0
        while pos < len(text):
            word_len = random.randint(3, 8)
            words.append(text[pos:pos+word_len])
            pos += word_len
        text = ' '.join(words)
    
    return text


def caesar_cipher(text: str, shift: int) -> str:
    """Caesar cipher"""
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shifted = chr((ord(char) - base + shift) % 26 + base)
            result.append(shifted)
        else:
            result.append(char)
    return ''.join(result)


def atbash_cipher(text: str) -> str:
    """Atbash cipher"""
    result = []
    for char in text:
        if char.isalpha():
            if char.isupper():
                result.append(chr(ord('Z') - (ord(char) - ord('A'))))
            else:
                result.append(chr(ord('z') - (ord(char) - ord('a'))))
        else:
            result.append(char)
    return ''.join(result)


def main():
    print("="*70)
    print("🤖 DAVINCI DECODER - TREINAMENTO DE MACHINE LEARNING".center(70))
    print("="*70)
    
    if not ML_AVAILABLE:
        print("\n❌ scikit-learn não está instalado!")
        print("\nPara instalar:")
        print("  pip install scikit-learn")
        print("\nDepois execute este script novamente.")
        return
    
    print("\n📚 Este script vai:")
    print("  1. Gerar dados de treinamento sintéticos")
    print("  2. Extrair features de cada exemplo")
    print("  3. Treinar modelo Random Forest")
    print("  4. Avaliar acurácia")
    print("  5. Salvar modelo treinado")
    
    print("\n⏱️  Tempo estimado: 1-2 minutos")
    print("💻 Usando CPU (todos os cores)")
    
    input("\nPressione ENTER para começar o treinamento...")
    
    # Gerar dados
    print("\n" + "="*70)
    training_data = generate_training_data(samples_per_class=100)
    
    # Mostrar distribuição
    from collections import Counter
    labels = [label for _, label in training_data]
    distribution = Counter(labels)
    
    print(f"\n📊 Distribuição dos dados:")
    for label, count in sorted(distribution.items()):
        print(f"  • {label}: {count} exemplos")
    
    # Criar e treinar
    print("\n" + "="*70)
    engine = CipherMLEngine(model_path='backend/ml_model.pkl')
    engine.train(training_data, test_size=0.2)
    
    # Testar predições
    print("\n" + "="*70)
    print("🧪 TESTANDO PREDIÇÕES")
    print("="*70)
    
    test_cases = [
        ("SGVsbG8gV29ybGQh", "Base64"),
        ("48656c6c6f", "Hexadecimal"),
        ("Khoor Zruog", "Caesar"),
        ("5d41402abc4b2a76b9719d911017c592", "MD5"),
        (".... . .-.. .-.. ---", "Morse"),
    ]
    
    for ciphertext, expected in test_cases:
        predictions = engine.predict(ciphertext, top_n=3)
        
        print(f"\n📝 Ciphertext: {ciphertext}")
        print(f"   Esperado: {expected}")
        print(f"   Predições:")
        for i, (label, prob) in enumerate(predictions, 1):
            emoji = "✅" if label == expected else "  "
            print(f"   {emoji} {i}. {label}: {prob*100:.1f}%")
    
    print("\n" + "="*70)
    print("✅ TREINAMENTO COMPLETO!")
    print("="*70)
    print(f"\n💾 Modelo salvo em: backend/ml_model.pkl")
    print(f"📊 Pronto para classificar cifras automaticamente!")
    print(f"\n💡 Integre com decoder_manager.py para melhorar auto-detecção!")


if __name__ == '__main__':
    main()
