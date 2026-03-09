"""
Teste simples Base64
"""
import sys
sys.path.insert(0, 'backend')

print("🧪 TESTE SUPER SIMPLES")

try:
    # Import
    from decoders.encodings import Base64Decoder
    print("✅ Import OK")
    
    # Criar decoder
    decoder = Base64Decoder()
    print(f"✅ Decoder criado: {decoder.get_algorithm_name()}")
    
    # Testar decrypt
    ciphertext = "SGVsbG8gV29ybGQh"
    print(f"\n📝 Input: {ciphertext}")
    
    # Chamar com parâmetros padrão
    result = decoder.decrypt(ciphertext)
    
    if result:
        print(f"✅ Result: {result}")
    else:
        print("❌ Result: None")
        
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
