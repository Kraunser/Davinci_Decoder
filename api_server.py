"""DaVinci Decoder - Flask API server."""

from __future__ import annotations

import json
import os
import base64
import binascii
import re
import sys
import threading
import uuid
from functools import lru_cache
from typing import Any, Dict, List, Optional

from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

sys.path.insert(0, "backend")

from decoders import decoder_manager  # noqa: E402

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

MAX_CIPHERTEXT_SIZE = 100_000
MAX_FILE_SIZE = 2_000_000
MAX_WORDLIST_ITEMS = 20_000
MAX_WORD_LENGTH = 256
DEFAULT_MAX_RESULTS = 5
MAX_RESULTS_LIMIT = 20
TEXT_PRINTABLE_THRESHOLD = 0.85
DATA_URL_PATTERN = re.compile(r"^data:(?P<mime>[\w.+/-]+);base64,(?P<data>[A-Za-z0-9+/=\s]+)$", re.IGNORECASE)
DOWNLOAD_EXTENSIONS = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
    "audio/wav": "wav",
    "audio/mpeg": "mp3",
    "audio/ogg": "ogg",
    "audio/flac": "flac",
    "application/octet-stream": "bin",
}


def _safe_payload() -> Dict[str, Any]:
    payload = request.get_json(silent=True)
    return payload if isinstance(payload, dict) else {}


def _safe_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


@lru_cache(maxsize=1)
def _load_default_wordlist() -> List[str]:
    expanded_wordlist = os.path.join("backend", "wordlists", "wordlist_expandida.txt")
    fallback_wordlist = os.path.join("backend", "wordlists", "wordlist.txt")
    candidate_path = expanded_wordlist if os.path.exists(expanded_wordlist) else fallback_wordlist

    if not os.path.exists(candidate_path):
        return []

    with open(candidate_path, "r", encoding="utf-8") as file:
        words = [line.strip() for line in file if line.strip()]
    return words[:MAX_WORDLIST_ITEMS]


def _normalize_wordlist(raw_wordlist: Any) -> List[str]:
    if raw_wordlist is None:
        return []
    if not isinstance(raw_wordlist, list):
        raise ValueError("wordlist must be a list")

    normalized: List[str] = []
    seen = set()
    for item in raw_wordlist:
        word = str(item).strip()
        if not word:
            continue
        if len(word) > MAX_WORD_LENGTH:
            word = word[:MAX_WORD_LENGTH]
        if word in seen:
            continue
        seen.add(word)
        normalized.append(word)
        if len(normalized) >= MAX_WORDLIST_ITEMS:
            break

    return normalized


def _parse_form_wordlist(raw_wordlist: Any) -> List[str]:
    if raw_wordlist in (None, ""):
        return []
    if isinstance(raw_wordlist, str):
        stripped = raw_wordlist.strip()
        if not stripped:
            return []
        if stripped.startswith("["):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError("wordlist must be a JSON list or newline-separated text") from exc
            return _normalize_wordlist(parsed)
        return _normalize_wordlist(stripped.splitlines())
    return _normalize_wordlist(raw_wordlist)


def _validate_ciphertext(ciphertext: str) -> None:
    if not ciphertext:
        raise ValueError("Ciphertext is required")
    if len(ciphertext) > MAX_CIPHERTEXT_SIZE:
        raise OverflowError("Ciphertext too large (max 100KB)")


def _looks_like_text(text: str) -> bool:
    if not text:
        return False

    printable = 0
    total = 0
    for char in text:
        total += 1
        if char.isprintable() or char in "\r\n\t":
            printable += 1

    if total == 0:
        return False
    return (printable / total) >= TEXT_PRINTABLE_THRESHOLD


