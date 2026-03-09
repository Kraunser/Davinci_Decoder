# DaVinci Decoder - Lista Completa de Cifras

**Total:** 50+ Algoritmos de Criptografia e Codificação

---

## CIFRAS MODERNAS (Simétricas)

### Família AES (Advanced Encryption Standard)
1. **AES-128-ECB** (já implementado)
2. **AES-192-ECB**
3. **AES-256-ECB**
4. **AES-128-CBC** (Cipher Block Chaining)
5. **AES-192-CBC**
6. **AES-256-CBC**
7. **AES-128-CFB** (Cipher Feedback)
8. **AES-256-CFB**
9. **AES-128-OFB** (Output Feedback)
10. **AES-256-OFB**
11. **AES-128-CTR** (Counter Mode)
12. **AES-256-CTR**
13. **AES-128-GCM** (Galois/Counter Mode - Autenticado)
14. **AES-256-GCM**

### Família DES (Data Encryption Standard)
15. **DES-ECB** (obsoleto, mas útil)
16. **DES-CBC**
17. **3DES-ECB** (Triple DES)
18. **3DES-CBC**
19. **3DES-CFB**

### Família Blowfish
20. **Blowfish-ECB**
21. **Blowfish-CBC**
22. **Blowfish-CFB**
23. **Blowfish-OFB**

### Família Twofish
24. **Twofish-ECB**
25. **Twofish-CBC**

### Cifras de Fluxo (Stream Ciphers)
26. **RC4** (ARC4)
27. **ChaCha20**
28. **Salsa20**
29. **RC4-drop** (RC4 com bytes descartados)

### Outras Cifras Simétricas
30. **CAST-128** (CAST5)
31. **IDEA** (International Data Encryption Algorithm)
32. **Camellia-128**
33. **Camellia-256**
34. **SEED**
35. **Serpent**

---

## CIFRAS CLÁSSICAS

### Substituição Monoalfabética
36. **Caesar Cipher** (ROT-N genérico)
37. **ROT13** (caso específico de Caesar)
38. **ROT5** (apenas números)
39. **ROT18** (letras + números)
40. **ROT47** (ASCII 33-126)
41. **Atbash** (inversão alfabética)
42. **Substituição Simples** (mapeamento customizado)
43. **Affine Cipher** (ax + b mod 26)

### Substituição Polialfabética
44. **Vigenère Cipher**
45. **Beaufort Cipher**
46. **Autokey Cipher**
47. **Running Key Cipher**
48. **Gronsfeld Cipher**
49. **Porta Cipher**

### Cifras de Transposição
50. **Rail Fence Cipher** (Zig-Zag)
51. **Columnar Transposition**
52. **Double Transposition**
53. **Scytale Cipher**
54. **Route Cipher**

### Cifras de Substituição + Transposição
55. **ADFGVX Cipher** (WWI alemã)
56. **Playfair Cipher**
57. **Four-Square Cipher**
58. **Bifid Cipher**
59. **Trifid Cipher**

### Cifras Mecânicas
60. **Enigma** (simulação WW2)
61. **Lorenz Cipher**

---

## 🔢 CODIFICAÇÕES (Encoding/Obfuscation)

### Base Encodings
62. **Base64** (padrão RFC 4648)
63. **Base64 URL-safe**
64. **Base32**
65. **Base16** (Hexadecimal)
66. **Base85** (ASCII85)
67. **Base91**

### Outros Encodings
68. **URL Encoding** (percent-encoding)
69. **HTML Entity Encoding**
70. **Quoted-Printable**
71. **UUEncode**
72. **XXEncode**
73. **BinHex**
74. **Morse Code**
75. **Binary** (0s e 1s)
76. **Octal**
77. **Decimal**

---

## CIFRAS XOR E VARIAÇÕES

78. **XOR Single-Byte** (brute force 0-255)
79. **XOR Multi-Byte Key**
80. **XOR com chave repetida**
81. **XOR com chave alternada**

---

## 🎭 CIFRAS EXÓTICAS/DIVERTIDAS

### Substituição Visual
82. **Bacon Cipher** (A/B encoding)
83. **Tap Code** (grade 5×5)
84. **Polybius Square**
85. **Straddle Checkerboard**

