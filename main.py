"""
DaVinci Decoder - Main Interface (Updated)
Interface profissional com menu hierárquico e suporte multi-algoritmo
"""
import os
import sys
import webbrowser
from pathlib import Path

# Avoid cp1252 emoji crashes on Windows terminals.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Adicionar backend ao path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from decoders.decoder_manager import decoder_manager


def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def exibir_header():
    """Exibe header principal"""
    print("=" * 80)
    print("🎨  DAVINCI DECODER - Universal Cipher Breaker".center(80))
    print("=" * 80)
    print()


def menu_principal():
    """Menu principal hierárquico"""
    while True:
        limpar_tela()
        exibir_header()
        
        print("📋 MODO DE OPERAÇÃO:\n")
        print("1. 🤖 Auto-Detect (Recomendado)")
        print("2. 🔐 Cifras Modernas")
        print("3. 📜 Cifras Clássicas")
        print("4. 📊 Listar Todos os Algoritmos")
        print("5. 🌐 Abrir Interface Web (Frontend)")
        print("6. 📚 Abrir README")
        print("0. ❌ Sair")
        print()
        
        escolha = input("Escolha uma opção: ").strip()
        
        if escolha == '1':
            modo_auto_detect()
        elif escolha == '2':
            menu_cifras_modernas()
        elif escolha == '3':
            menu_cifras_classicas()
        elif escolha == '4':
            limpar_tela()
            exibir_header()
            decoder_manager.list_algorithms()
            input("\nPressione ENTER para continuar...")
        elif escolha == '5':
            abrir_frontend()
        elif escolha == '6':
            abrir_readme()
        elif escolha == '0':
            print("\n👋 Até logo!")
            break
        else:
            print("\n❌ Opção inválida!")
            input("Pressione ENTER para continuar...")


def modo_auto_detect():
    """Modo de auto-detecção inteligente"""
    limpar_tela()
    exibir_header()
    
    print("🤖 MODO AUTO-DETECT")
    print("=" * 80)
    print()
    
    # Input do ciphertext
    ciphertext = input("📋 Cole o ciphertext: ").strip()
    
    if not ciphertext:
        print("❌ Nenhum ciphertext fornecido!")
        input("\nPressione ENTER para continuar...")
        return
    
    # Carregar wordlist
    wordlist = carregar_wordlist()
    if not wordlist:
        return
    
    # Auto-detect e decifrar
    resultados = decoder_manager.decrypt_auto(ciphertext, wordlist, max_decoders=5)
    
    exibir_resultados(resultados)
    input("\n\nPressione ENTER para voltar ao menu...")


def menu_cifras_modernas():
    """Submenu para cifras modernas"""
    while True:
        limpar_tela()
        exibir_header()
        
        print("🔐 CIFRAS MODERNAS:\n")
        
        modernas = decoder_manager.get_all_modern()
        
        for i, decoder in enumerate(modernas, 1):
            print(f"{i}. {decoder.get_algorithm_name()}")
        
        print(f"\n0. ← Voltar")
        print()
        
        escolha = input("Escolha um algoritmo: ").strip()
        
        if escolha == '0':
            break
        
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(modernas):
                executar_decoder(modernas[idx])
            else:
                print("\n❌ Opção inválida!")
                input("Pressione ENTER para continuar...")
        except ValueError:
            print("\n❌ Opção inválida!")
            input("Pressione ENTER para continuar...")


def menu_cifras_classicas():
    """Submenu para cifras clássicas"""
    while True:
        limpar_tela()
        exibir_header()
        
        print("📜 CIFRAS CLÁSSICAS:\n")
        
        classicas = decoder_manager.get_all_classical()
        
        for i, decoder in enumerate(classicas, 1):
            print(f"{i}. {decoder.get_algorithm_name()}")
        
        print(f"\n0. ← Voltar")
        print()
        
        escolha = input("Escolha um algoritmo: ").strip()
        
        if escolha == '0':
            break
        
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(classicas):
                executar_decoder(classicas[idx])
            else:
                print("\n❌ Opção inválida!")
                input("Pressione ENTER para continuar...")
        except ValueError:
            print("\n❌ Opção inválida!")
            input("Pressione ENTER para continuar...")


