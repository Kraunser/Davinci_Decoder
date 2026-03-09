"""
Teste direto: decrypt_auto com AES
"""
import sys
sys.path.insert(0, 'backend')

from decoders import decoder_manager

ciphertext = "C0bK1HadIqsf2mt3gFvbeU-5NAYN1OIidqPAzors7zexrX6CFuqpLmZFkXQ7gs0zTGU1IM6uCacJYhyfLGvaYAw"
wordlist = ["mana"]

print("="*70)
print("🤖 AUTO-DETECT COM WORDLIST")
print("="*70)

results = decoder_manager.decrypt_auto(
    ciphertext=ciphertext,
    wordlist=wordlist,
    max_decoders=10  # Testar mais algoritmos
)

print("\n" + "="*70)
print("📊 RESULTADOS:")
print("="*70)

if results:
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r.method}")
        print(f"   Plaintext: {r.plaintext[:100]}")
        print(f"   Confidence: {r.confidence:.1f}%")
        print(f"   Password: {r.password}")
else:
    print("\n❌ Nenhum resultado encontrado")

print("\n" + "="*70)
