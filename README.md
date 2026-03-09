# 🎨 DaVinci Decoder

**Sistema Universal de Quebra de Cifras - 102 Algoritmos**

Uma ferramenta profissional de decifração com interface web moderna e sistema de auto-detecção inteligente.

---

## 🌟 Features

- ✨ **Interface Web Moderna** - Design responsivo com gradientes e animações
- 🤖 **Auto-Detecção Inteligente** - Sistema ML identifica o algoritmo automaticamente
- 🔒 **102 Algoritmos** - Cifras modernas, clássicas, encodings e hash crackers
- 🧠 **Wordlist Inteligente** - 8.200+ senhas com expansão automática
- ⚡ **API REST** - Backend Flask com CORS habilitado
- 📊 **Análise de Ciphertext** - Entropia, charset, block size detection

---

## 📊 Algoritmos Implementados

| Categoria | Quantidade | Exemplos |
|-----------|------------|----------|
| 🔐 Cifras Modernas | 36 | AES-128/192/256 (ECB/CBC/GCM/CFB/OFB/CTR), 3DES, Blowfish, ChaCha20, RC4, Twofish, CAST5, Camellia, IDEA, Serpent |
| 📜 Cifras Clássicas | 32 | Caesar, ROT13, Vigenère, Atbash, XOR, Rail Fence, Beaufort, Playfair, Columnar Transposition, Affine, ADFGVX |
| 🔤 Encodings | 21 | Base64, Base32, Hex, Base85, URL, HTML Entity, Binary, Octal, Morse, UUEncode, Quoted-Printable |
| #️⃣ Hash Crackers | 13 | MD5, SHA1, SHA256, SHA512, SHA3, BLAKE2, bcrypt, scrypt, Argon2, NTLM, MySQL |

**Total: 102 algoritmos** ✅

---

## 🚀 Início Rápido

### 1️⃣ Instalar Dependências

```powershell
cd Decoder
pip install -r requirements.txt
```

**Dependências principais:**
- `flask` + `flask-cors` (API web)
- `pycryptodome` (criptografia)
- `scikit-learn` (machine learning)
- `bcrypt` (key derivation)

### 2️⃣ Iniciar API Server

**Opção A - Script Automático (Recomendado):**
```powershell
# Execute o arquivo .bat
Start API Server.bat
```

**Opção B - Manual:**
```powershell
cd davinci-decoder
python api_server.py
```

O servidor iniciará em: **http://localhost:5000**

### 3️⃣ Abrir Interface Web

Abra seu navegador em: **http://localhost:5000**

> ⚠️ **IMPORTANTE:** Não abra o arquivo `index.html` diretamente! A interface precisa da API rodando.

---

## 🎮 Modos de Uso

### 🌐 Modo Web (Recomendado)

1. Inicie a API com `Start API Server.bat`
2. Abra http://localhost:5000 no navegador
3. Cole o ciphertext
4. (Opcional) Adicione wordlist customizada
5. Clique em **Auto-Detect & Decrypt**

**Features da Interface:**
- ✅ Auto-detecção de algoritmo
- ✅ Seleção manual de algoritmo específico
- ✅ Análise em tempo real (entropia, charset)
- ✅ Múltiplos resultados com confiança
- ✅ Wordlist padrão automática (8.200+ senhas)

### 💻 Modo CLI

```powershell
cd davinci-decoder
python main.py
```

**Menu interativo:**
1. Auto-Detect (Recomendado)
2. Cifras Modernas
3. Cifras Clássicas
4. Listar Algoritmos
5. Abrir Interface Web
6. README

---

## 📂 Estrutura do Projeto

```
Decoder/
├── Start API Server.bat         # Script de inicialização (NOVO!)
├── DaVinci Decoder.bat           # CLI (interface texto)
├── requirements.txt              # Dependências (atualizado)
├── .gitignore                    # Exclusões git (NOVO!)
│
└── davinci-decoder/
    ├── main.py                   # Interface CLI
    ├── api_server.py             # API REST Flask
    │
    ├── backend/
    │   ├── ml_engine.py          # Machine Learning (Random Forest)
    │   ├── decoder_engine.py     # Motor principal
    │   ├── crypto_analyzer.py    # Análise de ciphertext
    │   ├── result_scorer.py      # Scoring de resultados
    │   │
    │   ├── decoders/
    │   │   ├── decoder_manager.py    # Gerenciador (102 algoritmos)
    │   │   ├── base_decoder.py       # Classe base
    │   │   ├── modern_ciphers.py     # AES, 3DES
    │   │   ├── classical_ciphers.py  # Caesar, Vigenère
    │   │   ├── encodings.py          # Base64, Hex, Morse
    │   │   ├── hash_crackers.py      # MD5, SHA, bcrypt
    │   │   └── ... (13 módulos)
    │   │
    │   └── wordlists/
    │       ├── wordlist.txt              # 223 palavras base
    │       └── wordlist_expandida.txt    # 8.200+ variações
    │
    └── frontend/
        ├── index.html            # Página principal
        ├── css/styles.css        # Design moderno
        └── js/
            ├── app.js            # Lógica principal
            └── animations.js     # Efeitos visuais
```

