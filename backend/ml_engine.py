"""
DaVinci Decoder - Machine Learning Engine
Sistema de aprendizado para classificação automática de cifras
"""
import numpy as np
import pickle
import os
from collections import Counter
from typing import List, Dict, Tuple
import string

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  scikit-learn não instalado. Execute: pip install scikit-learn")


class CipherMLEngine:
    """
    Motor de Machine Learning para classificação de cifras
    Usa Random Forest com features extraídas do ciphertext
    """
    
    def __init__(self, model_path='ml_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.label_encoder = {}
        self.reverse_encoder = {}
        self.is_trained = False
        
        # Carregar modelo se existir
        if os.path.exists(model_path):
            self.load_model()
    
    # ========== FEATURE EXTRACTION ==========
    
    def extract_features(self, ciphertext: str) -> np.array:
        """
        Extrai 25 features do ciphertext para classificação
        
        Features:
        1-8: Estatísticas básicas
        9-16: Análise de charset
        17-20: N-grams
        21-25: Padrões específicos
        """
        features = []
        
        if not ciphertext:
            return np.zeros(25)
        
        # 1. Tamanho
        features.append(len(ciphertext))
        
        # 2. Entropia Shannon
        entropy = self._calculate_entropy(ciphertext)
        features.append(entropy)
        
        # 3. Espaços ratio
        space_ratio = ciphertext.count(' ') / len(ciphertext) if len(ciphertext) > 0 else 0
        features.append(space_ratio)
        
        # 4. Uppercase ratio
        upper_ratio = sum(1 for c in ciphertext if c.isupper()) / len(ciphertext) if len(ciphertext) > 0 else 0
        features.append(upper_ratio)
        
        # 5. Lowercase ratio
        lower_ratio = sum(1 for c in ciphertext if c.islower()) / len(ciphertext) if len(ciphertext) > 0 else 0
        features.append(lower_ratio)
        
        # 6. Digits ratio
        digit_ratio = sum(1 for c in ciphertext if c.isdigit()) / len(ciphertext) if len(ciphertext) > 0 else 0
        features.append(digit_ratio)
        
        # 7. Special chars ratio
        special_ratio = sum(1 for c in ciphertext if not c.isalnum() and c != ' ') / len(ciphertext) if len(ciphertext) > 0 else 0
        features.append(special_ratio)
        
        # 8. Caracteres únicos
        unique_chars = len(set(ciphertext))
        features.append(unique_chars)
        
        # 9-12. Charset detection
        is_base64 = 1 if self._is_base64_like(ciphertext) else 0
        is_hex = 1 if self._is_hex_like(ciphertext) else 0
        is_binary = 1 if self._is_binary_like(ciphertext) else 0
        is_morse = 1 if '-' in ciphertext and '.' in ciphertext else 0
        features.extend([is_base64, is_hex, is_binary, is_morse])
        
        # 13. Block size (múltiplo de 8, 16, 32)
        is_block_8 = 1 if len(ciphertext) % 8 == 0 else 0
        is_block_16 = 1 if len(ciphertext) % 16 == 0 else 0
        is_block_32 = 1 if len(ciphertext) % 32 == 0 else 0
        features.extend([is_block_8, is_block_16, is_block_32])
        
        # 16. Comprimento médio de palavras
        words = ciphertext.split()
        avg_word_len = np.mean([len(w) for w in words]) if words else 0
        features.append(avg_word_len)
        
        # 17-19. Top 3 caracteres mais comuns
        char_freq = Counter(ciphertext.replace(' ', ''))
        top_chars = char_freq.most_common(3)
        for i in range(3):
            if i < len(top_chars):
                # Normalizar frequência
                freq = top_chars[i][1] / len(ciphertext) if len(ciphertext) > 0 else 0
                features.append(freq)
            else:
                features.append(0)
        
        # 20. Repetições de blocos (ECB pattern)
        block_repeat_score = self._detect_repeating_blocks(ciphertext)
        features.append(block_repeat_score)
        
        # 21-22. Bigram entropy
        bigram_entropy = self._calculate_bigram_entropy(ciphertext)
        trigram_entropy = self._calculate_trigram_entropy(ciphertext)
        features.extend([bigram_entropy, trigram_entropy])
        
        # 23. Ratio alfabético
        alpha_ratio = sum(1 for c in ciphertext if c.isalpha()) / len(ciphertext) if len(ciphertext) > 0 else 0
        features.append(alpha_ratio)
        
        # 24. Index of Coincidence (IoC)
        ioc = self._calculate_ioc(ciphertext)
        features.append(ioc)
        
        # 25. Padrão de padding (=, %, etc)
        has_padding = 1 if ciphertext.endswith('=') or ciphertext.endswith('%') else 0
        features.append(has_padding)
        
        return np.array(features)
    
    def _calculate_entropy(self, text: str) -> float:
        """Calcula entropia Shannon"""
        if not text:
            return 0
        
        freq = Counter(text)
        entropy = 0
        total = len(text)
        
        for count in freq.values():
            p = count / total
            entropy -= p * np.log2(p)
        
        return entropy
    
    def _calculate_ioc(self, text: str) -> float:
        """Calcula Index of Coincidence"""
        text = ''.join(c for c in text if c.isalpha()).upper()
        if len(text) < 2:
            return 0
        
        freq = Counter(text)
        n = len(text)
        
        ioc = sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))
        return ioc
    
    def _calculate_bigram_entropy(self, text: str) -> float:
        """Entropia de bigramas"""
        if len(text) < 2:
            return 0
        
        bigrams = [text[i:i+2] for i in range(len(text)-1)]
        freq = Counter(bigrams)
        
        entropy = 0
        total = len(bigrams)
        
        for count in freq.values():
            p = count / total
            entropy -= p * np.log2(p)
        
        return entropy
    
    def _calculate_trigram_entropy(self, text: str) -> float:
        """Entropia de trigramas"""
        if len(text) < 3:
            return 0
        
        trigrams = [text[i:i+3] for i in range(len(text)-2)]
        freq = Counter(trigrams)
        
        entropy = 0
        total = len(trigrams)
        
        for count in freq.values():
            p = count / total
            entropy -= p * np.log2(p)
        
        return entropy
    
    def _is_base64_like(self, text: str) -> bool:
        """Verifica se parece Base64"""
        base64_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        text_chars = set(text.replace(' ', '').replace('\n', ''))
        return len(text_chars - base64_chars) == 0 and len(text) % 4 == 0
    
    def _is_hex_like(self, text: str) -> bool:
        """Verifica se parece Hexadecimal"""
        hex_chars = set('0123456789ABCDEFabcdef')
        text_chars = set(text.replace(' ', '').replace('\n', ''))
        return len(text_chars - hex_chars) == 0
    
    def _is_binary_like(self, text: str) -> bool:
        """Verifica se parece Binário"""
        binary_chars = set('01 ')
        text_chars = set(text)
        return len(text_chars - binary_chars) == 0
    
    def _detect_repeating_blocks(self, text: str, block_size: int = 16) -> float:
        """Detecta blocos repetidos (padrão ECB)"""
        if len(text) < block_size * 2:
            return 0
        
        blocks = [text[i:i+block_size] for i in range(0, len(text), block_size)]
        unique_blocks = len(set(blocks))
        total_blocks = len(blocks)
        
        if total_blocks == 0:
            return 0
        
        # Score: quanto MENOR, mais repetições (mais provável ECB)
        return unique_blocks / total_blocks
    
    # ========== TRAINING ==========
    
    def train(self, training_data: List[Tuple[str, str]], test_size: float = 0.2):
        """
        Treina o modelo com dados de treinamento
        
        Args:
            training_data: Lista de (ciphertext, label)
            test_size: Proporção para teste (0.2 = 20%)
        """
        if not ML_AVAILABLE:
            print("❌ scikit-learn não está instalado!")
            return
        
        print("🤖 Iniciando treinamento do modelo ML...")
        print(f"📊 Total de exemplos: {len(training_data)}")
        
        # Extrair features
        X = []
        y = []
        
        for ciphertext, label in training_data:
            features = self.extract_features(ciphertext)
            X.append(features)
            y.append(label)
        
        X = np.array(X)
        y = np.array(y)
        
        # Criar encoder de labels
        unique_labels = list(set(y))
        self.label_encoder = {label: i for i, label in enumerate(unique_labels)}
        self.reverse_encoder = {i: label for label, i in self.label_encoder.items()}
        
        # Converter labels para números
        y_encoded = np.array([self.label_encoder[label] for label in y])
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=42
        )
        
        print(f"🎓 Treinamento: {len(X_train)} exemplos")
        print(f"🧪 Teste: {len(X_test)} exemplos")
        
        # Treinar Random Forest
        print("🌲 Treinando Random Forest...")
        self.model = RandomForestClassifier(
            n_estimators=100,  # 100 árvores
            max_depth=20,      # Profundidade máxima
            random_state=42,
            n_jobs=-1          # Usar todos os cores da CPU
        )
        
        self.model.fit(X_train, y_train)
        
        # Avaliar
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n✅ Treinamento completo!")
        print(f"📊 Acurácia: {accuracy*100:.1f}%")
        
        # Feature importance
        feature_names = self._get_feature_names()
        importances = self.model.feature_importances_
        top_features = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)[:5]
        
        print(f"\n🔝 Top 5 features mais importantes:")
        for name, importance in top_features:
            print(f"  • {name}: {importance:.3f}")
        
        self.is_trained = True
        
        # Salvar modelo
        self.save_model()
        print(f"\n💾 Modelo salvo em: {self.model_path}")
    
    def _get_feature_names(self) -> List[str]:
        """Nomes das 25 features"""
        return [
            "length", "entropy", "space_ratio", "upper_ratio", "lower_ratio",
            "digit_ratio", "special_ratio", "unique_chars", "is_base64", "is_hex",
            "is_binary", "is_morse", "is_block_8", "is_block_16", "is_block_32",
            "avg_word_len", "top_char_1", "top_char_2", "top_char_3",
            "block_repeat", "bigram_entropy", "trigram_entropy", "alpha_ratio",
            "ioc", "has_padding"
        ]
    
    # ========== PREDICTION ==========
    
    def predict(self, ciphertext: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Prediz o tipo de cifra
        
        Returns:
            Lista de (label, probabilidade) ordenada por probabilidade
        """
        if not self.is_trained or self.model is None:
            print("⚠️  Modelo não treinado!")
            return []
        
        # Extrair features
        features = self.extract_features(ciphertext).reshape(1, -1)
        
        # Predizer probabilidades
        probas = self.model.predict_proba(features)[0]
        
        # Ordenar por probabilidade
        sorted_indices = np.argsort(probas)[::-1][:top_n]
        
        results = []
        for idx in sorted_indices:
            label = self.reverse_encoder[idx]
            probability = probas[idx]
            results.append((label, probability))
        
        return results
    
    # ========== SAVE/LOAD ==========
    
    def save_model(self):
        """Salva o modelo treinado"""
        if self.model is None:
            return
        
        data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'reverse_encoder': self.reverse_encoder,
            'is_trained': self.is_trained
        }
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(data, f)
    
    def load_model(self):
        """Carrega modelo salvo"""
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
            
            self.model = data['model']
            self.label_encoder = data['label_encoder']
            self.reverse_encoder = data['reverse_encoder']
            self.is_trained = data['is_trained']
            
            print(f"✅ Modelo carregado de: {self.model_path}")
        except Exception as e:
            print(f"⚠️  Erro ao carregar modelo: {e}")


# ========== EXEMPLO DE USO ==========

if __name__ == '__main__':
    print("🤖 DaVinci Decoder - ML Engine")
    print("="*70)
    
    if not ML_AVAILABLE:
        print("\n❌ scikit-learn não instalado!")
        print("Execute: pip install scikit-learn")
    else:
        # Criar engine
        engine = CipherMLEngine()
        
        # Exemplo de features
        test_ciphertext = "SGVsbG8gV29ybGQh"
        features = engine.extract_features(test_ciphertext)
        
        print(f"\n📊 Features extraídas de '{test_ciphertext}':")
        print(f"   Entropia: {features[1]:.2f}")
        print(f"   Parece Base64: {'Sim' if features[8] == 1 else 'Não'}")
        print(f"   Tamanho: {int(features[0])}")
        print(f"   IoC: {features[23]:.4f}")
        
        print(f"\n💡 Use train_ml.py para treinar o modelo!")
