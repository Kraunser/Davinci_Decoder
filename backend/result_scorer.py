"""
Sistema de Scoring de Resultados
Valida e pontua textos decifrados para filtrar falsos positivos
"""
import re
import unicodedata

class ResultScorer:
    def __init__(self):
        # Distribuição de letras em Português (aproximada)
        self.PT_FREQ = {
            'a': 14.63, 'e': 12.57, 'o': 10.73, 's': 7.81, 'r': 6.53,
            'i': 6.18, 'n': 5.05, 'd': 4.99, 'm': 4.74, 'u': 4.63,
            't': 4.34, 'c': 3.88, 'l': 2.78, 'p': 2.52, 'v': 1.67
        }
        
        # Palavras muito comuns em português
        self.COMMON_WORDS = {
            'o', 'a', 'de', 'da', 'do', 'e', 'que', 'para', 'com', 'em',
            'um', 'uma', 'os', 'as', 'no', 'na', 'por', 'mais', 'se',
            'é', 'não', 'ao', 'são', 'dos', 'das', 'como', 'mas', 'foi'
        }
        
        # Palavras do tema Ordem Paranormal
        self.THEME_WORDS = {
            'mana', 'moira', 'runas', 'ritual', 'ordem', 'paranormal',
            'ocultismo', 'medo', 'sangue', 'conhecimento', 'energia',
            'arcano', 'elemento', 'bruxa', 'arcanista', 'grimório'
        }
    
    def score_plaintext(self, text):
        """
        Pontua um texto decifrado (0-100)
        >80 = Muito provável ser texto real
        50-80 = Possível
        <50 = Provavelmente lixo
        """
        if not text or len(text) < 3:
            return 0
        
        score = 0
        
        # 1. Caracteres imprimíveis (30 pontos)
        printable_score = self._score_printable_chars(text)
        score += printable_score * 30
        
        # 2. Distribuição de letras português (25 pontos)
        freq_score = self._score_letter_frequency(text)
        score += freq_score * 25
        
        # 3. Palavras comuns (25 pontos)
        word_score = self._score_common_words(text)
        score += word_score * 25
        
        # 4. Entropia baixa (10 pontos) - texto real tem menos entropia que lixo
        entropy_score = self._score_entropy(text)
        score += entropy_score * 10
        
        # 5. Palavras temáticas (10 pontos bônus)
        theme_score = self._score_theme_words(text)
        score += theme_score * 10
        
        return min(100, int(score))
    
    def _score_printable_chars(self, text):
        """Porcentagem de caracteres imprimíveis"""
        printable = sum(1 for c in text if 32 <= ord(c) <= 126 or c in '\n\r\t')
        return printable / len(text)
    
    def _score_letter_frequency(self, text):
        """
        Compara distribuição de letras com português
        Retorna 0-1
        """
        # Normalizar: remover acentos e tornar minúsculo
        normalized = ''.join(c for c in unicodedata.normalize('NFD', text.lower()) 
                           if unicodedata.category(c) != 'Mn')
        
        # Contar apenas letras
        letters = [c for c in normalized if c.isalpha()]
        if not letters:
            return 0
        
        # Calcular distribuição
        total = len(letters)
        text_freq = {}
        for letter in letters:
            text_freq[letter] = text_freq.get(letter, 0) + 1
        
        # Comparar com português (usando distância euclidiana invertida)
        distance = 0
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            expected = self.PT_FREQ.get(letter, 0.5)
            actual = (text_freq.get(letter, 0) / total) * 100
            distance += (expected - actual) ** 2
        
        # Normalizar (distância 0 = perfeito, >1000 = muito diferente)
        similarity = max(0, 1 - (distance / 1000))
        return similarity
    
    def _score_common_words(self, text):
        """Detecta palavras comuns em português"""
        words = re.findall(r'\w+', text.lower())
        if not words:
            return 0
        
        common_count = sum(1 for word in words if word in self.COMMON_WORDS)
        return min(1, common_count / max(1, len(words) * 0.3))
    
    def _score_entropy(self, text):
        """
        Texto real tem entropia moderada (4-6 bits/char)
        Lixo binário tem entropia muito alta (~8)
        """
        from collections import Counter
        import math
        
        if not text:
            return 0
        
        counter = Counter(text)
        length = len(text)
        entropy = 0.0
        
        for count in counter.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        # Entropia ideal para texto: 4-6 bits
        if 4 <= entropy <= 6:
            return 1.0
        elif 3 <= entropy <= 7:
            return 0.7
        else:
            return 0.3
    
    def _score_theme_words(self, text):
        """Detecta palavras do tema (bônus)"""
        words = re.findall(r'\w+', text.lower())
        theme_count = sum(1 for word in words if word in self.THEME_WORDS)
        return min(1, theme_count / 2)  # Máximo 2 palavras temáticas = 100%
    
    def is_valid_result(self, text, min_score=60):
        """
        Retorna True se o texto parece válido
        """
        score = self.score_plaintext(text)
        return score >= min_score
    
    def format_result(self, text, score):
        """Formata resultado com cor baseada no score"""
        if score >= 80:
            emoji = "✅"
            status = "ALTA CONFIANÇA"
        elif score >= 60:
            emoji = "⚠️"
            status = "CONFIANÇA MÉDIA"
        else:
            emoji = "❌"
            status = "BAIXA CONFIANÇA"
        
        return f"{emoji} Score: {score}/100 [{status}]\n   Texto: {text[:100]}{'...' if len(text) > 100 else ''}"


if __name__ == "__main__":
    # Testes
    scorer = ResultScorer()
    
    test_cases = [
        ("Parabéns, você conseguiu decifrar o código secreto da Ordem!", "Texto válido em português"),
        ("A mana flui através das runas ancestrais de Moira", "Texto temático"),
        ("asdjfk23k4j5h234kjh5k23j4h5k", "Lixo aleatório"),
        ("AAAAAAAAAAAAAAAAAAAAAAAAA", "Padrão repetitivo"),
        ("\x00\x01\x02\x03\x04\x05", "Bytes binários"),
    ]
    
    print("TESTANDO SISTEMA DE SCORING\n")
    print("=" * 70)
    
    for text, description in test_cases:
        score = scorer.score_plaintext(text)
        print(f"\n{description}:")
        print(f"   Input: {repr(text[:50])}")
        print(f"   {scorer.format_result(text, score)}")
    
    print("\n" + "=" * 70)
