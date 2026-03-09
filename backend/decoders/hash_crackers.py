"""Hash cracking decoders with expanded hash family coverage."""

from __future__ import annotations

import hashlib
from typing import Callable, List, Optional

from .base_decoder import BaseDecoder, DecoderResult

try:
    from Crypto.Hash import MD4  # type: ignore
except Exception:  # pragma: no cover - optional runtime dependency
    MD4 = None


class BaseHashCracker(BaseDecoder):
    def __init__(self, algorithm_name: str, hasher: Callable[[bytes], Optional[str]]) -> None:
        super().__init__(algorithm_name, "hash")
        self._hasher = hasher

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        target = (ciphertext or "").strip().lower()
        if not target:
            return []

        words = list(wordlist or [])
        if not words:
            return []
        if max_attempts is not None:
            words = words[:max_attempts]

        for password in words:
            digest = self._hasher(password.encode("utf-8", errors="ignore"))
            if not digest:
                continue
            if digest.lower() == target:
                return [
                    DecoderResult(
                        success=True,
                        plaintext=password,
                        confidence=100.0,
                        method=self.get_algorithm_name(),
                        password=password,
                        decoder_name=self.get_algorithm_name(),
                        algorithm=self.get_algorithm_name(),
                    )
                ]
        return []


class DigestByLengthCracker(BaseHashCracker):
    def __init__(self, algorithm_name: str, digest_len: int, hasher: Callable[[bytes], str]) -> None:
        self._digest_len = digest_len
        super().__init__(algorithm_name, hasher)

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        if len((ciphertext or "").strip()) != self._digest_len:
            return []
        return super().attack(ciphertext, wordlist=wordlist, max_attempts=max_attempts)


def _ntlm_hash(data: bytes) -> Optional[str]:
    if MD4 is None:
        return None
    try:
        text = data.decode("utf-8", errors="ignore")
        payload = text.encode("utf-16le")
        return MD4.new(payload).hexdigest()
    except Exception:
        return None


class Blake2bCracker(BaseHashCracker):
    def __init__(self) -> None:
        super().__init__("BLAKE2b Hash", lambda data: hashlib.blake2b(data).hexdigest())

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        target = (ciphertext or "").strip().lower()
        if len(target) not in {64, 128}:
            return []
        words = list(wordlist or [])
        if not words:
            return []
        if max_attempts is not None:
            words = words[:max_attempts]

        for password in words:
            raw = password.encode("utf-8", errors="ignore")
            digests = [
                hashlib.blake2b(raw).hexdigest(),  # 128 hex
                hashlib.blake2b(raw, digest_size=32).hexdigest(),  # 64 hex
            ]
            if target in (d.lower() for d in digests):
                return [
                    DecoderResult(
                        success=True,
                        plaintext=password,
                        confidence=100.0,
                        method=self.get_algorithm_name(),
                        password=password,
                        decoder_name=self.get_algorithm_name(),
                        algorithm=self.get_algorithm_name(),
                    )
                ]
        return []


def get_decoders() -> List[BaseDecoder]:
    return [
        DigestByLengthCracker("MD5 Hash", 32, lambda data: hashlib.md5(data).hexdigest()),
        DigestByLengthCracker("SHA1 Hash", 40, lambda data: hashlib.sha1(data).hexdigest()),
        DigestByLengthCracker("SHA224 Hash", 56, lambda data: hashlib.sha224(data).hexdigest()),
        DigestByLengthCracker("SHA256 Hash", 64, lambda data: hashlib.sha256(data).hexdigest()),
        DigestByLengthCracker("SHA384 Hash", 96, lambda data: hashlib.sha384(data).hexdigest()),
        DigestByLengthCracker("SHA512 Hash", 128, lambda data: hashlib.sha512(data).hexdigest()),
        DigestByLengthCracker("SHA3-256 Hash", 64, lambda data: hashlib.sha3_256(data).hexdigest()),
        DigestByLengthCracker("SHA3-512 Hash", 128, lambda data: hashlib.sha3_512(data).hexdigest()),
        Blake2bCracker(),
        BaseHashCracker("bcrypt Hash", lambda data: None),
        BaseHashCracker("scrypt Hash", lambda data: None),
        BaseHashCracker("Argon2 Hash", lambda data: None),
        DigestByLengthCracker("NTLM Hash", 32, _ntlm_hash),
    ]
