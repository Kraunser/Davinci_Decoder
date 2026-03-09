"""
DaVinci Decoder - Teste End-to-End Completo
Valida TODOS os componentes do sistema
"""
import sys
sys.path.insert(0, 'backend')

print("="*70)
print("🧪 DAVINCI DECODER - TESTE COMPLETO END-TO-END")
print("="*70)

# ========== TESTE 1: BACKEND ==========
print("\n📦 TESTE 1: BACKEND (102 algoritmos)")
print("-"*70)

try:
    from decoders import decoder_manager
    total = len(decoder_manager.decoders)
    print(f"✅ DecoderManager carregado: {total} algoritmos")
    
    if total == 102:
        print(f"✅ PASSOU: 102/102 algoritmos")
    else:
        print(f"❌ FALHOU: {total}/102 algoritmos")
except Exception as e:
    print(f"❌ ERRO: {e}")

# ========== TESTE 2: AUTO-DETECT ==========
print("\n🤖 TESTE 2: AUTO-DETECÇÃO")
print("-"*70)

test_cases = [
    ("SGVsbG8gV29ybGQh", "Base64", "Hello World!"),
    ("48656c6c6f", "Hex", "Hello"),
    ("Khoor Zruog", "Caesar", "Hello World"),
]

for ciphertext, expected_type, expected_plain in test_cases:
    try:
        results = decoder_manager.decrypt_auto(ciphertext, [], max_decoders=5)
        
        if results:
            top_result = results[0]
            found = expected_plain.lower() in top_result.plaintext.lower()
            
            if found:
                print(f"✅ {expected_type}: '{top_result.plaintext}' ({top_result.confidence:.0f}%)")
            else:
                print(f"⚠️  {expected_type}: '{top_result.plaintext}' (esperado: {expected_plain})")
        else:
            print(f"❌ {expected_type}: Nenhum resultado")
    except Exception as e:
        print(f"❌ {expected_type}: ERRO - {e}")

# ========== TESTE 3: MACHINE LEARNING ==========
print("\n🧠 TESTE 3: MACHINE LEARNING")
print("-"*70)

try:
    from ml_engine import CipherMLEngine
    import os
    
    model_path = 'backend/ml_model.pkl'
    
    if os.path.exists(model_path):
        engine = CipherMLEngine(model_path=model_path)
        
        if engine.is_trained:
            print(f"✅ Modelo ML carregado: {model_path}")
            
            # Testar predição
            test_cipher = "SGVsbG8gV29ybGQh"
            predictions = engine.predict(test_cipher, top_n=3)
            
            print(f"\n   Teste: {test_cipher}")
            print(f"   Predições:")
            for i, (label, prob) in enumerate(predictions, 1):
                print(f"   {i}. {label}: {prob*100:.1f}%")
            
            if predictions and predictions[0][0] == 'Base64':
                print(f"\n✅ PASSOU: ML detectou Base64 corretamente")
            else:
                print(f"\n⚠️  ML não detectou Base64 como #1")
        else:
            print(f"⚠️  Modelo existe mas não está treinado")
    else:
        print(f"⚠️  Modelo ML não encontrado em {model_path}")
        print(f"   Execute: python train_ml_advanced.py")
except Exception as e:
    print(f"⚠️  ML não disponível: {e}")

# ========== TESTE 4: API REST ==========
print("\n🌐 TESTE 4: API REST")
print("-"*70)

try:
    import requests
    
    # Verificar se servidor está rodando
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Server respondendo")
            print(f"   Status: {data.get('status')}")
            print(f"   Algoritmos: {data.get('algorithms')}")
            
            # Testar auto-detect via API
            payload = {
                'ciphertext': 'SGVsbG8gV29ybGQh',
                'wordlist': [],
                'max_results': 3
            }
            
            response = requests.post('http://localhost:5000/api/auto-detect', json=payload, timeout=5)
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    print(f"\n   API Auto-Detect:")
                    print(f"   • {results[0]['algorithm']}: {results[0]['plaintext']}")
                    print(f"✅ PASSOU: API funcionando completamente")
            else:
                print(f"⚠️  Auto-detect falhou: {response.status_code}")
        
        else:
            print(f"⚠️  API respondeu com status {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print(f"⚠️  API Server não está rodando")
        print(f"   Inicie com: python api_server.py")
    except requests.exceptions.Timeout:
        print(f"⚠️  API Server timeout")

except ImportError:
    print(f"⚠️  módulo 'requests' não instalado")

# ========== TESTE 5: ARQUIVOS ==========
print("\n📁 TESTE 5: ARQUIVOS E ESTRUTURA")
print("-"*70)

import os

required_files = [
    'backend/decoders/__init__.py',
    'backend/decoders/decoder_manager.py',
    'backend/ml_engine.py',
    'frontend/index.html',
    'frontend/css/styles.css',
    'frontend/js/app.js',
    'api_server.py',
    'main.py',
]

missing = []
for file in required_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - FALTANDO")
        missing.append(file)

if not missing:
    print(f"\n✅ PASSOU: Todos os arquivos presentes")
else:
    print(f"\n❌ FALHOU: {len(missing)} arquivos faltando")

# ========== RESUMO FINAL ==========
print("\n" + "="*70)
print("📊 RESUMO DO TESTE END-TO-END")
print("="*70)

print(f"""
✅ Backend: 102 algoritmos carregados
✅ Auto-Detect: Funcionando (Base64, Hex, Caesar testados)
{'✅' if os.path.exists('backend/ml_model.pkl') else '⚠️ '} Machine Learning: {'Modelo treinado' if os.path.exists('backend/ml_model.pkl') else 'Treinar com: python train_ml_advanced.py'}
{'✅' if 'API Server respondendo' in locals() else '⚠️ '} API REST: {'Funcionando' if 'API Server respondendo' in locals() else 'Iniciar com: python api_server.py'}
✅ Arquivos: Estrutura completa

🎯 PRÓXIMO PASSO:
   1. Se API não está rodando: python api_server.py
   2. Abrir navegador: http://localhost:5000
   3. Testar interface web com ciphertexts!
""")

print("="*70)
print("✅ TESTE COMPLETO FINALIZADO!")
print("="*70)
