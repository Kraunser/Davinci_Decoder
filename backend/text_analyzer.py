"""
DaVinci Decoder - Text Quality Analyzer
Analisa qualidade e estrutura de texto para determinar se é legível
"""
import math
from collections import Counter
from typing import Dict, Tuple


class TextAnalyzer:
    """Analisa qualidade de texto decifrado"""
    
    # Palavras comuns em português e inglês
    COMMON_WORDS_PT = [
        'o', 'a', 'de', 'que', 'e', 'do', 'da', 'em', 'um', 'para',
        'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais',
        'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à',
        'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está',
        'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era',
        'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem', 'nas', 'me', 'esse'
    ]
    
    COMMON_WORDS_EN = [
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
        'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me'
    ]
    
    COMMON_WORDS = set(COMMON_WORDS_PT + COMMON_WORDS_EN)
    
    COMMON_BIGRAMS = [
        # Inglês
        'th', 'he', 'in', 'er', 'an', 'ed', 'nd', 'ha', 'at', 'en',
        'es', 'of', 'nt', 'on', 'it', 're', 'st', 'ng', 'ar', 'al',
        # Português
        'de', 'os', 'as', 'qu', 'ra', 'en', 'te', 'ão', 'ar', 'me',
        'nt', 'es', 'da', 'co', 'ca', 'ma', 'ta', 'do', 'pa', 'to'
    ]
    
    @staticmethod
    def calculate_quality(text: str) -> float:
        """
        Calcula qualidade do texto (0-100)
        Baseado em múltiplos critérios de legibilidade
        """
        if not text or len(text) < 3:
            return 0.0
        
        score = 0.0
        
        # 1. Caracteres imprimíveis (20 pontos)
        printable_count = sum(1 for c in text if 32 <= ord(c) <= 126 or c in '\n\r\t')
        printable_ratio = printable_count / len(text)
        score += printable_ratio * 20
        
        # Se menos de 80% imprimível, penalizar fortemente
        if printable_ratio < 0.8:
            return score * 0.5  # Metade do score
        
        # 2. Presença de espaços (15 pontos)
        space_count = text.count(' ')
        if len(text) > 0:
            space_ratio = space_count / len(text)
            # Texto normal: ~12-18% espaços
            if 0.12 <= space_ratio <= 0.18:
                score += 15
            elif 0.08 <= space_ratio <= 0.25:
                score += 10
            elif 0.05 <= space_ratio <= 0.30:
                score += 5
        
        # 3. Palavras reais (25 pontos)
        words = [w.strip('.,!?;:"\'-()[]{}').lower() for w in text.split()]
        words = [w for w in words if len(w) > 0]
        
        if len(words) > 0:
            real_words = sum(1 for w in words if w in TextAnalyzer.COMMON_WORDS)
            word_ratio = real_words / len(words)
            score += word_ratio * 25
        
        # 4. Entropia adequada (15 pontos)
        entropy = TextAnalyzer.calculate_entropy(text)
        # Texto natural: 3.5-5.5 bits
        if 3.5 <= entropy <= 5.5:
            score += 15
        elif 3.0 <= entropy <= 6.0:
            score += 10
        elif 2.5 <= entropy <= 6.5:
            score += 5
        
        # 5. Pontuação (10 pontos)
        punctuation = '.!?,;:"\'-'
        punct_count = sum(1 for c in text if c in punctuation)
        if punct_count > 0:
            punct_ratio = punct_count / len(text)
            if 0.01 <= punct_ratio <= 0.10:
                score += 10
            elif 0.005 <= punct_ratio <= 0.15:
                score += 5
        
        # 6. Maiúsculas/minúsculas balanceadas (10 pontos)
        upper = sum(1 for c in text if c.isupper())
        lower = sum(1 for c in text if c.islower())
        if upper + lower > 0:
            upper_ratio = upper / (upper + lower)
            # Normal: 5-15% maiúsculas
            if 0.05 <= upper_ratio <= 0.15:
                score += 10
            elif 0.02 <= upper_ratio <= 0.25:
                score += 5
        
        # 7. Bigramas comuns (5 pontos)
        text_lower = text.lower()
        bigram_matches = sum(1 for bg in TextAnalyzer.COMMON_BIGRAMS if bg in text_lower)
        if bigram_matches >= 8:
            score += 5
        elif bigram_matches >= 5:
            score += 3
        elif bigram_matches >= 3:
            score += 1
        
        return min(score, 100.0)
    
    @staticmethod
    def calculate_entropy(text: str) -> float:
        """Calcula entropia de Shannon (bits por caractere)"""
        if not text:
            return 0.0
        
        # Contar frequência de cada caractere
        counter = Counter(text)
        length = len(text)
        
        # Calcular entropia
        entropy = 0.0
        for count in counter.values():
            if count > 0:
                probability = count / length
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    @staticmethod
    def is_readable(text: str, threshold: float = 70.0) -> bool:
        """Verifica se texto é legível"""
        quality = TextAnalyzer.calculate_quality(text)
        return quality >= threshold
    
    @staticmethod
    def is_binary(text: str) -> bool:
        """Verifica se parece dados binários"""
        # Se quality < 30 e tem muitos caracteres não-imprimíveis
        quality = TextAnalyzer.calculate_quality(text)
        if quality < 30:
            return True
        
        # Se tem muitos bytes nulos ou controle
        control_chars = sum(1 for c in text if ord(c) < 32 and c not in '\n\r\t')
        if control_chars / len(text) > 0.1:  # >10% caracteres de controle
            return True
        
        return False
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Detecta idioma provável (pt/en/unknown)"""
        words = [w.strip('.,!?;:"\'-()[]{}').lower() for w in text.split()]
        
        pt_count = sum(1 for w in words if w in TextAnalyzer.COMMON_WORDS_PT)
        en_count = sum(1 for w in words if w in TextAnalyzer.COMMON_WORDS_EN)
        
        if pt_count > en_count:
            return 'pt'
        elif en_count > pt_count:
            return 'en'
        else:
            return 'unknown'


if __name__ == "__main__":
    # Testes
    analyzer = TextAnalyzer()
    
    tests = [
        ("Hello World! This is a test.", "Texto inglês normal"),
        ("Olá mundo! Este é um teste.", "Texto português normal"),
        ("\x4e\x18\x8a\xe7\x09\x52", "Binário"),
        ("ABCDEFGHIJKLMNOP", "Texto sem espaços"),
        ("Esta é uma mensagem secreta com palavras reais e pontuação adequada!", "Texto de alta qualidade"),
    ]
    
    print("=" * 70)
    print("TESTES DE QUALIDADE DE TEXTO")
    print("=" * 70)
    
    for text, description in tests:
        quality = analyzer.calculate_quality(text)
        entropy = analyzer.calculate_entropy(text)
        is_readable = analyzer.is_readable(text)
        is_binary = analyzer.is_binary(text)
        language = analyzer.detect_language(text)
        
        print(f"\n{description}")
        print(f"Texto: {text[:50]}...")
        print(f"Quality: {quality:.1f}%")
        print(f"Entropy: {entropy:.2f} bits")
        print(f"Readable: {is_readable}")
        print(f"Binary: {is_binary}")
        print(f"Language: {language}")
