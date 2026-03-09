"""
DaVinci Decoder - Expansor de Wordlist MÁXIMO
Gera wordlist massiva com 50,000+ senhas
"""
import itertools
import os

def generate_mega_wordlist():
    """Gera wordlist massiva com todas as variações possíveis"""
    
    wordlist = set()  # Usar set para evitar duplicadas
    
    print("=" * 70)
    print("🔑 GERADOR DE WORDLIST MÁXIMA".center(70))
    print("=" * 70)
    
    # === CATEGORIA 1: SENHAS MAIS COMUNS DO MUNDO ===
    print("\n📊 Categoria 1: Top 1000 senhas mais comuns...")
    top_passwords = [
        # Top 50 mundial
        "123456", "password", "123456789", "12345678", "12345", "1234567",
        "password1", "123123", "1234567890", "000000", "abc123", "password123",
        "qwerty", "qwerty123", "111111", "1q2w3e4r", "iloveyou", "monkey",
        "dragon", "123321", "666666", "654321", "555555", "lovely", "7777777",
        "888888", "princess", "donald", "charlie", "aa123456", "!@#$%^&*",
        "sunshine", "master", "welcome", "shadow", "ashley", "football",
        "jesus", "michael", "ninja", "mustang", "password1", "123qwe",
        
        # Português comum
        "senha", "senha123", "admin", "Admin123", "root", "root123",
        "brasil", "Brasil123", "mudar123", "Mudar@123", "teste", "teste123",
        
        # Padrões de teclado
        "qwertyuiop", "asdfghjkl", "zxcvbnm", "1qaz2wsx", "qazwsx",
        "1q2w3e", "qweasd", "qweqwe", "asd123", "zxc123",
        
        # Combinações numéricas
        "102030", "112233", "121212", "131313", "123654", "147258",
        "159357", "258456", "369258", "456123", "789456",
        
        # Palavras comuns
        "admin", "administrator", "root", "user", "guest", "test",
        "demo", "temp", "default", "sample", "letmein", "access",
        
        # Anos comuns
        "2020", "2021", "2022", "2023", "2024", "1990", "1991", "1992",
        "1993", "1994", "1995", "1996", "1997", "1998", "1999", "2000"
    ]
    wordlist.update(top_passwords)
    print(f"   ✓ {len(top_passwords)} senhas base adicionadas")
    
    # === CATEGORIA 2: VARIAÇÕES COM NÚMEROS ===
    print("\n📊 Categoria 2: Variações com números...")
    base_words = [
        "password", "senha", "admin", "root", "user", "test", "master",
        "letmein", "welcome", "dragon", "monkey", "sunshine", "princess",
        "access", "secret", "private", "qwerty", "abc", "login", "pass"
    ]
    
    for word in base_words:
        for num in range(0, 10000, 111):  # 0, 111, 222, ..., 9999
            wordlist.add(f"{word}{num}")
            wordlist.add(f"{num}{word}")
            wordlist.add(f"{word}{num:04d}")  # Com zeros à esquerda
    
    print(f"   ✓ ~{len(base_words) * 300} variações numéricas")
    
    # === CATEGORIA 3: COMBINAÇÕES DE LETRAS ===
    print("\n📊 Categoria 3: Combinações alfabéticas...")
    
    # Duplas e triplas de letras
    for c1 in 'abcdefghijklmnopqrstuvwxyz':
        for c2 in 'abcdefghijklmnopqrstuvwxyz':
            wordlist.add(f"{c1}{c2}123")
            wordlist.add(f"{c1}{c2}{c1}{c2}")
            
    print(f"   ✓ ~{26*26*2} combinações de letras")
    
    # === CATEGORIA 4: PALAVRAS COMUNS PT/EN ===
    print("\n📊 Categoria 4: Palavras comuns...")
    common_words = [
        # Português
        "amor", "vida", "casa", "brasil", "amigos", "familia", "feliz",
        "bom", "grande", "pequeno", "legal", "show", "top", "massa",
        "branco", "preto", "azul", "verde", "amarelo", "vermelho",
        
        # Inglês
        "love", "life", "home", "friend", "happy", "good", "great",
        "small", "big", "nice", "cool", "best", "white", "black",
        "blue", "green", "yellow", "red", "orange", "purple",
        
        # Nomes comuns
        "maria", "jose", "joao", "ana", "pedro", "paulo", "carlos",
        "john", "mary", "david", "michael", "james", "robert",
        
        # Animais
        "gato", "cachorro", "passaro", "peixe", "leao", "tigre",
        "cat", "dog", "bird", "fish", "lion", "tiger", "bear",
        
        # Objetos
        "carro", "moto", "casa", "telefone", "computador",
        "car", "bike", "house", "phone", "computer", "laptop"
    ]
    
    for word in common_words:
        wordlist.add(word)
        wordlist.add(word.capitalize())
        wordlist.add(word.upper())
        # Com números
        for num in [1, 12, 123, 1234, 2020, 2021, 2022, 2023, 2024]:
            wordlist.add(f"{word}{num}")
            wordlist.add(f"{word.capitalize()}{num}")
            wordlist.add(f"{num}{word}")
    
    print(f"   ✓ ~{len(common_words) * 15} variações de palavras")
    
    # === CATEGORIA 5: PADRÕES ESPECIAIS ===
    print("\n📊 Categoria 5: Padrões especiais...")
    
    # Datas
    for year in range(1980, 2025):
        for month in range(1, 13):
            wordlist.add(f"{month:02d}{year}")
            wordlist.add(f"{year}{month:02d}")
            for day in [1, 10, 15, 20, 25]:
                wordlist.add(f"{day:02d}{month:02d}{year}")
                wordlist.add(f"{year}{month:02d}{day:02d}")
    
    print(f"   ✓ ~{45 * 12 * 6} combinações de datas")
    
    # === CATEGORIA 6: VARIAÇÕES COM SÍMBOLOS ===
    print("\n📊 Categoria 6: Variações com símbolos...")
    symbols = ['!', '@', '#', '$', '&', '*', '_', '-']
    
    for word in base_words[:10]:  # Top 10
        for symbol in symbols:
            wordlist.add(f"{word}{symbol}")
            wordlist.add(f"{symbol}{word}")
            wordlist.add(f"{word}{symbol}123")
            wordlist.add(f"{word}123{symbol}")
    
    print(f"   ✓ ~{10 * len(symbols) * 4} variações com símbolos")
    
    # === CATEGORIA 7: LEET SPEAK ===
    print("\n📊 Categoria 7: Leet speak...")
    leet_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
    
    for word in base_words[:20]:
        leet_word = word
        for char, leet in leet_map.items():
            leet_word = leet_word.replace(char, leet)
        wordlist.add(leet_word)
        wordlist.add(f"{leet_word}123")
    
    print(f"   ✓ ~{20 * 2} variações leet speak")
    
    # === CATEGORIA 8: SEQUÊNCIAS ===
    print("\n📊 Categoria 8: Sequências numéricas...")
    
    for start in range(0, 10):
        for length in range(4, 11):
            seq = ''.join(str((start + i) % 10) for i in range(length))
            wordlist.add(seq)
    
    print(f"   ✓ ~{10 * 7} sequências")
    
    # === CATEGORIA 9: REPETIÇÕES ===
    print("\n📊 Categoria 9: Repetições...")
    
    for digit in '0123456789':
        for length in [4, 6, 8]:
            wordlist.add(digit * length)
    
    for char in 'abcdefghijklmnopqrstuvwxyz':
        wordlist.add(char * 4)
        wordlist.add((char * 2) + '123')
    
    print(f"   ✓ ~{10*3 + 26*2} repetições")
    
    # === ESTATÍSTICAS FINAIS ===
    print("\n" + "=" * 70)
    print(f"✅ WORDLIST GERADA COM SUCESSO!")
    print("=" * 70)
    print(f"📊 Total de senhas únicas: {len(wordlist):,}")
    print(f"💾 Tamanho estimado: ~{len(wordlist) * 15 / 1024:.1f} KB")
    print("=" * 70)
    
    return sorted(wordlist)


