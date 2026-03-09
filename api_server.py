"""DaVinci Decoder - Flask API server."""

from __future__ import annotations

import json
import os
import sys
import threading
import uuid
from functools import lru_cache
from typing import Any, Dict, List

from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

sys.path.insert(0, "backend")

from decoders import decoder_manager  # noqa: E402

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

MAX_CIPHERTEXT_SIZE = 100_000
MAX_WORDLIST_ITEMS = 20_000
MAX_WORD_LENGTH = 256
DEFAULT_MAX_RESULTS = 5
MAX_RESULTS_LIMIT = 20


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


def _format_decoder_results(results) -> List[Dict[str, Any]]:
    formatted = []
    for result in results:
        formatted.append(
            {
                "algorithm": result["algorithm"],
                "plaintext": result["plaintext"],
                "confidence": result["confidence"],
                "password": result["password"],
                "method": result["method"],
            }
        )
    return formatted


def _algorithm_counts() -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for decoder in decoder_manager.decoders:
        algo_type = decoder.get_algorithm_type()
        counts[algo_type] = counts.get(algo_type, 0) + 1
    return counts


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

        if not ciphertext:
            return jsonify({"success": False, "error": "Ciphertext is required"}), 400
        if len(ciphertext) > MAX_CIPHERTEXT_SIZE:
            return jsonify({"success": False, "error": "Ciphertext too large (max 100KB)"}), 413

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
            return jsonify({"success": False, "error": "Detection timeout"}), 504
        if results_holder["error"]:
            return jsonify({"success": False, "error": results_holder["error"]}), 500

        cascade_results = results_holder["results"] or []
        formatted = [
            {
                "algorithm": result.chain if result.chain else result.algorithm,
                "plaintext": result.plaintext,
                "confidence": result.quality_score,
                "password": result.password,
                "method": result.algorithm,
                "layer": result.layer,
            }
            for result in cascade_results[:max_results]
        ]

        return jsonify({"success": True, "session_id": session_id, "results": formatted})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


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

        if not ciphertext:
            return jsonify({"success": False, "error": "Ciphertext is required"}), 400
        if len(ciphertext) > MAX_CIPHERTEXT_SIZE:
            return jsonify({"success": False, "error": "Ciphertext too large (max 100KB)"}), 413
        if not algorithm:
            return jsonify({"success": False, "error": "Algorithm is required"}), 400

        results = decoder_manager.decrypt_specific(
            ciphertext=ciphertext,
            algorithm_name=algorithm,
            wordlist=wordlist,
            max_results=max_results,
        )
        return jsonify({"success": True, "results": _format_decoder_results(results)})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


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
    print("   - POST /api/decrypt")
    print("   - GET  /api/progress/<id>")
    print("   - GET  /api/health")
    print("=" * 70 + "\n")

    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
