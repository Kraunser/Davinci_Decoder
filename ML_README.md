# DaVinci Decoder - Machine Learning Engine

## Sistema de Aprendizado Automático

O DaVinci Decoder agora possui um **motor de Machine Learning** que aprende a classificar cifras automaticamente!

---

## O Que Foi Implementado

### 1. ML Engine (`backend/ml_engine.py`)
Motor de classificação com **Random Forest** e **25 features**

#### Features Extraídas:
1-8. **Estatísticas Básicas:**
 - Tamanho do texto
 - Entropia Shannon
 - Ratios (espaços, maiúsculas, minúsculas, dígitos, especiais)
 - Caracteres únicos

9-16. **Análise de Charset:**
 - É Base64?
 - É Hexadecimal?
 - É Binário?
 - É Morse?
 - Múltiplo de 8/16/32? (block ciphers)
 - Tamanho médio de palavras

17-20. **N-Grams:**
 - Top 3 caracteres mais frequentes
 - Entropia de bigramas
 - Entropia de trigramas
 - Blocos repetidos (ECB pattern)

21-25. **Padrões Específicos:**
 - Ratio alfabético
 - Index of Coincidence (IoC)
 - Tem padding (=, %)?

### 2. Script de Treinamento (`train_ml.py`)
Gera **dados sintéticos** e treina o modelo

#### Classes Suportadas (14):
- **Encodings:** Base64, Hex, Binary, URL, Morse
- **Clássicas:** Caesar, ROT13, Atbash, Reverse
- **Modernas:** AES
- **Hashes:** MD5, SHA1, SHA256

---

## Como Usar

### Passo 1: Instalar scikit-learn
```bash
pip install scikit-learn
```

### Passo 2: Treinar o Modelo
```bash
python train_ml.py
```

Isso vai:
1. Gerar 1.400 exemplos (100 por classe × 14 classes)
2. Extrair 25 features de cada
3. Treinar Random Forest com 100 árvores
4. Avaliar acurácia (esperado: >90%)
5. Salvar modelo em `backend/ml_model.pkl`

**Tempo:** 1-2 minutos usando CPU

### Passo 3: Usar para Classificação
```python
from backend.ml_engine import CipherMLEngine

# Carregar modelo treinado
engine = CipherMLEngine(model_path='backend/ml_model.pkl')

# Classificar
predictions = engine.predict("SGVsbG8gV29ybGQh", top_n=3)

for label, probability in predictions:
 print(f"{label}: {probability*100:.1f}%")
```

---

## Modelo Random Forest

### Configuração:
- **Algoritmo:** Random Forest Classifier
- **Árvores:** 100
- **Profundidade:** 20
- **CPU:** Usa todos os cores (-1)
- **Features:** 25
- **Classes:** 14

### Performance Esperada:
- **Acurácia:** >90% no conjunto de teste
- **Tempo de predição:** <10ms
- **Tamanho do modelo:** ~5-10 MB

---

## Integração com Auto-Detect

O modelo ML pode ser integrado no `decoder_manager.py` para:

1. **Pré-filtrar** algoritmos antes de testar
2. **Priorizar** decoders mais prováveis
3. **Reduzir** tempo de processamento
4. **Melhorar** acurácia geral

### Exemplo de Integração:
```python
def auto_detect_ml(self, ciphertext, wordlist):
 # 1. Usar ML para pré-classificar
 ml_predictions = self.ml_engine.predict(ciphertext, top_n=5)
 
 # 2. Filtrar decoders relevantes
 relevant_decoders = []
 for label, prob in ml_predictions:
  if prob > 0.1: # >10% probabilidade
   decoder = self.get_decoder_by_type(label)
   relevant_decoders.append((decoder, prob))
 
 # 3. Testar apenas decoders relevantes
 results = []
 for decoder, ml_prob in relevant_decoders:
  result = decoder.decrypt_with_keys(ciphertext, wordlist)
  if result:
   # Combinar ML probability com confidence
   combined_score = (ml_prob + result.confidence) / 2
   results.append((result, combined_score))
 
 return results
```

---

## Detalhes Técnicos

### Features Mais Importantes:
Após treinamento, geralmente são:
1. **Entropia** - Distingue hash vs texto
2. **IsBase64** - Detecta Base64
3. **IsHex** - Detecta Hexadecimal
4. **IoC** - Distingue cifras de substituição
5. **Bigram Entropy** - Padrões de linguagem

### Vantagens do Random Forest:
 Rápido para treinar e predizer 
 Não precisa de GPU 
 Robusto a outliers 
 Interpretável (feature importance) 
 Não requer normalização

---

## Expandindo o Sistema

### Adicionar Novas Classes:
1. Edite `generate_training_data()` em `train_ml.py`
2. Adicione lógica de geração para nova cifra
3. Re-treine o modelo

### Melhorar Acurácia:
- Aumentar `samples_per_class` (padrão: 100)
- Adicionar mais features específicas
- Usar ensemble de múltiplos modelos
- Treinar com dados reais (CTFs, exemplos)

### Usar GPU (opcional):
```python
# Com XGBoost (suporta GPU)
from xgboost import XGBClassifier

model = XGBClassifier(
 tree_method='gpu_hist', # Usar GPU
 n_estimators=100
)
```

---

## Conceitos de ML

### Supervisionado
O modelo **aprende** com exemplos rotulados:
- Input: Ciphertext
- Output: Tipo de cifra
- Aprende padrões que diferenciam cada tipo

### Random Forest
**Ensemble** de 100 árvores de decisão:
- Cada árvore vota
- Voto majoritário ganha
- Mais robusto que árvore única

### Features
Características **extraídas** do ciphertext:
- Não usa o texto cru
- Usa estatísticas e padrões
- 25 números por ciphertext

---

## Resultado Final

Após treinar, o sistema será capaz de:

 **Classificar** cifras com >90% de acurácia 
 **Priorizar** algoritmos mais prováveis 
 **Acelerar** auto-detecção (pula impossíveis) 
 **Aprender** novos padrões com re-treinamento 
 **Funcionar** 100% offline na CPU

---

## Próximos Passos

1. Execute `python train_ml.py`
2. Veja as predições de teste
3. Integre no `decoder_manager.py`
4. Teste com ciphertexts reais!

**Desenvolvido por: Matheus Bueno**

**Sistema agora é inteligente! **
