
// === NEW FEATURES ===

// === Theme Management ===
function loadTheme() {
    const theme = localStorage.getItem('theme') || 'dark';
    document.body.setAttribute('data-theme', theme);
    updateThemeButton(theme);
}

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeButton(newTheme);
}

function updateThemeButton(theme) {
    if (theme === 'light') {
        elements.themeIcon.textContent = '☀️';
        elements.themeText.textContent = 'Light';
    } else {
        elements.themeIcon.textContent = '🌙';
        elements.themeText.textContent = 'Dark';
    }
}

// === History Management ===
function addToHistory(ciphertext, results) {
    const historyItem = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        ciphertext: ciphertext.substring(0, 100) + (ciphertext.length > 100 ? '...' : ''),
        results: results.map(r => ({
            algorithm: r.algorithm,
            plaintext: r.plaintext.substring(0, 200),
            confidence: r.confidence,
            password: r.password
        }))
    };

    state.history.unshift(historyItem);

    // Keep only last 50 items
    if (state.history.length > 50) {
        state.history = state.history.slice(0, 50);
    }

    localStorage.setItem('decryptionHistory', JSON.stringify(state.history));
}

function showHistoryModal() {
    renderHistory();
    elements.historyModal.classList.add('active');
}

function hideHistoryModal() {
    elements.historyModal.classList.remove('active');
}

function renderHistory() {
    elements.historyList.innerHTML = '';

    if (state.history.length === 0) {
        elements.historyList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📂</div>
                <h3>Nenhum histórico ainda</h3>
                <p>Suas decifrações aparecerão aqui</p>
            </div>
        `;
        return;
    }

    state.history.forEach(item => {
        const date = new Date(item.timestamp);
        const timeAgo = getTimeAgo(date);

        const historyCard = document.createElement('div');
        historyCard.className = 'history-card';
        historyCard.innerHTML = `
            <div class="history-header">
                <span class="history-time">${timeAgo}</span>
                <button class="history-delete" data-id="${item.id}">🗑️</button>
            </div>
            <div class="history-ciphertext">${escapeHtml(item.ciphertext)}</div>
            <div class="history-results">
                ${item.results.length} resultado(s) encontrado(s)
            </div>
            <button class="btn btn-secondary history-load" data-id="${item.id}" style="margin-top: 0.5rem; padding: 0.5rem 1rem; font-size: 0.875rem;">
                <span class="btn-icon">📂</span>
                Carregar
            </button>
        `;

        elements.historyList.appendChild(historyCard);
    });

    // Add event listeners
    document.querySelectorAll('.history-delete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.target.dataset.id);
            deleteHistoryItem(id);
        });
    });

    document.querySelectorAll('.history-load').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.target.dataset.id);
            loadHistoryItem(id);
        });
    });
}

function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);

    if (seconds < 60) return 'Agora mesmo';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} min atrás`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hora(s) atrás`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)} dia(s) atrás`;
    return date.toLocaleDateString('pt-BR');
}

function deleteHistoryItem(id) {
    state.history = state.history.filter(item => item.id !== id);
    localStorage.setItem('decryptionHistory', JSON.stringify(state.history));
    renderHistory();
}

function loadHistoryItem(id) {
    const item = state.history.find(h => h.id === id);
    if (!item) return;

    hideHistoryModal();
    displayResults(item.results);
    elements.resultStatus.textContent = `${item.results.length} resultado(s) do histórico`;
}

// === Export Functionality ===
function exportResults() {
    if (!state.currentResults || state.currentResults.length === 0) {
        alert('Nenhum resultado para exportar');
        return;
    }

    // Show export format selection
    const format = prompt('Escolha o formato de exportação:\n1. JSON\n2. TXT\n3. CSV\n\nDigite o número:', '1');

    if (!format) return;

    switch (format.trim()) {
        case '1':
            exportAsJSON();
            break;
        case '2':
            exportAsTXT();
            break;
        case '3':
            exportAsCSV();
            break;
        default:
            alert('Formato inválido');
    }
}

function exportAsJSON() {
    const data = {
        timestamp: new Date().toISOString(),
        ciphertext: state.currentCiphertext,
        results: state.currentResults
    };

    downloadFile(
        JSON.stringify(data, null, 2),
        `davinci-decrypt-${Date.now()}.json`,
        'application/json'
    );
}

function exportAsTXT() {
    let content = '🎨 DaVinci Decoder - Resultados\\n';
    content += '='.repeat(70) + '\\n\\n';
    content += `Data: ${new Date().toLocaleString('pt-BR')}\\n`;
    content += `Ciphertext: ${state.currentCiphertext.substring(0, 100)}...\\n\\n`;

    state.currentResults.forEach((result, index) => {
        content += `Resultado #${index + 1}\\n`;
        content += '-'.repeat(70) + '\\n';
        content += `Algoritmo: ${result.algorithm}\\n`;
        content += `Confiança: ${result.confidence}%\\n`;
        if (result.password) content += `Senha: ${result.password}\\n`;
        content += `Plaintext:\\n${result.plaintext}\\n\\n`;
    });

    downloadFile(
        content,
        `davinci-decrypt-${Date.now()}.txt`,
        'text/plain'
    );
}

function exportAsCSV() {
    let csv = 'Algoritmo,Confiança,Senha,Plaintext\\n';

    state.currentResults.forEach(result => {
        csv += `"${result.algorithm}",`;
        csv += `${result.confidence},`;
        csv += `"${result.password || ''}",`;
        csv += `"${result.plaintext.replace(/"/g, '""')}"\\n`;
    });

    downloadFile(
        csv,
        `davinci-decrypt-${Date.now()}.csv`,
        'text/csv'
    );
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// === Config Management ===
function loadConfig() {
    const savedUrl = localStorage.getItem('apiUrl');
    if (savedUrl) {
        API_URL = savedUrl;
        elements.configApiUrl.value = savedUrl;
    }
}

function showConfigModal() {
    elements.configModal.classList.add('active');
}

function hideConfigModal() {
    elements.configModal.classList.remove('active');
}

function saveConfig() {
    const newUrl = elements.configApiUrl.value.trim();

    if (!newUrl) {
        alert('URL da API não pode estar vazia');
        return;
    }

    API_URL = newUrl;
    localStorage.setItem('apiUrl', newUrl);

    alert('Configurações salvas com sucesso!');
    hideConfigModal();
}

// Add to window for console access
window.clearHistory = () => {
    if (confirm('Tem certeza que deseja limpar todo o histórico?')) {
        state.history = [];
        localStorage.removeItem('decryptionHistory');
        renderHistory();
    }
};

console.log('✨ Melhorias UX carregadas!');
console.log('📚 Use window.clearHistory() para limpar histórico');
