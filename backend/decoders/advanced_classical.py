"""Reserved module for advanced classical ciphers."""

from __future__ import annotations

from typing import List

from .base_decoder import BaseDecoder


def get_decoders() -> List[BaseDecoder]:
    return []
