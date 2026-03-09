"""
DaVinci Decoder - Pattern Detection Helper
Detecta padrões em ciphertext para priorizar algoritmos
"""
import re
from typing import List, Dict, Tuple


class PatternDetector:
    """Detecta padrões comuns em ciphertext para priorizar decoders"""
    
    @staticmethod
    def detect_patterns(ciphertext: str) -> Dict[str, float]:
        """
        Detecta padrões e retorna probabilidades para cada categoria
        Retorna: {pattern_name: probability (0-1)}
        """
        patterns = {}
        text = ciphertext.strip()
        
        # Base64: alfanumérico + /+ e padding opcional com =
        if re.match(r'^[A-Za-z0-9+/]+={0,2}$', text) and len(text) % 4 == 0:
            patterns['base64'] = 0.9
        elif re.match(r'^[A-Za-z0-9+/]+$', text):
            patterns['base64'] = 0.7
        
        # Base64 URL-Safe: alfanumérico + -_
        if re.match(r'^[A-Za-z0-9_-]+$', text):
            patterns['base64url'] = 0.8
        
        # Hex: apenas 0-9a-fA-F
        if re.match(r'^[0-9a-fA-F]+$', text):
            if len(text) == 32:
                patterns['md5'] = 0.9
            elif len(text) == 40:
                patterns['sha1'] = 0.9
            elif len(text) == 64:
                patterns['sha256'] = 0.9
            else:
                patterns['hex'] = 0.85
        
        # URL Encoding: % seguido de hex
        if '%' in text and re.search(r'%[0-9A-Fa-f]{2}', text):
            patterns['url'] = 0.9
        
        # HTML Entities: &xxx;
        if '&' in text and ';' in text and re.search(r'&[a-zA-Z0-9#]+;', text):
            patterns['html'] = 0.9
        
        # Binary: apenas 0 e 1
        if re.match(r'^[01]+$', text):
            patterns['binary'] = 0.95
        
        # Octal: apenas 0-7
        if re.match(r'^[0-7]+$', text) and len(text) > 6:
            patterns['octal'] = 0.8
        
        # Morse: apenas .- e espaços
        if re.match(r'^[\.\-\s/]+$', text):
            patterns['morse'] = 0.95
        
        # Base32: A-Z2-7 e padding =
        if re.match(r'^[A-Z2-7]+=*$', text) and len(text) % 8 == 0:
            patterns['base32'] = 0.9
        
        # ROT13/Caesar: letras com distribuição incomum
        if text.isalpha():
            patterns['caesar'] = 0.5
            patterns['rot13'] = 0.5
            patterns['vigenere'] = 0.4
        
        # AES/Cifras binárias: Base64 de binário (múltiplo de 16 bytes)
        if patterns.get('base64', 0) > 0.7:
            try:
                import base64
                decoded = base64.b64decode(text)
                if len(decoded) % 16 == 0 and len(decoded) >= 16:
                    patterns['aes'] = 0.6
                    patterns['des'] = 0.5
            except:
                pass
        
        return patterns
    
    @staticmethod
    def get_priority_algorithms(patterns: Dict[str, float]) -> List[Tuple[str, float]]:
        """
        Retorna lista de algoritmos priorizados baseado nos padrões
        Retorna: [(algorithm_name, priority_score)]
        """
        priorities = []
        
        # Mapeamento padrão -> algoritmos
        pattern_to_algorithms = {
            'base64': [
                ('Base64 Encoding', 0.95),
                ('Base64 URL-Safe Encoding', 0.8)
            ],
            'base64url': [
                ('Base64 URL-Safe Encoding', 0.95),
                ('Base64 Encoding', 0.7)
            ],
            'hex': [
                ('Hex Encoding', 0.95)
            ],
            'md5': [
                ('MD5 Hash', 0.95)
            ],
            'sha1': [
                ('SHA-1 Hash', 0.95)
            ],
            'sha256': [
                ('SHA-256 Hash', 0.95)
            ],
            'url': [
                ('URL Encoding', 0.95)
            ],
            'html': [
                ('HTML Entity Encoding', 0.95)
            ],
            'binary': [
                ('Binary Encoding', 0.95)
            ],
            'octal': [
                ('Octal Encoding', 0.9)
            ],
            'morse': [
                ('Morse Code', 0.95)
            ],
            'base32': [
                ('Base32 Encoding', 0.95)
            ],
            'caesar': [
                ('Caesar Cipher', 0.7),
                ('ROT13 Cipher', 0.6),
                ('Atbash Cipher', 0.5)
            ],
            'rot13': [
                ('ROT13 Cipher', 0.8),
                ('Caesar Cipher', 0.7)
            ],
            'vigenere': [
                ('Vigenere Cipher', 0.6),
                ('Beaufort Cipher', 0.5)
            ],
            'aes': [
                ('AES-256-CBC', 0.6),
                ('AES-128-CBC', 0.6),
                ('AES-256-ECB', 0.5)
            ]
        }
        
        # Coletar algoritmos baseado nos padrões detectados
        algorithm_scores = {}
        for pattern, prob in patterns.items():
            if pattern in pattern_to_algorithms:
                for algo_name, base_priority in pattern_to_algorithms[pattern]:
                    # Score = probabilidade do padrão * prioridade base
                    score = prob * base_priority
                    if algo_name in algorithm_scores:
                        algorithm_scores[algo_name] = max(algorithm_scores[algo_name], score)
                    else:
                        algorithm_scores[algo_name] = score
        
        # Ordenar por score
        priorities = sorted(algorithm_scores.items(), key=lambda x: x[1], reverse=True)
        
        return priorities


