// SQL Editor JavaScript

let monacoEditor = null;
let currentSchema = {};

// Initialize Monaco Editor
function initSQLEditor() {
    require.config({ paths: { vs: 'https://unpkg.com/monaco-editor@0.44.0/min/vs' } });
    
    require(['vs/editor/editor.main'], function () {
        const theme = document.documentElement.getAttribute('data-theme');
        
        monacoEditor = monaco.editor.create(document.getElementById('sql-editor'), {
            value: '-- Write your SQL query here\nSELECT * FROM users LIMIT 10;',
            language: 'sql',
            theme: theme === 'dark' ? 'vs-dark' : 'vs',
            automaticLayout: true,
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            wordWrap: 'on',
            scrollBeyondLastLine: false,
            folding: true,
            renderLineHighlight: 'all',
            selectOnLineNumbers: true,
            roundedSelection: false,
            readOnly: false,
            cursorStyle: 'line',
            automaticLayout: true,
        });

        // Add keyboard shortcuts
        monacoEditor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, executeQuery);
        
        // Update editor theme when page theme changes
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.attributeName === 'data-theme') {
                    const newTheme = document.documentElement.getAttribute('data-theme');
                    monaco.editor.setTheme(newTheme === 'dark' ? 'vs-dark' : 'vs');
                }
            });
        });
        
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });
    });
}

// Execute SQL Query
async function executeQuery() {
    if (!monacoEditor) return;
    
    const query = monacoEditor.getValue().trim();
    if (!query) {
        showMessage('Please enter a SQL query', 'warning');
        return;
    }
    
    const executeBtn = document.querySelector('.execute-query-btn');
    setLoading(executeBtn, true);
    
    try {
        const response = await apiRequest('/editor/api/execute/', {
            method: 'POST',
            body: JSON.stringify({ query })
        });
        
        if (response.success) {
            displayResults(response);
            showMessage('Query executed successfully', 'success');
        } else {
            displayError(response.error || 'Query execution failed');
            showMessage(response.error || 'Query execution failed', 'error');
        }
    } catch (error) {
        console.error('Query execution error:', error);
        displayError('Failed to execute query. Please try again.');
        showMessage('Failed to execute query. Please try again.', 'error');
    } finally {
        setLoading(executeBtn, false);
    }
}

// Display Query Results
function displayResults(response) {
    const container = document.getElementById('results-container');
    
    if (response.results && response.results.length > 0) {
        const table = createResultsTable(response.results, response.columns);
        container.innerHTML = '';
        container.appendChild(table);
        
        // Enable export button
        const exportBtn = document.querySelector('.results-actions button[onclick="exportResults()"]');
        if (exportBtn) exportBtn.disabled = false;
    } else if (response.changes !== undefined) {
        // For INSERT, UPDATE, DELETE queries
        container.innerHTML = `
            <div class="query-success">
                <span class="material-icons">check_circle</span>
                <p>Query executed successfully</p>
                <p class="query-stats">${response.changes} row(s) affected</p>
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="query-success">
                <span class="material-icons">check_circle</span>
                <p>Query executed successfully</p>
            </div>
        `;
    }
}

// Display Query Error
function displayError(error) {
    const container = document.getElementById('results-container');
    container.innerHTML = `
        <div class="query-error">
            <span class="material-icons">error</span>
            <p>Query Error</p>
            <pre class="error-message">${error}</pre>
        </div>
    `;
}

// Create Results Table
function createResultsTable(results, columns) {
    const tableContainer = document.createElement('div');
    tableContainer.className = 'results-table';
    
    const table = document.createElement('table');
    
    // Create header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    columns.forEach(column => {
        const th = document.createElement('th');
        th.textContent = column;
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create body
    const tbody = document.createElement('tbody');
    
    results.forEach(row => {
        const tr = document.createElement('tr');
        
        columns.forEach(column => {
            const td = document.createElement('td');
            const value = row[column];
            td.textContent = value !== null && value !== undefined ? value : 'NULL';
            tr.appendChild(td);
        });
        
        tbody.appendChild(tr);
    });
    
    table.appendChild(tbody);
    tableContainer.appendChild(table);
    
    return tableContainer;
}