def executar_decoder(decoder):
    """Executa um decoder específico"""
    limpar_tela()
    exibir_header()
    
    print(f"🎯 {decoder.get_algorithm_name()}")
    print("=" * 80)
    print()
    
    # Input
    ciphertext = input("📋 Cole o ciphertext: ").strip()
    
    if not ciphertext:
        print("❌ Nenhum ciphertext fornecido!")
        input("\nPressione ENTER para continuar...")
        return
    
    # Carregar wordlist
    wordlist = carregar_wordlist()
    if not wordlist:
        return
    
    # Atacar
    resultados = decoder.attack(ciphertext, wordlist)
    
    exibir_resultados(resultados)
    input("\n\nPressione ENTER para voltar ao menu...")


def carregar_wordlist():
    """Carrega wordlist expandida"""
    wordlist_expandida = Path(__file__).parent / "backend" / "wordlists" / "wordlist_expandida.txt"
    wordlist_padrao = Path(__file__).parent / "backend" / "wordlists" / "wordlist.txt"
    
    if wordlist_expandida.exists():
        wordlist_path = wordlist_expandida
        print(f"\n✅ Wordlist expandida carregada")
    elif wordlist_padrao.exists():
        wordlist_path = wordlist_padrao
        print(f"\n⚠️ Wordlist padrão carregada")
    else:
        print("\n❌ Nenhuma wordlist encontrada!")
        input("Pressione ENTER para continuar...")
        return None
    
    with open(wordlist_path, 'r', encoding='utf-8') as f:
        wordlist = [linha.strip() for linha in f if linha.strip()]
    
    print(f"📊 {len(wordlist)} senhas carregadas\n")
    
    return wordlist


def exibir_resultados(resultados):
    """Exibe resultados formatados"""
    print("\n" + "=" * 80)
    
    if resultados:
        print("🎉 SUCESSO!".center(80))
        print("=" * 80)
        
        for resultado in resultados:
            print(f"\n🔑 Senha: {resultado.password}")
            print(f"⚙️ Método: {resultado.method}")
            print(f"🔐 Chave: {resultado.key_hex[:32]}...")
            print(f"📊 Confiança: {resultado.confidence:.1f}%")
            print(f"\n📜 MENSAGEM DECIFRADA:")
            print("-" * 80)
            print(resultado.plaintext[:500])
            if len(resultado.plaintext) > 500:
                print(f"... (+{len(resultado.plaintext) - 500} caracteres)")
            print("-" * 80)
    else:
        print("❌ FALHA".center(80))
        print("=" * 80)
        print("\nNenhuma senha da wordlist funcionou.")
        print("\n💡 Dicas:")
        print("• Verifique se o ciphertext está correto")
        print("• Tente outro algoritmo")
        print("• Adicione mais senhas à wordlist")


def abrir_frontend():
    """Abre interface web"""
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    
    if frontend_path.exists():
        print(f"\n🌐 Abrindo {frontend_path}")
        webbrowser.open(str(frontend_path.absolute()))
    else:
        print(f"\n❌ Arquivo não encontrado: {frontend_path}")
    
    input("\nPressione ENTER para continuar...")


def abrir_readme():
    """Abre README"""
    readme_path = Path(__file__).parent / "README.md"
    
    if readme_path.exists():
        print(f"\n📚 Abrindo {readme_path}")
        webbrowser.open(str(readme_path.absolute()))
    else:
        print(f"\n❌ Arquivo não encontrado: {readme_path}")
    
    input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário. Até logo!")
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        input("Pressione ENTER para sair...")