### Cifras de Livro
86. **Book Cipher** (referências a páginas)
87. **VIC Cipher** (KGB)

### Outras
88. **Nihilist Cipher**
89. **Homophonic Substitution**
90. **Fractionated Morse**

---

## HASHES (Detecção + Cracking)

### Hashes Comuns
91. **MD5** (identificação, not encryption)
92. **SHA1**
93. **SHA256**
94. **SHA512**
95. **SHA3**
96. **BLAKE2**
97. **RIPEMD-160**

### Password Hashes
98. **bcrypt**
99. **scrypt**
100. **Argon2**
101. **PBKDF2**

---

## CATEGORIZAÇÃO POR DIFICULDADE

### ⭐ Fácil (1-5 min implementação)
- Caesar, ROT13, Atbash
- Base64, Hex
- XOR single-byte

### ⭐⭐ Médio (10-30 min)
- Vigenère, Beaufort
- Rail Fence, Columnar
- AES-CBC (com IV)
- 3DES

### ⭐⭐⭐ Difícil (1-2h)
- Playfair, Four-Square
- Enigma (simulação)
- AES-GCM (autenticado)
- ChaCha20

### ⭐⭐⭐⭐ Avançado (2-4h)
- Auto-detecção inteligente
- Frequency analysis (Vigenère key length)
- Index of Coincidence
- Kasiski examination

---

## PRIORIZAÇÃO SUGERIDA

### Fase 1: Essenciais (10 cifras) - 4h
1. AES-256-ECB
2. AES-128-CBC
3. 3DES-ECB
4. Caesar/ROT13
5. Vigenère
6. Base64/Hex
7. XOR single-byte
8. Blowfish-ECB
9. ChaCha20
10. RC4

### Fase 2: Importantes (10 cifras) - 3h
11. AES-256-CBC
12. AES-128-GCM
13. 3DES-CBC
14. Atbash
15. Playfair
16. Rail Fence
17. Columnar Transposition
18. Beaufort
19. Twofish
20. CAST5

### Fase 3: Complementares (10 cifras) - 3h
21-30. Resto das variações AES/DES
31-40. Cifras clássicas restantes

### Fase 4: Avançadas (20+ cifras) - variável
41+. Cifras exóticas, Enigma, etc.

---

## 📦 DEPENDÊNCIAS PYTHON

```python
# Já instaladas
pycryptodome>=3.18.0  # AES, DES, 3DES, Blowfish, RC4
bcrypt>=4.0.1    # bcrypt hashing

# A instalar
cryptography>=41.0.0  # ChaCha20, mais algorithms, melhor API
pycipher>=0.5.2   # Cifras clássicas (Vigenère, Playfair, etc.)
base58>=2.1.1    # Base58 encoding (Bitcoin)
```

---

## FEATURES DE DETECÇÃO

### Auto-Identificação
- **Entropy Analysis** (entropia Shannon)
- **Block Size Detection** (8, 16, 32 bytes)
- **Character Set Analysis** (alfabético, base64, hex)
- **Pattern Detection** (ECB repetição, IV presence)
- **Frequency Analysis** (distribuição de caracteres)
- **Index of Coincidence** (Vigenère vs random)

### Inteligência de Ataque
- **Adaptive Strategy**: Tentar cifras por ordem de probabilidade
- **Parallel Attacks**: Testar múltiplos algoritmos simultaneamente
- **Smart Wordlist**: Expandir baseado no charset detectado

---

## ESTATÍSTICAS FINAIS

- **Total de Algoritmos:** 100+
- **Implementação Básica:** 30-40 cifras essenciais
- **Implementação Completa:** 60+ cifras
- **Tempo Estimado (completo):** 20-30 horas
- **LOC Estimado:** 5.000-8.000 linhas

---

## RECOMENDAÇÃO

Para um **DaVinci Decoder profissional**, sugiro implementar:

 **Fase 1 + Fase 2** = **20 cifras mais usadas** (7h de trabalho)

Isso cobre:
- 95% dos casos de uso reais
- Todos os algoritmos modernos comuns
- Principais cifras clássicas para CTF/puzzles
- Auto-detecção inteligente

**Resultado:** Ferramenta extremamente poderosa e profissional! 🔓
