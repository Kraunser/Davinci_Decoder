import sys
import os

# Adiciona o diretório atual ao path para importações funcionarem
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.decoders.decoder_manager import DecoderManager

def run_test():
    dm = DecoderManager()
    
    # 1. Testar ROT13
    print("\n--- Testando ROT13 ---")
    ciphertext = "Uryyb Jbeyq"  # "Hello World"
    print(f"Ciphertext: {ciphertext}")
    
    results = dm.decrypt_auto(
        ciphertext, 
        wordlist=['test'],
        max_decoders=5
    )
    
    for r in results:
        print(f"[{r.decoder_name}] -> {r.plaintext} ({r.confidence:.1f}%)")
        
    # 2. Testar Caesar 
    print("\n--- Testando Caesar (shift 5) ---")
    # Hello World + 5 = Mjqqt Btwqi
    ciphertext = "Mjqqt Btwqi"
    print(f"Ciphertext: {ciphertext}")
    
    results = dm.decrypt_auto(
        ciphertext, 
        wordlist=['test'],
        max_decoders=5
    )
    
    for r in results:
        print(f"[{r.decoder_name}] -> {r.plaintext} ({r.confidence:.1f}%)")

if __name__ == '__main__':
    run_test()
