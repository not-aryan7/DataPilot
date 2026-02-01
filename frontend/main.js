// DataPilot Frontend - Main Application Logic

const API_BASE = 'http://127.0.0.1:8000/api';

// Generate stars background (dense field like NexusData)
function generateStars() {
  const starsContainer = document.getElementById('stars');
  if (!starsContainer) return;

  const starCount = 400;

  for (let i = 0; i < starCount; i++) {
    const star = document.createElement('div');
    star.className = 'star';

    // Varied size classes for depth perception
    const sizeRandom = Math.random();
    if (sizeRandom < 0.5) star.classList.add('tiny');
    else if (sizeRandom < 0.8) star.classList.add('small');
    else if (sizeRandom < 0.95) star.classList.add('medium');
    else star.classList.add('large');

    // Random position
    star.style.left = Math.random() * 100 + '%';
    star.style.top = Math.random() * 100 + '%';

    // Random animation timing
    star.style.setProperty('--duration', (2 + Math.random() * 3) + 's');
    star.style.setProperty('--delay', Math.random() * 5 + 's');
    star.style.opacity = Math.random() * 0.7 + 0.1;

    starsContainer.appendChild(star);
  }
}

// State
let currentDataset = null;
let datasets = [];
let recentQueries = [];

// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadZone = document.getElementById('uploadZone');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const chatArea = document.getElementById('chatArea');
const welcomeState = document.getElementById('welcomeState');
const datasetList = document.getElementById('datasetList');
const queryList = document.getElementById('queryList');
const currentDatasetEl = document.getElementById('currentDataset');
const latencyEl = document.getElementById('latency');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  generateStars();
  setupEventListeners();
  fetchDatasets();
  lucide.createIcons();
});

// Helper to get helper SVG string
function getIcon(name, size = 16, className = '') {
  // Use lucide API if available
  if (window.lucide && window.lucide.icons[name]) {
    // Convert kebab-case (e.g. file-spreadsheet) to PascalCase (FileSpreadsheet) for lookup if needed,
    // but icons[name] usually expects PascalCase? 
    // Actually looking at lucide docs, icons is an object with PascalCase keys.
    // Let's make a quick mapper or try to convert.
    const pascalName = name.split('-').map(p => p.charAt(0).toUpperCase() + p.slice(1)).join('');
    const iconNode = window.lucide.icons[pascalName];
    if (iconNode) {
      return iconNode.toSvg({ width: size, height: size, class: className });
    }
  }
  return '';
}

function setupEventListeners() {
  // File upload
  fileInput.addEventListener('change', handleFileUpload);
  uploadZone.addEventListener('dragover', handleDragOver);
  uploadZone.addEventListener('dragleave', handleDragLeave);
  uploadZone.addEventListener('drop', handleDrop);

  // Question input
  questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  });
  sendBtn.addEventListener('click', handleAsk);

  // New analysis button
  newAnalysisBtn.addEventListener('click', resetToWelcome);
}

// File Upload Handlers
function handleDragOver(e) {
  e.preventDefault();
  uploadZone.classList.add('dragover');
}

function handleDragLeave(e) {
  e.preventDefault();
  uploadZone.classList.remove('dragover');
}

function handleDrop(e) {
  e.preventDefault();
  uploadZone.classList.remove('dragover');
  const files = e.dataTransfer.files;
  if (files.length > 0 && files[0].name.endsWith('.csv')) {
    uploadFile(files[0]);
  }
}

function handleFileUpload(e) {
  const file = e.target.files[0];
  if (file) {
    uploadFile(file);
  }
}

async function uploadFile(file) {
  showLoading('Uploading ' + file.name + '...');

  const formData = new FormData();
  formData.append('file', file);

  try {
    const startTime = performance.now();
    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData
    });
    const endTime = performance.now();
    updateLatency(endTime - startTime);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    const data = await response.json();

    // Update state
    currentDataset = {
      id: data.dataset_id,
      name: file.name,
      table_name: data.table_name,
      schema: data.schema,
      row_count: data.row_count
    };

    // Add to datasets list
    datasets.push(currentDataset);
    saveToLocalStorage();
    updateDatasetList();

    // Update UI
    currentDatasetEl.textContent = file.name;
    enableInput();
    hideWelcome();

    // Show success message
    showUploadSuccess(currentDataset);

  } catch (error) {
    showError('Upload failed: ' + error.message);
  }
}