---

## 🔧 API Endpoints

### 🏥 Health Check
```
GET /api/health
```

### 📋 Listar Algoritmos
```
GET /api/algorithms
Response: { algorithms: [...], count: 102 }
```

### 🤖 Auto-Detect
```
POST /api/auto-detect
Body: {
  "ciphertext": "SGVsbG8gV29ybGQh",
  "wordlist": ["password", "123456"],  // Opcional
  "max_results": 5
}
```

### ⚙️ Decifrar com Algoritmo Específico
```
POST /api/decrypt
Body: {
  "ciphertext": "...",
  "algorithm": "AES-256-CBC",
  "wordlist": [...]  // Opcional
}
```

> 💡 **Wordlist Automática:** Se você não enviar wordlist, a API carrega automaticamente `wordlist_expandida.txt` (8.200+ senhas)!

---

## ⚙️ Configuração Avançada

### Mudar Porta da API

Edite `api_server.py` linha 244:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Mude 5000
```

E `frontend/js/app.js` linha 7:
```javascript
const API_URL = 'http://localhost:5000/api';  // Mude 5000
```

### Validações de Segurança

- ✅ **Max ciphertext:** 100KB (evita DoS)
- ✅ **CORS habilitado:** Permite frontend local
- ✅ **Timeout frontend:** 2 minutos por requisição
- ✅ **Validação de tipos:** JSON schema

---

## 📝 Exemplos de Uso

### Exemplo 1: Base64 (sem senha)
```
Ciphertext: SGVsbG8gV29ybGQh
Algoritmo: Base64 Encoding
Plaintext: Hello World!
Confiança: 95%
```

### Exemplo 2: Caesar Cipher
```
Ciphertext: Khoor Zruog
Algoritmo: Caesar Cipher (shift=3)
Plaintext: Hello World
Confiança: 88%
```

### Exemplo 3: AES-256-CBC
```
Ciphertext: CObK1Hwdtqsf2mt3qFvbeU... (Base64)
Senha: bruxabiotica
Método: AES-256-CBC (PBKDF2-SHA256-10000-salt)
Plaintext: Mensagem secreta do RPG Ordem Paranormal
Confiança: 97%
```

---

## 🧪 Testando o Sistema

### Teste Rápido - API
```powershell
cd davinci-decoder
python teste_auto_com_senha.py
```

### Teste Completo - Todos Algoritmos
```powershell
python test_todos_algoritmos.py
```

### Gerar Seu Próprio Teste
```powershell
python GERAR_SEU_TESTE.py
```

---

## 🐛 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'flask'"
**Solução:**
```powershell
pip install -r requirements.txt
```

### ❌ "Failed to load algorithms" no frontend
**Causa:** API não está rodando

**Solução:**
1. Execute `Start API Server.bat`
2. Verifique se `http://localhost:5000/api/health` retorna OK
3. Abra `http://localhost:5000` (não `file://`)

### ❌ "Nenhuma senha funcionou"
**Possíveis causas:**
- Senha não está na wordlist
- Algoritmo errado detectado
- Ciphertext corrompido

**Solução:**
1. Adicione a senha correta na wordlist
2. Tente selecionar o algoritmo manualmente
3. Verifique se o ciphertext está completo (incluindo padding)

### ❌ "Timeout" após 2 minutos
**Causa:** Wordlist muito grande ou algoritmo lento

**Solução:**
- Use wordlist menor
- Selecione algoritmo específico em vez de Auto-Detect

---

## 🎓 Documentação Adicional

- `STATUS_IMPLEMENTACAO.md` - Status de desenvolvimento
- `CIFRAS_COMPLETAS.md` - Lista completa de algoritmos
- `COMO_TESTAR.md` - Guia de testes
- `ML_README.md` - Sistema de Machine Learning
- `UI_README.md` - Documentação do frontend

---

## 📜 Licença

Livre para uso educacional e pesquisa em criptoanálise.

---

## 🎨 Créditos

**Nome:** Matheus Bueno  
**Inspiração:** Leonardo da Vinci 


---

**Desenvolvido com ❤️ para decifradores e entusiastas de criptografia.**

🚀 **Versão 2.0** - Agora com 102 algoritmos e API REST completa!
