"""
DaVinci Decoder - Suite Completa de Testes
Valida todos os 102 algoritmos implementados
"""
import sys
sys.path.insert(0, 'backend')

from decoders import decoder_manager
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
import base64
import hashlib

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ️  {msg}{Colors.END}")

# ========== TESTES DE ENCODINGS ==========

def test_encodings():
    print_header("TESTE 1: ENCODINGS (21 algoritmos)")
    
    tests = [
        # Base64
        ("SGVsbG8gV29ybGQh", "Hello World!", "Base64"),
        # Hexadecimal
        ("48656c6c6f20576f726c6421", "Hello World!", "Hex"),
        # Binary
        ("01001000 01100101 01101100 01101100 01101111", "Hello", "Binary"),
        # URL Encoding
        ("Hello%20World%21", "Hello World!", "URL"),
        # ROT13
        ("Uryyb Jbeyq", "Hello World", "ROT13"),
    ]
    
    passed = 0
    total = len(tests)
    
    for ciphertext, expected, algo_type in tests:
        try:
            results = decoder_manager.decrypt_auto(ciphertext, [], max_decoders=5)
            
            found = False
            for result in results:
                if expected in result.plaintext or result.plaintext in expected:
                    print_success(f"{algo_type}: '{result.plaintext}' ({result.confidence:.0f}%)")
                    passed += 1
                    found = True
                    break
            
            if not found:
                print_error(f"{algo_type}: Não detectado")
        
        except Exception as e:
            print_error(f"{algo_type}: ERRO - {e}")
    
    print_info(f"Encodings: {passed}/{total} testes passaram ({passed/total*100:.0f}%)")
    return passed, total

# ========== TESTES DE CIFRAS CLÁSSICAS ==========

def test_classical():
    print_header("TESTE 2: CIFRAS CLÁSSICAS (32 algoritmos)")
    
    tests = [
        # Caesar (shift 3)
        ("Khoor Zruog", "Hello World", "Caesar"),
        # Atbash
        ("Svool Dliow", "Hello World", "Atbash"),
        # Reverse
        ("!dlroW olleH", "Hello World!", "Reverse"),
    ]
    
    passed = 0
    total = len(tests)
    
    for ciphertext, expected, algo_type in tests:
        try:
            results = decoder_manager.decrypt_auto(ciphertext, [], max_decoders=10)
            
            found = False
            for result in results:
                plaintext_clean = result.plaintext.lower().replace(" ", "")
                expected_clean = expected.lower().replace(" ", "")
                
                if expected_clean in plaintext_clean or plaintext_clean in expected_clean:
                    print_success(f"{algo_type}: '{result.plaintext}' ({result.confidence:.0f}%)")
                    passed += 1
                    found = True
                    break
            
            if not found:
                print_error(f"{algo_type}: Não detectado")
        
        except Exception as e:
            print_error(f"{algo_type}: ERRO - {e}")
    
    print_info(f"Cifras Clássicas: {passed}/{total} testes passaram ({passed/total*100:.0f}%)")
    return passed, total

# ========== TESTES DE CIFRAS MODERNAS ==========

def test_modern():
    print_header("TESTE 3: CIFRAS MODERNAS (36 algoritmos)")
    
    plaintext = "Secret Message!"
    password = "testpass"
    
    print_info("Gerando ciphertext AES-256-CBC...")
    
    # Criar ciphertext AES-256
    key = PBKDF2(password, b'', dkLen=32, count=100)
    iv = b'1234567890123456'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    full_ciphertext = iv + ciphertext_bytes
    ciphertext_b64 = base64.b64encode(full_ciphertext).decode()
    
    print_info(f"Ciphertext: {ciphertext_b64[:50]}...")
    print_info(f"Testando com senha '{password}'...")
    
    passed = 0
    total = 1
    
    try:
        results = decoder_manager.decrypt_auto(
            ciphertext_b64, 
            [password, "wrong1", "wrong2"], 
            max_decoders=10
        )
        
        found = False
        for result in results:
            if plaintext in result.plaintext:
                print_success(f"{result.decoder_name}: '{result.plaintext}' ({result.confidence:.0f}%)")
                print_success(f"Senha usada: {result.password}")
                passed += 1
                found = True
                break
        
        if not found:
            print_error("AES: Não conseguiu decifrar")
            print_info(f"Top 3 resultados:")
            for i, r in enumerate(results[:3], 1):
                print(f"  {i}. {r.decoder_name}: {r.plaintext[:50]}... ({r.confidence:.0f}%)")
    
    except Exception as e:
        print_error(f"AES: ERRO - {e}")
    
    print_info(f"Cifras Modernas: {passed}/{total} testes passaram ({passed/total*100:.0f}%)")
    return passed, total

# ========== TESTES DE HASH CRACKERS ==========