// Ask Question Handler
async function handleAsk() {
  const question = questionInput.value.trim();
  if (!question) return;

  if (!currentDataset) {
    showError("Please select or upload a dataset first!");
    return;
  }

  // Clear input
  questionInput.value = '';

  // Show user message
  addUserMessage(question);

  // Show loading
  const loadingId = addLoadingMessage();

  try {
    const startTime = performance.now();
    const response = await fetch(`${API_BASE}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dataset_id: currentDataset.id,
        question: question
      })
    });
    const endTime = performance.now();
    updateLatency(endTime - startTime);

    // Remove loading
    removeMessage(loadingId);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Query failed');
    }

    const data = await response.json();

    // Add to recent queries
    addRecentQuery(question);

    // Show response
    addAssistantMessage(data);

  } catch (error) {
    removeMessage(loadingId);
    showError('Query failed: ' + error.message);
  }
}

// UI Updates
function updateDatasetList() {
  if (datasets.length === 0) {
    datasetList.innerHTML = `
      <li class="dataset-item placeholder">
        <i data-lucide="file-spreadsheet" class="file-icon"></i>
        Upload a CSV to start
      </li>
    `;
    lucide.createIcons();
    return;
  }

  datasetList.innerHTML = datasets.map((ds, index) => `
    <li class="dataset-item ${ds.id === currentDataset?.id ? 'active' : ''}">
      <span class="item-content" onclick="selectDataset(${index})">
        <i data-lucide="file-spreadsheet" class="file-icon"></i>
        <span class="item-name">${ds.name}</span>
      </span>
      <button class="delete-btn" onclick="event.stopPropagation(); deleteDataset(${index})" title="Delete dataset">
        <i data-lucide="trash-2"></i>
      </button>
    </li>
  `).join('');
  lucide.createIcons();
}

window.selectDataset = function (index) {
  currentDataset = datasets[index];
  currentDatasetEl.textContent = currentDataset.name;
  updateDatasetList();
  enableInput();
  hideWelcome();
};

function enableInput() {
  questionInput.disabled = false;
  sendBtn.disabled = false;
  questionInput.placeholder = 'Ask DataPilot about your dataset...';
}

function addRecentQuery(question) {
  const truncated = question.length > 30 ? question.substring(0, 30) + '...' : question;
  recentQueries.unshift(truncated);
  if (recentQueries.length > 5) recentQueries.pop();
  saveToLocalStorage();
  updateQueryList();
}

function updateQueryList() {
  if (recentQueries.length === 0) {
    queryList.innerHTML = `<li class="query-item placeholder"><i data-lucide="clock" class="file-icon"></i>No queries yet</li>`;
    lucide.createIcons();
    return;
  }

  queryList.innerHTML = recentQueries.map((q, index) => `
    <li class="query-item">
      <span class="item-content" onclick="useSuggestion('${q.replace(/'/g, "\\'")}')"> 
        <i data-lucide="message-square" class="file-icon"></i>
        <span class="item-name">${q}</span>
      </span>
      <button class="delete-btn" onclick="event.stopPropagation(); deleteQuery(${index})" title="Delete query">
        <i data-lucide="x"></i>
      </button>
    </li>
  `).join('');
  lucide.createIcons();
}

function hideWelcome() {
  welcomeState.style.display = 'none';
}

function resetToWelcome() {
  currentDataset = null;
  currentDatasetEl.textContent = 'No dataset selected';
  // Input remains enabled to allow typing
  chatArea.innerHTML = `
    <div class="welcome-state" id="welcomeState">
      <div class="welcome-icon-container">
         <i data-lucide="bar-chart-2" size="48" color="#10b981"></i>
      </div>
      <h2>Welcome to DataPilot</h2>
      <p>Upload a CSV file to start analyzing your data with natural language queries</p>
      <label class="upload-zone" id="uploadZone">
        <input type="file" id="fileInput" accept=".csv" hidden>
        <div class="upload-content">
          <i data-lucide="upload-cloud" size="32" class="upload-icon-lucide"></i>
          <span>Drop CSV here or click to upload</span>
        </div>
      </label>
    </div>
  `;
  // Re-init generic icons
  lucide.createIcons();

  // Re-attach listeners
  const newFileInput = document.getElementById('fileInput');

  const newUploadZone = document.getElementById('uploadZone');
  newFileInput.addEventListener('change', handleFileUpload);
  newUploadZone.addEventListener('dragover', handleDragOver);
  newUploadZone.addEventListener('dragleave', handleDragLeave);
  newUploadZone.addEventListener('drop', handleDrop);
}

// Message Rendering
function addUserMessage(question) {
  const userIcon = getIcon('user', 20);
  const html = `
    <div class="message message-user">
      <div class="message-avatar">${userIcon}</div>
      <div class="message-content"><p>${escapeHtml(question)}</p></div>
    </div>
  `;
  chatArea.insertAdjacentHTML('beforeend', html);
  scrollToBottom();
}

function addLoadingMessage() {
  const id = 'loading-' + Date.now();
  const botIcon = getIcon('bot', 20);
  const html = `
    <div class="message message-assistant" id="${id}">
      <div class="message-avatar">${botIcon}</div>
      <div class="message-content">
        <div class="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  `;
  chatArea.insertAdjacentHTML('beforeend', html);
  scrollToBottom();
  return id;
}

function removeMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function addAssistantMessage(data) {
  const tableHtml = renderResultsTable(data.data);
  const sqlHtml = highlightSQL(data.sql_query);
  const botIcon = getIcon('bot', 20);

  const html = `
    <div class="message message-assistant">
      <div class="message-avatar">${botIcon}</div>
      <div class="message-content">
        <p class="assistant-intro">
          I've analyzed the <span class="dataset-link">${currentDataset.name}</span> dataset. 
          ${data.answer}
        </p>
        
        <div class="sql-block">
          <div class="sql-header">
            <span class="sql-label">DUCKDB SQL</span>
            <button class="copy-btn" onclick="copySQL(\`${escapeHtml(data.sql_query)}\`)">
              📋 Copy
            </button>
          </div>
          <pre class="sql-code">${sqlHtml}</pre>
        </div>
        
        ${tableHtml}
      </div>
    </div>
  `;
  chatArea.insertAdjacentHTML('beforeend', html);
  scrollToBottom();
}

function renderResultsTable(data) {
  if (!data || data.length === 0) {
    return '<p class="no-results">No results found.</p>';
  }

  const columns = Object.keys(data[0]);
  const headerHtml = columns.map(col => `<th>${col.toUpperCase()}</th>`).join('');

  const rowsHtml = data.slice(0, 10).map(row => {
    const cells = columns.map(col => {
      let value = row[col];
      let className = '';

      // Format numbers
      if (typeof value === 'number') {
        if (col.toLowerCase().includes('growth') || col.toLowerCase().includes('change')) {
          className = value >= 0 ? 'growth-positive' : 'growth-negative';
          value = (value >= 0 ? '+' : '') + value.toFixed(1) + '%';
        } else if (col.toLowerCase().includes('revenue') || col.toLowerCase().includes('price') || col.toLowerCase().includes('amount')) {
          value = '$' + value.toLocaleString();
        }
      }

      return `<td class="${className}">${value}</td>`;
    }).join('');
    return `<tr>${cells}</tr>`;
  }).join('');

  let footer = '';
  if (data.length > 10) {
    footer = `<p class="table-footer">Showing 10 of ${data.length} rows</p>`;
  }

  return `
    <div class="results-table-container">
      <table class="results-table">
        <thead><tr>${headerHtml}</tr></thead>
        <tbody>${rowsHtml}</tbody>
      </table>
    </div>
    ${footer}
  `;
}

function highlightSQL(sql) {
  const keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'LIMIT', 'AS', 'AND', 'OR', 'JOIN', 'ON', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'DESC', 'ASC'];
  const functions = ['SUM', 'COUNT', 'AVG', 'MIN', 'MAX', 'date_trunc'];

  let highlighted = escapeHtml(sql);

  keywords.forEach(kw => {
    const regex = new RegExp(`\\b${kw}\\b`, 'gi');
    highlighted = highlighted.replace(regex, `<span class="sql-keyword">${kw}</span>`);
  });

  functions.forEach(fn => {
    const regex = new RegExp(`\\b${fn}\\b`, 'gi');
    highlighted = highlighted.replace(regex, `<span class="sql-function">${fn}</span>`);
  });

  // Highlight strings
  highlighted = highlighted.replace(/'([^']+)'/g, `<span class="sql-string">'$1'</span>`);

  return highlighted;
}