def boost_confidence(base_confidence: float, algorithm_name: str, 
                     ciphertext: str, has_wordlist: bool) -> float:
    """
    Aplica boost ou penalty na confiança baseado em contexto
    """
    confidence = base_confidence
    
    # Boost para encodings que combinam com padrão
    detector = PatternDetector()
    patterns = detector.detect_patterns(ciphertext)
    
    # Boost para algoritmos que combinam com padrão detectado
    if 'Base64' in algorithm_name and patterns.get('base64', 0) > 0.7:
        confidence += 20
    elif 'Hex' in algorithm_name and patterns.get('hex', 0) > 0.8:
        confidence += 20
    elif 'URL' in algorithm_name and patterns.get('url', 0) > 0.8:
        confidence += 20
    elif 'HTML' in algorithm_name and patterns.get('html', 0) > 0.8:
        confidence += 20
    elif 'Binary' in algorithm_name and patterns.get('binary', 0) > 0.9:
        confidence += 25
    elif 'Morse' in algorithm_name and patterns.get('morse', 0) > 0.9:
        confidence += 25
    
    # MUDANÇA IMPORTANTE: Se tem wordlist, BOOST cifras em vez de penalty!
    if has_wordlist:
        # Boost para cifras modernas (usuário forneceu senha)
        if 'AES' in algorithm_name or 'DES' in algorithm_name:
            confidence += 40  # Grande boost quando tem wordlist
        elif 'Blowfish' in algorithm_name or 'Twofish' in algorithm_name:
            confidence += 35
        elif 'RC4' in algorithm_name or 'ChaCha' in algorithm_name:
            confidence += 30
        
        # Pequeno penalty para encodings (preferir cifras quando tem senha)
        if algorithm_name in ['Base64 Encoding', 'Hex Encoding', 'URL Encoding']:
            confidence -= 10  # Leve penalty
    else:
        # SEM wordlist: penalty para cifras
        if 'AES' in algorithm_name or 'DES' in algorithm_name:
            confidence -= 30
        elif 'Blowfish' in algorithm_name or 'Twofish' in algorithm_name:
            confidence -= 30
        elif 'RC4' in algorithm_name or 'ChaCha' in algorithm_name:
            confidence -= 25
    
    # Penalty para cifras clássicas com texto curto
    if len(ciphertext) < 20:
        if 'Vigenere' in algorithm_name or 'Playfair' in algorithm_name:
            confidence -= 15
    
    # Garantir range 0-100
    return max(0, min(confidence, 100))


if __name__ == "__main__":
    # Testes
    detector = PatternDetector()
    
    test_cases = [
        ("SGVsbG8gV29ybGQh", "Base64"),
        ("48656c6c6f20576f726c6421", "Hex"),
        ("Hello%20World", "URL"),
        (".... . .-.. .-.. ---", "Morse"),
        ("5d41402abc4b2a76b9719d911017c592", "MD5"),
    ]
    
    print("Pattern Detection Tests:")
    print("=" * 70)
    for text, expected in test_cases:
        patterns = detector.detect_patterns(text)
        priorities = detector.get_priority_algorithms(patterns)
        print(f"\nInput: {text[:50]}")
        print(f"Expected: {expected}")
        print(f"Patterns: {dict(list(patterns.items())[:3])}")
        print(f"Top priority: {priorities[0] if priorities else 'None'}")