def _extract_ciphertext_from_upload() -> tuple[str, Dict[str, Any]]:
    uploaded_file = request.files.get("file")
    if uploaded_file is None or not uploaded_file.filename:
        raise ValueError("File is required")

    raw_bytes = uploaded_file.read(MAX_FILE_SIZE + 1)
    if len(raw_bytes) > MAX_FILE_SIZE:
        raise OverflowError("File too large (max 2MB)")
    if not raw_bytes:
        raise ValueError("Uploaded file is empty")

    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            decoded = raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

        if _looks_like_text(decoded):
            ciphertext = decoded.strip()
            _validate_ciphertext(ciphertext)
            return ciphertext, {
                "type": "file",
                "filename": uploaded_file.filename,
                "size": len(raw_bytes),
                "encoding": encoding,
            }

    raise ValueError("Only text-based encrypted files are supported right now")


def _sniff_media_mime(raw: bytes) -> Optional[str]:
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if raw.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if raw.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if raw.startswith(b"RIFF") and raw[8:12] == b"WEBP":
        return "image/webp"
    if raw.startswith(b"RIFF") and raw[8:12] == b"WAVE":
        return "audio/wav"
    if raw.startswith(b"ID3") or (len(raw) >= 2 and raw[0] == 0xFF and (raw[1] & 0xE0) == 0xE0):
        return "audio/mpeg"
    if raw.startswith(b"OggS"):
        return "audio/ogg"
    if raw.startswith(b"fLaC"):
        return "audio/flac"
    return None


def _build_preview_payload(raw: bytes, mime_type: str, source_encoding: str) -> Dict[str, Any]:
    kind = "binary"
    if mime_type.startswith("image/"):
        kind = "image"
    elif mime_type.startswith("audio/"):
        kind = "audio"

    return {
        "kind": kind,
        "mime_type": mime_type,
        "size": len(raw),
        "source_encoding": source_encoding,
        "download_name": f"decoded.{DOWNLOAD_EXTENSIONS.get(mime_type, 'bin')}",
        "data_url": f"data:{mime_type};base64,{base64.b64encode(raw).decode('ascii')}",
    }


def _detect_preview_payload(plaintext: str) -> Optional[Dict[str, Any]]:
    value = plaintext.strip()
    if not value:
        return None

    data_url_match = DATA_URL_PATTERN.fullmatch(value)
    if data_url_match:
        compact_data = re.sub(r"\s+", "", data_url_match.group("data"))
        padded = compact_data + "=" * ((4 - (len(compact_data) % 4)) % 4)
        try:
            raw = base64.b64decode(padded, validate=False)
        except (ValueError, binascii.Error):
            return None
        mime_type = data_url_match.group("mime").lower()
        return _build_preview_payload(raw, mime_type or "application/octet-stream", "data-url")

    compact = re.sub(r"\s+", "", value)

    if len(compact) >= 32 and re.fullmatch(r"[A-Za-z0-9+/=]+", compact):
        padded = compact + "=" * ((4 - (len(compact) % 4)) % 4)
        try:
            raw = base64.b64decode(padded, validate=False)
        except (ValueError, binascii.Error):
            raw = b""
        mime_type = _sniff_media_mime(raw)
        if mime_type:
            return _build_preview_payload(raw, mime_type, "base64")

    if len(compact) >= 32 and len(compact) % 2 == 0 and re.fullmatch(r"[0-9A-Fa-f]+", compact):
        try:
            raw = binascii.unhexlify(compact)
        except (ValueError, binascii.Error):
            raw = b""
        mime_type = _sniff_media_mime(raw)
        if mime_type:
            return _build_preview_payload(raw, mime_type, "hex")

    return None


def _enrich_result_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    enriched = dict(entry)
    plaintext = str(enriched.get("plaintext", ""))
    preview = _detect_preview_payload(plaintext)
    if preview:
        enriched["output_type"] = preview["kind"]
        enriched["mime_type"] = preview["mime_type"]
        enriched["preview"] = preview
    else:
        enriched["output_type"] = "text"
    return enriched


