"""
DaVinci Decoder - Script de Testes Completos
Valida todos os componentes do sistema
"""
import sys
sys.path.insert(0, 'backend')

from decoders import decoder_manager

def print_section(title):
    print('\n' + '='*70)
    print(title.center(70))
    print('='*70)

def test_1_loading():
    """Teste 1: Carregamento do Sistema"""
    print_section('TESTE 1: CARREGAMENTO DO SISTEMA')
    
    try:
        total = len(decoder_manager.decoders)
        print(f'\n✅ DecoderManager carregado')
        print(f'✅ Total de algoritmos: {total}')
        
        if total == 102:
            print(f'✅ PASSOU: 102 algoritmos esperados')
            return True
        else:
            print(f'❌ FALHOU: Esperado 102, obtido {total}')
            return False
    except Exception as e:
        print(f'❌ ERRO: {e}')
        return False

def test_2_categories():
    """Teste 2: Categorização"""
    print_section('TESTE 2: CATEGORIZAÇÃO')
    
    try:
        modern = len([d for d in decoder_manager.decoders if d.get_algorithm_type() == 'modern'])
        classical = len([d for d in decoder_manager.decoders if d.get_algorithm_type() == 'classical'])
        encoding = len([d for d in decoder_manager.decoders if d.get_algorithm_type() == 'encoding'])
        hashes = len([d for d in decoder_manager.decoders if d.get_algorithm_type() == 'hash'])
        
        print(f'\n🔐 Cifras Modernas: {modern}')
        print(f'📜 Cifras Clássicas: {classical}')
        print(f'🔤 Encodings: {encoding}')
        print(f'#️⃣ Hash Crackers: {hashes}')
        print(f'\n📊 TOTAL: {modern + classical + encoding + hashes}')
        
        if modern == 36 and classical == 32 and encoding == 21 and hashes == 13:
            print(f'\n✅ PASSOU: Todas as categorias corretas')
            return True
        else:
            print(f'\n❌ FALHOU: Categorias incorretas')
            return False
    except Exception as e:
        print(f'❌ ERRO: {e}')
        return False

def test_3_base64():
    """Teste 3: Decifração Base64"""
    print_section('TESTE 3: DECIFRAÇÃO BASE64')
    
    try:
        ciphertext = 'SGVsbG8gV29ybGQh'
        print(f'\nCiphertext: {ciphertext}')
        
        decoder = decoder_manager.get_decoder_by_name('Base64 Encoding')
        if not decoder:
            print('❌ FALHOU: Decoder Base64 não encontrado')
            return False
        
        keys = decoder.derive_keys('')
        for method, key in keys.items():
            result = decoder.decrypt(ciphertext, key, method)
            if result:
                print(f'✅ DECIFRADO: {result}')
                
                if result == 'Hello World!':
                    print(f'✅ PASSOU: Resultado correto')
                    return True
                else:
                    print(f'❌ FALHOU: Esperado "Hello World!", obtido "{result}"')
                    return False
        
        print('❌ FALHOU: Não conseguiu decifrar')
        return False
    except Exception as e:
        print(f'❌ ERRO: {e}')
        return False

def test_4_caesar():
    """Teste 4: Caesar Cipher"""
    print_section('TESTE 4: CAESAR CIPHER')
    
    try:
        ciphertext = 'Khoor Zruog'
        print(f'\nCiphertext: {ciphertext}')
        
        decoder = decoder_manager.get_decoder_by_name('Caesar Cipher')
        if not decoder:
            print('❌ FALHOU: Decoder Caesar não encontrado')
            return False
        
        keys = decoder.derive_keys('')
        for method, key in keys.items():
            result = decoder.decrypt(ciphertext, key, method)
            if result and 'hello world' in result.lower():
                print(f'✅ DECIFRADO com {method}: {result}')
                print(f'✅ PASSOU: Resultado correto')
                return True
        
        print('❌ FALHOU: Não conseguiu decifrar')
        return False
    except Exception as e:
        print(f'❌ ERRO: {e}')
        return False

def test_5_autodetect():
    """Teste 5: Auto-detecção"""
    print_section('TESTE 5: AUTO-DETECÇÃO')
    
    try:
        ciphertext = 'SGVsbG8gV29ybGQh'
        print(f'\nCiphertext: {ciphertext}')
        
        candidates = decoder_manager.auto_detect(ciphertext, top_n=5)
        
        print(f'\nTop 5 detectados:')
        for i, (decoder, prob) in enumerate(candidates, 1):
            print(f'  {i}. {decoder.get_algorithm_name()} ({prob*100:.1f}%)')
        
        if candidates and 'Base64' in candidates[0][0].get_algorithm_name():
            print(f'\n✅ PASSOU: Base64 detectado como #1')
            return True
        else:
            print(f'\n❌ FALHOU: Base64 não foi detectado como #1')
            return False
    except Exception as e:
        print(f'❌ ERRO: {e}')
        return False

def run_all_tests():
    """Executa todos os testes"""
    print_section('🧪 SUITE DE TESTES DAVINCI DECODER')
    
    tests = [
        test_1_loading,
        test_2_categories,
        test_3_base64,
        test_4_caesar,
        test_5_autodetect
    ]
    
    results = []
    for test in tests:
        try:
            passed = test()
            results.append((test.__doc__, passed))
        except Exception as e:
            print(f'\n❌ ERRO CRÍTICO em {test.__name__}: {e}')
            results.append((test.__doc__, False))
    
    # Resumo
    print_section('📊 RESUMO DOS TESTES')
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f'\n')
    for desc, result in results:
        status = '✅ PASSOU' if result else '❌ FALHOU'
        print(f'{status}: {desc}')
    
    print(f'\n{"="*70}')
    print(f'RESULTADO FINAL: {passed}/{total} testes passaram ({passed/total*100:.0f}%)'.center(70))
    print(f'{"="*70}')
    
    if passed == total:
        print(f'\n🎉 SISTEMA 100% FUNCIONAL! 🎉'.center(70))
    else:
        print(f'\n⚠️  Alguns testes falharam'.center(70))
    
    return passed == total

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
