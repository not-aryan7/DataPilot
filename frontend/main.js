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
  loadFromLocalStorage();
});

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
  if (!question || !currentDataset) return;

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
        <span class="file-icon">📄</span>
        Upload a CSV to start
      </li>
    `;
    return;
  }

  datasetList.innerHTML = datasets.map((ds, index) => `
    <li class="dataset-item ${ds.id === currentDataset?.id ? 'active' : ''}" 
        onclick="selectDataset(${index})">
      <span class="file-icon">📊</span>
      ${ds.name}
    </li>
  `).join('');
}

window.selectDataset = function (index) {
  currentDataset = datasets[index];
  currentDatasetEl.textContent = currentDataset.name;
  updateDatasetList();
  enableInput();
  hideWelcome();
};

function addRecentQuery(question) {
  const truncated = question.length > 30 ? question.substring(0, 30) + '...' : question;
  recentQueries.unshift(truncated);
  if (recentQueries.length > 5) recentQueries.pop();
  saveToLocalStorage();
  updateQueryList();
}

function updateQueryList() {
  if (recentQueries.length === 0) {
    queryList.innerHTML = '<li class="query-item placeholder">No queries yet</li>';
    return;
  }

  queryList.innerHTML = recentQueries.map(q => `
    <li class="query-item">${q}</li>
  `).join('');
}

function enableInput() {
  questionInput.disabled = false;
  sendBtn.disabled = false;
  questionInput.placeholder = 'Ask DataPilot about your dataset...';
}

function hideWelcome() {
  welcomeState.style.display = 'none';
}

function resetToWelcome() {
  currentDataset = null;
  currentDatasetEl.textContent = 'No dataset selected';
  questionInput.disabled = true;
  sendBtn.disabled = true;
  chatArea.innerHTML = `
    <div class="welcome-state" id="welcomeState">
      <div class="welcome-icon">📊</div>
      <h2>Welcome to DataPilot</h2>
      <p>Upload a CSV file to start analyzing your data with natural language</p>
      <label class="upload-zone" id="uploadZone">
        <input type="file" id="fileInput" accept=".csv" hidden>
        <div class="upload-content">
          <span class="upload-icon">📁</span>
          <span>Drop CSV here or click to upload</span>
        </div>
      </label>
    </div>
  `;
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
  const html = `
    <div class="message message-user">
      <div class="message-avatar">👤</div>
      <div class="message-content">${escapeHtml(question)}</div>
    </div>
  `;
  chatArea.insertAdjacentHTML('beforeend', html);
  scrollToBottom();
}

function addLoadingMessage() {
  const id = 'loading-' + Date.now();
  const html = `
    <div class="message message-assistant" id="${id}">
      <div class="message-avatar">🤖</div>
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

  const html = `
    <div class="message message-assistant">
      <div class="message-avatar">🤖</div>
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

  const html = `
    <div class="message message-assistant">
      <div class="message-avatar">🤖</div>
      <div class="message-content">
        <p class="assistant-intro">
          ✅ Successfully uploaded <span class="dataset-link">${dataset.name}</span>!
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
        <p style="color: var(--text-secondary); font-size: 14px;">
          Now you can ask questions about your data! Try something like:
          <br>• "Show me the first 5 rows"
          <br>• "What's the average of [column]?"
          <br>• "Count rows by [column]"
        </p>
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
  const html = `
    <div class="message message-assistant">
      <div class="message-avatar">⚠️</div>
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

// Local Storage
function saveToLocalStorage() {
  localStorage.setItem('datapilot_datasets', JSON.stringify(datasets));
  localStorage.setItem('datapilot_queries', JSON.stringify(recentQueries));
}

function loadFromLocalStorage() {
  try {
    datasets = JSON.parse(localStorage.getItem('datapilot_datasets')) || [];
    recentQueries = JSON.parse(localStorage.getItem('datapilot_queries')) || [];
    updateDatasetList();
    updateQueryList();
  } catch (e) {
    console.error('Failed to load from localStorage:', e);
  }
}
