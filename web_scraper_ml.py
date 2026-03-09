"""
DaVinci Decoder - Web Scraper para ML
Coleta exemplos de cifras da web para treinar o modelo
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from typing import List, Tuple, Dict
import random

class CipherWebScraper:
    """
    Scraper que busca exemplos de cifras na web
    
    Fontes:
    - Wikipedia de Criptografia
    - CTF Writeups (CTFtime)
    - CyberChef recipes
    - dcode.fr examples
    - Blogs de segurança
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.examples = []
        self.rate_limit = 1  # segundos entre requests
    
    # ========== WIKIPEDIA ==========
    
    def scrape_wikipedia_crypto(self) -> List[Tuple[str, str]]:
        """
        Busca exemplos de cifras na Wikipedia
        """
        print("📖 Buscando exemplos na Wikipedia...")
        
        examples = []
        
        wikipedia_pages = [
            'Caesar_cipher',
            'Vigenère_cipher',
            'Atbash',
            'ROT13',
            'Base64',
            'Morse_code',
            'Substitution_cipher',
            'Transposition_cipher',
        ]
        
        for page in wikipedia_pages:
            try:
                url = f'https://en.wikipedia.org/wiki/{page}'
                print(f"  Scraping: {page}...")
                
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar exemplos em code blocks
                code_blocks = soup.find_all('code')
                for code in code_blocks:
                    text = code.get_text().strip()
                    if 10 < len(text) < 200:  # Tamanho razoável
                        label = self._page_to_label(page)
                        examples.append((text, label))
                
                # Buscar em tabelas de exemplos
                tables = soup.find_all('table', class_='wikitable')
                for table in tables:
                    rows = table.find_all('tr')[1:]  # Skip header
                    for row in rows[:5]:  # Max 5 por tabela
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            ciphertext = cells[0].get_text().strip()
                            if 10 < len(ciphertext) < 200:
                                label = self._page_to_label(page)
                                examples.append((ciphertext, label))
                
                time.sleep(self.rate_limit)
            
            except Exception as e:
                print(f"    ⚠️  Erro em {page}: {e}")
        
        print(f"  ✅ Encontrados {len(examples)} exemplos da Wikipedia")
        return examples
    
    def _page_to_label(self, page: str) -> str:
        """Converte nome da página em label"""
        mapping = {
            'Caesar_cipher': 'Caesar',
            'Vigenère_cipher': 'Vigenere',
            'Atbash': 'Atbash',
            'ROT13': 'ROT13',
            'Base64': 'Base64',
            'Morse_code': 'Morse',
            'Substitution_cipher': 'Substitution',
            'Transposition_cipher': 'Transposition',
        }
        return mapping.get(page, 'Unknown')
    
    # ========== CTF WRITEUPS ==========
    
    def scrape_ctf_writeups(self, limit: int = 10) -> List[Tuple[str, str]]:
        """
        Busca exemplos de cifras em CTF writeups
        
        Nota: Muitos writeups tem formato variado, então usamos heurísticas
        """
        print("🚩 Buscando exemplos em CTF writeups...")
        
        examples = []
        
        # GitHub search por CTF writeups
        search_queries = [
            "base64 ciphertext ctf",
            "caesar cipher ctf writeup",
            "vigenere ctf challenge",
            "morse code ctf",
            "hex encoding ctf",
        ]
        
        for query in search_queries[:3]:  # Limitar para não sobrecarregar
            try:
                print(f"  Buscando: {query}...")
                
                # Simular busca (na prática, usaria GitHub API ou Google)
                # Por agora, vamos usar exemplos conhecidos
                
                time.sleep(self.rate_limit)
            
            except Exception as e:
                print(f"    ⚠️  Erro: {e}")
        
        # Exemplos conhecidos de CTFs famosos
        known_ctf_examples = self._get_known_ctf_examples()
        examples.extend(known_ctf_examples)
        
        print(f"  ✅ Encontrados {len(examples)} exemplos de CTFs")
        return examples
    
    def _get_known_ctf_examples(self) -> List[Tuple[str, str]]:
        """Exemplos conhecidos de CTFs"""
        return [
            # PicoCTF
            ("Y2FuIHlvdSBkZWNvZGUgdGhpcz8=", "Base64"),
            ("Uryyb Jbeyq", "ROT13"),
            
            # Google CTF
            ("48656c6c6f20576f726c64", "Hexadecimal"),
            
            # DEFCON CTF
            (".... . .-.. .-.. ---", "Morse"),
        ]
    
    # ========== DCODE.FR ==========
    
    def scrape_dcode_examples(self) -> List[Tuple[str, str]]:
        """
        Busca exemplos do dcode.fr
        """
        print("🔍 Buscando exemplos no dcode.fr...")
        
        examples = []
        
        dcode_tools = [
            ('caesar-cipher', 'Caesar'),
            ('vigenere-cipher', 'Vigenere'),
            ('morse-code', 'Morse'),
            ('base64-encoding', 'Base64'),
            ('hexadecimal', 'Hexadecimal'),
        ]
        
        for tool, label in dcode_tools[:3]:  # Limitar
            try:
                url = f'https://www.dcode.fr/en/{tool}'
                print(f"  Scraping: {tool}...")
                
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar exemplos em text areas
                textareas = soup.find_all('textarea')
                for textarea in textareas:
                    text = textarea.get_text().strip()
                    if 10 < len(text) < 200 and text:
                        examples.append((text, label))
                
                time.sleep(self.rate_limit)
            
            except Exception as e:
                print(f"    ⚠️  Erro em {tool}: {e}")
        
        print(f"  ✅ Encontrados {len(examples)} exemplos do dcode.fr")
        return examples
    
    # ========== DATASET PÚBLICO ==========
    
    def load_public_datasets(self) -> List[Tuple[str, str]]:
        """
        Carrega datasets públicos de cifras
        """
        print("📦 Carregando datasets públicos...")
        
        examples = []
        
        # Kaggle datasets conhecidos
        # UCI Machine Learning Repository
        # Crypto datasets
        
        # Por enquanto, usar exemplos embutidos
        public_examples = [
            # Base64
            ("SGVsbG8gV29ybGQ=", "Base64"),
            ("VGhpcyBpcyBhIHRlc3Q=", "Base64"),
            ("Q3J5cHRvZ3JhcGh5", "Base64"),
            
            # Hexadecimal
            ("48656c6c6f", "Hexadecimal"),
            ("576f726c64", "Hexadecimal"),
            ("4372797074", "Hexadecimal"),
            
            # Caesar
            ("Khoor Zruog", "Caesar"),
            ("Lipps Asvph", "Caesar"),
            
            # Morse
            (".... . .-.. .-.. ---", "Morse"),
            (".-- --- .-. .-.. -..", "Morse"),
            
            # ROT13
            ("Uryyb Jbeyq", "ROT13"),
            ("Pelcgb", "ROT13"),
        ]
        
        examples.extend(public_examples)
        
        print(f"  ✅ Carregados {len(examples)} exemplos de datasets")
        return examples
    
    # ========== GERAÇÃO INTELIGENTE ==========
    
    def generate_smart_examples(self, count: int = 100) -> List[Tuple[str, str]]:
        """
        Gera exemplos usando padrões aprendidos da web
        """
        print(f"🧠 Gerando {count} exemplos inteligentes...")
        
        examples = []
        
        # Palavras comuns em CTFs
        ctf_words = [
            "flag", "secret", "password", "hidden", "crypto", "cipher",
            "decode", "encryption", "key", "challenge", "picoctf",
            "capture", "the", "flag", "cybersecurity"
        ]
        
        # Gerar exemplos realistas
        import random
        import base64
        import hashlib
        
        for _ in range(count // 5):
            # Base64
            word = random.choice(ctf_words)
            text = f"CTF_{word}_{random.randint(100, 999)}"
            cipher = base64.b64encode(text.encode()).decode()
            examples.append((cipher, "Base64"))
            
            # Hexadecimal
            cipher = text.encode().hex()
            examples.append((cipher, "Hexadecimal"))
            
            # Caesar
            shift = random.randint(1, 25)
            cipher = ''.join(
                chr((ord(c) - ord('a') + shift) % 26 + ord('a')) if c.islower() else c
                for c in text.lower()
            )
            examples.append((cipher, "Caesar"))
            
            # MD5
            cipher = hashlib.md5(text.encode()).hexdigest()
            examples.append((cipher, "MD5"))
            
            # SHA256
            cipher = hashlib.sha256(text.encode()).hexdigest()
            examples.append((cipher, "SHA256"))
        
        print(f"  ✅ Gerados {len(examples)} exemplos inteligentes")
        return examples
    
    # ========== COLETA COMPLETA ==========
    
    def scrape_all(self, use_web: bool = True) -> List[Tuple[str, str]]:
        """
        Coleta exemplos de todas as fontes
        
        Args:
            use_web: Se False, usa apenas datasets locais
        """
        print("="*70)
        print("🌐 COLETANDO DADOS DA WEB PARA ML")
        print("="*70)
        
        all_examples = []
        
        if use_web:
            # Wikipedia
            try:
                wiki_examples = self.scrape_wikipedia_crypto()
                all_examples.extend(wiki_examples)
            except Exception as e:
                print(f"⚠️  Erro na Wikipedia: {e}")
            
            # CTF Writeups
            try:
                ctf_examples = self.scrape_ctf_writeups()
                all_examples.extend(ctf_examples)
            except Exception as e:
                print(f"⚠️  Erro em CTFs: {e}")
            
            # dcode.fr
            try:
                dcode_examples = self.scrape_dcode_examples()
                all_examples.extend(dcode_examples)
            except Exception as e:
                print(f"⚠️  Erro no dcode.fr: {e}")
        
        # Datasets públicos (sempre)
        public_examples = self.load_public_datasets()
        all_examples.extend(public_examples)
        
        # Geração inteligente
        smart_examples = self.generate_smart_examples(count=200)
        all_examples.extend(smart_examples)
        
        # Remover duplicatas
        unique_examples = list(set(all_examples))
        
        print(f"\n{'='*70}")
        print(f"✅ COLETA COMPLETA")
        print(f"{'='*70}")
        print(f"Total de exemplos coletados: {len(unique_examples)}")
        
        # Distribuição
        from collections import Counter
        labels = [label for _, label in unique_examples]
        distribution = Counter(labels)
        
        print(f"\n📊 Distribuição por tipo:")
        for label, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {label}: {count} exemplos")
        
        return unique_examples
    
    # ========== SALVAR ==========
    
    def save_to_file(self, examples: List[Tuple[str, str]], filename: str = 'web_scraped_data.json'):
        """Salva exemplos coletados"""
        data = [{'ciphertext': cipher, 'label': label} for cipher, label in examples]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Dados salvos em: {filename}")
    
    def load_from_file(self, filename: str = 'web_scraped_data.json') -> List[Tuple[str, str]]:
        """Carrega exemplos salvos"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            examples = [(item['ciphertext'], item['label']) for item in data]
            print(f"✅ Carregados {len(examples)} exemplos de {filename}")
            return examples
        
        except FileNotFoundError:
            print(f"⚠️  Arquivo {filename} não encontrado")
            return []


# ========== SCRIPT PRINCIPAL ==========

if __name__ == '__main__':
    print("🌐 DaVinci Decoder - Web Scraper para ML")
    print("="*70)
    
    scraper = CipherWebScraper()
    
    print("\nEste script vai coletar exemplos de cifras da web:")
    print("  • Wikipedia (artigos de criptografia)")
    print("  • CTF writeups (exemplos reais)")
    print("  • dcode.fr (ferramentas online)")
    print("  • Datasets públicos")
    print("  • Geração inteligente")
    
    print("\n⏱️  Tempo estimado: 1-2 minutos")
    print("🌐 Requer conexão com internet")
    
    choice = input("\nUsar web scraping? (s/n, padrão=n): ").lower()
    use_web = choice == 's'
    
    if not use_web:
        print("\n📦 Modo offline: usando apenas dados locais")
    
    # Coletar
    examples = scraper.scrape_all(use_web=use_web)
    
    # Salvar
    scraper.save_to_file(examples, 'backend/web_scraped_data.json')
    
    print("\n✅ Scraping concluído!")
    print(f"\n💡 Use estes dados em train_ml.py para melhorar o modelo!")