function showUploadSuccess(dataset) {
  const schemaHtml = dataset.schema.map(col =>
    `<li><strong>${col.column}</strong>: ${col.type}</li>`
  ).join('');

  const botIcon = getIcon('bot', 20);

  const html = `
    <div class="message message-assistant">
      <div class="message-avatar">${botIcon}</div>
      <div class="message-content">
        <p class="assistant-intro">
          Successfully uploaded <span class="dataset-link">${dataset.name}</span>!
        </p>
        <div class="sql-block">
          <div class="sql-header">
            <span class="sql-label">DATASET INFO</span>
          </div>
          <div class="sql-code">
Table: ${dataset.table_name}
Rows: ${dataset.row_count.toLocaleString()}

Columns:
${dataset.schema.map(c => `  • ${c.column} (${c.type})`).join('\n')}
          </div>
        </div>
        <p style="color: var(--text-secondary); font-size: 14px; margin-bottom: 8px;">
          Now you can ask questions about your data! Try these examples:
        </p>
        <div class="suggestion-chip-container">
          <button class="suggestion-chip" onclick="useSuggestion('Show me the first 5 rows')">Show me the first 5 rows</button>
          <button class="suggestion-chip" onclick="useSuggestion('Count rows by ${dataset.schema[0]?.column || 'column'}')">Count rows by ${dataset.schema[0]?.column || 'column'}</button>
          <button class="suggestion-chip" onclick="useSuggestion('What is the average of [column]?')">What is the average of [column]?</button>
        </div>
      </div>
    </div>
  `;
  chatArea.insertAdjacentHTML('beforeend', html);
  scrollToBottom();
}

