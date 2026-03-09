"""
DaVinci Decoder - Cascade Detection System
Multi-layer chain detection with bounded breadth/depth and cumulative scoring.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional

try:
    from text_analyzer import TextAnalyzer
    from decoders.base_decoder import DecoderResult
    from decoders import decoder_manager
except ImportError:
    from .text_analyzer import TextAnalyzer
    from .decoders.base_decoder import DecoderResult
    from .decoders import decoder_manager


@dataclass
class CascadeResult:
    """Extended result object with cascade metadata."""

    algorithm: str
    plaintext: str
    quality_score: float
    confidence: float
    password: Optional[str] = None
    layer: int = 1
    chain: str = ""


@dataclass
class ChainNode:
    text: str
    chain: List[str]
    depth: int
    cumulative_score: float


class CascadeDetector:
    """Cascade detector for multi-layer decryption."""

    MODERN_BINARY_WORDLIST_CAP = 2500
    MODERN_DIRECT_WORDLIST_CAP = 1500
    MODERN_BINARY_DECODER_LIMIT = 6
    MODERN_DIRECT_DECODER_LIMIT = 8
    CLASSICAL_DECODER_LIMIT = 12
    ENCODING_DECODER_LIMIT = 15
    MAX_CHAIN_DEPTH = 3
    CHAIN_FRONTIER_LIMIT = 8
    NEXT_FRONTIER_LIMIT = 16
    SHORT_CIRCUIT_QUALITY = 50.0

    def __init__(self):
        self.analyzer = TextAnalyzer()
        self.decoders = decoder_manager.decoders
        self.total_attempts = 0

    @staticmethod
    def _cap_wordlist(wordlist: List[str], cap: int) -> List[str]:
        if len(wordlist) <= cap:
            return wordlist
        return wordlist[:cap]

    @staticmethod
    def _result_label(result: DecoderResult) -> str:
        base = (result.algorithm or result.decoder_name or result.method or "").strip()
        method = (result.method or "").strip()
        if method and base and method.lower() != base.lower():
            return f"{base} ({method})"
        return base or method or "Unknown"

    @staticmethod
    def _combine_scores(previous_score: float, previous_depth: int, step_score: float) -> float:
        if previous_depth <= 0:
            return min(100.0, step_score)
        averaged = ((previous_score * previous_depth) + step_score) / (previous_depth + 1)
        depth_bonus = min(6.0, previous_depth * 1.5)
        return min(100.0, averaged + depth_bonus)

    def _dedupe_cascade_results(self, results: List[CascadeResult]) -> List[CascadeResult]:
        unique: List[CascadeResult] = []
        seen = set()
        for result in results:
            key = (result.chain or result.algorithm, result.plaintext, result.password)
            if key in seen:
                continue
            seen.add(key)
            unique.append(result)
        return unique

    def _has_readable_encoding_result(self, results: List[CascadeResult]) -> bool:
        for result in results:
            if result.layer < 1:
                continue
            if result.quality_score >= self.SHORT_CIRCUIT_QUALITY and not self.analyzer.is_binary(result.plaintext):
                return True
        return False

    @staticmethod
    def _should_try_classical(ciphertext: str, has_binary_encoding: bool) -> bool:
        if has_binary_encoding:
            return False
        text = (ciphertext or "").strip()
        if not text:
            return False

        letters = sum(1 for ch in text if ch.isalpha())
        allowed = sum(1 for ch in text if ch.isalpha() or ch.isspace() or ch in ".,!?;:'\"-")
        alpha_ratio = letters / len(text)
        allowed_ratio = allowed / len(text)
        return alpha_ratio >= 0.6 and allowed_ratio >= 0.9

    def detect_all(
        self,
        ciphertext: str,
        wordlist: List[str] = None,
        max_results: int = 10,
        max_time: int = 300,
        progress_callback=None,
    ) -> List[CascadeResult]:
        """Full cascade detection with adaptive runtime controls."""
        if wordlist is None:
            wordlist = []

        all_results: List[CascadeResult] = []
        start_time = time.time()

        modern_binary_words = min(len(wordlist), self.MODERN_BINARY_WORDLIST_CAP)
        modern_direct_words = min(len(wordlist), self.MODERN_DIRECT_WORDLIST_CAP)
        encoding_budget = self.ENCODING_DECODER_LIMIT * self.MAX_CHAIN_DEPTH * self.CHAIN_FRONTIER_LIMIT
        total_attempts = encoding_budget + self.CLASSICAL_DECODER_LIMIT
        if wordlist:
            total_attempts += modern_binary_words * self.MODERN_BINARY_DECODER_LIMIT
            total_attempts += modern_direct_words * self.MODERN_DIRECT_DECODER_LIMIT

        current_attempt = 0

        def update_progress(algorithm: str, status: str = "testing"):
            nonlocal current_attempt
            current_attempt += 1
            if progress_callback:
                progress_callback(current_attempt, total_attempts, algorithm, status)

        print("\n" + "=" * 70)
        print("CASCADE DETECTION - UNIVERSAL".center(70))
        print("=" * 70)
        print(f"Ciphertext: {len(ciphertext)} chars")
        print(f"Wordlist: {len(wordlist)} passwords")
        print(f"Timeout: {max_time}s")
        print(f"Estimated attempts: {total_attempts}")
        print("=" * 70)

        print("\nLayer 1..N: encoding chain")
        encoding_results, binary_nodes = self._try_encoding_chain(ciphertext, progress_callback=update_progress)
        all_results.extend(encoding_results)
        has_binary_encoding = len(binary_nodes) > 0

        if wordlist and binary_nodes:
            for node in binary_nodes:
                elapsed = time.time() - start_time
                remaining = max_time - elapsed
                if remaining <= 10:
                    break
                print("  binary payload from chain, trying modern ciphers")
                layer2_results = self._try_ciphers_on_data(
                    binary_data=node.text,
                    wordlist=wordlist,
                    base_algorithm=" -> ".join(node.chain),
                    base_layer=node.depth,
                    base_score=node.cumulative_score,
                    max_time=remaining,
                    progress_callback=update_progress,
                )
                all_results.extend(layer2_results)

        has_readable_encoding = self._has_readable_encoding_result(encoding_results)
        if wordlist and not has_readable_encoding:
            elapsed = time.time() - start_time
            remaining = max_time - elapsed
            if remaining > 20:
                print("\nLayer modern-direct: trying modern ciphers on original payload")
                layer2_direct = self._try_modern_ciphers(
                    ciphertext=ciphertext,
                    wordlist=wordlist,
                    max_time=remaining,
                    progress_callback=update_progress,
                )
                all_results.extend(layer2_direct)
        elif wordlist and has_readable_encoding:
            print("\nModern direct skipped: readable chain candidate already found")

        elapsed = time.time() - start_time
        remaining = max_time - elapsed
        if remaining > 5 and self._should_try_classical(ciphertext, has_binary_encoding):
            print("\nLayer classical: trying classical ciphers")
            layer3_results = self._try_classical_ciphers(
                ciphertext=ciphertext,
                max_attempts=50,
                progress_callback=update_progress,
            )
            all_results.extend(layer3_results)
        else:
            print("\nClassical layer skipped: low likelihood or timeout budget")

        all_results = self._dedupe_cascade_results(all_results)
        all_results.sort(key=lambda item: item.quality_score, reverse=True)

        print("\n" + "=" * 70)
        print(f"Detection done: {len(all_results)} results")
        print(f"Elapsed: {time.time() - start_time:.1f}s")
        print(f"Attempts: {current_attempt}/{total_attempts}")
        print("=" * 70)

        print("\nTop 3 results:")
        for idx, result in enumerate(all_results[:3], 1):
            chain = result.chain if result.chain else result.algorithm
            print(f"{idx}. {chain} (quality={result.quality_score:.0f}%)")
            print(f"   {result.plaintext[:80]}...")

        return all_results[:max_results]

    def _try_encoding_chain(self, ciphertext: str, progress_callback=None) -> tuple[List[CascadeResult], List[ChainNode]]:
        encoding_decoders = [d for d in self.decoders if d.get_algorithm_type() == "encoding"]
        frontier = [ChainNode(text=ciphertext, chain=[], depth=0, cumulative_score=0.0)]
        visited = {ciphertext}

        chain_results: List[CascadeResult] = []
        binary_nodes: List[ChainNode] = []

        for depth in range(1, self.MAX_CHAIN_DEPTH + 1):
            if not frontier:
                break
            next_candidates: List[ChainNode] = []

            for node in frontier[: self.CHAIN_FRONTIER_LIMIT]:
                for decoder in encoding_decoders[: self.ENCODING_DECODER_LIMIT]:
                    try:
                        if progress_callback:
                            progress_callback(decoder.get_algorithm_name(), "testing")
                        self.total_attempts += 1
                        result_list = decoder.attack(node.text, wordlist=[], max_attempts=1)
                    except Exception:
                        continue

                    for result in result_list[:1]:
                        if not result.success:
                            continue
                        plaintext = (result.plaintext or "").strip("\x00")
                        if not plaintext or plaintext == node.text:
                            continue

                        step_quality = self.analyzer.calculate_quality(plaintext)
                        combined = self._combine_scores(node.cumulative_score, node.depth, step_quality)
                        label = self._result_label(result)
                        new_chain = node.chain + [label]

                        chain_results.append(
                            CascadeResult(
                                algorithm=label,
                                plaintext=plaintext,
                                quality_score=combined,
                                confidence=combined,
                                password=result.password,
                                layer=depth,
                                chain=" -> ".join(new_chain),
                            )
                        )

                        next_node = ChainNode(
                            text=plaintext,
                            chain=new_chain,
                            depth=depth,
                            cumulative_score=combined,
                        )

                        if self.analyzer.is_binary(plaintext):
                            binary_nodes.append(next_node)

                        if depth < self.MAX_CHAIN_DEPTH and plaintext not in visited and len(plaintext) <= 20000:
                            visited.add(plaintext)
                            next_candidates.append(next_node)

            if not next_candidates:
                break

            next_candidates.sort(key=lambda item: item.cumulative_score, reverse=True)
            unique_frontier: List[ChainNode] = []
            seen_text = set()
            for node in next_candidates:
                if node.text in seen_text:
                    continue
                seen_text.add(node.text)
                unique_frontier.append(node)
                if len(unique_frontier) >= self.NEXT_FRONTIER_LIMIT:
                    break
            frontier = unique_frontier

        # Keep unique binary states by chain and text.
        unique_binary: List[ChainNode] = []
        seen_binary = set()
        for node in binary_nodes:
            key = (" -> ".join(node.chain), node.text)
            if key in seen_binary:
                continue
            seen_binary.add(key)
            unique_binary.append(node)

        return self._dedupe_cascade_results(chain_results), unique_binary

    def _try_ciphers_on_data(
        self,
        binary_data: str,
        wordlist: List[str],
        base_algorithm: str,
        base_layer: int,
        base_score: float,
        max_time: float,
        progress_callback=None,
    ) -> List[CascadeResult]:
        results: List[CascadeResult] = []
        start_time = time.time()
        capped_wordlist = self._cap_wordlist(wordlist, self.MODERN_BINARY_WORDLIST_CAP)

        modern_ciphers = [
            decoder
            for decoder in self.decoders
            if decoder.get_algorithm_type() == "modern"
            and ("AES" in decoder.get_algorithm_name() or "DES" in decoder.get_algorithm_name())
        ]

        if len(capped_wordlist) < len(wordlist):
            print(f"    wordlist capped (binary mode): {len(capped_wordlist)}/{len(wordlist)}")
        print(f"    testing {len(modern_ciphers)} modern ciphers with {len(capped_wordlist)} passwords")

        for decoder in modern_ciphers[: self.MODERN_BINARY_DECODER_LIMIT]:
            if time.time() - start_time > max_time:
                print("    timeout hit")
                break

            try:
                if progress_callback:
                    progress_callback(decoder.get_algorithm_name(), "testing")
                self.total_attempts += len(capped_wordlist)
                result_list = decoder.attack(
                    binary_data,
                    wordlist=capped_wordlist,
                    max_attempts=len(capped_wordlist),
                )
                for result in result_list:
                    if not result.success:
                        continue
                    quality = self.analyzer.calculate_quality(result.plaintext)
                    if quality <= 70:
                        continue

                    combined_quality = self._combine_scores(base_score, base_layer, quality)
                    label = self._result_label(result)
                    chain = f"{base_algorithm} -> {label}"
                    results.append(
                        CascadeResult(
                            algorithm=label,
                            plaintext=result.plaintext,
                            quality_score=combined_quality,
                            confidence=combined_quality,
                            password=result.password,
                            layer=base_layer + 1,
                            chain=chain,
                        )
                    )
                    print(f"    ok {chain}: quality={combined_quality:.0f}%")
            except Exception:
                continue

        return results

    def _try_modern_ciphers(
        self,
        ciphertext: str,
        wordlist: List[str],
        max_time: float,
        progress_callback=None,
    ) -> List[CascadeResult]:
        results: List[CascadeResult] = []
        start_time = time.time()
        capped_wordlist = self._cap_wordlist(wordlist, self.MODERN_DIRECT_WORDLIST_CAP)

        modern_ciphers = [decoder for decoder in self.decoders if decoder.get_algorithm_type() == "modern"]

        if len(capped_wordlist) < len(wordlist):
            print(f"  wordlist capped (direct mode): {len(capped_wordlist)}/{len(wordlist)}")
        print(f"  testing {len(modern_ciphers)} modern ciphers")

        for decoder in modern_ciphers[: self.MODERN_DIRECT_DECODER_LIMIT]:
            if time.time() - start_time > max_time:
                print("  timeout hit")
                break

            try:
                if progress_callback:
                    progress_callback(decoder.get_algorithm_name(), "testing")
                self.total_attempts += len(capped_wordlist)
                result_list = decoder.attack(
                    ciphertext,
                    wordlist=capped_wordlist,
                    max_attempts=len(capped_wordlist),
                )
                for result in result_list:
                    if not result.success:
                        continue
                    quality = self.analyzer.calculate_quality(result.plaintext)
                    if quality <= 70:
                        continue
                    label = self._result_label(result)
                    results.append(
                        CascadeResult(
                            algorithm=label,
                            plaintext=result.plaintext,
                            quality_score=quality,
                            confidence=quality,
                            password=result.password,
                            layer=1,
                            chain=label,
                        )
                    )
                    print(f"  ok {label}: quality={quality:.0f}%")
            except Exception:
                continue

        return results

    def _try_classical_ciphers(
        self,
        ciphertext: str,
        max_attempts: int = 50,
        progress_callback=None,
    ) -> List[CascadeResult]:
        results: List[CascadeResult] = []
        classical_ciphers = [decoder for decoder in self.decoders if decoder.get_algorithm_type() == "classical"]
        print(f"  testing {len(classical_ciphers)} classical ciphers")

        for decoder in classical_ciphers[: self.CLASSICAL_DECODER_LIMIT]:
            try:
                if progress_callback:
                    progress_callback(decoder.get_algorithm_name(), "testing")
                self.total_attempts += 1
                result_list = decoder.attack(ciphertext, wordlist=[], max_attempts=max_attempts)
                for result in result_list[:3]:
                    if not result.success:
                        continue
                    quality = self.analyzer.calculate_quality(result.plaintext)
                    if quality <= 60:
                        continue
                    label = self._result_label(result)
                    results.append(
                        CascadeResult(
                            algorithm=label,
                            plaintext=result.plaintext,
                            quality_score=quality,
                            confidence=quality,
                            layer=1,
                            chain=label,
                        )
                    )
                    print(f"  ok {label}: quality={quality:.0f}%")
            except Exception:
                continue

        return results


if __name__ == "__main__":
    detector = CascadeDetector()
    detector.detect_all("SGVsbG8gV29ybGQh", wordlist=[])
