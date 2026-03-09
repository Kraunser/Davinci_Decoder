/**
 * DaVinci Decoder - Frontend Application
 * Connects to Python Backend with 102 Algorithms
 */

// === Configuration ===
let API_URL = localStorage.getItem('apiUrl') || 'http://localhost:5000/api';

// === State Management ===
const state = {
    algorithms: [],
    currentCiphertext: '',
    currentWordlist: [],
    isProcessing: false,
    currentResults: [],
    history: JSON.parse(localStorage.getItem('decryptionHistory') || '[]')
};

// === DOM Elements ===
const elements = {
    ciphertext: document.getElementById('ciphertext'),
    wordlist: document.getElementById('wordlist'),
    btnAutoDetect: document.getElementById('btnAutoDetect'),
    btnManual: document.getElementById('btnManual'),
    resultContainer: document.getElementById('resultContainer'),
    resultStatus: document.getElementById('resultStatus'),
    charCount: document.getElementById('charCount'),
    entropy: document.getElementById('entropy'),
    charset: document.getElementById('charset'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    loadingText: document.getElementById('loadingText'),
    algorithmModal: document.getElementById('algorithmModal'),
    modalOverlay: document.getElementById('modalOverlay'),
    modalClose: document.getElementById('modalClose'),
    algorithmList: document.getElementById('algorithmList'),
    algorithmSearch: document.getElementById('algorithmSearch'),

    // New elements
    btnHistory: document.getElementById('btnHistory'),
    btnExport: document.getElementById('btnExport'),
    btnThemeToggle: document.getElementById('btnThemeToggle'),
    btnConfig: document.getElementById('btnConfig'),
    historyModal: document.getElementById('historyModal'),
    historyOverlay: document.getElementById('historyOverlay'),
    historyClose: document.getElementById('historyClose'),
    historyList: document.getElementById('historyList'),
    configModal: document.getElementById('configModal'),
    configOverlay: document.getElementById('configOverlay'),
    configClose: document.getElementById('configClose'),
    configApiUrl: document.getElementById('configApiUrl'),
    btnSaveConfig: document.getElementById('btnSaveConfig'),
    themeIcon: document.getElementById('themeIcon'),
    themeText: document.getElementById('themeText'),
    btnImport: document.getElementById('btnImport'),
    btnStats: document.getElementById('btnStats')
};

// === Initialization ===
document.addEventListener('DOMContentLoaded', async () => {
    initEventListeners();
    await loadAlgorithms();
    updateStats();
    loadTheme();
    loadConfig();
});

// === Event Listeners ===
function initEventListeners() {
    // Input tracking
    elements.ciphertext.addEventListener('input', handleCiphertextChange);

    // Button actions
    elements.btnAutoDetect.addEventListener('click', handleAutoDetect);
    elements.btnManual.addEventListener('click', showAlgorithmModal);

    // Modal
    elements.modalClose.addEventListener('click', hideAlgorithmModal);
    elements.modalOverlay.addEventListener('click', hideAlgorithmModal);
    elements.algorithmSearch.addEventListener('input', handleAlgorithmSearch);

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboard);

    // New buttons
    elements.btnHistory.addEventListener('click', showHistoryModal);
    elements.btnExport.addEventListener('click', exportResults);
    elements.btnThemeToggle.addEventListener('click', toggleTheme);
    elements.btnConfig.addEventListener('click', showConfigModal);

    // History modal
    elements.historyClose.addEventListener('click', hideHistoryModal);
    elements.historyOverlay.addEventListener('click', hideHistoryModal);

    // Config modal
    elements.configClose.addEventListener('click', hideConfigModal);
    elements.configOverlay.addEventListener('click', hideConfigModal);
    elements.btnSaveConfig.addEventListener('click', saveConfig);

    // Medium features
    elements.btnImport.addEventListener('click', importFromJSON);
    elements.btnStats.addEventListener('click', showStatistics);
}

// === Ciphertext Handler ===
function handleCiphertextChange() {
    state.currentCiphertext = elements.ciphertext.value;
    updateStats();
}

// === Stats Calculator ===
function updateStats() {
    const text = state.currentCiphertext;

    // Character count
    elements.charCount.textContent = text.length;

    // Entropy calculation (Shannon)
    const entropy = calculateEntropy(text);
    elements.entropy.textContent = entropy.toFixed(2);

    // Charset detection
    const charset = detectCharset(text);
    elements.charset.textContent = charset;
}

function calculateEntropy(text) {
    if (!text) return 0;

    const freq = {};
    for (const char of text) {
        freq[char] = (freq[char] || 0) + 1;
    }

    let entropy = 0;
    const len = text.length;

    for (const count of Object.values(freq)) {
        const p = count / len;
        entropy -= p * Math.log2(p);
    }

    return entropy;
}

