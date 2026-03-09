# Por Que AES Não Foi Detectado Automaticamente?

## 🔍 Problema Identificado

**AES requer:**
1. Ciphertext válido em Base64
2. **SENHA na wordlist** (você provavelmente não colocou)
3. **Derivação de chave correta**

## 🤔 Como AES Funciona

### Sem Senha
```
Input: <ciphertext_aes>
Wordlist: (vazio)
Resultado: Nada (AES precisa de senha!)
```

### Com Senha
```
Input: <ciphertext_aes>
Wordlist: minhaSenha123
Resultado: Plaintext decifrado!
```

## Processo de Auto-Detecção

```python
1. Analisa ciphertext → Base64 
2. Charset → UTF-8/Base64 
3. Tamanho múltiplo de 16 → 
4. Tenta decoders:
 - Base64 → (não é plaintext)
 - Hex → (não é hex)
 - AES → (precisa senha!)
 - Caesar → (não é substituição)
```

**Resultado:** Sem wordlist, AES não consegue decifrar!

---

## Solução: Use o Teste Gerado

Acabei de gerar um teste completo de AES-192:

```bash
python gerar_teste_aes192.py
```

Isso criou:
- Ciphertext válido
- Senha correta
- Arquivo `teste_aes192.txt` com tudo

### Copie e Cole:

1. **Ciphertext** → Campo "Ciphertext"
2. **Senha** → Campo "Wordlist" (uma por linha)
3. **Clique** → "Auto-Detect & Decrypt"

---

## Exemplo Prático

### Teste 1: Base64 (SEM senha)
```
Ciphertext: SGVsbG8gV29ybGQh
Wordlist: (vazio)
 Funciona! → "Hello World!"
```

### Teste 2: AES-192 (COM senha)
```
Ciphertext: <do arquivo teste_aes192.txt>
Wordlist: minhaSenha123
 Funciona! → "Teste do DaVinci Decoder..."
```

### Teste 3: AES-192 (SEM senha)
```
Ciphertext: <do arquivo teste_aes192.txt>
Wordlist: (vazio)
 NÃO funciona! → Sem resultados
```

---

## Dica Importante

**AES/3DES/Blowfish SEMPRE precisam de senha!**

- Caesar, ROT13, Base64 → Funciona sem senha
- AES, 3DES, Blowfish → Precisa senha na wordlist

---

## Teste Agora

Veja o output do comando que executei!

Copie:
1. O CIPHERTEXT
2. A SENHA

Cole na interface e teste! 