// Load Database Schema
async function loadSchema() {
    try {
        const response = await apiRequest('/schemas/api/schema/');
        currentSchema = response;
        displaySchema(response);
    } catch (error) {
        console.error('Failed to load schema:', error);
        const container = document.getElementById('schema-container');
        container.innerHTML = `
            <div class="empty-state">
                <span class="material-icons">error</span>
                <p>Failed to load schema</p>
            </div>
        `;
    }
}

// Display Database Schema
function displaySchema(schema) {
    const container = document.getElementById('schema-container');
    
    if (!schema.tables || Object.keys(schema.tables).length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <span class="material-icons">table_chart</span>
                <p>No tables found. Create some tables to get started!</p>
            </div>
        `;
        return;
    }
    
    const schemaTree = document.createElement('div');
    schemaTree.className = 'schema-tree';
    
    Object.entries(schema.tables).forEach(([tableName, table]) => {
        const tableElement = createSchemaTable(tableName, table);
        schemaTree.appendChild(tableElement);
    });
    
    container.innerHTML = '';
    container.appendChild(schemaTree);
}

// Create Schema Table Element
function createSchemaTable(tableName, table) {
    const tableDiv = document.createElement('div');
    tableDiv.className = 'schema-table';
    
    const header = document.createElement('div');
    header.className = 'schema-table-header';
    header.onclick = () => toggleSchemaTable(tableDiv);
    
    const nameDiv = document.createElement('div');
    nameDiv.className = 'schema-table-name';
    nameDiv.innerHTML = `
        <span class="material-icons">table_chart</span>
        ${tableName}
    `;
    
    const toggle = document.createElement('span');
    toggle.className = 'material-icons schema-table-toggle';
    toggle.textContent = 'expand_more';
    
    header.appendChild(nameDiv);
    header.appendChild(toggle);
    
    const columnsDiv = document.createElement('div');
    columnsDiv.className = 'schema-columns';
    
    table.columns.forEach(column => {
        const columnDiv = document.createElement('div');
        columnDiv.className = 'schema-column';
        
        const nameSpan = document.createElement('span');
        nameSpan.className = 'schema-column-name';
        nameSpan.textContent = column.name;
        
        const typeSpan = document.createElement('span');
        typeSpan.className = 'schema-column-type';
        typeSpan.textContent = `${column.type} ${column.constraints || ''}`.trim();
        
        columnDiv.appendChild(nameSpan);
        columnDiv.appendChild(typeSpan);
        columnsDiv.appendChild(columnDiv);
    });
    
    tableDiv.appendChild(header);
    tableDiv.appendChild(columnsDiv);
    
    return tableDiv;
}

// Toggle Schema Table Expansion
function toggleSchemaTable(tableElement) {
    tableElement.classList.toggle('expanded');
}

// Refresh Schema
async function refreshSchema() {
    const refreshBtn = document.querySelector('.schema-actions button[onclick="refreshSchema()"]');
    setLoading(refreshBtn, true);
    
    try {
        await loadSchema();
        showMessage('Schema refreshed successfully', 'success');
    } catch (error) {
        showMessage('Failed to refresh schema', 'error');
    } finally {
        setLoading(refreshBtn, false);
    }
}

// Clear Results
function clearResults() {
    const container = document.getElementById('results-container');
    container.innerHTML = `
        <div class="empty-state">
            <span class="material-icons">play_circle_outline</span>
            <p>Run a SQL query to see results here</p>
        </div>
    `;
    
    // Disable export button
    const exportBtn = document.querySelector('.results-actions button[onclick="exportResults()"]');
    if (exportBtn) exportBtn.disabled = true;
}

// Export Results
function exportResults() {
    const query = monacoEditor ? monacoEditor.getValue().trim() : '';

    if (!query) {
        showMessage('No query to export results for', 'warning');
        return;
    }

    // Show export format selection modal
    showExportModal(query);
}

// Show Export Modal
function showExportModal(query) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Export Results</h3>
                <button class="modal-close" onclick="closeModal(this)">
                    <span class="material-icons">close</span>
                </button>
            </div>
            <div class="modal-body">
                <p>Choose export format:</p>
                <div class="export-options">
                    <button class="btn btn-primary export-option" data-format="csv">
                        <span class="material-icons">table_chart</span>
                        Export as CSV
                    </button>
                    <button class="btn btn-primary export-option" data-format="json">
                        <span class="material-icons">code</span>
                        Export as JSON
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Add event listeners
    modal.querySelectorAll('.export-option').forEach(btn => {
        btn.addEventListener('click', function() {
            const format = this.dataset.format;
            exportResultsInFormat(query, format);
            closeModal(modal);
        });
    });

    // Close modal when clicking outside
    modal.addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal(this);
        }
    });
}

// Export Results in Specific Format
async function exportResultsInFormat(query, format) {
    try {
        const response = await fetch(`/editor/api/export/${format}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ query })
        });

        if (response.ok) {
            // Check if response is JSON (error) or file download
            const contentType = response.headers.get('content-type');

            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                if (!data.success) {
                    showMessage(data.error || 'Export failed', 'error');
                    return;
                }
            } else {
                // File download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;

                // Get filename from Content-Disposition header
                const disposition = response.headers.get('Content-Disposition');
                let filename = `query_results.${format}`;
                if (disposition) {
                    const filenameMatch = disposition.match(/filename="(.+)"/);
                    if (filenameMatch) {
                        filename = filenameMatch[1];
                    }
                }

                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                showMessage(`Results exported as ${format.toUpperCase()}`, 'success');
            }
        } else {
            const data = await response.json();
            showMessage(data.error || 'Export failed', 'error');
        }
    } catch (error) {
        console.error('Export error:', error);
        showMessage('Export failed. Please try again.', 'error');
    }
}

