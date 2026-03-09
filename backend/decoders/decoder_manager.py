"""Central decoder registry and high-level decode orchestration."""

from __future__ import annotations

import base64
import re
from typing import List, Optional, Sequence, Tuple

from .advanced_classical import get_decoders as get_advanced_classical_decoders
from .advanced_encodings import get_decoders as get_advanced_encoding_decoders
from .base_decoder import BaseDecoder, DecoderResult
from .classical_ciphers import get_decoders as get_classical_decoders
from .encodings import get_decoders as get_encoding_decoders
from .exotic_ciphers import get_decoders as get_exotic_classical_decoders
from .exotic_modern import get_decoders as get_exotic_modern_decoders
from .hash_crackers import get_decoders as get_hash_decoders
from .missing_algorithms import get_decoders as get_missing_decoders
from .modern_ciphers import get_decoders as get_modern_decoders
from .stream_ciphers import get_decoders as get_stream_decoders


def _looks_base64(value: str) -> bool:
    cleaned = value.strip().replace("-", "+").replace("_", "/")
    if not cleaned or len(cleaned) < 8:
        return False
    if not re.fullmatch(r"[A-Za-z0-9+/=]+", cleaned):
        return False
    if len(cleaned) % 4 == 1:
        return False
    padding = (4 - (len(cleaned) % 4)) % 4
    try:
        decoded = base64.b64decode(cleaned + ("=" * padding), validate=False)
    except Exception:
        return False
    return len(decoded) > 0


def _looks_hex(value: str) -> bool:
    cleaned = value.strip()
    return (
        bool(cleaned)
        and len(cleaned) >= 6
        and len(cleaned) % 2 == 0
        and bool(re.fullmatch(r"[0-9a-fA-F]+", cleaned))
    )


def _looks_binary(value: str) -> bool:
    chunks = [chunk for chunk in value.strip().split() if chunk]
    return bool(chunks) and all(len(chunk) == 8 and set(chunk).issubset({"0", "1"}) for chunk in chunks)


def _looks_base32(value: str) -> bool:
    cleaned = value.strip().upper().replace(" ", "")
    return bool(cleaned) and len(cleaned) >= 8 and bool(re.fullmatch(r"[A-Z2-7=]+", cleaned))


def _looks_base58(value: str) -> bool:
    cleaned = value.strip()
    return bool(cleaned) and len(cleaned) >= 6 and bool(re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]+", cleaned))


def _looks_base62(value: str) -> bool:
    cleaned = value.strip()
    return bool(cleaned) and len(cleaned) >= 6 and bool(re.fullmatch(r"[0-9A-Za-z]+", cleaned))


def _looks_base85(value: str) -> bool:
    cleaned = value.strip()
    return bool(cleaned) and len(cleaned) >= 5 and all(33 <= ord(ch) <= 126 for ch in cleaned)


def _looks_morse(value: str) -> bool:
    cleaned = value.strip()
    return bool(cleaned) and bool(re.fullmatch(r"[.\-/\s]+", cleaned))


def _looks_jwt(value: str) -> bool:
    parts = value.strip().split(".")
    if len(parts) != 3:
        return False
    pattern = re.compile(r"^[A-Za-z0-9_-]+$")
    return all(bool(pattern.fullmatch(part)) for part in parts if part)


def _looks_octal(value: str) -> bool:
    parts = [p for p in value.strip().replace("\\", " ").split() if p]
    return len(parts) >= 2 and all(bool(re.fullmatch(r"[0-7]{1,3}", part)) for part in parts)


def _looks_decimal(value: str) -> bool:
    parts = [p for p in value.strip().split() if p]
    return len(parts) >= 2 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)


def _looks_hash(value: str) -> bool:
    cleaned = value.strip()
    return bool(re.fullmatch(r"[0-9a-fA-F]{32}|[0-9a-fA-F]{40}|[0-9a-fA-F]{56}|[0-9a-fA-F]{64}|[0-9a-fA-F]{96}|[0-9a-fA-F]{128}", cleaned))


def _hash_length(value: str) -> int:
    return len(value.strip())


