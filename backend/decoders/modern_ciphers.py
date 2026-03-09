"""Modern cipher decoders and placeholders."""

from __future__ import annotations

import base64
import hashlib
from typing import Dict, List, Optional

from Crypto.Cipher import AES, DES3
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad

from .base_decoder import BaseDecoder, DecoderResult, PlaceholderDecoder, score_plaintext


def _decode_base64_payload(ciphertext: str) -> Optional[bytes]:
    cleaned = ciphertext.strip().replace("-", "+").replace("_", "/")
    if not cleaned:
        return None
    padding = (4 - (len(cleaned) % 4)) % 4
    cleaned += "=" * padding
    try:
        return base64.b64decode(cleaned, validate=False)
    except Exception:
        return None


class AES256CBCDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("AES-256-CBC", "modern")

    def derive_keys(self, password: str) -> Dict[str, bytes]:
        if not password:
            return {}
        raw = password.encode("utf-8", errors="ignore")
        return {
            "PBKDF2-100-empty-salt": PBKDF2(password, b"", dkLen=32, count=100),
            "SHA256": hashlib.sha256(raw).digest(),
            "RAW-32": raw.ljust(32, b"\x00")[:32],
        }

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        payload = _decode_base64_payload(ciphertext)
        if not payload or len(payload) < 32:
            return None

        iv, data = payload[:16], payload[16:]
        if len(data) % AES.block_size != 0:
            return None

        try:
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            plaintext = unpad(cipher.decrypt(data), AES.block_size)
            return plaintext.decode("utf-8")
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        words = list(wordlist or [])
        if not words:
            return []
        if max_attempts is not None:
            words = words[:max_attempts]

        results: List[DecoderResult] = []
        for password in words:
            for method, key in self.derive_keys(password).items():
                plaintext = self.decrypt(ciphertext, key, method)
                if not plaintext:
                    continue
                results.append(
                    DecoderResult(
                        success=True,
                        plaintext=plaintext,
                        confidence=max(85.0, score_plaintext(plaintext)),
                        method=method,
                        password=password,
                        key_hex=key.hex(),
                        decoder_name=self.get_algorithm_name(),
                        algorithm=self.get_algorithm_name(),
                    )
                )

        results.sort(key=lambda item: item.confidence, reverse=True)
        return results


class AES128ECBDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("AES-128-ECB", "modern")

    def derive_keys(self, password: str) -> Dict[str, bytes]:
        if not password:
            return {}
        raw = password.encode("utf-8", errors="ignore")
        return {
            "MD5": hashlib.md5(raw).digest(),
            "RAW-16": raw.ljust(16, b"\x00")[:16],
        }

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        payload = _decode_base64_payload(ciphertext)
        if not payload or len(payload) % AES.block_size != 0:
            return None
        try:
            cipher = AES.new(key, AES.MODE_ECB)
            plaintext = cipher.decrypt(payload)
            try:
                plaintext = unpad(plaintext, AES.block_size)
            except ValueError:
                pass
            return plaintext.decode("utf-8")
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        words = list(wordlist or [])
        if not words:
            return []
        if max_attempts is not None:
            words = words[:max_attempts]

        results: List[DecoderResult] = []
        for password in words:
            for method, key in self.derive_keys(password).items():
                plaintext = self.decrypt(ciphertext, key, method)
                if not plaintext:
                    continue
                results.append(
                    DecoderResult(
                        success=True,
                        plaintext=plaintext,
                        confidence=max(82.0, score_plaintext(plaintext)),
                        method=method,
                        password=password,
                        key_hex=key.hex(),
                        decoder_name=self.get_algorithm_name(),
                        algorithm=self.get_algorithm_name(),
                    )
                )

        results.sort(key=lambda item: item.confidence, reverse=True)
        return results


