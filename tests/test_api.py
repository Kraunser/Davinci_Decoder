"""
DaVinci Decoder - Test Suite
Pytest configuration and basic tests
"""

import pytest
import sys
import os
import io
import base64
import hashlib
import wave

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_server import app
from backend.decoder_engine import DecoderEngine
from backend.decoders.decoder_manager import DecoderManager


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def decoder_manager():
    """Decoder manager instance"""
    return DecoderManager()


@pytest.fixture
def decoder_engine():
    """Decoder engine instance"""
    return DecoderEngine()


# === API Tests ===

def test_health_endpoint(client):
    """Test /api/health endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'algorithms' in data
    assert data['algorithms'] > 0


def test_algorithms_endpoint(client):
    """Test /api/algorithms endpoint"""
    response = client.get('/api/algorithms')
    assert response.status_code == 200
    data = response.get_json()
    assert 'algorithms' in data
    assert 'count' in data
    assert 'by_type' in data
    assert len(data['algorithms']) == data['count']
    assert data['count'] >= 102
    assert sum(data['by_type'].values()) == data['count']


def test_auto_detect_base64(client):
    """Test auto-detect with Base64"""
    payload = {
        'ciphertext': 'SGVsbG8gV29ybGQh',
        'wordlist': [],
        'max_results': 5
    }
    response = client.post('/api/auto-detect',
                          json=payload,
                          content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert 'success' in data
    
    if data['success']:
        assert len(data['results']) > 0
        # Should detect Base64
        assert any('Base64' in r['algorithm'] for r in data['results'])


def test_auto_detect_empty_ciphertext(client):
    """Test auto-detect with empty ciphertext"""
    payload = {
        'ciphertext': '',
        'wordlist': []
    }
    response = client.post('/api/auto-detect',
                          json=payload,
                          content_type='application/json')
    assert response.status_code == 400


def test_auto_detect_too_large(client):
    """Test auto-detect with oversized ciphertext"""
    payload = {
        'ciphertext': 'A' * 200000,  # >100KB
        'wordlist': []
    }
    response = client.post('/api/auto-detect',
                          json=payload,
                          content_type='application/json')
    assert response.status_code == 413


def test_auto_detect_invalid_wordlist_type(client):
    """Wordlist must be list"""
    payload = {
        'ciphertext': 'SGVsbG8gV29ybGQh',
        'wordlist': 'not-a-list'
    }
    response = client.post('/api/auto-detect', json=payload)
    assert response.status_code == 400


def test_auto_detect_string_max_results(client):
    """max_results accepts numeric strings"""
    payload = {
        'ciphertext': 'SGVsbG8gV29ybGQh',
        'wordlist': [],
        'max_results': '2'
    }
    response = client.post('/api/auto-detect', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['results']) <= 2


def test_auto_detect_file_upload(client):
    """Auto-detect should accept text file uploads"""
    response = client.post(
        '/api/auto-detect-file',
        data={
            'file': (io.BytesIO(b'SGVsbG8gV29ybGQh'), 'cipher.txt'),
            'wordlist': '',
            'max_results': '5',
        },
        content_type='multipart/form-data',
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['source']['filename'] == 'cipher.txt'
    assert any('Base64' in r['algorithm'] and r['plaintext'] == 'Hello World!' for r in data['results'])


def test_decrypt_file_upload_specific_algorithm(client):
    """Specific decrypt should accept text file uploads"""
    response = client.post(
        '/api/decrypt-file',
        data={
            'file': (io.BytesIO(b'SGVsbG8gV29ybGQh'), 'cipher.txt'),
            'algorithm': 'Base64 Encoding',
            'wordlist': '',
        },
        content_type='multipart/form-data',
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['source']['filename'] == 'cipher.txt'
    assert len(data['results']) > 0
    assert data['results'][0]['plaintext'] == 'Hello World!'


def test_decrypt_image_preview_payload(client):
    """Binary image payloads should be exposed as image previews"""
    png_ciphertext = (
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQImWNgYGD4DwABBAEAAPp0WQAAAABJRU5ErkJggg=='
    )
    response = client.post(
        '/api/decrypt',
        json={
            'ciphertext': png_ciphertext,
            'algorithm': 'Base64 Encoding',
            'wordlist': [],
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    preview = data['results'][0]['preview']
    assert data['results'][0]['output_type'] == 'image'
    assert preview['mime_type'] == 'image/png'
    assert preview['data_url'].startswith('data:image/png;base64,')


def test_decrypt_audio_preview_payload(client):
    """Binary audio payloads should be exposed as audio previews"""
    audio_buffer = io.BytesIO()
    with wave.open(audio_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(8000)
        wav_file.writeframes(b'\x00\x00' * 16)

    audio_ciphertext = base64.b64encode(audio_buffer.getvalue()).decode('ascii')
    response = client.post(
        '/api/decrypt',
        json={
            'ciphertext': audio_ciphertext,
            'algorithm': 'Base64 Encoding',
            'wordlist': [],
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    preview = data['results'][0]['preview']
    assert data['results'][0]['output_type'] == 'audio'
    assert preview['mime_type'] == 'audio/wav'
    assert preview['data_url'].startswith('data:audio/wav;base64,')


# === Decoder Manager Tests ===

def test_decoder_manager_initialization(decoder_manager):
    """Test decoder manager initializes correctly"""
    assert len(decoder_manager.active_decoders) > 0
    assert len(decoder_manager.list_algorithms()) >= 102


def test_decoder_manager_list_algorithms(decoder_manager):
    """Test algorithm listing"""
    algorithms = decoder_manager.list_algorithms()
    
    # Check for key algorithms
    assert 'Base64 Encoding' in algorithms
    assert 'Caesar Cipher' in algorithms
    assert any('AES' in algo for algo in algorithms)


def test_base64_decoding(decoder_manager):
    """Test Base64 decoding"""
    ciphertext = 'SGVsbG8gV29ybGQh'
    results = decoder_manager.decrypt_auto(
        ciphertext=ciphertext,
        wordlist=[],
        max_decoders=5
    )
    
    assert len(results) > 0
    # First result should be Base64 with high confidence
    best_result = results[0]
    assert 'Base64' in best_result['algorithm']
    assert best_result['plaintext'] == 'Hello World!'
    assert best_result['confidence'] > 80


def test_base32_decoding(decoder_manager):
    """Test Base32 decoding"""
    ciphertext = base64.b32encode(b'Hello World!').decode('ascii')
    results = decoder_manager.decrypt_auto(
        ciphertext=ciphertext,
        wordlist=[],
        max_decoders=5
    )
    assert len(results) > 0
    assert any('Base32' in r['algorithm'] and r['plaintext'] == 'Hello World!' for r in results)


def test_caesar_cipher(decoder_manager):
    """Test Caesar cipher decoding"""
    # "Hello" with shift 3 = "Khoor"
    ciphertext = 'Khoor'
    results = decoder_manager.decrypt_auto(
        ciphertext=ciphertext,
        wordlist=[],
        max_decoders=10
    )
    
    # Should find Caesar cipher
    caesar_results = [r for r in results if 'Caesar' in r['algorithm']]
    assert len(caesar_results) > 0


def test_vigenere_cipher_with_wordlist(decoder_manager):
    """Test Vigenere decoding with provided key"""
    ciphertext = 'LXFOPVEFRNHR'
    results = decoder_manager.decrypt_auto(
        ciphertext=ciphertext,
        wordlist=['lemon'],
        max_decoders=10
    )
    assert len(results) > 0
    assert any('Vigenere' in r['algorithm'] and 'ATTACKATDAWN' in r['plaintext'].upper() for r in results)


def test_sha512_hash_cracker(decoder_manager):
    """Test SHA512 hash cracking"""
    password = 'admin123'
    ciphertext = hashlib.sha512(password.encode()).hexdigest()
    results = decoder_manager.decrypt_auto(
        ciphertext=ciphertext,
        wordlist=['wrong', password, 'other'],
        max_decoders=10
    )
    assert len(results) > 0
    assert any('SHA512' in r['algorithm'] and r['plaintext'] == password for r in results)


def test_auto_detect_ranking_for_short_classical(decoder_manager):
    """Short alphabetic ciphertext should prioritize classical over Base64"""
    candidates = decoder_manager.auto_detect('Khoor', top_n=3)
    assert len(candidates) > 0
    top_decoder = candidates[0][0]
    assert 'Caesar' in top_decoder.get_algorithm_name()


def test_invalid_algorithm_name(decoder_manager):
    """Test using invalid algorithm name"""
    results = decoder_manager.decrypt_specific(
        ciphertext='test',
        algorithm_name='NonExistentAlgorithm',
        wordlist=[]
    )
    
    assert len(results) == 0


# === Decoder Engine Tests ===

def test_decoder_engine_initialization(decoder_engine):
    """Test decoder engine initializes"""
    assert decoder_engine is not None
    assert hasattr(decoder_engine, 'decoder_manager')


def test_decoder_engine_auto_with_wordlist(decoder_engine):
    """Test auto-detect with wordlist"""
    ciphertext = 'SGVsbG8gV29ybGQh'
    wordlist = ['hello', 'world', 'test']
    
    results = decoder_engine.auto_detect_and_decrypt(
        ciphertext=ciphertext,
        wordlist=wordlist,
        max_results=5
    )
    
    assert len(results) > 0
    assert results[0]['plaintext'] == 'Hello World!'


# === Integration Tests ===

def test_full_workflow_base64(client):
    """Test complete workflow: auto-detect Base64"""
    # Step 1: Check health
    health = client.get('/api/health')
    assert health.status_code == 200
    
    # Step 2: Get algorithms
    algos = client.get('/api/algorithms')
    assert algos.status_code == 200
    
    # Step 3: Auto-detect
    payload = {
        'ciphertext': 'VGVzdGluZyAxMjM=',
        'wordlist': [],
        'max_results': 3
    }
    response = client.post('/api/auto-detect', json=payload)
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert len(data['results']) > 0
    assert data['results'][0]['plaintext'] == 'Testing 123'


def test_full_workflow_multilayer_base64(client):
    """Test chain detection: Base64 -> Base64"""
    payload = {
        'ciphertext': 'U0dWc2JHOGdWMjl5YkdRaA==',  # base64("SGVsbG8gV29ybGQh")
        'wordlist': [],
        'max_results': 10
    }
    response = client.post('/api/auto-detect', json=payload)
    assert response.status_code == 200

    data = response.get_json()
    assert data['success'] is True
    assert len(data['results']) > 0
    assert any(
        ('->' in r['algorithm']) and ('Base64 Encoding' in r['algorithm']) and (r['plaintext'] == 'Hello World!')
        for r in data['results']
    )


def test_full_workflow_specific_algorithm(client):
    """Test decrypt with specific algorithm"""
    payload = {
        'ciphertext': 'SGVsbG8gV29ybGQh',
        'algorithm': 'Base64 Encoding',
        'wordlist': []
    }
    response = client.post('/api/decrypt', json=payload)
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert len(data['results']) > 0
    assert data['results'][0]['plaintext'] == 'Hello World!'


def test_decrypt_requires_algorithm(client):
    """Specific decrypt requires algorithm field"""
    payload = {
        'ciphertext': 'SGVsbG8gV29ybGQh',
        'wordlist': []
    }
    response = client.post('/api/decrypt', json=payload)
    assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