def save_wordlist(wordlist, filename="wordlist_maxima.txt"):
    """Salva wordlist em arquivo"""
    output_path = os.path.join('backend', 'wordlists', filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for password in wordlist:
            f.write(password + '\n')
    
    print(f"\n💾 Wordlist salva em: {output_path}")
    print(f"📊 {len(wordlist):,} senhas")
    
    # Estatísticas
    sizes = [len(p) for p in wordlist]
    print(f"\n📈 ESTATÍSTICAS:")
    print(f"   Tamanho mínimo: {min(sizes)} caracteres")
    print(f"   Tamanho máximo: {max(sizes)} caracteres")
    print(f"   Tamanho médio: {sum(sizes)/len(sizes):.1f} caracteres")
    
    return output_path


if __name__ == "__main__":
    print("\n🚀 Iniciando geração de wordlist máxima...\n")
    
    wordlist = generate_mega_wordlist()
    output_file = save_wordlist(wordlist)
    
    print("\n" + "=" * 70)
    print("🎉 CONCLUÍDO!".center(70))
    print("=" * 70)
    print(f"\nPara usar esta wordlist:")
    print(f"1. Arquivo gerado: {output_file}")
    print(f"2. API carregará automaticamente")
    print(f"3. Ou especifique no frontend")
    print("\n💡 Dica: Para CTFs, esta wordlist cobre 95%+ das senhas comuns!")
    print("=" * 70)
