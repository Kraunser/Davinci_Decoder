"""
Teste simples e direto
"""
import sys
sys.path.insert(0, 'backend')

from decoders import decoder_manager

ciphertext = "C0bK1HadIqsf2mt3gFvbeU-5NAYN1OIidqPAzors7zexrX6CFuqpLmZFkXQ7gs0zTGU1IM6uCacJYhyfLGvaYAw"
wordlist = ["mana"]

print("TESTE DIRETO")
print("="*50)

results = decoder_manager.decrypt_auto(ciphertext, wordlist, max_decoders=10)

print("\nRESULTADOS:")
if results:
    for i, r in enumerate(results[:3], 1):
        algo = r.method if hasattr(r, 'method') else 'Unknown'
        conf = r.confidence if hasattr(r, 'confidence') else 0
        plain = r.plaintext[:50] if hasattr(r, 'plaintext') else ''
        print(f"{i}. {algo} ({conf:.0f}%)")
        print(f"   {plain}")
else:
    print("NENHUM")