def _auto_detect_result_sort_key(entry: Dict[str, Any]):
    return (
        1 if entry.get("output_type") == "text" else 0,
        1 if "->" not in str(entry.get("algorithm", "")) else 0,
        float(entry.get("confidence", 0.0)),
    )


def _format_decoder_results(results) -> List[Dict[str, Any]]:
    formatted = []
    for result in results:
        formatted.append(
            _enrich_result_entry(
            {
                "algorithm": result["algorithm"],
                "plaintext": result["plaintext"],
                "confidence": result["confidence"],
                "password": result["password"],
                "method": result["method"],
            }
            )
        )
    return formatted


def _algorithm_counts() -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for decoder in decoder_manager.decoders:
        algo_type = decoder.get_algorithm_type()
        counts[algo_type] = counts.get(algo_type, 0) + 1
    return counts


def _run_auto_detect(ciphertext: str, wordlist: List[str], max_results: int) -> Dict[str, Any]:
    _validate_ciphertext(ciphertext)
    if not wordlist:
        wordlist = _load_default_wordlist()

    from cascade_detector import CascadeDetector
    from progress_manager import progress_manager

    session_id = str(uuid.uuid4())
    progress_manager.create_session(session_id)

    def progress_callback(current, total, algorithm, status):
        progress_manager.update_progress(session_id, current, total, algorithm, status)

    results_holder = {"results": None, "error": None}

    def run_detection():
        try:
            detector = CascadeDetector()
            results_holder["results"] = detector.detect_all(
                ciphertext=ciphertext,
                wordlist=wordlist,
                max_results=max_results * 3,
                max_time=300,
                progress_callback=progress_callback,
            )
        except Exception as exc:
            results_holder["error"] = str(exc)

    detection_thread = threading.Thread(target=run_detection, daemon=True)
    detection_thread.start()
    detection_thread.join(timeout=310)

    if detection_thread.is_alive():
        raise TimeoutError("Detection timeout")
    if results_holder["error"]:
        raise RuntimeError(results_holder["error"])

    cascade_results = results_holder["results"] or []
    candidate_entries = [
        _enrich_result_entry(
            {
                "algorithm": result.chain if result.chain else result.algorithm,
                "plaintext": result.plaintext,
                "confidence": result.quality_score,
                "password": result.password,
                "method": result.algorithm,
                "layer": result.layer,
            }
        )
        for result in cascade_results[: max_results * 4]
    ]
    candidate_entries.sort(key=_auto_detect_result_sort_key, reverse=True)
    formatted = candidate_entries[:max_results]
    return {"session_id": session_id, "results": formatted}


def _run_specific_decrypt(
    ciphertext: str,
    algorithm: str,
    wordlist: List[str],
    max_results: int,
) -> Dict[str, Any]:
    _validate_ciphertext(ciphertext)
    if not algorithm:
        raise ValueError("Algorithm is required")

    results = decoder_manager.decrypt_specific(
        ciphertext=ciphertext,
        algorithm_name=algorithm,
        wordlist=wordlist,
        max_results=max_results,
    )
    return {"results": _format_decoder_results(results)}


def _error_response(exc: Exception):
    if isinstance(exc, ValueError):
        return jsonify({"success": False, "error": str(exc)}), 400
    if isinstance(exc, OverflowError):
        return jsonify({"success": False, "error": str(exc)}), 413
    if isinstance(exc, TimeoutError):
        return jsonify({"success": False, "error": str(exc)}), 504
    return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")


@app.route("/<path:path>")
def serve_static(path: str):
    return send_from_directory("frontend", path)


