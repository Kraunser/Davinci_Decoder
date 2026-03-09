
// === MEDIUM-LEVEL FEATURES ===

// === Real-time Progress (Simulated) ===
// Since we can't easily add WebSockets without modifying Flask,
// we'll simulate progress with incremental updates

let progressInterval = null;
let currentProgress = 0;

function startProgressSimulation(totalPasswords) {
    currentProgress = 0;
    const progressBar = document.createElement('div');
    progressBar.className = 'progress-bar-container';
    progressBar.innerHTML = `
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill"></div>
        </div>
        <div class="progress-text" id="progressText">0 / ${totalPasswords} senhas testadas</div>
    `;

    elements.loadingText.insertAdjacentElement('afterend', progressBar);

    // Simulate progress (approximate)
    const estimatedTime = totalPasswords * 0.05; // ~50ms per password
    const updateInterval = 200; // Update every 200ms
    const increment = (totalPasswords / (estimatedTime * 1000 / updateInterval));

    progressInterval = setInterval(() => {
        currentProgress += increment;
        if (currentProgress > totalPasswords) currentProgress = totalPasswords;

        updateProgress(Math.floor(currentProgress), totalPasswords);

        if (currentProgress >= totalPasswords) {
            clearInterval(progressInterval);
        }
    }, updateInterval);
}

function updateProgress(current, total) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    if (progressFill && progressText) {
        const percentage = (current / total) * 100;
        progressFill.style.width = `${percentage}%`;
        progressText.textContent = `${current} / ${total} senhas testadas (${percentage.toFixed(1)}%)`;
    }
}

function stopProgressSimulation() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }

    // Remove progress bar
    const progressBar = document.querySelector('.progress-bar-container');
    if (progressBar) {
        progressBar.remove();
    }
}

// === History Filters ===
let historyFilters = {
    searchText: '',
    algorithm: 'all',
    minConfidence: 0,
    dateRange: 'all' // all, today, week, month
};

function showHistoryModalWithFilters() {
    renderHistoryWithFilters();
    elements.historyModal.classList.add('active');
}

function renderHistoryWithFilters() {
    // Create filter UI
    const filterUI = `
        <div class="history-filters">
            <input type="text" 
                   id="historySearch" 
                   class="filter-input" 
                   placeholder="🔍 Buscar no histórico..."
                   value="${historyFilters.searchText}">
            
            <select id="historyAlgorithm" class="filter-select">
                <option value="all">Todos algoritmos</option>
                <option value="modern">Cifras Modernas</option>
                <option value="classical">Cifras Clássicas</option>
                <option value="encoding">Encodings</option>
            </select>
            
            <select id="historyDate" class="filter-select">
                <option value="all">Todo período</option>
                <option value="today">Hoje</option>
                <option value="week">Última semana</option>
                <option value="month">Último mês</option>
            </select>
            
            <div class="filter-slider">
                <label>Confiança mínima: <span id="confidenceValue">${historyFilters.minConfidence}%</span></label>
                <input type="range" 
                       id="historyConfidence" 
                       min="0" 
                       max="100" 
                       value="${historyFilters.minConfidence}"
                       class="confidence-slider">
            </div>
            
            <button class="btn btn-secondary" id="btnClearFilters" style="padding: 0.5rem 1rem; font-size: 0.875rem;">
                <span>🔄</span>
                Limpar Filtros
            </button>
        </div>
    `;

    elements.historyList.innerHTML = filterUI;

    // Add event listeners
    document.getElementById('historySearch').addEventListener('input', (e) => {
        historyFilters.searchText = e.target.value;
        filterAndRenderHistory();
    });

    document.getElementById('historyAlgorithm').addEventListener('change', (e) => {
        historyFilters.algorithm = e.target.value;
        filterAndRenderHistory();
    });

    document.getElementById('historyDate').addEventListener('change', (e) => {
        historyFilters.dateRange = e.target.value;
        filterAndRenderHistory();
    });

    document.getElementById('historyConfidence').addEventListener('input', (e) => {
        historyFilters.minConfidence = parseInt(e.target.value);
        document.getElementById('confidenceValue').textContent = e.target.value + '%';
        filterAndRenderHistory();
    });

    document.getElementById('btnClearFilters').addEventListener('click', () => {
        historyFilters = { searchText: '', algorithm: 'all', minConfidence: 0, dateRange: 'all' };
        renderHistoryWithFilters();
    });

    filterAndRenderHistory();
}

