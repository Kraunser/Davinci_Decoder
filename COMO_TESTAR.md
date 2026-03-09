# 🔧 Como Testar o DaVinci Decoder

## ❌ Problema Identificado

Você está usando **demo.html** que é apenas uma **demonstração visual**. Ele não conecta com o backend Python real!

### demo.html = Apenas UI estática
- ✅ Mostra o design
- ❌ **NÃO** conecta com os 102 algoritmos
- ❌ **NÃO** detecta AES realmente
- ❌ Só simula Base64

---

## ✅ Solução: 3 Formas de Testar

### Opção 1: CLI (Mais Rápido) ⚡
```bash
cd davinci-decoder
python main.py
```

Então:
1. Escolha "1. Auto-Detect"
2. Cole o ciphertext
3. Digite senha(s) na wordlist
4. Veja os resultados!

---

### Opção 2: Python Direto 🐍
```python
import sys
sys.path.insert(0, 'backend')
from decoders import decoder_manager

# Testar com ciphertext AES
ciphertext = "seu_ciphertext_aqui"
wordlist = ["senha123", "password", "admin"]

results = decoder_manager.decrypt_auto(
    ciphertext=ciphertext,
    wordlist=wordlist,
    max_decoders=10
)

for r in results:
    print(f"✅ {r.algorithm}: {r.plaintext} ({r.confidence}%)")
```

---

### Opção 3: Interface Web Completa 🌐

#### Passo 1: Iniciar Servidor
```bash
python api_server.py
```

Aguarde até ver:
```
🚀 DaVinci Decoder API Server
✅ Loaded 102 algorithms
🌐 Server running at: http://localhost:5000
```

#### Passo 2: Abrir Interface
- Abra `index.html` (não demo.html!)
- Ou acesse: `http://localhost:5000`

#### Passo 3: Usar
1. Cole ciphertext
2. Adicione senha(s) na wordlist
3. Clique "Auto-Detect & Decrypt"

---

## 🧪 Teste Rápido de AES

Execute o script que acabei de criar:

```bash
python gerar_teste_aes.py
```

Isso vai gerar:
- Ciphertext AES-256-CBC
- Senha correta
- Instruções de teste

Copie e cole na interface!

---

## 📊 O Que Esperar

### Base64 (sem senha)
```
Input: SGVsbG8gV29ybGQh
Output: Hello World!
Algorithm: Base64 Encoding
Confidence: 95%
```

### AES (com senha)
```
Input: <ciphertext_gerado>
Wordlist: senha123
Output: Esta é uma mensagem secreta...
Algorithm: AES-256-CBC
Confidence: 85%
```

### Caesar (sem senha)
```
Input: Khoor Zruog
Output: Hello World
Algorithm: Caesar Cipher
Confidence: 90%
```

---

## ⚠️ Importante

| Arquivo | Funciona? | Backend? | Casos de Uso |
|---------|-----------|----------|-------------|
| **demo.html** | ✅ Visual | ❌ Não | Ver design |
| **index.html** | ✅ Completo | ✅ Sim | Testar de verdade |
| **main.py** | ✅ CLI | ✅ Sim | Via terminal |
| **Python direto** | ✅ Script | ✅ Sim | Integração |

---

## 🎯 Próximos Passos

1. **Execute:** `python gerar_teste_aes.py`
2. **Copie** o ciphertext gerado
3. **Teste** com uma das 3 opções acima
4. **Veja** a mágica acontecer! ✨

Quer que eu ajude a iniciar o servidor Flask agora?