function detectCharset(text) {
    if (!text) return '-';

    const hasBase64 = /^[A-Za-z0-9+/=]+$/.test(text);
    const hasHex = /^[0-9A-Fa-f]+$/.test(text);
    const hasBinary = /^[01]+$/.test(text);
    const hasAlpha = /[A-Za-z]/.test(text);

    if (hasBase64 && text.length % 4 === 0) return 'Base64';
    if (hasHex) return 'Hexadecimal';
    if (hasBinary) return 'Binário';
    if (hasAlpha) return 'Alfabético';
    return 'Misto';
}

// === Auto-Detect Handler ===
async function handleAutoDetect() {
    const ciphertext = state.currentCiphertext.trim();

    if (!ciphertext) {
        showError('Por favor, insira um ciphertext');
        return;
    }

    const wordlist = elements.wordlist.value
        .split('\n')
        .map(w => w.trim())
        .filter(w => w.length > 0);

    state.currentWordlist = wordlist;

    showLoading('Analisando e detectando algoritmo...');

    try {
        // Timeout de 2 minutos
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000);

        const response = await fetch(`${API_URL}/auto-detect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ciphertext,
                wordlist,
                max_results: 5
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Falha na requisição');
        }

        const payload = await response.json();
        if (payload && payload.success === false) {
            throw new Error(payload.error || 'Falha na requisição');
        }
        hideLoading();
        displayResults(normalizeApiResults(payload));

    } catch (error) {
        hideLoading();
        if (error.name === 'AbortError') {
            showError('Timeout: Operação demorou muito (>2 minutos). Tente com menos senhas ou um ciphertext menor.');
        } else {
            showError(`Erro ao processar: ${error.message}`);
        }
    }
}

// === Algorithm Loader ===
async function loadAlgorithms() {
    try {
        const response = await fetch(`${API_URL}/algorithms`);
        if (!response.ok) throw new Error('Failed to load algorithms');

        const data = await response.json();
        state.algorithms = data.algorithms || [];

        renderAlgorithmList(state.algorithms);
    } catch (error) {
        console.error('Error loading algorithms:', error);
        // Fallback to mock data if backend not available
        state.algorithms = getMockAlgorithms();
        renderAlgorithmList(state.algorithms);
    }
}

// === Algorithm List Renderer ===
function renderAlgorithmList(algorithms) {
    elements.algorithmList.innerHTML = '';

    const categories = {
        'modern': { title: '🔐 Cifras Modernas', items: [] },
        'classical': { title: '📜 Cifras Clássicas', items: [] },
        'encoding': { title: '🔤 Encodings', items: [] },
        'hash': { title: '#️⃣ Hash Crackers', items: [] }
    };

    algorithms.forEach(algo => {
        if (categories[algo.type]) {
            categories[algo.type].items.push(algo);
        }
    });

    for (const [type, category] of Object.entries(categories)) {
        if (category.items.length === 0) continue;

        const categoryTitle = document.createElement('h3');
        categoryTitle.textContent = category.title;
        categoryTitle.style.cssText = 'margin: 1rem 0 0.5rem; color: var(--text-secondary); font-size: 0.875rem;';
        elements.algorithmList.appendChild(categoryTitle);

        category.items.forEach(algo => {
            const item = document.createElement('div');
            item.className = 'algorithm-item';
            item.textContent = algo.name;
            item.addEventListener('click', () => selectAlgorithm(algo.name));
            elements.algorithmList.appendChild(item);
        });
    }
}

// === Algorithm Selector ===
function selectAlgorithm(algorithmName) {
    hideAlgorithmModal();
    decryptWithAlgorithm(algorithmName);
}

async function decryptWithAlgorithm(algorithmName) {
    const ciphertext = state.currentCiphertext.trim();

    if (!ciphertext) {
        showError('Por favor, insira um ciphertext');
        return;
    }

    const wordlist = elements.wordlist.value
        .split('\n')
        .map(w => w.trim())
        .filter(w => w.length > 0);

    showLoading(`Decifrando com ${algorithmName}...`);

    try {
        // Timeout de 2 minutos
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000);

        const response = await fetch(`${API_URL}/decrypt`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ciphertext,
                algorithm: algorithmName,
                wordlist
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Falha na requisição');
        }

        const payload = await response.json();
        if (payload && payload.success === false) {
            throw new Error(payload.error || 'Falha na requisição');
        }
        hideLoading();
        displayResults(normalizeApiResults(payload));

    } catch (error) {
        hideLoading();
        if (error.name === 'AbortError') {
            showError('Timeout: Operação demorou muito (>2 minutos).');
        } else {
            showError(`Erro ao processar: ${error.message}`);
        }
    }
}

// === Results Display ===
function displayResults(results) {
    results = normalizeApiResults(results);
    elements.resultContainer.innerHTML = '';

    // Save results to state
    state.currentResults = results;

    // Enable export button if we have results
    if (results && results.length > 0) {
        elements.btnExport.disabled = false;

        // Add to history
        if (state.currentCiphertext) {
            addToHistory(state.currentCiphertext, results);
        }
    } else {
        elements.btnExport.disabled = true;
    }

    if (!results || results.length === 0) {
        elements.resultContainer.className = 'result-empty';
        elements.resultContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">❌</div>
                <h3>Nenhum resultado encontrado</h3>
                <p>Não foi possível decifrar o texto com os algoritmos testados</p>
            </div>
        `;
        elements.resultStatus.textContent = 'Sem resultados';
        return;
    }

    elements.resultContainer.className = '';
    elements.resultStatus.textContent = `${results.length} resultado(s) encontrado(s)`;

    results.forEach((result, index) => {
        const card = createResultCard(result, index);
        elements.resultContainer.appendChild(card);
    });
}

