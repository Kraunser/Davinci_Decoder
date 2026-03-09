"""Encoding decoders with broader algorithm coverage."""

from __future__ import annotations

import base64
import binascii
import codecs
import html
import json
import quopri
import re
from typing import Dict, List, Optional
from urllib.parse import unquote

from .base_decoder import BaseDecoder, DecoderResult, score_plaintext

MORSE_TABLE: Dict[str, str] = {
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
    "-----": "0",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
}

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def _single_result(decoder: BaseDecoder, plaintext: str, minimum_confidence: float, method: str) -> List[DecoderResult]:
    return [
        DecoderResult(
            success=True,
            plaintext=plaintext,
            confidence=max(minimum_confidence, score_plaintext(plaintext)),
            method=method,
            decoder_name=decoder.get_algorithm_name(),
            algorithm=decoder.get_algorithm_name(),
        )
    ]


def _decode_base_n(value: str, alphabet: str) -> Optional[bytes]:
    if not value:
        return None
    if any(ch not in alphabet for ch in value):
        return None

    number = 0
    for ch in value:
        number = number * len(alphabet) + alphabet.index(ch)

    raw = number.to_bytes((number.bit_length() + 7) // 8, "big") if number > 0 else b""
    prefix = b"\x00" * (len(value) - len(value.lstrip(alphabet[0])))
    return prefix + raw


class Base64EncodingDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Base64 Encoding", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        cleaned = ciphertext.strip().replace("-", "+").replace("_", "/")
        if not cleaned or not re.fullmatch(r"[A-Za-z0-9+/=]+", cleaned):
            return None
        cleaned += "=" * ((4 - (len(cleaned) % 4)) % 4)
        try:
            return base64.b64decode(cleaned, validate=False).decode("utf-8")
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "base64")
        return _single_result(self, plaintext, 90.0, self.get_algorithm_name()) if plaintext else []


class Base32EncodingDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Base32 Encoding", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        cleaned = ciphertext.strip().upper().replace(" ", "")
        if not cleaned or not re.fullmatch(r"[A-Z2-7=]+", cleaned):
            return None
        cleaned += "=" * ((8 - (len(cleaned) % 8)) % 8)
        try:
            return base64.b32decode(cleaned, casefold=True).decode("utf-8")
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "base32")
        return _single_result(self, plaintext, 88.0, self.get_algorithm_name()) if plaintext else []


class Base58EncodingDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Base58 Encoding", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        cleaned = ciphertext.strip()
        if len(cleaned) < 6:
            return None
        raw = _decode_base_n(cleaned, BASE58_ALPHABET)
        if raw is None:
            return None
        try:
            return raw.decode("utf-8")
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "base58")
        return _single_result(self, plaintext, 76.0, self.get_algorithm_name()) if plaintext else []


class Base62EncodingDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Base62 Encoding", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        cleaned = ciphertext.strip()
        if len(cleaned) < 6:
            return None
        raw = _decode_base_n(cleaned, BASE62_ALPHABET)
        if raw is None:
            return None
        try:
            return raw.decode("utf-8")
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "base62")
        return _single_result(self, plaintext, 74.0, self.get_algorithm_name()) if plaintext else []


class Base85EncodingDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Base85 Encoding", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        cleaned = ciphertext.strip()
        if len(cleaned) < 5:
            return None
        try:
            return base64.b85decode(cleaned.encode("ascii")).decode("utf-8")
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "base85")
        return _single_result(self, plaintext, 84.0, self.get_algorithm_name()) if plaintext else []


class Ascii85EncodingDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("ASCII85 Encoding", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        cleaned = ciphertext.strip()
        if len(cleaned) < 5:
            return None
        try:
            return base64.a85decode(cleaned.encode("ascii"), adobe=False).decode("utf-8")
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "ascii85")
        return _single_result(self, plaintext, 84.0, self.get_algorithm_name()) if plaintext else []


class HexEncodingDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Hex Encoding", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        value = ciphertext.strip()
        if not value or len(value) % 2 != 0 or not re.fullmatch(r"[0-9a-fA-F]+", value):
            return None
        try:
            return binascii.unhexlify(value).decode("utf-8")
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "hex")
        return _single_result(self, plaintext, 88.0, self.get_algorithm_name()) if plaintext else []


class BinaryEncodingDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Binary Encoding", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        chunks = [chunk for chunk in ciphertext.strip().split() if chunk]
        if not chunks:
            return None
        if not all(len(chunk) == 8 and set(chunk).issubset({"0", "1"}) for chunk in chunks):
            return None
        try:
            return "".join(chr(int(chunk, 2)) for chunk in chunks)
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "binary")
        return _single_result(self, plaintext, 86.0, self.get_algorithm_name()) if plaintext else []


class UrlEncodingDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("URL Encoding", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        value = ciphertext.strip()
        if "%" not in value and "+" not in value:
            return None
        decoded = unquote(value)
        return decoded if decoded != value else None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "url")
        return _single_result(self, plaintext, 82.0, self.get_algorithm_name()) if plaintext else []


class QuotedPrintableDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Quoted-Printable", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        value = ciphertext.strip()
        if "=" not in value:
            return None
        try:
            decoded = quopri.decodestring(value.encode("utf-8")).decode("utf-8")
            return decoded if decoded != value else None
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "quoted-printable")
        return _single_result(self, plaintext, 80.0, self.get_algorithm_name()) if plaintext else []


class MorseCodeDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Morse Code", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        cleaned = ciphertext.strip()
        if not cleaned or not re.fullmatch(r"[.\-/\s]+", cleaned):
            return None

        words = cleaned.replace("/", " / ").split(" / ")
        decoded_words: List[str] = []
        for word in words:
            letters = []
            for symbol in word.split():
                letter = MORSE_TABLE.get(symbol)
                if not letter:
                    return None
                letters.append(letter)
            if letters:
                decoded_words.append("".join(letters))

        result = " ".join(decoded_words).strip()
        return result if result else None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "morse")
        return _single_result(self, plaintext, 84.0, self.get_algorithm_name()) if plaintext else []


class HtmlEntityDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("HTML Entity Decode", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        value = ciphertext.strip()
        if "&" not in value or ";" not in value:
            return None
        decoded = html.unescape(value)
        return decoded if decoded != value else None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "html-entity")
        return _single_result(self, plaintext, 82.0, self.get_algorithm_name()) if plaintext else []


class XmlEntityDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("XML Entity Decode", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        value = ciphertext.strip()
        if "&" not in value or ";" not in value:
            return None
        decoded = html.unescape(value)
        return decoded if decoded != value else None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "xml-entity")
        return _single_result(self, plaintext, 82.0, self.get_algorithm_name()) if plaintext else []


class UnicodeEscapeDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Unicode Escape Decode", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        value = ciphertext.strip()
        if "\\u" not in value and "\\x" not in value:
            return None
        try:
            decoded = codecs.decode(value, "unicode_escape")
            return decoded if decoded != value else None
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "unicode-escape")
        return _single_result(self, plaintext, 84.0, self.get_algorithm_name()) if plaintext else []


class JsonEscapeDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("JSON Escape Decode", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        value = ciphertext.strip()
        if "\\n" not in value and "\\t" not in value and '\\"' not in value and "\\u" not in value:
            return None
        try:
            decoded = json.loads(f'"{value}"')
            return decoded if decoded != value else None
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "json-escape")
        return _single_result(self, plaintext, 80.0, self.get_algorithm_name()) if plaintext else []


class OctalEncodingDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Octal Encoding", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        value = ciphertext.strip().replace("\\", " ")
        if not value:
            return None
        parts = [p for p in value.split() if p]
        if not parts:
            return None
        if not all(re.fullmatch(r"[0-7]{1,3}", p) for p in parts):
            return None
        try:
            decoded = "".join(chr(int(p, 8)) for p in parts)
            return decoded if decoded else None
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "octal")
        return _single_result(self, plaintext, 78.0, self.get_algorithm_name()) if plaintext else []


class DecimalEncodingDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Decimal Encoding", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        value = ciphertext.strip()
        parts = [p for p in value.split() if p]
        if not parts or len(parts) < 2:
            return None
        if not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            return None
        try:
            decoded = "".join(chr(int(p)) for p in parts)
            return decoded if decoded else None
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "decimal")
        return _single_result(self, plaintext, 76.0, self.get_algorithm_name()) if plaintext else []


class PunycodeDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("Punycode Decode", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        value = ciphertext.strip()
        if "xn--" not in value:
            return None
        labels = value.split(".")
        decoded_labels = []
        changed = False
        for label in labels:
            if label.startswith("xn--"):
                try:
                    decoded_labels.append(label[4:].encode("ascii").decode("punycode"))
                    changed = True
                except Exception:
                    return None
            else:
                decoded_labels.append(label)
        decoded = ".".join(decoded_labels)
        return decoded if changed else None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "punycode")
        return _single_result(self, plaintext, 85.0, self.get_algorithm_name()) if plaintext else []


class JwtPayloadDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("JWT Payload Decode", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        token = ciphertext.strip()
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload = parts[1].replace("-", "+").replace("_", "/")
        payload += "=" * ((4 - (len(payload) % 4)) % 4)
        try:
            decoded = base64.b64decode(payload, validate=False).decode("utf-8")
            return decoded if decoded else None
        except Exception:
            return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "jwt-payload")
        return _single_result(self, plaintext, 92.0, self.get_algorithm_name()) if plaintext else []


class Rot13Decoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("ROT13 Encoding", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        value = ciphertext.strip()
        if not value:
            return None
        decoded = codecs.decode(value, "rot_13")
        return decoded if decoded != value else None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "rot13")
        return _single_result(self, plaintext, 78.0, self.get_algorithm_name()) if plaintext else []


class UuencodeDecoder(BaseDecoder):
    def __init__(self) -> None:
        super().__init__("UUEncode", "encoding")

    def decrypt(self, ciphertext: str, key: bytes, method: str) -> Optional[str]:
        value = ciphertext.strip()
        if not value:
            return None
        lines = value.splitlines() or [value]
        for line in lines:
            try:
                decoded = binascii.a2b_uu(line.encode("ascii")).decode("utf-8")
                if decoded:
                    return decoded
            except Exception:
                continue
        return None

    def attack(self, ciphertext: str, wordlist=None, max_attempts=None) -> List[DecoderResult]:
        plaintext = self.decrypt(ciphertext, b"", "uuencode")
        return _single_result(self, plaintext, 75.0, self.get_algorithm_name()) if plaintext else []


def get_decoders() -> List[BaseDecoder]:
    # Keep 21 encoding algorithms in total.
    return [
        Base64EncodingDecoder(),
        Base32EncodingDecoder(),
        Base58EncodingDecoder(),
        Base62EncodingDecoder(),
        Base85EncodingDecoder(),
        UuencodeDecoder(),
        QuotedPrintableDecoder(),
        MorseCodeDecoder(),
        Ascii85EncodingDecoder(),
        HtmlEntityDecoder(),
        UnicodeEscapeDecoder(),
        OctalEncodingDecoder(),
        DecimalEncodingDecoder(),
        PunycodeDecoder(),
        JwtPayloadDecoder(),
        JsonEscapeDecoder(),
        XmlEntityDecoder(),
        HexEncodingDecoder(),
        BinaryEncodingDecoder(),
        UrlEncodingDecoder(),
        Rot13Decoder(),
    ]
