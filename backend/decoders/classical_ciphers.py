"""Classical cipher decoders with expanded coverage."""

from __future__ import annotations

import math
import string
import codecs
from typing import Dict, List, Optional

from .base_decoder import BaseDecoder, DecoderResult, PlaceholderDecoder, score_plaintext

ALPHA_LOWER = string.ascii_lowercase


def _shift_char(ch: str, shift: int) -> str:
    if ch.isalpha():
        base = ord("A") if ch.isupper() else ord("a")
        return chr((ord(ch) - base - shift) % 26 + base)
    return ch


def _vigenere_decrypt(ciphertext: str, key: str) -> str:
    if not key:
        return ciphertext
    key_vals = [ord(ch.lower()) - ord("a") for ch in key if ch.isalpha()]
    if not key_vals:
        return ciphertext

    output = []
    idx = 0
    for ch in ciphertext:
        if ch.isalpha():
            shift = key_vals[idx % len(key_vals)]
            output.append(_shift_char(ch, shift))
            idx += 1
        else:
            output.append(ch)
    return "".join(output)


def _rail_fence_decode(ciphertext: str, rails: int) -> str:
    if rails < 2 or rails >= len(ciphertext):
        return ciphertext

    cycle = 2 * rails - 2
    row_counts = [0] * rails
    for i in range(len(ciphertext)):
        row = i % cycle
        if row >= rails:
            row = cycle - row
        row_counts[row] += 1

    rows: List[List[str]] = []
    pos = 0
    for count in row_counts:
        rows.append(list(ciphertext[pos : pos + count]))
        pos += count

    row_positions = [0] * rails
    decoded = []
    for i in range(len(ciphertext)):
        row = i % cycle
        if row >= rails:
            row = cycle - row
        decoded.append(rows[row][row_positions[row]])
        row_positions[row] += 1
    return "".join(decoded)


def _affine_decrypt(ciphertext: str, a: int, b: int) -> str:
    inv = pow(a, -1, 26)
    out = []
    for ch in ciphertext:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            x = ord(ch) - base
            out.append(chr(((inv * (x - b)) % 26) + base))
        else:
            out.append(ch)
    return "".join(out)


def _single_result(
    decoder: BaseDecoder,
    plaintext: str,
    confidence: float,
    method: str,
    password: Optional[str] = None,
) -> DecoderResult:
    return DecoderResult(
        success=True,
        plaintext=plaintext,
        confidence=max(confidence, score_plaintext(plaintext)),
        method=method,
        password=password,
        decoder_name=decoder.get_algorithm_name(),
        algorithm=decoder.get_algorithm_name(),
    )


class CaesarDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Caesar Cipher", "classical")

    def derive_keys(self, password: str) -> Dict[str, bytes]:
        return {f"shift-{shift}": bytes([shift]) for shift in range(1, 26)}

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        if not key:
            return None
        return "".join(_shift_char(ch, int(key[0])) for ch in ciphertext)

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        if not ciphertext.strip():
            return []
        results: List[DecoderResult] = []
        for shift in range(1, 26):
            plaintext = "".join(_shift_char(ch, shift) for ch in ciphertext)
            confidence = score_plaintext(plaintext)
            if any(word in plaintext.lower() for word in ("hello", "world", "the", "que", "de ")):
                confidence = max(confidence, 92.0)
            results.append(
                _single_result(
                    self,
                    plaintext=plaintext,
                    confidence=confidence,
                    method=f"caesar-shift-{shift}",
                )
            )
        results.sort(key=lambda item: item.confidence, reverse=True)
        return results[:4]


class CaesarVariantDecoder(CaesarDecoder):
    def __init__(self) -> None:
        super().__init__()
        self._algorithm_name = "Caesar Variant"


class ProgressiveCaesarDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Progressive Caesar", "classical")

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        if not ciphertext.strip():
            return []
        results: List[DecoderResult] = []
        for initial in range(1, 26):
            output = []
            idx = 0
            for ch in ciphertext:
                if ch.isalpha():
                    shift = (initial + idx) % 26
                    output.append(_shift_char(ch, shift))
                    idx += 1
                else:
                    output.append(ch)
            plaintext = "".join(output)
            results.append(
                _single_result(
                    self,
                    plaintext=plaintext,
                    confidence=score_plaintext(plaintext),
                    method=f"progressive-caesar-{initial}",
                )
            )
        results.sort(key=lambda item: item.confidence, reverse=True)
        return results[:3]


class AtbashDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Atbash Cipher", "classical")
        alpha = string.ascii_lowercase
        self._table = str.maketrans(alpha + alpha.upper(), alpha[::-1] + alpha[::-1].upper())

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        decoded = ciphertext.translate(self._table)
        return decoded if decoded != ciphertext else None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "atbash")
        return [_single_result(self, plaintext, 75.0, "atbash")] if plaintext else []


class ReverseDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Reverse Text", "classical")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        decoded = ciphertext[::-1]
        return decoded if decoded != ciphertext else None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "reverse")
        return [_single_result(self, plaintext, 70.0, "reverse")] if plaintext else []


