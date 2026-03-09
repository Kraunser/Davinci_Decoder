"""High-level engine facade used by tests and API integrations."""

from __future__ import annotations

from typing import List, Optional

from .decoders.decoder_manager import DecoderManager
from .decoders.base_decoder import DecoderResult


class DecoderEngine:
    """Facade around DecoderManager with explicit method names."""

    def __init__(self, manager: Optional[DecoderManager] = None) -> None:
        self.decoder_manager = manager or DecoderManager()

    def auto_detect_and_decrypt(
        self,
        ciphertext: str,
        wordlist: Optional[List[str]] = None,
        max_results: int = 5,
    ) -> List[DecoderResult]:
        return self.decoder_manager.decrypt_auto(
            ciphertext=ciphertext,
            wordlist=wordlist or [],
            max_decoders=max_results,
        )

    def decrypt_with_algorithm(
        self,
        ciphertext: str,
        algorithm_name: str,
        wordlist: Optional[List[str]] = None,
        max_results: int = 5,
    ) -> List[DecoderResult]:
        return self.decoder_manager.decrypt_specific(
            ciphertext=ciphertext,
            algorithm_name=algorithm_name,
            wordlist=wordlist or [],
            max_results=max_results,
        )