function showLoading(message) {
  hideWelcome();
  chatArea.innerHTML = `
    <div class="message message-assistant">
      <div class="message-avatar">🤖</div>
      <div class="message-content">
        <div class="loading-dots">
          <span></span><span></span><span></span>
        </div>
        <p style="margin-top: 8px; color: var(--text-secondary);">${message}</p>
      </div>
    </div>
  `;
}

function showError(message) {
  const alertIcon = getIcon('triangle-alert', 20);
  const html = `
    <div class="message message-assistant">
      <div class="message-avatar" style="color: var(--accent-red); border-color: var(--accent-red);">${alertIcon}</div>
      <div class="message-content" style="color: var(--accent-red);">
        ${message}
      </div>
    </div>
  `;
  chatArea.insertAdjacentHTML('beforeend', html);
  scrollToBottom();
}

// Utilities
function scrollToBottom() {
  chatArea.scrollTop = chatArea.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function updateLatency(ms) {
  latencyEl.textContent = ms.toFixed(0) + 'ms';
}

window.copySQL = function (sql) {
  navigator.clipboard.writeText(sql);
};

window.useSuggestion = function (text) {
  const input = document.getElementById('questionInput');
  input.value = text;
  input.focus();
  input.disabled = false; // Ensure it's enabled
  document.getElementById('sendBtn').disabled = false;
};

// Fetch Datasets from API
async function fetchDatasets() {
  try {
    const response = await fetch(`${API_BASE}/datasets`);
    if (response.ok) {
      datasets = await response.json();
      updateDatasetList();

      // Auto-select the most recent dataset if available
      if (datasets.length > 0) {
        // Datasets are expected to be in order, or we can sort/find the latest.
        // Assuming latest is at the end or we just pick the last one.
        // Let's pick the last one (latest uploaded).
        selectDataset(datasets.length - 1);
      }

      // Restore recent queries from local storage
      const storedQueries = localStorage.getItem('datapilot_queries');
      if (storedQueries) {
        recentQueries = JSON.parse(storedQueries);
        updateQueryList();
      }
    }
  } catch (e) {
    console.error('Failed to fetch datasets:', e);
  }
}

// Local Storage for Queries only
function saveToLocalStorage() {
  // localStorage.setItem('datapilot_datasets', JSON.stringify(datasets)); // No longer syncing datasets
  localStorage.setItem('datapilot_queries', JSON.stringify(recentQueries));
}

// Delete dataset handler
window.deleteDataset = async function (index) {
  const dataset = datasets[index];
  if (!dataset) return;

  if (!confirm(`Delete dataset "${dataset.name}"? This cannot be undone.`)) {
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/datasets/${dataset.id}`, {
      method: 'DELETE'
    });

    if (response.ok || response.status === 404) {
      // Remove from local array
      datasets.splice(index, 1);

      // Clear current if it was deleted
      if (currentDataset?.id === dataset.id) {
        currentDataset = datasets.length > 0 ? datasets[0] : null;
        currentDatasetEl.textContent = currentDataset?.name || 'No dataset selected';
      }

      updateDatasetList();
    } else {
      showError('Failed to delete dataset');
    }
  } catch (e) {
    console.error('Delete dataset error:', e);
    // Still remove locally even if API fails
    datasets.splice(index, 1);
    updateDatasetList();
  }
};

// Delete query handler
window.deleteQuery = function (index) {
  recentQueries.splice(index, 1);
  saveToLocalStorage();
  updateQueryList();
};