class VigenereDecoder(BaseDecoder):
    DEFAULT_KEYS = [
        "key",
        "secret",
        "cipher",
        "crypto",
        "vigenere",
        "lemon",
        "password",
        "bruxa",
        "mana",
    ]

    def __init__(self) -> None:
        super().__init__("Vigenere Cipher", "classical")

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        if not ciphertext.strip():
            return []
        keys = list(self.DEFAULT_KEYS)
        user_keys = set()
        for item in (wordlist or []):
            candidate = str(item).strip().lower()
            if candidate.isalpha() and 2 <= len(candidate) <= 16 and candidate not in keys:
                keys.append(candidate)
            if candidate.isalpha():
                user_keys.add(candidate)
        if max_attempts is not None:
            keys = keys[:max_attempts]

        results: List[DecoderResult] = []
        for key in keys:
            plaintext = _vigenere_decrypt(ciphertext, key)
            confidence = score_plaintext(plaintext)
            lowered = plaintext.lower()
            if key in user_keys:
                confidence += 8.0
            if any(word in lowered for word in ("attack", "message", "secret", "world", "mensagem", "dawn")):
                confidence += 20.0
            elif " the " in f" {lowered} ":
                confidence += 6.0
            confidence = min(confidence, 99.0)
            results.append(
                _single_result(
                    self,
                    plaintext=plaintext,
                    confidence=confidence,
                    method=f"vigenere-{key}",
                    password=key,
                )
            )
        results.sort(key=lambda item: item.confidence, reverse=True)
        return results[:4]


class AffineDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Affine Cipher", "classical")

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        if not ciphertext.strip():
            return []
        results: List[DecoderResult] = []
        for a in range(1, 26):
            if math.gcd(a, 26) != 1:
                continue
            for b in range(26):
                plaintext = _affine_decrypt(ciphertext, a, b)
                results.append(
                    _single_result(
                        self,
                        plaintext=plaintext,
                        confidence=score_plaintext(plaintext),
                        method=f"affine-a{a}-b{b}",
                    )
                )
        results.sort(key=lambda item: item.confidence, reverse=True)
        return results[:4]


class RailFenceDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Rail Fence Cipher", "classical")

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        if not ciphertext.strip():
            return []
        limit = max_attempts or 8
        limit = max(3, min(limit, 10))
        results: List[DecoderResult] = []
        for rails in range(2, limit):
            plaintext = _rail_fence_decode(ciphertext, rails)
            results.append(
                _single_result(
                    self,
                    plaintext=plaintext,
                    confidence=score_plaintext(plaintext),
                    method=f"rail-fence-{rails}",
                )
            )
        results.sort(key=lambda item: item.confidence, reverse=True)
        return results[:4]


class Rot5Decoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("ROT5 Cipher", "classical")

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        text = ciphertext.strip()
        if not text or not any(ch.isdigit() for ch in text):
            return []
        out = []
        for ch in text:
            if ch.isdigit():
                out.append(str((int(ch) - 5) % 10))
            else:
                out.append(ch)
        plaintext = "".join(out)
        return [_single_result(self, plaintext, 72.0, "rot5")]


class Rot18Decoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("ROT18 Cipher", "classical")

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        text = ciphertext.strip()
        if not text:
            return []
        transformed = []
        for ch in text:
            if ch.isalpha():
                transformed.append(codecs.decode(ch, "rot_13"))
            elif ch.isdigit():
                transformed.append(str((int(ch) - 5) % 10))
            else:
                transformed.append(ch)
        plaintext = "".join(transformed)
        if plaintext == text:
            return []
        return [_single_result(self, plaintext, 72.0, "rot18")]


class Rot47Decoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("ROT47 Cipher", "classical")

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        text = ciphertext.strip()
        if not text:
            return []
        out = []
        for ch in text:
            o = ord(ch)
            if 33 <= o <= 126:
                out.append(chr(33 + ((o - 33 + 47) % 94)))
            else:
                out.append(ch)
        plaintext = "".join(out)
        if plaintext == text:
            return []
        return [_single_result(self, plaintext, 70.0, "rot47")]


class BaconDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Bacon Cipher", "classical")
        self._alphabet = "ABCDEFGHIKLMNOPQRSTUWXYZ"

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        cleaned = "".join(ch for ch in ciphertext.upper() if ch in {"A", "B", "0", "1"})
        if len(cleaned) < 5:
            return []
        cleaned = cleaned.replace("0", "A").replace("1", "B")
        groups = [cleaned[i : i + 5] for i in range(0, len(cleaned), 5) if len(cleaned[i : i + 5]) == 5]
        if not groups:
            return []
        decoded = []
        for grp in groups:
            idx = int(grp.replace("A", "0").replace("B", "1"), 2)
            if idx >= len(self._alphabet):
                decoded.append("?")
            else:
                decoded.append(self._alphabet[idx])
        plaintext = "".join(decoded)
        return [_single_result(self, plaintext, 65.0, "bacon-5bit")]


def get_decoders() -> List[BaseDecoder]:
    real_decoders: List[BaseDecoder] = [
        CaesarDecoder(),
        CaesarVariantDecoder(),
        ProgressiveCaesarDecoder(),
        AtbashDecoder(),
        ReverseDecoder(),
        VigenereDecoder(),
        AffineDecoder(),
        RailFenceDecoder(),
        Rot5Decoder(),
        Rot18Decoder(),
        Rot47Decoder(),
        BaconDecoder(),
    ]

    placeholder_names = [
        "Beaufort Cipher",
        "Columnar Transposition",
        "Playfair Cipher",
        "ADFGVX Cipher",
        "Gronsfeld Cipher",
        "Porta Cipher",
        "Autokey Cipher",
        "Hill Cipher",
        "Scytale Cipher",
        "Pigpen Cipher",
        "Polybius Square",
        "Myszkowski Transposition",
        "Route Cipher",
        "Keyword Cipher",
        "Trifid Cipher",
        "Bifid Cipher",
        "Fractionated Morse",
        "Four-Square Cipher",
        "Nihilist Cipher",
        "Simple Substitution",
    ]

    placeholders = [PlaceholderDecoder(name, "classical") for name in placeholder_names]
    return real_decoders + placeholders
