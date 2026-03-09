"""
Teste direto do backend - sem API
"""
import sys
sys.path.insert(0, 'backend')

print("🧪 Testando backend diretamente...")

try:
    from decoders import decoder_manager
    
    # Teste 1: Base64
    print("\n1️⃣ Teste Base64:")
    ciphertext = "SGVsbG8gV29ybGQh"
    results = decoder_manager.decrypt_auto(ciphertext, [], max_decoders=3)
    
    if results:
        for r in results:
            print(f"   ✅ {r.algorithm}: {r.plaintext} ({r.confidence:.0f}%)")
    else:
        print("   ❌ Nenhum resultado")
    
    # Teste 2: Hex
    print("\n2️⃣ Teste Hexadecimal:")
    ciphertext = "48656c6c6f"
    results = decoder_manager.decrypt_auto(ciphertext, [], max_decoders=3)
    
    if results:
        for r in results:
            print(f"   ✅ {r.algorithm}: {r.plaintext} ({r.confidence:.0f}%)")
    else:
        print("   ❌ Nenhum resultado")
    
    # Teste 3: Listar todos algoritmos
    print(f"\n3️⃣ Total de algoritmos: {len(decoder_manager.decoders)}")
    
    print("\n✅ BACKEND ESTÁ FUNCIONANDO!")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
