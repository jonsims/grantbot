// Daily News Agent - Config Editor JavaScript
// Simple interface to edit sources-v4.yaml via GitHub API

const GITHUB_OWNER = 'jonsims';  // Your GitHub username
const GITHUB_REPO = 'daily-news-agent';  // Your repo name
const CONFIG_PATH = 'config/sources-v4.yaml';
const BRANCH = 'v4-development';
const STATUS_PATH = 'config/feed-status.json';
const SUGGESTIONS_PATH = 'config/feed-suggestions.json';

let currentConfig = null;
let currentSHA = null;
let feedStatus = {}; // Store feed status from JSON
let feedSuggestions = {}; // Store feed suggestions from JSON

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check for saved token
    const savedToken = localStorage.getItem('github_token');
    if (savedToken) {
        document.getElementById('github-token').value = savedToken;
        loadConfig();
    }
});

// Save GitHub token to localStorage
function saveToken() {
    const token = document.getElementById('github-token').value.trim();
    if (!token) {
        showStatus('Please enter a GitHub token', 'error');
        return;
    }
    localStorage.setItem('github_token', token);
    showStatus('Token saved! Loading configuration...', 'success');
    loadConfig();
}

// Load configuration from GitHub
async function loadConfig() {
    const token = localStorage.getItem('github_token');
    if (!token) {
        showStatus('Please save your GitHub token first', 'error');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(
            `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${CONFIG_PATH}?ref=${BRANCH}`,
            {
                headers: {
                    'Authorization': `token ${token}`,
                    'Accept': 'application/vnd.github.v3+json'
                }
            }
        );

        if (!response.ok) {
            throw new Error(`GitHub API error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        currentSHA = data.sha;

        // Decode base64 content
        const yamlContent = atob(data.content);
        currentConfig = parseYAML(yamlContent);

        // Load feed status and suggestions from logs
        await loadFeedStatus();
        await loadFeedSuggestions();

        renderConfig();
        document.getElementById('config-editor').classList.remove('hidden');
        showStatus('Configuration loaded successfully', 'success');
    } catch (error) {
        showStatus(`Error loading config: ${error.message}`, 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

// Simple YAML parser (handles the basic structure we need)
function parseYAML(yamlText) {
    const config = { categories: {} };
    const lines = yamlText.split('\n');
    let currentCategory = null;
    let currentSource = null;
    let inSources = false;

    for (let line of lines) {
        const trimmed = line.trim();

        // Skip comments and empty lines
        if (trimmed.startsWith('#') || !trimmed) continue;

        // Category name
        if (line.match(/^  \w+:$/)) {
            currentCategory = line.trim().replace(':', '');
            config.categories[currentCategory] = {
                priority: 'medium',
                word_target: 200,
                sources: []
            };
            inSources = false;
        }
        // Priority
        else if (trimmed.startsWith('priority:')) {
            const priority = trimmed.split(':')[1].trim();
            config.categories[currentCategory].priority = priority;
        }
        // Word target
        else if (trimmed.startsWith('word_target:')) {
            const wordTarget = parseInt(trimmed.split(':')[1].trim());
            config.categories[currentCategory].word_target = wordTarget;
        }
        // Sources section
        else if (trimmed === 'sources:') {
            inSources = true;
        }
        // Source item
        else if (inSources && trimmed.startsWith('- name:')) {
            currentSource = {
                name: trimmed.split('name:')[1].trim().replace(/^["']|["']$/g, ''),
                url: '',
                type: 'rss',
                enabled: true
            };
            config.categories[currentCategory].sources.push(currentSource);
        }
        // Source URL
        else if (currentSource && trimmed.startsWith('url:')) {
            currentSource.url = trimmed.split('url:')[1].trim().replace(/^["']|["']$/g, '');
        }
        // Source type
        else if (currentSource && trimmed.startsWith('type:')) {
            currentSource.type = trimmed.split('type:')[1].trim();
        }
    }

    return config;
}

// Render configuration UI
function renderConfig() {
    const container = document.getElementById('categories-container');
    container.innerHTML = '';

    for (const [categoryName, categoryData] of Object.entries(currentConfig.categories)) {
        const section = document.createElement('div');
        section.className = 'category-section';

        section.innerHTML = `
            <div class="category-header">
                <div class="category-name">${formatCategoryName(categoryName)}</div>
                <div class="word-target">
                    <label>Word Target:</label>
                    <input type="number" value="${categoryData.word_target}"
                           onchange="updateWordTarget('${categoryName}', this.value)"
                           min="50" max="1000" step="50">
                </div>
            </div>
            <div id="sources-${categoryName}"></div>
            <button onclick="showAddSourceForm('${categoryName}')">+ Add Source</button>
            <div id="add-source-${categoryName}" class="add-source-form hidden">
                <div class="form-row">
                    <label>Source Name:</label>
                    <input type="text" id="new-name-${categoryName}" placeholder="Example Blog">
                </div>
                <div class="form-row">
                    <label>RSS Feed URL:</label>
                    <input type="url" id="new-url-${categoryName}" placeholder="https://example.com/feed.xml">
                    <button onclick="testNewFeedUrl('${categoryName}')" class="secondary" style="margin-left: 10px;" title="Open feed in new tab to verify it works">🔗 Test</button>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button onclick="addNewSource('${categoryName}')">Add</button>
                    <button onclick="hideAddSourceForm('${categoryName}')" class="secondary">Cancel</button>
                </div>
            </div>
        `;

        container.appendChild(section);

        // Render sources
        renderSources(categoryName);

        // Render suggestions if available
        renderSuggestions(categoryName);
    }
}

// Render sources for a category
function renderSources(categoryName) {
    const container = document.getElementById(`sources-${categoryName}`);
    const sources = currentConfig.categories[categoryName].sources;

    container.innerHTML = sources.map((source, index) => {
        const status = feedStatus[source.name] || { status: 'unknown', tooltip: 'No data' };
        const statusIcon = getStatusIcon(status.status);
        const statusClass = `status-${status.status}`;
        const isEnabled = source.enabled !== false;
        const itemStyle = isEnabled ? '' : 'opacity: 0.5;';

        return `
        <div class="source-item" style="${itemStyle}">
            <input type="checkbox" id="source-${categoryName}-${index}"
                   ${isEnabled ? 'checked' : ''}
                   onchange="toggleSource('${categoryName}', ${index}, this.checked)">
            <label for="source-${categoryName}-${index}">
                <span class="status-indicator ${statusClass}" title="${status.tooltip}">${statusIcon}</span>
                ${source.name} ${!isEnabled ? '(disabled)' : ''}
            </label>
            <button onclick="toggleUrl('${categoryName}', ${index})" class="url-toggle">Show URL</button>
            <a href="${source.url || '#'}" target="_blank" rel="noopener noreferrer" class="test-feed-link" title="Open feed in new tab to verify it works">🔗 Test Feed</a>
            ${!isEnabled ? `<button onclick="removeSource('${categoryName}', ${index})" class="secondary" style="background: #dc3545;">Delete</button>` : ''}
        </div>
        <div id="url-${categoryName}-${index}" class="source-url hidden">
            <code>${source.url || 'No URL'}</code>
        </div>
    `}).join('');
}

// Update word target
function updateWordTarget(category, value) {
    currentConfig.categories[category].word_target = parseInt(value);
}

// Toggle source enabled/disabled
function toggleSource(category, index, enabled) {
    currentConfig.categories[category].sources[index].enabled = enabled;
    // Re-render to show/hide delete button and update styling
    renderSources(category);
}

// Remove source (only available when source is disabled)
function removeSource(category, index) {
    const source = currentConfig.categories[category].sources[index];
    if (confirm(`Permanently delete "${source.name}"? This cannot be undone.\n\nTip: Uncheck the box to disable instead of deleting.`)) {
        currentConfig.categories[category].sources.splice(index, 1);
        renderSources(category);
    }
}

// Show add source form
function showAddSourceForm(category) {
    document.getElementById(`add-source-${category}`).classList.remove('hidden');
}

// Hide add source form
function hideAddSourceForm(category) {
    document.getElementById(`add-source-${category}`).classList.add('hidden');
}

// Add new source
function addNewSource(category) {
    const name = document.getElementById(`new-name-${category}`).value.trim();
    const url = document.getElementById(`new-url-${category}`).value.trim();

    if (!name || !url) {
        alert('Please enter both name and URL');
        return;
    }

    currentConfig.categories[category].sources.push({
        name: name,
        url: url,
        type: 'rss',
        enabled: true
    });

    // Clear form
    document.getElementById(`new-name-${category}`).value = '';
    document.getElementById(`new-url-${category}`).value = '';
    hideAddSourceForm(category);

    renderSources(category);
}

// Test feed URL by opening in new tab
function testNewFeedUrl(category) {
    const url = document.getElementById(`new-url-${category}`).value.trim();

    if (!url) {
        alert('Please enter a feed URL first');
        return;
    }

    // Open feed in new tab for manual verification
    window.open(url, '_blank', 'noopener,noreferrer');
}

// Convert config to YAML
function configToYAML() {
    let yaml = '# Updated Configuration with NYTimes feeds and new structure\n';
    yaml += 'categories:\n';

    for (const [categoryName, categoryData] of Object.entries(currentConfig.categories)) {
        yaml += `  ${categoryName}:\n`;
        yaml += `    priority: ${categoryData.priority}\n`;
        yaml += `    word_target: ${categoryData.word_target}\n`;

        if (categoryData.sources && categoryData.sources.length > 0) {
            yaml += `    sources:\n`;
            for (const source of categoryData.sources) {
                // Only include enabled sources in YAML
                if (source.enabled !== false) {
                    yaml += `      - name: ${source.name}\n`;
                    yaml += `        url: ${source.url}\n`;
                    if (source.html_url) yaml += `        html_url: ${source.html_url}\n`;
                    yaml += `        type: ${source.type}\n`;
                }
            }
        }
        yaml += '\n';
    }

    return yaml;
}

// Save configuration to GitHub
async function saveConfig() {
    const token = localStorage.getItem('github_token');
    if (!token) {
        showStatus('Please save your GitHub token first', 'error');
        return;
    }

    if (!confirm('Save configuration to GitHub? This will update sources-v4.yaml on the v4-development branch.')) {
        return;
    }

    showLoading(true);

    try {
        const yamlContent = configToYAML();
        const base64Content = btoa(yamlContent);

        const response = await fetch(
            `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${CONFIG_PATH}`,
            {
                method: 'PUT',
                headers: {
                    'Authorization': `token ${token}`,
                    'Accept': 'application/vnd.github.v3+json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: '🎨 Config updated via web UI',
                    content: base64Content,
                    sha: currentSHA,
                    branch: BRANCH
                })
            }
        );

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || `GitHub API error: ${response.status}`);
        }

        const data = await response.json();
        currentSHA = data.content.sha;

        showStatus('✅ Configuration saved to GitHub successfully!', 'success');
    } catch (error) {
        showStatus(`❌ Error saving config: ${error.message}`, 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

// Download configuration as backup
function downloadConfig() {
    const yamlContent = configToYAML();
    const blob = new Blob([yamlContent], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sources-v4-backup-${new Date().toISOString().split('T')[0]}.yaml`;
    a.click();
    URL.revokeObjectURL(url);
}

// Utility functions
function formatCategoryName(name) {
    return name.split('_').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

function showStatus(message, type) {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = `status ${type}`;
    status.style.display = 'block';

    if (type === 'success') {
        setTimeout(() => {
            status.style.display = 'none';
        }, 5000);
    }
}

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

// Load feed status from JSON file
async function loadFeedStatus() {
    const token = localStorage.getItem('github_token');
    if (!token) return;

    try {
        const response = await fetch(
            `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${STATUS_PATH}?ref=${BRANCH}`,
            {
                headers: {
                    'Authorization': `token ${token}`,
                    'Accept': 'application/vnd.github.v3+json'
                }
            }
        );

        if (!response.ok) {
            console.log('Feed status file not found (will be generated on next run)');
            return;
        }

        const data = await response.json();
        const statusContent = atob(data.content);
        const statusData = JSON.parse(statusContent);

        // Convert JSON format to our internal format
        feedStatus = {};
        for (const [sourceName, sourceData] of Object.entries(statusData.feeds || {})) {
            feedStatus[sourceName] = {
                status: sourceData.status,
                tooltip: sourceData.tooltip
            };
        }

        console.log('Feed status loaded:', Object.keys(feedStatus).length, 'feeds');
        console.log('Status generated:', statusData.generated_at);
    } catch (error) {
        console.log('Error loading feed status:', error.message);
    }
}

// Get status icon based on status
function getStatusIcon(status) {
    switch (status) {
        case 'success': return '●';
        case 'empty': return '○';
        case 'warning': return '▲';
        case 'error': return '✗';
        default: return '?';
    }
}

// Toggle URL display
function toggleUrl(category, index) {
    const urlDiv = document.getElementById(`url-${category}-${index}`);
    const button = event.target;

    if (urlDiv.classList.contains('hidden')) {
        urlDiv.classList.remove('hidden');
        button.textContent = 'Hide URL';
    } else {
        urlDiv.classList.add('hidden');
        button.textContent = 'Show URL';
    }
}

// Load feed suggestions from JSON file
async function loadFeedSuggestions() {
    const token = localStorage.getItem('github_token');
    if (!token) return;

    try {
        const response = await fetch(
            `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${SUGGESTIONS_PATH}?ref=${BRANCH}`,
            {
                headers: {
                    'Authorization': `token ${token}`,
                    'Accept': 'application/vnd.github.v3+json'
                }
            }
        );

        if (!response.ok) {
            console.log('Feed suggestions file not found (will be generated on next weekly run)');
            return;
        }

        const data = await response.json();
        const suggestionsContent = atob(data.content);
        const suggestionsData = JSON.parse(suggestionsContent);

        feedSuggestions = suggestionsData.suggestions || {};

        console.log('Feed suggestions loaded:', Object.keys(feedSuggestions).length, 'categories');
        console.log('Suggestions generated:', suggestionsData.generated_at);
    } catch (error) {
        console.log('Error loading feed suggestions:', error.message);
    }
}

// Render suggestions for a category
function renderSuggestions(categoryName) {
    const suggestions = feedSuggestions[categoryName];
    if (!suggestions || suggestions.length === 0) {
        return; // Don't show section if no suggestions
    }

    const categorySection = document.querySelector(`#sources-${categoryName}`).parentElement;

    // Create suggestions section
    const suggestionsDiv = document.createElement('div');
    suggestionsDiv.className = 'suggestions-section';
    suggestionsDiv.id = `suggestions-${categoryName}`;

    suggestionsDiv.innerHTML = `
        <div class="suggestions-header" onclick="toggleSuggestions('${categoryName}')">
            <h3>💡 Suggested Feeds (${suggestions.length})</h3>
            <span class="suggestions-toggle" id="toggle-${categoryName}">▼ Show</span>
        </div>
        <div id="suggestions-list-${categoryName}" class="hidden"></div>
    `;

    categorySection.appendChild(suggestionsDiv);

    // Render each suggestion
    const listContainer = document.getElementById(`suggestions-list-${categoryName}`);

    suggestions.forEach((suggestion, index) => {
        const suggestionDiv = document.createElement('div');
        suggestionDiv.className = 'suggestion-item';

        const confidenceClass = suggestion.confidence === 'high' ? 'confidence-high' :
                               suggestion.confidence === 'medium' ? 'confidence-medium' : '';

        suggestionDiv.innerHTML = `
            <div class="suggestion-info">
                <div class="suggestion-name">
                    ${suggestion.name}
                    <span class="confidence-badge ${confidenceClass}">${suggestion.confidence || 'medium'}</span>
                </div>
                <div class="suggestion-description">${suggestion.description}</div>
                <div class="suggestion-meta">
                    <span>📊 ${suggestion.estimated_posts_per_week}</span>
                    <span>🔗 <a href="${suggestion.preview_link}" target="_blank">Preview</a></span>
                </div>
                ${suggestion.sample_headline ? `<div class="suggestion-sample">Sample: "${suggestion.sample_headline}"</div>` : ''}
            </div>
            <div class="suggestion-actions">
                <button class="add-suggestion-btn" onclick="addSuggestion('${categoryName}', ${index})">
                    + Add Feed
                </button>
            </div>
        `;

        listContainer.appendChild(suggestionDiv);
    });
}

// Toggle suggestions visibility
function toggleSuggestions(categoryName) {
    const listDiv = document.getElementById(`suggestions-list-${categoryName}`);
    const toggleSpan = document.getElementById(`toggle-${categoryName}`);

    if (listDiv.classList.contains('hidden')) {
        listDiv.classList.remove('hidden');
        toggleSpan.textContent = '▲ Hide';
    } else {
        listDiv.classList.add('hidden');
        toggleSpan.textContent = '▼ Show';
    }
}

// Add a suggested feed to the category
function addSuggestion(categoryName, suggestionIndex) {
    const suggestion = feedSuggestions[categoryName][suggestionIndex];

    if (!suggestion) {
        alert('Suggestion not found');
        return;
    }

    // Check if feed already exists
    const exists = currentConfig.categories[categoryName].sources.some(
        source => source.url === suggestion.url || source.name === suggestion.name
    );

    if (exists) {
        alert('This feed is already in your sources!');
        return;
    }

    // Add to config
    currentConfig.categories[categoryName].sources.push({
        name: suggestion.name,
        url: suggestion.url,
        type: suggestion.type || 'rss',
        enabled: true
    });

    // Re-render sources
    renderSources(categoryName);

    // Remove the suggestion from the list
    const suggestionItem = event.target.closest('.suggestion-item');
    suggestionItem.style.opacity = '0.5';
    suggestionItem.innerHTML = '<div class="no-suggestions">✓ Added! Save changes to commit.</div>';

    showStatus(`Added "${suggestion.name}" to ${formatCategoryName(categoryName)}. Don't forget to save!`, 'success');
}