class AES128CBCDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("AES-128-CBC", "modern")

    def derive_keys(self, password: str) -> Dict[str, bytes]:
        if not password:
            return {}
        raw = password.encode("utf-8", errors="ignore")
        return {
            "MD5": hashlib.md5(raw).digest(),
            "PBKDF2-100-empty-salt": PBKDF2(password, b"", dkLen=16, count=100),
            "RAW-16": raw.ljust(16, b"\x00")[:16],
        }

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        payload = _decode_base64_payload(ciphertext)
        if not payload or len(payload) < 32:
            return None
        iv, data = payload[:16], payload[16:]
        if len(data) % AES.block_size != 0:
            return None
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            plaintext = unpad(cipher.decrypt(data), AES.block_size)
            return plaintext.decode("utf-8")
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        words = list(wordlist or [])
        if not words:
            return []
        if max_attempts is not None:
            words = words[:max_attempts]
        results: List[DecoderResult] = []
        for password in words:
            for method, key in self.derive_keys(password).items():
                plaintext = self.decrypt(ciphertext, key, method)
                if not plaintext:
                    continue
                results.append(
                    DecoderResult(
                        success=True,
                        plaintext=plaintext,
                        confidence=max(84.0, score_plaintext(plaintext)),
                        method=method,
                        password=password,
                        key_hex=key.hex(),
                        decoder_name=self.get_algorithm_name(),
                        algorithm=self.get_algorithm_name(),
                    )
                )
        results.sort(key=lambda item: item.confidence, reverse=True)
        return results


class TripleDESCBCDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("3DES-CBC", "modern")

    def derive_keys(self, password: str) -> Dict[str, bytes]:
        if not password:
            return {}
        raw = password.encode("utf-8", errors="ignore")

        candidates = {
            "SHA256-24": hashlib.sha256(raw).digest()[:24],
            "PBKDF2-24": PBKDF2(password, b"", dkLen=24, count=100),
            "RAW-24": raw.ljust(24, b"\x00")[:24],
        }

        adjusted: Dict[str, bytes] = {}
        for name, key in candidates.items():
            try:
                adjusted[name] = DES3.adjust_key_parity(key)
            except Exception:
                continue
        return adjusted

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        payload = _decode_base64_payload(ciphertext)
        if not payload or len(payload) < 16:
            return None
        iv, data = payload[:8], payload[8:]
        if len(data) % DES3.block_size != 0:
            return None
        try:
            cipher = DES3.new(key, DES3.MODE_CBC, iv=iv)
            plaintext = unpad(cipher.decrypt(data), DES3.block_size)
            return plaintext.decode("utf-8")
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        words = list(wordlist or [])
        if not words:
            return []
        if max_attempts is not None:
            words = words[:max_attempts]
        results: List[DecoderResult] = []
        for password in words:
            for method, key in self.derive_keys(password).items():
                plaintext = self.decrypt(ciphertext, key, method)
                if not plaintext:
                    continue
                results.append(
                    DecoderResult(
                        success=True,
                        plaintext=plaintext,
                        confidence=max(82.0, score_plaintext(plaintext)),
                        method=method,
                        password=password,
                        key_hex=key.hex(),
                        decoder_name=self.get_algorithm_name(),
                        algorithm=self.get_algorithm_name(),
                    )
                )
        results.sort(key=lambda item: item.confidence, reverse=True)
        return results


def get_decoders() -> List[BaseDecoder]:
    real_decoders: List[BaseDecoder] = [
        AES256CBCDecoder(),
        AES128ECBDecoder(),
        AES128CBCDecoder(),
        TripleDESCBCDecoder(),
    ]

    placeholder_names = [
        "AES-192-CBC",
        "AES-256-ECB",
        "AES-128-GCM",
        "AES-192-GCM",
        "AES-256-GCM",
        "AES-128-CFB",
        "AES-192-CFB",
        "AES-256-CFB",
        "AES-128-OFB",
        "AES-192-OFB",
        "AES-256-OFB",
        "AES-128-CTR",
        "AES-192-CTR",
        "AES-256-CTR",
        "3DES-ECB",
        "Blowfish-ECB",
        "Blowfish-CBC",
        "ChaCha20",
        "RC4",
        "RC5",
        "RC6",
        "Twofish",
        "CAST5",
        "Camellia",
        "IDEA",
        "Serpent",
        "SM4",
        "XTEA",
        "Salsa20",
        "Rabbit",
        "HC-128",
        "SEED",
    ]

    placeholders = [PlaceholderDecoder(name, "modern") for name in placeholder_names]
    return real_decoders + placeholders
