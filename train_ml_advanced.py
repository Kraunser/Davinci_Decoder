"""
DaVinci Decoder - Treinamento ML Avançado
Usa dados sintéticos + dados coletados da web
"""
import sys
sys.path.insert(0, 'backend')

from ml_engine import CipherMLEngine, ML_AVAILABLE
from web_scraper_ml import CipherWebScraper
import os

def main():
    print("="*70)
    print("🤖 DAVINCI DECODER - TREINAMENTO ML AVANÇADO".center(70))
    print("="*70)
    
    if not ML_AVAILABLE:
        print("\n❌ scikit-learn não está instalado!")
        print("\nPara instalar:")
        print("  pip install scikit-learn beautifulsoup4 requests")
        return
    
    print("\n📚 Este script oferece 3 opções de treinamento:")
    print("  1. Dados sintéticos apenas (rápido, ~1 min)")
    print("  2. Dados da web + sintéticos (completo, ~2-3 min)")
    print("  3. Usar dados salvos anteriormente")
    
    choice = input("\nEscolha uma opção (1/2/3, padrão=1): ").strip() or "1"
    
    training_data = []
    
    # ========== OPÇÃO 1: SINTÉTICOS ==========
    if choice == "1":
        print("\n📝 Gerando dados sintéticos...")
        from train_ml import generate_training_data
        training_data = generate_training_data(samples_per_class=100)
    
    # ========== OPÇÃO 2: WEB + SINTÉTICOS ==========
    elif choice == "2":
        print("\n🌐 Coletando dados da web...")
        
        use_web = input("Conectar à internet para scraping? (s/n, padrão=n): ").lower() == 's'
        
        scraper = CipherWebScraper()
        web_data = scraper.scrape_all(use_web=use_web)
        
        # Salvar dados coletados
        scraper.save_to_file(web_data, 'backend/web_scraped_data.json')
        
        print(f"\n✅ Coletados {len(web_data)} exemplos da web")
        
        # Adicionar dados sintéticos
        print("\n📝 Complementando com dados sintéticos...")
        from train_ml import generate_training_data
        synthetic_data = generate_training_data(samples_per_class=50)
        
        # Combinar
        training_data = web_data + synthetic_data
        print(f"\n📊 Total: {len(training_data)} exemplos (web + sintéticos)")
    
    # ========== OPÇÃO 3: DADOS SALVOS ==========
    elif choice == "3":
        print("\n📦 Carregando dados salvos...")
        
        scraper = CipherWebScraper()
        web_data = scraper.load_from_file('backend/web_scraped_data.json')
        
        if not web_data:
            print("⚠️  Nenhum dado salvo encontrado!")
            print("Execute a opção 2 primeiro para coletar dados da web.")
            return
        
        training_data = web_data
        
        # Opcional: adicionar sintéticos
        add_synthetic = input("\nAdicionar dados sintéticos? (s/n, padrão=s): ").lower() != 'n'
        
        if add_synthetic:
            from train_ml import generate_training_data
            synthetic_data = generate_training_data(samples_per_class=50)
            training_data.extend(synthetic_data)
            print(f"📊 Total: {len(training_data)} exemplos")
    
    else:
        print("❌ Opção inválida!")
        return
    
    # ========== TREINAR MODELO ==========
    
    if not training_data:
        print("❌ Nenhum dado de treinamento!")
        return
    
    # Mostrar distribuição
    from collections import Counter
    labels = [label for _, label in training_data]
    distribution = Counter(labels)
    
    print(f"\n📊 Distribuição dos dados:")
    for label, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {label}: {count} exemplos")
    
    # Criar e treinar
    print("\n" + "="*70)
    print("🎓 INICIANDO TREINAMENTO")
    print("="*70)
    
    engine = CipherMLEngine(model_path='backend/ml_model.pkl')
    engine.train(training_data, test_size=0.2)
    
    # ========== TESTAR ==========
    
    print("\n" + "="*70)
    print("🧪 TESTANDO MODELO TREINADO")
    print("="*70)
    
    test_cases = [
        ("SGVsbG8gV29ybGQh", "Base64"),
        ("48656c6c6f", "Hexadecimal"),
        ("Khoor Zruog", "Caesar"),
        ("5d41402abc4b2a76b9719d911017c592", "MD5"),
        (".... . .-.. .-.. ---", "Morse"),
        ("Uryyb", "ROT13"),
        ("01001000 01100101 01101100 01101100 01101111", "Binary"),
    ]
    
    correct = 0
    for ciphertext, expected in test_cases:
        predictions = engine.predict(ciphertext, top_n=3)
        
        print(f"\n📝 Ciphertext: {ciphertext[:50]}...")
        print(f"   Esperado: {expected}")
        print(f"   Predições:")
        
        for i, (label, prob) in enumerate(predictions, 1):
            emoji = "✅" if label == expected else "  "
            print(f"   {emoji} {i}. {label}: {prob*100:.1f}%")
            
            if i == 1 and label == expected:
                correct += 1
    
    accuracy = (correct / len(test_cases)) * 100
    
    print(f"\n{'='*70}")
    print(f"📊 Acurácia nos testes: {accuracy:.0f}% ({correct}/{len(test_cases)})")
    print(f"{'='*70}")
    
    # ========== CONCLUSÃO ==========
    
    print("\n✅ TREINAMENTO COMPLETO!")
    print(f"\n💾 Modelo salvo em: backend/ml_model.pkl")
    print(f"📊 Total de exemplos treinados: {len(training_data)}")
    print(f"🎯 Pronto para usar!")
    
    print(f"\n💡 Para usar o modelo:")
    print(f"   from backend.ml_engine import CipherMLEngine")
    print(f"   engine = CipherMLEngine()")
    print(f"   predictions = engine.predict('seu_ciphertext')")


if __name__ == '__main__':
    main()