// Close Modal
function closeModal(modal) {
    if (modal.remove) {
        modal.remove();
    } else {
        modal.parentNode.removeChild(modal);
    }
}

// Authentication-required functions
if (window.user && window.user.is_authenticated) {
    
    // Open History Modal
    async function openHistoryModal() {
        try {
            const response = await apiRequest('/editor/api/history/');
            displayHistoryList(response.history || []);
            openModal('historyModal');
        } catch (error) {
            showMessage('Failed to load query history', 'error');
        }
    }
    
    // Open Saved Queries Modal
    async function openSavedQueriesModal() {
        try {
            const response = await apiRequest('/editor/api/saved-queries/');
            displaySavedQueriesList(response.queries || []);
            openModal('savedQueriesModal');
        } catch (error) {
            showMessage('Failed to load saved queries', 'error');
        }
    }
    
    // Save Current Query
    function saveCurrentQuery() {
        if (!monacoEditor) return;
        
        const query = monacoEditor.getValue().trim();
        if (!query) {
            showMessage('Please enter a SQL query to save', 'warning');
            return;
        }
        
        openModal('saveQueryModal');
    }
    
    // Handle Save Query Form
    async function handleSaveQuery(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const query = monacoEditor.getValue().trim();
        
        const data = {
            title: formData.get('title'),
            description: formData.get('description'),
            query: query,
            is_favorite: formData.get('is_favorite') === 'on'
        };
        
        try {
            await apiRequest('/editor/api/save-query/', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            
            showMessage('Query saved successfully', 'success');
            closeModal('saveQueryModal');
            event.target.reset();
        } catch (error) {
            showMessage('Failed to save query', 'error');
        }
    }
    
    // Display History List
    function displayHistoryList(history) {
        const container = document.getElementById('history-list');
        
        if (history.length === 0) {
            container.innerHTML = '<p class="text-center">No query history found</p>';
            return;
        }
        
        container.innerHTML = history.map(item => `
            <div class="history-item" onclick="loadHistoryQuery('${item.query.replace(/'/g, "\\'")}')">
                <div class="history-item-query">${item.query}</div>
                <div class="history-item-meta">
                    <span>${new Date(item.executed_at).toLocaleString()}</span>
                    <span class="${item.success ? 'text-success' : 'text-error'}">
                        ${item.success ? 'Success' : 'Error'}
                    </span>
                </div>
            </div>
        `).join('');
    }
    
    // Display Saved Queries List
    function displaySavedQueriesList(queries) {
        const container = document.getElementById('saved-queries-list');
        
        if (queries.length === 0) {
            container.innerHTML = '<p class="text-center">No saved queries found</p>';
            return;
        }
        
        container.innerHTML = queries.map(item => `
            <div class="saved-query-item" onclick="loadSavedQuery('${item.query.replace(/'/g, "\\'")}')">
                <div class="saved-query-item-title">
                    ${item.title}
                    ${item.is_favorite ? '<span class="material-icons" style="color: gold; font-size: 16px;">star</span>' : ''}
                </div>
                <div class="saved-query-item-query">${item.query}</div>
                <div class="saved-query-item-meta">
                    <span>${new Date(item.created_at).toLocaleDateString()}</span>
                    <button class="btn btn-sm btn-danger" onclick="event.stopPropagation(); deleteSavedQuery(${item.id})">
                        Delete
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    // Load History Query
    function loadHistoryQuery(query) {
        if (monacoEditor) {
            monacoEditor.setValue(query);
            closeModal('historyModal');
        }
    }
    
    // Load Saved Query
    function loadSavedQuery(query) {
        if (monacoEditor) {
            monacoEditor.setValue(query);
            closeModal('savedQueriesModal');
        }
    }
    
    // Delete Saved Query
    async function deleteSavedQuery(queryId) {
        if (!confirm('Are you sure you want to delete this saved query?')) {
            return;
        }
        
        try {
            await apiRequest(`/editor/api/delete-query/${queryId}/`, {
                method: 'DELETE'
            });
            
            showMessage('Query deleted successfully', 'success');
            openSavedQueriesModal(); // Refresh the list
        } catch (error) {
            showMessage('Failed to delete query', 'error');
        }
    }
    
    // Make functions global for onclick handlers
    window.openHistoryModal = openHistoryModal;
    window.openSavedQueriesModal = openSavedQueriesModal;
    window.saveCurrentQuery = saveCurrentQuery;
    window.handleSaveQuery = handleSaveQuery;
    window.loadHistoryQuery = loadHistoryQuery;
    window.loadSavedQuery = loadSavedQuery;
    window.deleteSavedQuery = deleteSavedQuery;
}

// Schema Templates
async function openSchemaTemplates() {
    try {
        const response = await apiRequest('/schemas/api/templates/');
        displaySchemaTemplates(response.templates || []);
        openModal('schemaTemplatesModal');
    } catch (error) {
        showMessage('Failed to load schema templates', 'error');
    }
}

function displaySchemaTemplates(templates) {
    const container = document.getElementById('schema-templates-list');
    
    if (templates.length === 0) {
        container.innerHTML = '<p class="text-center">No schema templates available</p>';
        return;
    }
    
    container.innerHTML = templates.map(template => `
        <div class="card" style="margin-bottom: 1rem;">
            <div class="card-header">
                <h4 class="card-title">${template.name}</h4>
                <p class="card-subtitle">${template.description}</p>
            </div>
            <div class="card-actions">
                <button class="btn btn-primary" onclick="loadSchemaTemplate(${template.id})">
                    Load Template
                </button>
            </div>
        </div>
    `).join('');
}

async function loadSchemaTemplate(templateId) {
    try {
        await apiRequest(`/schemas/api/load-template/${templateId}/`, {
            method: 'POST'
        });
        
        showMessage('Schema template loaded successfully', 'success');
        closeModal('schemaTemplatesModal');
        await loadSchema(); // Refresh schema display
    } catch (error) {
        showMessage('Failed to load schema template', 'error');
    }
}

// Make functions global
window.executeQuery = executeQuery;
window.refreshSchema = refreshSchema;
window.clearResults = clearResults;
window.exportResults = exportResults;
window.openSchemaTemplates = openSchemaTemplates;
window.loadSchemaTemplate = loadSchemaTemplate;
