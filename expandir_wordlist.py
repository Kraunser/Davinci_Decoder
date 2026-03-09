"""
Expansor de Wordlist - Gera TODAS as variações possíveis
"""
import re
import unicodedata

def remover_acentos(texto):
    """Remove acentos de um texto"""
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn')

def gerar_variacoes_completas(palavra):
    """Gera TODAS as variações possíveis de uma palavra"""
    if not palavra or len(palavra) < 2:
        return []
    
    variacoes = set()
    
    # Original
    variacoes.add(palavra)
    
    # Sem acentos
    sem_acento = remover_acentos(palavra)
    variacoes.add(sem_acento)
    
    # Cases
    variacoes.add(palavra.lower())
    variacoes.add(palavra.upper())
    variacoes.add(palavra.capitalize())
    variacoes.add(palavra.title())
    
    # Sem acentos + cases
    variacoes.add(sem_acento.lower())
    variacoes.add(sem_acento.upper())
    variacoes.add(sem_acento.capitalize())
    variacoes.add(sem_acento.title())
    
    # Leet speak básico
    leet_map = {
        'a': ['4', '@'], 'e': ['3'], 'i': ['1', '!'], 'o': ['0'], 
        's': ['5', '$'], 't': ['7'], 'l': ['1']
    }
    
    for char, replacements in leet_map.items():
        for repl in replacements:
            leet = palavra.lower().replace(char, repl)
            if leet != palavra.lower():
                variacoes.add(leet)
                variacoes.add(leet.capitalize())
    
    return list(variacoes)

def expandir_frases(texto):
    """Extrai frases e gera variações de palavras combinadas"""
    variacoes = set()
    
    # Extrair frases importantes (2-4 palavras)
    palavras = re.findall(r'\b[A-Za-zÀ-ÿ]+\b', texto)
    
    # Gerar combinações de 2-3 palavras consecutivas
    for i in range(len(palavras) - 1):
        # 2 palavras
        combo2 = palavras[i] + palavras[i+1]
        combo2_espaco = palavras[i] + ' ' + palavras[i+1]
        combo2_hifen = palavras[i] + '-' + palavras[i+1]
        combo2_under = palavras[i] + '_' + palavras[i+1]
        
        variacoes.update(gerar_variacoes_completas(combo2))
        variacoes.add(combo2_espaco)
        variacoes.add(combo2_hifen)
        variacoes.add(combo2_under)
        
        # 3 palavras
        if i < len(palavras) - 2:
            combo3 = palavras[i] + palavras[i+1] + palavras[i+2]
            combo3_espaco = palavras[i] + ' ' + palavras[i+1] + ' ' + palavras[i+2]
            
            variacoes.update(gerar_variacoes_completas(combo3))
            variacoes.add(combo3_espaco)
    
    return list(variacoes)

# Ler wordlist base
print("🔄 Carregando wordlist base...")
with open(r'backend\wordlists\wordlist.txt', 'r', encoding='utf-8') as f:
    palavras_base = [linha.strip() for linha in f if linha.strip()]

print(f"📊 {len(palavras_base)} palavras base")

# Gerar todas as variações
print("⚙️ Gerando variações...")
todas_variacoes = set()

for palavra in palavras_base:
    variacoes = gerar_variacoes_completas(palavra)
    todas_variacoes.update(variacoes)
    
    # Se for frase (tem espaço), adicionar variações combinadas
    if ' ' in palavra:
        todas_variacoes.update(gerar_variacoes_completas(palavra.replace(' ', '')))
        todas_variacoes.update(gerar_variacoes_completas(palavra.replace(' ', '-')))
        todas_variacoes.update(gerar_variacoes_completas(palavra.replace(' ', '_')))

# Filtrar palavras muito curtas
todas_variacoes = [v for v in todas_variacoes if len(v) >= 3]
todas_variacoes_sorted = sorted(set(todas_variacoes))

# Salvar
print("💾 Salvando wordlist expandida...")
with open(r'backend\wordlists\wordlist_expandida.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(todas_variacoes_sorted))

print(f"\n✅ Concluído!")
print(f"📈 {len(palavras_base)} palavras → {len(todas_variacoes_sorted)} variações")
print(f"📊 Multiplicador: {len(todas_variacoes_sorted) / len(palavras_base):.1f}x")
print(f"\n🔍 Tentativas totais: {len(todas_variacoes_sorted)} × 50 derivações = ~{len(todas_variacoes_sorted) * 50:,}")