@app.route("/api/algorithms", methods=["GET"])
def get_algorithms():
    try:
        algorithms = [
            {
                "name": decoder.get_algorithm_name(),
                "type": decoder.get_algorithm_type(),
            }
            for decoder in decoder_manager.decoders
        ]
        return jsonify(
            {
                "success": True,
                "count": len(algorithms),
                "algorithms": algorithms,
                "by_type": _algorithm_counts(),
            }
        )
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/auto-detect", methods=["POST"])
def auto_detect():
    try:
        data = _safe_payload()
        ciphertext = str(data.get("ciphertext", "")).strip()
        max_results = _safe_int(
            data.get("max_results", DEFAULT_MAX_RESULTS),
            default=DEFAULT_MAX_RESULTS,
            minimum=1,
            maximum=MAX_RESULTS_LIMIT,
        )
        try:
            wordlist = _normalize_wordlist(data.get("wordlist"))
        except ValueError as exc:
            return jsonify({"success": False, "error": str(exc)}), 400
        result = _run_auto_detect(ciphertext, wordlist, max_results)
        return jsonify({"success": True, **result})
    except Exception as exc:
        return _error_response(exc)


@app.route("/api/decrypt", methods=["POST"])
def decrypt_specific():
    try:
        data = _safe_payload()
        ciphertext = str(data.get("ciphertext", "")).strip()
        algorithm = str(data.get("algorithm", "")).strip()
        max_results = _safe_int(
            data.get("max_results", DEFAULT_MAX_RESULTS),
            default=DEFAULT_MAX_RESULTS,
            minimum=1,
            maximum=MAX_RESULTS_LIMIT,
        )
        try:
            wordlist = _normalize_wordlist(data.get("wordlist"))
        except ValueError as exc:
            return jsonify({"success": False, "error": str(exc)}), 400
        result = _run_specific_decrypt(ciphertext, algorithm, wordlist, max_results)
        return jsonify({"success": True, **result})
    except Exception as exc:
        return _error_response(exc)


@app.route("/api/auto-detect-file", methods=["POST"])
def auto_detect_file():
    try:
        ciphertext, source = _extract_ciphertext_from_upload()
        max_results = _safe_int(
            request.form.get("max_results", DEFAULT_MAX_RESULTS),
            default=DEFAULT_MAX_RESULTS,
            minimum=1,
            maximum=MAX_RESULTS_LIMIT,
        )
        wordlist = _parse_form_wordlist(request.form.get("wordlist"))
        result = _run_auto_detect(ciphertext, wordlist, max_results)
        return jsonify({"success": True, "source": source, **result})
    except Exception as exc:
        return _error_response(exc)


@app.route("/api/decrypt-file", methods=["POST"])
def decrypt_specific_file():
    try:
        ciphertext, source = _extract_ciphertext_from_upload()
        algorithm = str(request.form.get("algorithm", "")).strip()
        max_results = _safe_int(
            request.form.get("max_results", DEFAULT_MAX_RESULTS),
            default=DEFAULT_MAX_RESULTS,
            minimum=1,
            maximum=MAX_RESULTS_LIMIT,
        )
        wordlist = _parse_form_wordlist(request.form.get("wordlist"))
        result = _run_specific_decrypt(ciphertext, algorithm, wordlist, max_results)
        return jsonify({"success": True, "source": source, **result})
    except Exception as exc:
        return _error_response(exc)


@app.route("/api/progress/<session_id>", methods=["GET"])
def get_progress(session_id: str):
    from progress_manager import progress_manager

    def generate():
        for update in progress_manager.get_updates(session_id):
            if "heartbeat" in update:
                yield f"event: heartbeat\ndata: {json.dumps({'alive': True})}\n\n"
            else:
                yield f"data: {json.dumps(update)}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "algorithms": len(decoder_manager.decoders)})


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DaVinci Decoder API Server".center(70))
    print("=" * 70)
    print(f"Loaded algorithms: {len(decoder_manager.decoders)}")
    print("Server: http://localhost:5000")
    print("Endpoints:")
    print("   - GET  /")
    print("   - GET  /api/algorithms")
    print("   - POST /api/auto-detect")
    print("   - POST /api/auto-detect-file")
    print("   - POST /api/decrypt")
    print("   - POST /api/decrypt-file")
    print("   - GET  /api/progress/<id>")
    print("   - GET  /api/health")
    print("=" * 70 + "\n")

    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
