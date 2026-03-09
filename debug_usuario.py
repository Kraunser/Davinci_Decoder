"""
Teste EXATO com o ciphertext do usuário
"""
import sys
sys.path.insert(0, 'backend')

from decoders import decoder_manager

# Texto EXATO do usuário
ciphertext = "C0bK1HadIqsf2mt3gFvbeU-5NAYN1OIidqPAzors7zexrX6CFuqpLmZFkXQ7gs0zTGU1IM6uCacJYhyfLGvaYAw"
wordlist = ["mana"]

print("="*70)
print("🔍 TESTE DIRETO - BACKEND")
print("="*70)
print(f"\nCiphertext: {ciphertext[:50]}...")
print(f"Wordlist: {wordlist}")

# Teste com decrypt_auto
results = decoder_manager.decrypt_auto(
    ciphertext=ciphertext,
    wordlist=wordlist,
    max_decoders=10
)

print("\n" + "="*70)
print("📊 RESULTADOS FINAIS:")
print("="*70)

if results:
    print(f"\n✅ {len(results)} resultado(s) encontrado(s):\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. Algoritmo: {r.method}")
        print(f"   Plaintext: {r.plaintext[:100]}")
        print(f"   Confiança: {r.confidence:.1f}%")
        print(f"   Senha: '{r.password}'")
        print()
else:
    print("\n❌ NENHUM RESULTADO ENCONTRADO!")
    print("\nPossíveis problemas:")
    print("1. Algoritmo não detectado")
    print("2. Derivação de chave incompatível")
    print("3. Threshold de confiança muito alto")

print("="*70)
