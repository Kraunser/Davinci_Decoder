# Guia de Teste Manual - DaVinci Decoder

## Sistema Validado (Teste Automatizado)

O teste end-to-end confirmou:
- Backend: 102 algoritmos carregados
- Auto-Detect: Funcional
- Machine Learning: Modelo treinado
- Estrutura de arquivos: Completa

---

## Teste Manual da Interface Web

### Passo 1: Verificar Servidor

Abra um terminal e execute:
```bash
python api_server.py
```

Aguarde ver:
```
 DaVinci Decoder inicializado
 Loaded 102 algorithms
 Server running at: http://localhost:5000
```

### Passo 2: Abrir Interface

No navegador, acesse:
```
http://localhost:5000
```

Você deve ver:
- Header "DaVinci Decoder" com gradiente purple/blue
- Campo de texto grande para "Ciphertext"
- Campo de texto para "Wordlist"
- Botão "Auto-Detect & Decrypt"
- Estatísticas em tempo real

---

## Casos de Teste

### Teste 1: Base64 (Encoding Simples)

**Input:**
```
Ciphertext: SGVsbG8gV29ybGQh
Wordlist: (vazio)
```

**Ação:** Clique "Auto-Detect & Decrypt"

**Resultado Esperado:**
```
 Algorithm: Base64 Encoding
 Plaintext: Hello World!
 Confidence: 95%
```

---

### Teste 2: Hexadecimal

**Input:**
```
Ciphertext: 48656c6c6f20576f726c64
Wordlist: (vazio)
```

**Ação:** Clique "Auto-Detect & Decrypt"

**Resultado Esperado:**
```
 Algorithm: Hexadecimal
 Plaintext: Hello World
 Confidence: 90%
```

---

### Teste 3: Caesar Cipher

**Input:**
```
Ciphertext: Khoor Zruog
Wordlist: (vazio)
```

**Ação:** Clique "Auto-Detect & Decrypt"

**Resultado Esperado:**
```
 Algorithm: Caesar Cipher
 Plaintext: Hello World
 Confidence: 85%
 Key: 3
```

---

### Teste 4: AES-192 (Com Senha)

**Passo 1:** Gerar ciphertext AES
```bash
python gerar_teste_aes192.py
```

**Passo 2:** Copiar output:
- Ciphertext: (gerado automaticamente)
- Senha: minhaSenha123

**Input na Interface:**
```
Ciphertext: <ciphertext_gerado>
Wordlist: minhaSenha123
```

**Ação:** Clique "Auto-Detect & Decrypt"

**Resultado Esperado:**
```
 Algorithm: AES-192-CBC or AES-256-CBC
 Plaintext: Teste do DaVinci Decoder com AES-192!
 Confidence: 80-85%
 Password: minhaSenha123
```

---

### Teste 5: MD5 Hash (Crack)

**Input:**
```
Ciphertext: 5d41402abc4b2a76b9719d911017c592
Wordlist: 
admin
password
hello
test
```

**Ação:** Clique "Auto-Detect & Decrypt"

**Resultado Esperado:**
```
 Algorithm: MD5 Hash Cracker
 Plaintext: hello
 Confidence: 95%
 Password: hello
```

---

### Teste 6: Morse Code

**Input:**
```
Ciphertext: .... . .-.. .-.. ---
Wordlist: (vazio)
```

**Ação:** Clique "Auto-Detect & Decrypt"

**Resultado Esperado:**
```
 Algorithm: Morse Code
 Plaintext: HELLO
 Confidence: 90%
```

---

### Teste 7: ROT13

**Input:**
```
Ciphertext: Uryyb Jbeyq
Wordlist: (vazio)
```

**Ação:** Clique "Auto-Detect & Decrypt"

**Resultado Esperado:**
```
 Algorithm: ROT13 Encoding
 Plaintext: Hello World
 Confidence: 90%
```

---

### Teste 8: Binary

**Input:**
```
Ciphertext: 01001000 01100101 01101100 01101100 01101111
Wordlist: (vazio)
```

**Ação:** Clique "Auto-Detect & Decrypt"

**Resultado Esperado:**
```
 Algorithm: Binary Encoding
 Plaintext: Hello
 Confidence: 95%
```

---

## O Que Observar

### Interface Funcionando:
- Estatísticas em tempo real (chars, entropy, charset)
- Loading overlay durante processamento
- Resultados ordenados por confiança
- Badges coloridos (HIGH/MEDIUM/LOW confidence)
- Botão "Try Algorithm" para cada resultado
- Animações suaves

### Performance:
- Encodings: <0.5s
- Cifras clássicas: <1s
- AES (com senha): 1-3s
- Hash crack (10 senhas): <1s

---

## Teste de Performance

### Input Longo (1000+ caracteres)

Copie um texto grande em Base64:
```bash
echo "Lorem ipsum dolor sit amet..." | base64
```

Cole na interface e teste. Deve processar em <1s.

---

## Troubleshooting

### Servidor não inicia
```bash
# Verificar porta
netstat -ano | findstr :5000

# Se ocupada, matar processo
taskkill /PID <pid> /F
```

### API não responde
```bash
# Testar via curl
curl http://localhost:5000/api/health

# Deve retornar:
{
 "status": "healthy",
 "algorithms": 102,
 "version": "2.0"
}
```

### Interface não carrega CSS
- Limpe cache do navegador (Ctrl+Shift+R)
- Verifique console (F12) por erros
- Confirme que `frontend/css/styles.css` existe

### Resultados não aparecem
- Abra DevTools (F12)
- Vá para "Network"
- Veja se requisição POST para `/api/auto-detect` completa
- Verifique response JSON

---

## Checklist de Validação

- [ ] Servidor inicia sem erros
- [ ] Interface carrega com design premium
- [ ] Teste 1 (Base64) funciona
- [ ] Teste 2 (Hex) funciona
- [ ] Teste 3 (Caesar) funciona
- [ ] Teste 4 (AES) funciona com senha
- [ ] Teste 5 (MD5) quebra hash
- [ ] Estatísticas atualizam em tempo real
- [ ] Loading overlay aparece
- [ ] Resultados mostram confiança
- [ ] Performance é aceitável

---

## 🎉 Sistema 100% Funcional!

Se todos os testes passaram:
- Backend: OK
- ML Engine: OK
- API: OK
- Frontend: OK

**SISTEMA PRODUCTION READY! **

---

## 📸 Screenshots Esperados

### Tela Inicial:
- Dark background com gradiente
- Logo "DaVinci Decoder" no topo
- 2 text areas grandes
- Botão destaque purple/blue
- Stats panel embaixo

### Após Teste:
- Results panel expandido
- Cards com resultados
- Badges de confiança
- Algoritmo em destaque
- Plaintext visível

---

**Bons testes! **