function filterAndRenderHistory() {
    let filtered = [...state.history];

    // Filter by search text
    if (historyFilters.searchText) {
        const search = historyFilters.searchText.toLowerCase();
        filtered = filtered.filter(item =>
            item.ciphertext.toLowerCase().includes(search) ||
            item.results.some(r =>
                r.algorithm.toLowerCase().includes(search) ||
                r.plaintext.toLowerCase().includes(search)
            )
        );
    }

    // Filter by algorithm type
    if (historyFilters.algorithm !== 'all') {
        const algorithmMap = {
            'modern': ['AES', '3DES', 'Blowfish', 'ChaCha20', 'RC4', 'Twofish', 'CAST'],
            'classical': ['Caesar', 'ROT', 'Vigenere', 'Atbash', 'XOR', 'Rail'],
            'encoding': ['Base64', 'Base32', 'Hex', 'Binary', 'Morse', 'URL']
        };

        const keywords = algorithmMap[historyFilters.algorithm] || [];
        filtered = filtered.filter(item =>
            item.results.some(r =>
                keywords.some(kw => r.algorithm.includes(kw))
            )
        );
    }

    // Filter by confidence
    if (historyFilters.minConfidence > 0) {
        filtered = filtered.filter(item =>
            item.results.some(r => r.confidence >= historyFilters.minConfidence)
        );
    }

    // Filter by date
    if (historyFilters.dateRange !== 'all') {
        const now = new Date();
        const cutoff = new Date();

        switch (historyFilters.dateRange) {
            case 'today':
                cutoff.setHours(0, 0, 0, 0);
                break;
            case 'week':
                cutoff.setDate(now.getDate() - 7);
                break;
            case 'month':
                cutoff.setMonth(now.getMonth() - 1);
                break;
        }

        filtered = filtered.filter(item => new Date(item.timestamp) >= cutoff);
    }

    // Render filtered results
    const resultsContainer = document.createElement('div');
    resultsContainer.className = 'history-results';

    if (filtered.length === 0) {
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <h3>Nenhum resultado encontrado</h3>
                <p>Tente ajustar os filtros</p>
            </div>
        `;
    } else {
        filtered.forEach(item => {
            const date = new Date(item.timestamp);
            const timeAgo = getTimeAgo(date);
            const maxConfidence = Math.max(...item.results.map(r => r.confidence));

            const historyCard = document.createElement('div');
            historyCard.className = 'history-card';
            historyCard.innerHTML = `
                <div class="history-header">
                    <span class="history-time">${timeAgo}</span>
                    <span class="confidence-badge" style="background: ${maxConfidence > 80 ? '#38ef7d' : '#f39c12'}">
                        ${maxConfidence.toFixed(0)}%
                    </span>
                    <button class="history-delete" data-id="${item.id}">🗑️</button>
                </div>
                <div class="history-ciphertext">${escapeHtml(item.ciphertext)}</div>
                <div class="history-results">
                    ${item.results.length} resultado(s) • ${item.results[0]?.algorithm || 'N/A'}
                </div>
                <button class="btn btn-secondary history-load" data-id="${item.id}" style="margin-top: 0.5rem; padding: 0.5rem 1rem; font-size: 0.875rem;">
                    <span class="btn-icon">📂</span>
                    Carregar
                </button>
            `;

            resultsContainer.appendChild(historyCard);
        });
    }

    elements.historyList.appendChild(resultsContainer);

    // Re-attach event listeners
    document.querySelectorAll('.history-delete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.target.dataset.id);
            deleteHistoryItem(id);
            renderHistoryWithFilters();
        });
    });

    document.querySelectorAll('.history-load').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.target.dataset.id);
            loadHistoryItem(id);
        });
    });
}

// === Import from JSON ===
function importFromJSON() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';

    input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const data = JSON.parse(event.target.result);

                // Validate format
                if (!data.results || !Array.isArray(data.results)) {
                    alert('Formato JSON inválido. Esperado: {results: [...]}');
                    return;
                }

                // Load results
                displayResults(data.results);

                // Optionally load ciphertext
                if (data.ciphertext) {
                    elements.ciphertext.value = data.ciphertext;
                    state.currentCiphertext = data.ciphertext;
                    updateStats();
                }

                alert(`✅ ${data.results.length} resultado(s) importado(s) com sucesso!`);

            } catch (error) {
                alert('Erro ao ler arquivo JSON: ' + error.message);
            }
        };

        reader.readAsText(file);
    };

    input.click();
}

// === Copy to Clipboard ===
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('✅ Copiado para a área de transferência!');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
        document.execCommand('copy');
        showToast('✅ Copiado para a área de transferência!');
    } catch (err) {
        alert('Erro ao copiar: ' + err);
    }
    document.body.removeChild(textarea);
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// === Statistics ===
function getUsageStatistics() {
    const stats = {
        totalDecryptions: state.history.length,
        algorithmCounts: {},
        avgConfidence: 0,
        successRate: 0
    };

    state.history.forEach(item => {
        item.results.forEach(result => {
            const algo = result.algorithm;
            stats.algorithmCounts[algo] = (stats.algorithmCounts[algo] || 0) + 1;
            stats.avgConfidence += result.confidence;
        });
    });

    const totalResults = state.history.reduce((sum, item) => sum + item.results.length, 0);
    if (totalResults > 0) {
        stats.avgConfidence /= totalResults;
        stats.successRate = (state.history.filter(h => h.results.length > 0).length / state.history.length) * 100;
    }

    return stats;
}

function showStatistics() {
    const stats = getUsageStatistics();
    const topAlgorithms = Object.entries(stats.algorithmCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

    const statsContent = document.getElementById('statsContent');
    const statsModal = document.getElementById('statsModal');

    statsContent.innerHTML = `
        <div class="stat-row">
            <span>Total de decifrações:</span>
            <strong>${stats.totalDecryptions}</strong>
        </div>
        
        <div class="stat-row">
            <span>Confiança média:</span>
            <strong>${stats.avgConfidence.toFixed(1)}%</strong>
        </div>
        
        <div class="stat-row">
            <span>Taxa de sucesso:</span>
            <strong>${stats.successRate.toFixed(1)}%</strong>
        </div>
        
        ${topAlgorithms.length > 0 ? `
            <h4 style="margin-top: 1rem; margin-bottom: 0.5rem;">🏆 Top 5 Algoritmos</h4>
            <div class="algorithm-stats">
                ${topAlgorithms.map(([algo, count]) => `
                    <div class="algo-stat">
                        <span>${algo}</span>
                        <span class="algo-count">${count}x</span>
                    </div>
                `).join('')}
            </div>
        ` : '<p style="text-align: center; color: var(--text-muted); margin-top: 1rem;">Nenhum dado disponível</p>'}
    `;

    statsModal.classList.add('active');

    // Add close handlers
    document.getElementById('statsClose').onclick = () => statsModal.classList.remove('active');
    document.getElementById('statsOverlay').onclick = () => statsModal.classList.remove('active');
}

// Override showHistoryModal to use filtered version
window.showHistoryModal = showHistoryModalWithFilters;

// Add import button functionality
window.importResults = importFromJSON;

console.log('📊 Melhorias médias carregadas!');
console.log('🔍 Filtros de histórico ativos');
console.log('📥 Use window.importResults() para importar JSON');
