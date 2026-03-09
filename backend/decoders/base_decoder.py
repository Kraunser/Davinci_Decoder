"""Core decoder primitives used by the decoder manager and API."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


def _printable_ratio(text: str) -> float:
    if not text:
        return 0.0
    printable = sum(1 for ch in text if 32 <= ord(ch) <= 126 or ch in "\n\r\t")
    return printable / len(text)


def score_plaintext(text: str) -> float:
    """Small heuristic score (0-100) for candidate plaintext."""
    if not text:
        return 0.0

    ratio = _printable_ratio(text)
    score = ratio * 60.0

    if any(ch.isspace() for ch in text):
        score += 10.0

    lower = text.lower()
    common = ("the", "and", "hello", "world", "de", "que", "uma", "para")
    if any(word in lower for word in common):
        score += 20.0

    # Penalize token-looking gibberish that frequently appears in false positives.
    if len(text) >= 10 and re.fullmatch(r"[A-Za-z0-9+/=_-]+", text) and " " not in text:
        score -= 15.0

    # Reward entropy range expected for natural language.
    counts = Counter(text)
    entropy = 0.0
    for count in counts.values():
        probability = count / len(text)
        entropy -= probability * math.log2(probability)

    if 3.0 <= entropy <= 5.8:
        score += 10.0
    elif entropy > 6.6 or entropy < 1.8:
        score -= 10.0

    return min(100.0, score)


@dataclass
class DecoderResult:
    """Common output model used by all decoders."""

    success: bool
    plaintext: str
    confidence: float
    method: str
    password: Optional[str] = None
    key_hex: str = ""
    decoder_name: str = ""
    algorithm: str = ""
    error: str = ""

    def __post_init__(self) -> None:
        if not self.decoder_name:
            self.decoder_name = self.algorithm or self.method
        if not self.algorithm:
            self.algorithm = self.decoder_name

    def __getitem__(self, key: str) -> Any:
        mapping = {
            "success": self.success,
            "algorithm": self.algorithm,
            "plaintext": self.plaintext,
            "confidence": self.confidence,
            "password": self.password,
            "method": self.method,
            "key_hex": self.key_hex,
            "decoder_name": self.decoder_name,
            "error": self.error,
        }
        return mapping[key]


class BaseDecoder:
    """Base decoder contract."""

    def __init__(self, algorithm_name: str, algorithm_type: str) -> None:
        self._algorithm_name = algorithm_name
        self._algorithm_type = algorithm_type

    def get_algorithm_name(self) -> str:
        return self._algorithm_name

    def get_algorithm_type(self) -> str:
        return self._algorithm_type

    def derive_keys(self, password: str) -> Dict[str, bytes]:
        value = password.encode("utf-8", errors="ignore")
        return {"raw": value}

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        return None

    def attack(
        self,
        ciphertext: str,
        wordlist: Optional[List[str]] = None,
        max_attempts: Optional[int] = None,
    ) -> List[DecoderResult]:
        passwords = list(wordlist or [""])
        if max_attempts is not None:
            passwords = passwords[:max_attempts]

        results: List[DecoderResult] = []
        for password in passwords:
            for method, key in self.derive_keys(password).items():
                plaintext = self.decrypt(ciphertext, key, method)
                if not plaintext:
                    continue
                results.append(
                    DecoderResult(
                        success=True,
                        plaintext=plaintext,
                        confidence=score_plaintext(plaintext),
                        method=method,
                        password=password or None,
                        key_hex=key.hex() if isinstance(key, (bytes, bytearray)) else "",
                        decoder_name=self.get_algorithm_name(),
                        algorithm=self.get_algorithm_name(),
                    )
                )

        results.sort(key=lambda r: r.confidence, reverse=True)
        return results


class PlaceholderDecoder(BaseDecoder):
    """Decoder stub used to preserve algorithm catalog size."""

    def __init__(self, algorithm_name: str, algorithm_type: str) -> None:
        super().__init__(algorithm_name, algorithm_type)

    def attack(
        self,
        ciphertext: str,
        wordlist: Optional[List[str]] = None,
        max_attempts: Optional[int] = None,
    ) -> List[DecoderResult]:
        return []
