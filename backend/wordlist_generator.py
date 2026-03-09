"""
Gerador Inteligente de Wordlists
Cria variações automáticas de palavras para aumentar chances de sucesso
"""
import unicodedata

class WordlistGenerator:
    def __init__(self):
        # Mapeamentos de leet speak
        self.LEET_MAPS = {
            'a': ['4', '@'],
            'e': ['3'],
            'i': ['1', '!'],
            'o': ['0'],
            's': ['5', '$'],
            'l': ['1'],
            't': ['7'],
            'g': ['9'],
            'b': ['8']
        }
        
        # Sufixos comuns
        self.COMMON_SUFFIXES = [
            '123', '321', '456', '!', '@', '#',
            '2024', '2025', '2026', '01', '00'
        ]
        
        # Prefixos comuns
        self.COMMON_PREFIXES = [
            'the', 'my', 'a'
        ]
        
        # Separadores
        self.SEPARATORS = ['', '_', '-', '.']
    
    def remover_acentos(self, texto):
        """Remove acentos de uma string"""
        return ''.join(c for c in unicodedata.normalize('NFD', texto) 
                      if unicodedata.category(c) != 'Mn')
    
    def generate_all_variations(self, word):
        """
        Gera TODAS as variações de uma palavra
        Retorna lista sem duplicatas
        """
        variations = set()
        
        # 1. Básicas
        variations.update(self._basic_variations(word))
        
        # 2. Com sufixos
        variations.update(self._add_suffixes(word))
        
        # 3. Leet speak
        variations.update(self._leet_speak(word))
        
        # 4. Sem espaços e acentos
        variations.update(self._normalize_variations(word))
        
        return list(variations)
    
    def _basic_variations(self, word):
        """Variações básicas de case"""
        return {
            word,
            word.lower(),
            word.upper(),
            word.title(),
            word.capitalize()
        }
    
    def _add_suffixes(self, word):
        """Adiciona sufixos comuns"""
        variations = set()
        for suffix in self.COMMON_SUFFIXES:
            variations.add(word + suffix)
            variations.add(word.lower() + suffix)
            variations.add(word.upper() + suffix)
        return variations
    
    def _leet_speak(self, word):
        """Gera variações de leet speak"""
        variations = {word.lower()}
        
        # Para cada letra que tem substituição leet
        for char, replacements in self.LEET_MAPS.items():
            new_variations = set()
            for variant in variations:
                for replacement in replacements:
                    new_variations.add(variant.replace(char, replacement))
            variations.update(new_variations)
        
        # Limitar para evitar explosão combinatória
        return list(variations)[:50]
    
    def _normalize_variations(self, word):
        """Remove acentos e espaços"""
        variations = set()
        
        # Sem acentos
        no_accents = self.remover_acentos(word)
        variations.add(no_accents)
        variations.add(no_accents.lower())
        variations.add(no_accents.upper())
        
        # Sem acentos e sem espaços
        no_spaces = no_accents.replace(' ', '')
        variations.add(no_spaces)
        variations.add(no_spaces.lower())
        variations.add(no_spaces.upper())
        
        # Original sem espaços (com acentos)
        variations.add(word.replace(' ', ''))
        
        return variations
    
    def combine_words(self, word1, word2):
        """Combina duas palavras com diferentes separadores"""
        combinations = set()
        
        w1_variants = [word1, word1.lower(), word1.capitalize()]
        w2_variants = [word2, word2.lower(), word2.capitalize()]
        
        for w1 in w1_variants:
            for w2 in w2_variants:
                for sep in self.SEPARATORS:
                    combinations.add(f"{w1}{sep}{w2}")
        
        return list(combinations)
    
    def expand_wordlist(self, words):
        """
        Expande uma lista de palavras com todas as variações
        """
        expanded = set()
        
        print(f"🔄 Expandindo {len(words)} palavras base...")
        
        for word in words:
            word = word.strip()
            if not word:
                continue
            
            # Gera variações
            variations = self.generate_all_variations(word)
            expanded.update(variations)
        
        # Combinar pares de palavras (opcional, mas muito forte)
        # Limitado para evitar explosão
        word_list = list(words)[:10]  # Pegar só as 10 primeiras para combinar
        for i, w1 in enumerate(word_list):
            for w2 in word_list[i+1:i+3]:  # Combinar com próximas 2
                combinations = self.combine_words(w1, w2)
                expanded.update(combinations)
        
        result = sorted(expanded)
        print(f"✅ Geradas {len(result)} variações únicas!")
        return result


if __name__ == "__main__":
    # Teste
    gen = WordlistGenerator()
    
    test_words = ["Moira", "Bruxa Biótica", "Runas"]
    
    print("Testando gerador de wordlist...")
    print(f"Palavras de entrada: {test_words}\n")
    
    expanded = gen.expand_wordlist(test_words)
    
    print(f"\nPrimeiras 50 variações geradas:")
    for i, word in enumerate(expanded[:50], 1):
        print(f"{i}. {word}")
    
    print(f"\n... e mais {len(expanded) - 50} variações.")
