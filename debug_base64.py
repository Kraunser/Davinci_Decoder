"""
Debug do Base64 Decoder
"""
import sys
sys.path.insert(0, 'backend')
import base64

print("🔍 DEBUG DO BASE64 DECODER")
print("="*70)

# Teste direto com base64
ciphertext = "SGVsbG8gV29ybGQh"
print(f"\n1️⃣ Teste Python Base64 padrão:")
print(f"   Input: {ciphertext}")

try:
    decoded = base64.b64decode(ciphertext).decode('utf-8')
    print(f"   ✅ Output: {decoded}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste com o decoder
print(f"\n2️⃣ Teste com BaseDecoder:")

try:
    from decoders.encodings import Base64Decoder
    
    decoder = Base64Decoder()
    print(f"   Algoritmo: {decoder.get_algorithm_name()}")
    
    # Tentar decifrar
    result = decoder.decrypt(ciphertext, [])
    
    if result:
        print(f"   ✅ Plaintext: {result.plaintext}")
        print(f"   ✅ Confiança: {result.confidence}")
    else:
        print(f"   ❌ Retornou None")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback
    traceback.print_exc()

# Teste gerenciador
print(f"\n3️⃣ Teste com DecoderManager:")

try:
    from decoders import decoder_manager
    
    print(f"   Total algoritmos: {len(decoder_manager.decoders)}")
    
    # Procurar Base64 decoder
    base64_decoder = None
    for d in decoder_manager.decoders:
        if 'base64' in d.get_algorithm_name().lower():
            base64_decoder = d
            print(f"   Encontrado: {d.get_algorithm_name()}")
            break
    
    if base64_decoder:
        result = base64_decoder.decrypt(ciphertext, [])
        if result:
            print(f"   ✅ {result.plaintext}")
        else:
            print(f"   ❌ Retornou None")
    
except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
