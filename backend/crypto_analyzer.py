"""
Módulo de Análise Criptográfica
Analisa características do ciphertext e sugere algoritmos prováveis
"""
import math
from collections import Counter

class CryptoAnalyzer:
    def __init__(self):
        # Block sizes comuns (em bytes)
        self.BLOCK_SIZES = {
            8: ["DES", "3DES", "Blowfish"],
            16: ["AES", "Blowfish (modo 128-bit)"]
        }
    
    def analyze_ciphertext(self, ciphertext_bytes):
        """
        Análise completa do ciphertext
        Retorna dicionário com informações e sugestões
        """
        size = len(ciphertext_bytes)
        entropy = self.calculate_entropy(ciphertext_bytes)
        has_patterns = self.detect_block_patterns(ciphertext_bytes)
        suggested_algos = self.suggest_algorithms(size)
        
        return {
            "tamanho": size,
            "tamanho_bits": size * 8,
            "entropia": round(entropy, 3),
            "entropia_max": 8.0,  # Máximo para bytes
            "aleatoriedade": "Alta" if entropy > 7.5 else "Média" if entropy > 6.5 else "Baixa",
            "padroes_repetidos": has_patterns,
            "provavel_modo": "ECB (blocos repetidos detectados)" if has_patterns else "CBC/ECB",
            "block_size_provavel": self._detect_block_size(size),
            "algoritmos_sugeridos": suggested_algos,
            "multiplo_de_8": size % 8 == 0,
            "multiplo_de_16": size % 16 == 0
        }
    
    def calculate_entropy(self, data):
        """
        Calcula entropia de Shannon (em bits por byte)
        Entropia alta (~8) = muito aleatório (bom para cifra)
        Entropia baixa (~4-5) = padrões detectáveis
        """
        if not data:
            return 0.0
        
        # Contar frequência de cada byte
        counter = Counter(data)
        length = len(data)
        
        # Calcular entropia
        entropy = 0.0
        for count in counter.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def detect_block_patterns(self, data, block_size=16):
        """
        Detecta blocos repetidos (indicativo de ECB)
        """
        if len(data) < block_size * 2:
            return False
        
        blocks = [data[i:i+block_size] for i in range(0, len(data), block_size)]
        
        # Se houver blocos duplicados, provavelmente é ECB
        return len(blocks) != len(set(blocks))
    
    def _detect_block_size(self, size):
        """Tenta detectar block size baseado no tamanho"""
        if size % 16 == 0:
            return 16
        elif size % 8 == 0:
            return 8
        else:
            return None
    
    def suggest_algorithms(self, size):
        """
        Sugere algoritmos baseado no tamanho do ciphertext
        """
        suggestions = []
        
        if size % 16 == 0:
            suggestions.append({
                "nome": "AES",
                "variantes": ["AES-128-ECB", "AES-256-ECB", "AES-128-CBC", "AES-256-CBC"],
                "prioridade": "ALTA",
                "razao": "Tamanho múltiplo de 16 bytes (block size do AES)"
            })
            suggestions.append({
                "nome": "Blowfish",
                "variantes": ["Blowfish-ECB", "Blowfish-CBC"],
                "prioridade": "MÉDIA",
                "razao": "Compatível com block size de 8 ou 16 bytes"
            })
        
        if size % 8 == 0:
            suggestions.append({
                "nome": "3DES",
                "variantes": ["3DES-ECB", "3DES-CBC"],
                "prioridade": "MÉDIA",
                "razao": "Tamanho múltiplo de 8 bytes (block size do 3DES)"
            })
        
        # Se não temos múltiplos óbvios
        if not suggestions:
            suggestions.append({
                "nome": "Stream Cipher ou padding não-padrão",
                "variantes": ["Possível RC4", "ChaCha20", "ou padding customizado"],
                "prioridade": "BAIXA",
                "razao": "Tamanho não é múltiplo de block sizes comuns"
            })
        
        return suggestions
    
    def format_analysis_report(self, analysis):
        """
        Formata a análise em texto legível
        """
        report = []
        report.append("=" * 60)
        report.append("ANÁLISE AUTOMÁTICA DO CIPHERTEXT")
        report.append("=" * 60)
        report.append(f"📏 Tamanho: {analysis['tamanho']} bytes ({analysis['tamanho_bits']} bits)")
        report.append(f"📊 Entropia: {analysis['entropia']}/8.0 ({analysis['aleatoriedade']})")
        report.append(f"🔍 Padrões Repetidos: {'Sim (provável ECB)' if analysis['padroes_repetidos'] else 'Não detectados'}")
        report.append(f"🔢 Múltiplo de 8: {'Sim' if analysis['multiplo_de_8'] else 'Não'}")
        report.append(f"🔢 Múltiplo de 16: {'Sim' if analysis['multiplo_de_16'] else 'Não'}")
        
        if analysis['block_size_provavel']:
            report.append(f"📦 Block Size Provável: {analysis['block_size_provavel']} bytes")
        
        report.append("\n🎯 ALGORITMOS RECOMENDADOS (por prioridade):")
        for i, algo in enumerate(analysis['algoritmos_sugeridos'], 1):
            report.append(f"\n{i}. {algo['nome']} [{algo['prioridade']}]")
            report.append(f"   Variantes: {', '.join(algo['variantes'])}")
            report.append(f"   Razão: {algo['razao']}")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)


if __name__ == "__main__":
    # Teste simples
    import base64
    
    analyzer = CryptoAnalyzer()
    
    # Ciphertext do desafio
    b64 = "CObK1Hwdtqsf2mt3qFvbeU-SNAYNiOiIdqPAzors7zwrX6CFuqpLmZFkXQ7qsOzTGUIHM6uCacJYhyHl6vaYAw"
    b64 = b64.replace('-', '+').replace('_', '/')
    while len(b64) % 4 != 0:
        b64 += '='
    
    ciphertext = base64.b64decode(b64)
    
    analysis = analyzer.analyze_ciphertext(ciphertext)
    print(analyzer.format_analysis_report(analysis))