class DecoderManager:
    """Loads all decoders and exposes common decode operations."""

    MAX_RESULTS_PER_ALGORITHM = 3

    def __init__(self) -> None:
        self.active_decoders: List[BaseDecoder] = self._load_decoders()
        self.decoders: List[BaseDecoder] = self.active_decoders

    def _load_decoders(self) -> List[BaseDecoder]:
        decoders: List[BaseDecoder] = []
        decoders.extend(get_modern_decoders())
        decoders.extend(get_classical_decoders())
        decoders.extend(get_encoding_decoders())
        decoders.extend(get_hash_decoders())
        decoders.extend(get_advanced_classical_decoders())
        decoders.extend(get_advanced_encoding_decoders())
        decoders.extend(get_exotic_classical_decoders())
        decoders.extend(get_exotic_modern_decoders())
        decoders.extend(get_stream_decoders())
        decoders.extend(get_missing_decoders())

        # Keep deterministic order for tests and API output.
        return decoders

    def list_algorithms(self) -> List[str]:
        return [decoder.get_algorithm_name() for decoder in self.active_decoders]

    def get_decoder_by_name(self, algorithm_name: str) -> Optional[BaseDecoder]:
        target = (algorithm_name or "").strip().lower()
        for decoder in self.active_decoders:
            if decoder.get_algorithm_name().lower() == target:
                return decoder
        return None

    def get_all_modern(self) -> List[BaseDecoder]:
        return [d for d in self.active_decoders if d.get_algorithm_type() == "modern"]

    def get_all_classical(self) -> List[BaseDecoder]:
        return [d for d in self.active_decoders if d.get_algorithm_type() == "classical"]

    def get_all_encodings(self) -> List[BaseDecoder]:
        return [d for d in self.active_decoders if d.get_algorithm_type() == "encoding"]

    def get_all_hashes(self) -> List[BaseDecoder]:
        return [d for d in self.active_decoders if d.get_algorithm_type() == "hash"]

    def auto_detect(self, ciphertext: str, top_n: int = 5) -> List[Tuple[BaseDecoder, float]]:
        """Returns top candidate decoders with heuristic probabilities."""
        text = (ciphertext or "").strip()
        ranked: List[Tuple[BaseDecoder, float]] = []

        for decoder in self.active_decoders:
            name = decoder.get_algorithm_name()
            dtype = decoder.get_algorithm_type()
            score = 0.01

            if dtype == "encoding":
                if "JWT Payload" in name and _looks_jwt(text):
                    score = 0.98
                elif "Base64" in name and _looks_base64(text):
                    score = 0.95
                elif "Base32" in name and _looks_base32(text):
                    score = 0.93
                elif "Base58" in name and _looks_base58(text):
                    score = 0.82
                elif "Base62" in name and _looks_base62(text):
                    score = 0.80
                elif ("Base85" in name or "ASCII85" in name) and _looks_base85(text):
                    score = 0.78
                elif "Hex" in name and _looks_hex(text):
                    score = 0.90
                elif "Binary" in name and _looks_binary(text):
                    score = 0.88
                elif "Morse" in name and _looks_morse(text):
                    score = 0.92
                elif "URL" in name and ("%" in text or "+" in text):
                    score = 0.82
                elif ("HTML Entity" in name or "XML Entity" in name) and ("&" in text and ";" in text):
                    score = 0.86
                elif "Unicode Escape" in name and ("\\u" in text or "\\x" in text):
                    score = 0.89
                elif "JSON Escape" in name and any(token in text for token in ("\\n", "\\t", "\\u", '\\"')):
                    score = 0.84
                elif "Octal" in name and _looks_octal(text):
                    score = 0.81
                elif "Decimal" in name and _looks_decimal(text):
                    score = 0.80
                elif "Punycode" in name and "xn--" in text:
                    score = 0.90
                elif "Quoted-Printable" in name and "=" in text:
                    score = 0.75
                elif "ROT13" in name and text.isascii():
                    score = 0.70
                else:
                    score = 0.05
            elif dtype == "classical":
                if "Caesar" in name and text.replace(" ", "").isalpha():
                    score = 0.88
                elif "Vigenere" in name and text.replace(" ", "").isalpha():
                    score = 0.82
                elif "Affine" in name and text.replace(" ", "").isalpha():
                    score = 0.78
                elif "Rail Fence" in name and text.replace(" ", "").isalnum():
                    score = 0.72
                elif "ROT5" in name and any(ch.isdigit() for ch in text):
                    score = 0.76
                elif "ROT18" in name and any(ch.isdigit() for ch in text) and any(ch.isalpha() for ch in text):
                    score = 0.78
                elif "ROT47" in name and any(not ch.isalnum() and not ch.isspace() for ch in text):
                    score = 0.70
                elif "Atbash" in name and text.replace(" ", "").isalpha():
                    score = 0.72
                else:
                    score = 0.04
            elif dtype == "hash":
                if _looks_hash(text):
                    hlen = _hash_length(text)
                    if hlen == 32 and ("MD5" in name or "NTLM" in name):
                        score = 0.90
                    elif hlen == 40 and "SHA1" in name:
                        score = 0.90
                    elif hlen == 56 and "SHA224" in name:
                        score = 0.90
                    elif hlen == 64 and ("SHA256" in name or "SHA3-256" in name):
                        score = 0.90
                    elif hlen == 96 and "SHA384" in name:
                        score = 0.90
                    elif hlen == 128 and ("SHA512" in name or "SHA3-512" in name or "BLAKE2b" in name):
                        score = 0.90
                    else:
                        score = 0.75
                else:
                    score = 0.03
            elif dtype == "modern":
                score = 0.35 if _looks_base64(text) else 0.02

            ranked.append((decoder, score))

        ranked.sort(key=lambda item: item[1], reverse=True)
        return ranked[: max(1, top_n)]

    @staticmethod
    def _dedupe_results(results: Sequence[DecoderResult]) -> List[DecoderResult]:
        unique: List[DecoderResult] = []
        seen = set()
        for result in results:
            key = (
                result.algorithm,
                result.plaintext,
                result.password,
                result.method,
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(result)
        return unique

    def _diversify_results(self, results: Sequence[DecoderResult]) -> List[DecoderResult]:
        per_algorithm = {}
        diversified: List[DecoderResult] = []
        for result in results:
            key = result.algorithm
            count = per_algorithm.get(key, 0)
            if count >= self.MAX_RESULTS_PER_ALGORITHM:
                continue
            per_algorithm[key] = count + 1
            diversified.append(result)
        return diversified

    def decrypt_auto(
        self,
        ciphertext: str,
        wordlist: Optional[List[str]] = None,
        max_decoders: int = 5,
    ) -> List[DecoderResult]:
        text = (ciphertext or "").strip()
        if not text:
            return []

        candidates = self.auto_detect(text, top_n=max(20, max_decoders * 6))
        results: List[DecoderResult] = []
        best_confidence = 0.0

        for decoder, probability in candidates:
            attack_results = decoder.attack(text, wordlist=wordlist or [], max_attempts=None)
            for item in attack_results:
                # Keep heuristic probability as a floor to stabilize ranking.
                item.confidence = max(item.confidence, round(probability * 100, 1))
                if item.confidence > best_confidence:
                    best_confidence = item.confidence
                results.append(item)

            # Early stop when a very strong candidate is already found.
            if best_confidence >= 95.0 and len(results) >= max_decoders and probability < 0.5:
                break

        results = self._dedupe_results(results)
        results.sort(key=lambda item: item.confidence, reverse=True)
        results = self._diversify_results(results)
        return results[: max(1, max_decoders)]

    def decrypt_specific(
        self,
        ciphertext: str,
        algorithm_name: str,
        wordlist: Optional[List[str]] = None,
        max_results: int = 5,
    ) -> List[DecoderResult]:
        decoder = self.get_decoder_by_name(algorithm_name)
        if decoder is None:
            return []
        results = decoder.attack((ciphertext or "").strip(), wordlist=wordlist or [], max_attempts=None)
        results.sort(key=lambda item: item.confidence, reverse=True)
        return results[: max(1, max_results)]


decoder_manager = DecoderManager()
decoders = decoder_manager.decoders
