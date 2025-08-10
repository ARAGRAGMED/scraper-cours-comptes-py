// Moroccan Court of Accounts Scraper - Frontend Application

class CourtAccountsScraper {
    constructor() {
        this.apiBase = '/api';
        this.currentStatus = null;
        this.init();
    }

    init() {
        this.bindEvents();
        // Wait for DOM to be fully ready before loading data
        setTimeout(() => {
            this.loadAvailableYears();
            this.checkStatus();
            this.loadCategories(); // Load categories dynamically
            this.loadData(); // Automatically load publications data
        }, 100);
    }

    bindEvents() {
        // Scraping controls
        document.getElementById('startScraping').addEventListener('click', () => this.startScraping());
        document.getElementById('stopScraping').addEventListener('click', () => this.stopScraping());
        document.getElementById('checkStatus').addEventListener('click', () => this.checkStatus());

        // Data controls
        document.getElementById('loadData').addEventListener('click', () => this.loadData());
        
        // Category filter change
        document.getElementById('categoryFilter').addEventListener('change', () => this.onCategoryChange());
    }

    // API Helper Methods
    async makeRequest(endpoint, options = {}) {
        const url = `${this.apiBase}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        const requestOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, requestOptions);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Scraping Methods
    async startScraping() {
        try {
            this.showMessage('Starting scraping...', 'info');
            
            const requestData = {
                max_pages: parseInt(document.getElementById('maxPages').value) || 10,
                force_rescrape: document.getElementById('forceRescrape').checked
            };

            const response = await this.makeRequest('/court-accounts/scrape', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            if (response.success) {
                this.showMessage(`Scraping completed! Found ${response.publications_count} publications.`, 'success');
                this.updateScrapingStatus(response);
                // Refresh categories and then load data
                await this.loadCategories();
                this.loadData();
            } else {
                this.showMessage(`Scraping failed: ${response.message}`, 'error');
            }
        } catch (error) {
            this.showMessage(`Error starting scraping: ${error.message}`, 'error');
        }
    }

    async stopScraping() {
        try {
            const response = await this.makeRequest('/court-accounts/stop', {
                method: 'POST'
            });

            if (response.success) {
                this.showMessage('Scraping stopped successfully.', 'success');
                this.updateScrapingStatus(response);
            } else {
                this.showMessage(`Failed to stop scraping: ${response.message}`, 'error');
            }
        } catch (error) {
            this.showMessage(`Error stopping scraping: ${error.message}`, 'error');
        }
    }

    async checkStatus() {
        try {
            const response = await this.makeRequest('/court-accounts/status');
            this.updateStatusDisplay(response);
        } catch (error) {
            this.showMessage(`Error checking status: ${error.message}`, 'error');
        }
    }

    // Data Loading Methods
    async loadData() {
        try {
            const container = document.getElementById('publicationsList');
            container.innerHTML = '<div class="loading-message">Loading publications...</div>';
            
            const category = document.getElementById('categoryFilter').value;
            let url = '/court-accounts/publications';
            
            if (category) {
                url = `/court-accounts/publications?category=${encodeURIComponent(category)}`;
            }
            
            const response = await this.makeRequest(url);
            
            if (response.publications && response.publications.length > 0) {
                this.displayPublications(response.publications);
            } else {
                container.innerHTML = `
                    <div class="loading-message">
                        📭 No publications found
                        <br><br>
                        <button onclick="app.loadData()" class="btn btn-info">🔄 Reload Data</button>
                    </div>
                `;
            }
        } catch (error) {
            const container = document.getElementById('publicationsList');
            container.innerHTML = `
                <div class="loading-message error">
                    ❌ Failed to load publications: ${error.message}
                    <br><br>
                    <button onclick="app.loadData()" class="btn btn-info">🔄 Reload Data</button>
                </div>
            `;
        }
    }

    async loadAvailableYears() {
        try {
            const response = await this.makeRequest('/court-accounts/status');
            // No need to populate year filter since it's removed
        } catch (error) {
            console.error('Error loading status:', error);
        }
    }

    async loadCategories() {
        try {
            const categorySelect = document.getElementById('categoryFilter');
            // Show loading state
            categorySelect.innerHTML = '<option value="">Loading categories...</option>';
            categorySelect.disabled = true;
            
            const response = await this.makeRequest('/court-accounts/categories');
            if (response.categories && Array.isArray(response.categories)) {
                categorySelect.innerHTML = ''; // Clear existing options
                categorySelect.innerHTML = '<option value="">All Categories</option>'; // Add default option
                response.categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category;
                    option.textContent = category;
                    categorySelect.appendChild(option);
                });
                // Re-select the current category if it's still available
                const currentCategory = document.getElementById('categoryFilter').value;
                if (currentCategory && response.categories.includes(currentCategory)) {
                    categorySelect.value = currentCategory;
                }
                categorySelect.disabled = false;
            } else {
                this.showMessage('Failed to load categories: Invalid response format', 'error');
                categorySelect.innerHTML = '<option value="">Error loading categories</option>';
                categorySelect.disabled = false;
            }
        } catch (error) {
            this.showMessage(`Error loading categories: ${error.message}`, 'error');
            const categorySelect = document.getElementById('categoryFilter');
            categorySelect.innerHTML = '<option value="">Error loading categories</option>';
            categorySelect.disabled = false;
        }
    }
    
    onCategoryChange() {
        // Automatically reload data when category changes
        const category = document.getElementById('categoryFilter').value;
        if (category) {
            this.showMessage(`Filtering publications by category: ${category}`, 'info');
        } else {
            this.showMessage('Showing all publications', 'info');
        }
        this.loadData();
    }

    // Display Methods
    displayPublications(publications) {
        const container = document.getElementById('publicationsList');
        
        if (!publications || publications.length === 0) {
            container.innerHTML = `
                <div class="loading-message">
                    📭 No publications found
                    <br><br>
                    <button onclick="app.loadData()" class="btn btn-info">🔄 Reload Data</button>
                </div>
            `;
            return;
        }

        const html = publications.map(pub => `
            <div class="publication-item">
                <div class="publication-title">${this.escapeHtml(pub.title)}</div>
                <div class="publication-meta">
                    <div class="meta-item">
                        <span class="meta-label">Category:</span>
                        <span class="meta-value">${this.escapeHtml(pub.category)}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Date:</span>
                        <span class="meta-value">${pub.date || 'N/A'}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Year:</span>
                        <span class="meta-value">${pub.year || 'N/A'}</span>
                    </div>
                    ${pub.commission ? `
                        <div class="meta-item">
                            <span class="meta-label">Commission:</span>
                            <span class="meta-value">${this.escapeHtml(pub.commission)}</span>
                        </div>
                    ` : ''}
                    ${pub.ministry ? `
                        <div class="meta-item">
                            <span class="meta-label">Ministry:</span>
                            <span class="meta-value">${this.escapeHtml(pub.ministry)}</span>
                        </div>
                    ` : ''}
                </div>
                ${pub.description ? `
                    <div class="publication-description">${this.escapeHtml(pub.description)}</div>
                ` : ''}
                <a href="${pub.url}" target="_blank" class="publication-link">View Publication →</a>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    updateScrapingStatus(response) {
        const statusPanel = document.getElementById('scrapingStatus');
        const statusContent = document.getElementById('statusContent');
        
        if (response.success) {
            statusContent.innerHTML = `
                <div class="status-item">
                    <strong>Status:</strong> Completed
                </div>
                <div class="status-item">
                    <strong>Publications Found:</strong> ${response.publications_count}
                </div>
                <div class="status-item">
                    <strong>Execution Time:</strong> ${response.execution_time ? response.execution_time.toFixed(2) + 's' : 'N/A'}
                </div>
                <div class="status-item">
                    <strong>File Path:</strong> ${response.file_path}
                </div>
            `;
        } else {
            statusContent.innerHTML = `
                <div class="status-item error">
                    <strong>Status:</strong> Failed
                </div>
                <div class="status-item">
                    <strong>Error:</strong> ${response.message}
                </div>
            `;
        }
        
        statusPanel.classList.remove('hidden');
    }

    updateStatusDisplay(status) {
        const statusPanel = document.getElementById('scrapingStatus');
        const statusContent = document.getElementById('statusContent');
        
        if (status.success && status.details) {
            const details = status.details;
            statusContent.innerHTML = `
                <div class="status-item">
                    <strong>Status:</strong> ${details.status || 'Unknown'}
                </div>
                <div class="status-item">
                    <strong>Running:</strong> ${details.is_running ? 'Yes' : 'No'}
                </div>
                <div class="status-item">
                    <strong>Total Publications:</strong> ${details.total_publications || 0}
                </div>
                <div class="status-item">
                    <strong>Available Years:</strong> ${details.available_years && Array.isArray(details.available_years) ? details.available_years.join(', ') : 'None'}
                </div>
                ${details.last_run ? `
                    <div class="status-item">
                        <strong>Last Run:</strong> ${new Date(details.last_run).toLocaleString()}
                    </div>
                ` : ''}
                ${details.last_run_duration ? `
                    <div class="status-item">
                        <strong>Last Run Duration:</strong> ${details.last_run_duration.toFixed(2)}s
                    </div>
                ` : ''}
            `;
        } else {
            statusContent.innerHTML = `
                <div class="status-item error">
                    <strong>Error:</strong> ${status.message || 'Failed to get status'}
                </div>
            `;
        }
        
        statusPanel.classList.remove('hidden');
    }

    // Utility Methods
    showMessage(message, type = 'info') {
        // Remove existing messages
        const existingMessage = document.querySelector('.message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // Create new message
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;

        // Insert after header
        const header = document.querySelector('header');
        header.parentNode.insertBefore(messageDiv, header.nextSibling);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new CourtAccountsScraper();
});