function normalizeApiResults(payload) {
    if (Array.isArray(payload)) return payload;
    if (payload && Array.isArray(payload.results)) return payload.results;
    return [];
}

function createResultCard(result, index) {
    const card = document.createElement('div');
    card.className = 'result-card';
    if (index === 0) card.classList.add('success');

    const confidence = result.confidence || 0;
    const confidenceColor = confidence > 80 ? '#38ef7d' : confidence > 60 ? '#f39c12' : '#e74c3c';

    card.innerHTML = `
        <div class="result-header">
            <div class="result-algorithm">
                ${index === 0 ? '🏆 ' : ''}${result.algorithm}
            </div>
            <div class="confidence-badge" style="background: ${confidenceColor}">
                ${confidence.toFixed(0)}% confiança
            </div>
        </div>
        ${result.password ? `
            <div style="margin-bottom: 1rem; font-size: 0.875rem; color: var(--text-secondary);">
                🔑 Senha: <span style="color: var(--text-primary); font-family: var(--font-mono);">${result.password}</span>
            </div>
        ` : ''}
        <div class="result-plaintext">
            ${escapeHtml(result.plaintext)}
            <button class="copy-btn" onclick="copyToClipboard('${escapeHtml(result.plaintext).replace(/'/g, "\\'")}')"
                    title="Copiar para área de transferência">
                <span>📋</span> Copiar
            </button>
        </div>
    `;

    return card;
}

// === Modal Handlers ===
function showAlgorithmModal() {
    elements.algorithmModal.classList.add('active');
    elements.algorithmSearch.value = '';
    elements.algorithmSearch.focus();
}

function hideAlgorithmModal() {
    elements.algorithmModal.classList.remove('active');
}

function handleAlgorithmSearch(e) {
    const query = e.target.value.toLowerCase();
    const filtered = state.algorithms.filter(algo =>
        algo.name.toLowerCase().includes(query)
    );
    renderAlgorithmList(filtered);
}

// === Loading Overlay ===
function showLoading(text = 'Processando...') {
    elements.loadingText.textContent = text;
    elements.loadingOverlay.classList.add('active');
    state.isProcessing = true;
}

function hideLoading() {
    elements.loadingOverlay.classList.remove('active');
    state.isProcessing = false;
}

// === Error Display ===
function showError(message) {
    elements.resultContainer.innerHTML = `
        <div class="result-empty">
            <div class="empty-state">
                <div class="empty-icon">⚠️</div>
                <h3>Erro</h3>
                <p>${escapeHtml(message)}</p>
            </div>
        </div>
    `;
    elements.resultStatus.textContent = 'Erro ao processar';
}

// === Keyboard Shortcuts ===
function handleKeyboard(e) {
    // Ctrl+Enter to auto-detect
    if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        handleAutoDetect();
    }

    // Escape to close modal
    if (e.key === 'Escape') {
        hideAlgorithmModal();
    }
}

// === Utilities ===
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// === Mock Data (Fallback) ===
function getMockAlgorithms() {
    return [
        { name: 'Base64 Encoding', type: 'encoding' },
        { name: 'Hexadecimal', type: 'encoding' },
        { name: 'Caesar Cipher', type: 'classical' },
        { name: 'ROT13', type: 'classical' },
        { name: 'Vigenère Cipher', type: 'classical' },
        { name: 'AES-256-CBC', type: 'modern' },
        { name: 'AES-128-ECB', type: 'modern' },
        { name: 'MD5 Hash', type: 'hash' },
        { name: 'SHA256 Hash', type: 'hash' }
    ];
}

// === Demo Mode (if backend unavailable) ===
window.runDemo = function () {
    // Base64 demo
    elements.ciphertext.value = 'SGVsbG8gV29ybGQh';
    updateStats();

    setTimeout(() => {
        const demoResults = [{
            algorithm: 'Base64 Encoding',
            plaintext: 'Hello World!',
            confidence: 95,
            password: null
        }];
        displayResults(demoResults);
    }, 500);
};

console.log('🎉 DaVinci Decoder UI carregado!');
console.log('📊 Execute window.runDemo() para testar sem backend');