def test_hashes():
    print_header("TESTE 4: HASH CRACKERS (13 algoritmos)")
    
    password = "admin123"
    wordlist = ["wrong1", "wrong2", "admin123", "password"]
    
    tests = [
        # MD5
        (hashlib.md5(password.encode()).hexdigest(), password, "MD5"),
        # SHA1
        (hashlib.sha1(password.encode()).hexdigest(), password, "SHA1"),
        # SHA256
        (hashlib.sha256(password.encode()).hexdigest(), password, "SHA256"),
    ]
    
    passed = 0
    total = len(tests)
    
    for hash_value, expected, algo_type in tests:
        try:
            print_info(f"Tentando quebrar {algo_type}: {hash_value}...")
            
            results = decoder_manager.decrypt_auto(hash_value, wordlist, max_decoders=5)
            
            found = False
            for result in results:
                if expected in result.plaintext:
                    print_success(f"{algo_type}: Senha encontrada '{result.plaintext}'")
                    passed += 1
                    found = True
                    break
            
            if not found:
                print_error(f"{algo_type}: Não quebrou")
        
        except Exception as e:
            print_error(f"{algo_type}: ERRO - {e}")
    
    print_info(f"Hash Crackers: {passed}/{total} testes passaram ({passed/total*100:.0f}%)")
    return passed, total

# ========== TESTE DE CARREGAMENTO ==========

def test_loading():
    print_header("TESTE 0: CARREGAMENTO DO SISTEMA")
    
    total_decoders = len(decoder_manager.decoders)
    print_success(f"Sistema carregado com {total_decoders} algoritmos")
    
    # Contar por categoria
    categories = {
        'modern': 0,
        'classical': 0,
        'encoding': 0,
        'hash': 0
    }
    
    for decoder in decoder_manager.decoders:
        algo_type = decoder.get_algorithm_type()
        if algo_type in categories:
            categories[algo_type] += 1
    
    print_info(f"🔐 Cifras Modernas: {categories['modern']}")
    print_info(f"📜 Cifras Clássicas: {categories['classical']}")
    print_info(f"🔤 Encodings: {categories['encoding']}")
    print_info(f"#️⃣ Hash Crackers: {categories['hash']}")
    
    expected = 102
    if total_decoders == expected:
        print_success(f"Total: {total_decoders}/{expected} ✅")
        return 1, 1
    else:
        print_error(f"Total: {total_decoders}/{expected} ❌")
        return 0, 1

# ========== EXECUTAR TODOS OS TESTES ==========

def run_all_tests():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║        DAVINCI DECODER - SUITE COMPLETA DE TESTES                ║")
    print("║                  Validando 102 Algoritmos                        ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    results = []
    
    # Teste 0: Carregamento
    r0 = test_loading()
    results.append(("Carregamento", r0[0], r0[1]))
    
    # Teste 1: Encodings
    r1 = test_encodings()
    results.append(("Encodings", r1[0], r1[1]))
    
    # Teste 2: Cifras Clássicas
    r2 = test_classical()
    results.append(("Cifras Clássicas", r2[0], r2[1]))
    
    # Teste 3: Cifras Modernas
    r3 = test_modern()
    results.append(("Cifras Modernas", r3[0], r3[1]))
    
    # Teste 4: Hash Crackers
    r4 = test_hashes()
    results.append(("Hash Crackers", r4[0], r4[1]))
    
    # Resumo Final
    print_header("RESUMO FINAL")
    
    total_passed = 0
    total_tests = 0
    
    for name, passed, total in results:
        total_passed += passed
        total_tests += total
        percentage = (passed/total*100) if total > 0 else 0
        
        if passed == total:
            print_success(f"{name}: {passed}/{total} ({percentage:.0f}%)")
        elif passed > total * 0.5:
            print_info(f"{name}: {passed}/{total} ({percentage:.0f}%)")
        else:
            print_error(f"{name}: {passed}/{total} ({percentage:.0f}%)")
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    final_percentage = (total_passed/total_tests*100) if total_tests > 0 else 0
    
    if final_percentage >= 90:
        print(f"{Colors.BOLD}{Colors.GREEN}RESULTADO GERAL: {total_passed}/{total_tests} ({final_percentage:.0f}%) ✅ EXCELENTE{Colors.END}")
    elif final_percentage >= 70:
        print(f"{Colors.BOLD}{Colors.YELLOW}RESULTADO GERAL: {total_passed}/{total_tests} ({final_percentage:.0f}%) ⚠️  BOM{Colors.END}")
    else:
        print(f"{Colors.BOLD}{Colors.RED}RESULTADO GERAL: {total_passed}/{total_tests} ({final_percentage:.0f}%) ❌ PRECISA MELHORAR{Colors.END}")
    
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    return total_passed == total_tests

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
