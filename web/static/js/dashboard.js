/**
 * Network Device Dashboard JavaScript
 */

// Global state
let currentSection = 'overview';
let connectionStatus = 'checking';
let apiBaseUrl = '';

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

/**
 * Initialize the dashboard
 */
async function initializeDashboard() {
    console.log('Initializing Network Device Dashboard...');
    
    // Check API connection
    await checkConnection();
    
    // Load initial data
    await loadOverviewData();
    
    // Set up periodic updates
    setInterval(checkConnection, 30000); // Check connection every 30 seconds
    setInterval(refreshCurrentSection, 60000); // Refresh current section every minute
    
    console.log('Dashboard initialized successfully');
}

/**
 * Check API connection status
 */
async function checkConnection() {
    const statusElement = document.getElementById('connectionStatus');
    
    try {
        statusElement.className = 'connection-status checking';
        statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Checking...</span>';
        
        const response = await fetch('/health');
        
        if (response.ok) {
            connectionStatus = 'connected';
            statusElement.className = 'connection-status connected';
            statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Connected</span>';
        } else {
            throw new Error('Health check failed');
        }
    } catch (error) {
        connectionStatus = 'disconnected';
        statusElement.className = 'connection-status disconnected';
        statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Disconnected</span>';
        
        showToast('Connection lost to MCP server', 'error');
        console.error('Connection check failed:', error);
    }
}

/**
 * Show/hide sections based on navigation
 */
function showSection(sectionId) {
    // Update navigation
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
    
    // Show selected section
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
        currentSection = sectionId;
        
        // Update active nav button
        event?.target?.classList.add('active');
        
        // Voice feedback for navigation
        if (typeof announceNavigationChange === 'function') {
            announceNavigationChange(sectionId);
        }
        
        // Load section-specific data
        loadSectionData(sectionId);
    }
}

/**
 * Show brand-specific section
 */
function showBrandSection(brandCode) {
    const sectionId = `brand-${brandCode}`;
    showSection(sectionId);
    loadBrandData(brandCode);
}

/**
 * Load data for specific section
 */
async function loadSectionData(sectionId) {
    switch (sectionId) {
        case 'overview':
            await loadOverviewData();
            break;
        case 'fortianalyzer':
            await loadFortiAnalyzerData();
            break;
        case 'webfilters':
            await loadWebFiltersData();
            break;
        case 'log-analysis':
            // Log analysis section is form-based, no initial data load needed
            break;
        case 'fortimanager':
            await loadFortiManagerData();
            break;
        case 'devices':
            await loadDevicesData();
            break;
        default:
            if (sectionId.startsWith('brand-')) {
                const brandCode = sectionId.replace('brand-', '');
                await loadBrandData(brandCode);
            }
            break;
    }
}

/**
 * Load overview dashboard data
 */
async function loadOverviewData() {
    try {
        showLoading(true);
        
        // Load supported brands
        const brandsResponse = await apiCall('/api/brands');
        if (brandsResponse.success) {
            updateBrandsGrid(brandsResponse.data);
        }
        
        // Load FortiManager instances for stats
        const fmResponse = await apiCall('/api/fortimanager');
        if (fmResponse.success) {
            updateStatsGrid(fmResponse.data);
        }
        
        showLoading(false);
    } catch (error) {
        showLoading(false);
        showToast('Failed to load overview data', 'error');
        console.error('Error loading overview:', error);
    }
}

/**
 * Update statistics grid
 */
function updateStatsGrid(data) {
    // Extract real data from FortiManager instances
    if (data && data.fortimanager_instances) {
        let totalDevices = 0;
        let onlineDevices = 0;
        
        data.fortimanager_instances.forEach(fm => {
            // Count devices from each FortiManager if device data is available
            if (fm.managed_devices) {
                totalDevices += fm.managed_devices.length || 0;
                onlineDevices += fm.managed_devices.filter(d => d.status === 'online').length || 0;
            }
        });
        
        document.getElementById('totalStores').textContent = totalDevices.toString();
        document.getElementById('healthyDevices').textContent = onlineDevices.toString();
        
        // Set placeholders for metrics we don't have yet
        document.getElementById('securityEvents').textContent = '-';
        document.getElementById('blockedUrls').textContent = '-';
    } else {
        // No data available - show dashes instead of fake numbers
        document.getElementById('totalStores').textContent = '-';
        document.getElementById('securityEvents').textContent = '-';
        document.getElementById('blockedUrls').textContent = '-';
        document.getElementById('healthyDevices').textContent = '-';
    }
}

/**
 * Update brands grid with supported brands
 */
function updateBrandsGrid(brandsData) {
    const brandsGrid = document.getElementById('brandsGrid');
    if (!brandsGrid || !brandsData.supported_restaurant_brands) return;
    
    brandsGrid.innerHTML = '';
    
    brandsData.supported_restaurant_brands.forEach(brand => {
        const brandCard = createBrandCard(brand);
        brandsGrid.appendChild(brandCard);
    });
}

/**
 * Create brand card element
 */
function createBrandCard(brand) {
    const card = document.createElement('div');
    card.className = `brand-card brand-${brand.brand_code.toLowerCase()}`;
    
    const iconMap = {
        'BWW': 'fas fa-utensils',
        'ARBYS': 'fas fa-hamburger', 
        'SONIC': 'fas fa-car'
    };
    
    card.innerHTML = `
        <div class="brand-header">
            <div class="brand-icon">
                <i class="${iconMap[brand.brand_code] || 'fas fa-store'}"></i>
            </div>
            <div>
                <h3 class="brand-title">${brand.name}</h3>
                <div class="brand-subtitle">${brand.description}</div>
            </div>
        </div>
        <div class="brand-metrics">
            <div class="brand-metric">
                <span class="brand-metric-value" id="${brand.brand_code}-stores">-</span>
                <span class="brand-metric-label">Stores</span>
            </div>
            <div class="brand-metric">
                <span class="brand-metric-value" id="${brand.brand_code}-events">-</span>
                <span class="brand-metric-label">Events</span>
            </div>
        </div>
        <div style="margin-top: 1rem;">
            <button class="btn btn-primary" onclick="showBrandSection('${brand.brand_code}')">
                <i class="fas fa-arrow-right"></i>
                View Details
            </button>
        </div>
    `;
    
    return card;
}

/**
 * Load brand-specific data
 */
async function loadBrandData(brandCode) {
    try {
        showLoading(true);
        
        const response = await apiCall(`/api/brands/${brandCode}/overview`);
        
        if (response.success) {
            updateBrandContent(brandCode, response.data);
        } else {
            showToast(`Failed to load ${brandCode} data`, 'error');
        }
        
        showLoading(false);
    } catch (error) {
        showLoading(false);
        showToast(`Error loading ${brandCode} data`, 'error');
        console.error(`Error loading brand ${brandCode}:`, error);
    }
}

/**
 * Update brand content section
 */
function updateBrandContent(brandCode, data) {
    const contentElement = document.getElementById(`brand-${brandCode}-content`);
    if (!contentElement) return;
    
    const brandInfo = data.brand_summary;
    const infraStatus = data.infrastructure_status;
    const securityOverview = data.security_overview;
    
    contentElement.innerHTML = `
        <div class="security-grid">
            <div class="security-card">
                <h3><i class="fas fa-info-circle"></i> Brand Information</h3>
                <div class="brand-info">
                    <p><strong>Brand:</strong> ${brandInfo.brand}</p>
                    <p><strong>Device Prefix:</strong> ${brandInfo.device_prefix}</p>
                    <p><strong>FortiManager:</strong> ${brandInfo.fortimanager}</p>
                    <p><strong>Status:</strong> ${brandInfo.fortimanager_configured ? 
                        '<span style="color: var(--success-color);">Configured</span>' : 
                        '<span style="color: var(--error-color);">Not Configured</span>'}</p>
                </div>
            </div>
            
            <div class="security-card">
                <h3><i class="fas fa-server"></i> Infrastructure Status</h3>
                <div class="infrastructure-status">
                    <p><strong>FortiManager Host:</strong> ${infraStatus.fortimanager_host}</p>
                    <p><strong>Total Devices:</strong> ${infraStatus.total_managed_devices}</p>
                    <p><strong>Online:</strong> ${infraStatus.online_devices}</p>
                    <p><strong>Offline:</strong> ${infraStatus.offline_devices}</p>
                </div>
            </div>
            
            <div class="security-card">
                <h3><i class="fas fa-shield-alt"></i> Security Overview</h3>
                <div class="security-overview">
                    <p><strong>Last Policy Update:</strong> ${new Date(securityOverview.last_policy_update).toLocaleDateString()}</p>
                    <p><strong>Active Policies:</strong> ${securityOverview.active_security_policies}</p>
                    <p><strong>Recent Events:</strong> ${securityOverview.recent_security_events}</p>
                    <p><strong>Compliance:</strong> ${securityOverview.compliance_status}</p>
                </div>
            </div>
        </div>
        
        <div style="margin-top: 2rem;">
            <h3>Quick Actions</h3>
            <div class="form-actions">
                <button class="btn btn-primary" onclick="quickInvestigation('${brandCode}')">
                    <i class="fas fa-search"></i>
                    Quick Store Investigation
                </button>
                <button class="btn btn-primary" onclick="viewFortiManager('${brandCode}')">
                    <i class="fas fa-shield-alt"></i>
                    View FortiManager
                </button>
            </div>
        </div>
    `;
    
    if (data.configuration_warning) {
        const warning = document.createElement('div');
        warning.className = 'toast warning';
        warning.innerHTML = `<i class="fas fa-exclamation-triangle"></i><span>${data.configuration_warning}</span>`;
        contentElement.insertBefore(warning, contentElement.firstChild);
    }
}

/**
 * Run store investigation
 */
async function runInvestigation() {
    const brand = document.getElementById('investigationBrand').value;
    const storeId = document.getElementById('investigationStore').value;
    const period = document.getElementById('investigationPeriod').value;
    
    if (!brand || !storeId) {
        showToast('Please select brand and enter store ID', 'warning');
        return;
    }
    
    try {
        showLoading(true, 'Investigating store...');
        
        // Show results section
        const resultsSection = document.getElementById('investigationResults');
        resultsSection.style.display = 'block';
        
        // Update store info
        const storeInfo = document.getElementById('storeInfo');
        const deviceName = `IBR-${brand}-${storeId.padStart(5, '0')}`;
        storeInfo.innerHTML = `
            <div><strong>Brand:</strong> ${brand}</div>
            <div><strong>Store ID:</strong> ${storeId}</div>
            <div><strong>Device:</strong> ${deviceName}</div>
            <div><strong>Period:</strong> ${period}</div>
        `;
        
        // Load security health
        const healthResponse = await apiCall(`/api/stores/${brand}/${storeId}/security?recommendations=true`);
        if (healthResponse.success) {
            updateSecurityHealthTab(healthResponse.data);
        }
        
        // Load URL blocking analysis
        const blockingResponse = await apiCall(`/api/stores/${brand}/${storeId}/url-blocking?period=${period}&export=true`);
        if (blockingResponse.success) {
            updateUrlBlockingTab(blockingResponse.data);
        }
        
        // Load security events
        const eventsResponse = await apiCall(`/api/devices/${deviceName}/security-events?timeframe=${period}&top_count=20`);
        if (eventsResponse.success) {
            updateSecurityEventsTab(eventsResponse.data);
        }
        
        showLoading(false);
        showToast('Investigation completed successfully', 'success');
        
    } catch (error) {
        showLoading(false);
        showToast('Investigation failed', 'error');
        console.error('Investigation error:', error);
    }
}

/**
 * Update security health tab
 */
function updateSecurityHealthTab(data) {
    const tabContent = document.getElementById('security-health');
    const healthData = data.store_security_health;
    const metrics = data.security_metrics;
    
    // Calculate score class
    const score = healthData.security_score;
    let scoreClass = 'score-poor';
    if (score >= 90) scoreClass = 'score-excellent';
    else if (score >= 80) scoreClass = 'score-good';
    else if (score >= 70) scoreClass = 'score-warning';
    
    tabContent.innerHTML = `
        <div class="security-grid">
            <div class="security-card">
                <h3><i class="fas fa-heartbeat"></i> Overall Health</h3>
                <div class="security-score">
                    <div class="score-circle ${scoreClass}">${score}</div>
                    <div>
                        <div><strong>Status:</strong> ${healthData.overall_status}</div>
                        <div><strong>Last Assessment:</strong> ${new Date(healthData.last_assessment).toLocaleString()}</div>
                    </div>
                </div>
            </div>
            
            <div class="security-card">
                <h3><i class="fas fa-shield-alt"></i> Security Metrics</h3>
                <div class="metrics-list">
                    <div><strong>Firewall:</strong> ${metrics.firewall_policies.status}</div>
                    <div><strong>Antivirus:</strong> ${metrics.antivirus_status.status}</div>
                    <div><strong>IPS:</strong> ${metrics.ips_protection.status}</div>
                    <div><strong>Web Filter:</strong> ${metrics.web_filtering.status}</div>
                    <div><strong>VPN:</strong> ${metrics.vpn_tunnels.status}</div>
                </div>
            </div>
            
            <div class="security-card">
                <h3><i class="fas fa-exclamation-circle"></i> Recent Activity</h3>
                <div class="activity-summary">
                    <div><strong>Threats Blocked (24h):</strong> ${data.recent_activity.threats_blocked_24h}</div>
                    <div><strong>Policy Violations:</strong> ${data.recent_activity.policy_violations_24h}</div>
                    <div><strong>System Alerts:</strong> ${data.recent_activity.system_alerts}</div>
                    <div><strong>Config Changes:</strong> ${data.recent_activity.configuration_changes}</div>
                </div>
            </div>
        </div>
    `;
    
    if (data.recommendations && data.recommendations.length > 0) {
        const recommendationsDiv = document.createElement('div');
        recommendationsDiv.className = 'security-card';
        recommendationsDiv.innerHTML = `
            <h3><i class="fas fa-lightbulb"></i> Recommendations</h3>
            <ul class="recommendations">
                ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        `;
        tabContent.appendChild(recommendationsDiv);
    }
}

/**
 * Update URL blocking tab
 */
function updateUrlBlockingTab(data) {
    const tabContent = document.getElementById('url-blocking');
    const analysis = data.store_analysis;
    const blocking = data.blocking_summary;
    
    tabContent.innerHTML = `
        <div class="security-grid">
            <div class="security-card">
                <h3><i class="fas fa-ban"></i> Blocking Summary</h3>
                <div class="blocking-stats">
                    <div><strong>Total Blocked URLs:</strong> ${blocking.total_blocked_urls}</div>
                    <div><strong>Unique Domains:</strong> ${blocking.unique_domains}</div>
                    <div><strong>Repeat Violations:</strong> ${blocking.repeat_violations}</div>
                </div>
            </div>
            
            <div class="security-card">
                <h3><i class="fas fa-chart-bar"></i> Policy Categories</h3>
                <div class="categories-list">
                    ${Object.entries(blocking.policy_categories).map(([category, count]) => 
                        `<div><strong>${category.replace('_', ' ').toUpperCase()}:</strong> ${count}</div>`
                    ).join('')}
                </div>
            </div>
            
            <div class="security-card">
                <h3><i class="fas fa-globe"></i> Top Blocked Patterns</h3>
                <div class="blocked-patterns">
                    ${data.top_blocked_patterns.map(pattern => 
                        `<div><strong>${pattern.domain}</strong> (${pattern.category}): ${pattern.block_count} blocks</div>`
                    ).join('')}
                </div>
            </div>
        </div>
    `;
    
    if (data.user_behavior_insights && data.user_behavior_insights.length > 0) {
        const insightsDiv = document.createElement('div');
        insightsDiv.className = 'security-card';
        insightsDiv.innerHTML = `
            <h3><i class="fas fa-eye"></i> User Behavior Insights</h3>
            <ul class="recommendations">
                ${data.user_behavior_insights.map(insight => `<li>${insight}</li>`).join('')}
            </ul>
        `;
        tabContent.appendChild(insightsDiv);
    }
    
    if (data.detailed_report_exported) {
        const exportDiv = document.createElement('div');
        exportDiv.className = 'security-card';
        exportDiv.innerHTML = `
            <h3><i class="fas fa-download"></i> Detailed Report</h3>
            <p>Full report exported to: <code>${data.detailed_report_exported}</code></p>
        `;
        tabContent.appendChild(exportDiv);
    }
}

/**
 * Update security events tab
 */
function updateSecurityEventsTab(data) {
    const tabContent = document.getElementById('security-events');
    const summary = data.executive_summary;
    const events = data.top_security_events;
    
    tabContent.innerHTML = `
        <div class="security-grid">
            <div class="security-card">
                <h3><i class="fas fa-exclamation-triangle"></i> Executive Summary</h3>
                <div class="events-summary">
                    <div><strong>Total Events:</strong> ${summary.total_events}</div>
                    <div><strong>Critical Alerts:</strong> ${summary.critical_alerts}</div>
                    <div><strong>Blocked Threats:</strong> ${summary.blocked_threats}</div>
                    <div><strong>Policy Violations:</strong> ${summary.policy_violations}</div>
                </div>
            </div>
            
            <div class="security-card">
                <h3><i class="fas fa-list"></i> Top Security Events</h3>
                <div class="events-list">
                    ${events.map(event => `
                        <div class="event-item">
                            <strong>${event.type.toUpperCase()}:</strong> ${event.count} events
                            ${event.top_blocked_url ? `<br><small>Top blocked: ${event.top_blocked_url}</small>` : ''}
                            ${event.top_signature ? `<br><small>Top signature: ${event.top_signature}</small>` : ''}
                            ${event.top_malware ? `<br><small>Top malware: ${event.top_malware}</small>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    if (data.recommendations && data.recommendations.length > 0) {
        const recommendationsDiv = document.createElement('div');
        recommendationsDiv.className = 'security-card';
        recommendationsDiv.innerHTML = `
            <h3><i class="fas fa-lightbulb"></i> Recommendations</h3>
            <ul class="recommendations">
                ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        `;
        tabContent.appendChild(recommendationsDiv);
    }
}

/**
 * Show investigation tab
 */
function showTab(tabId) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Show selected tab
    const tab = document.getElementById(tabId);
    if (tab) {
        tab.classList.add('active');
        event.target.classList.add('active');
    }
}

/**
 * Load FortiManager data
 */
async function loadFortiManagerData() {
    try {
        showLoading(true);
        
        const response = await apiCall('/api/fortimanager');
        
        if (response.success) {
            updateFortiManagerContent(response.data);
        }
        
        showLoading(false);
    } catch (error) {
        showLoading(false);
        showToast('Failed to load FortiManager data', 'error');
        console.error('Error loading FortiManager:', error);
    }
}

/**
 * Update FortiManager content
 */
function updateFortiManagerContent(data) {
    const content = document.getElementById('fortimanagerContent');
    if (!content) return;
    
    content.innerHTML = `
        <div class="security-grid">
            ${data.fortimanager_instances.map(fm => `
                <div class="security-card">
                    <h3><i class="fas fa-shield-alt"></i> ${fm.name}</h3>
                    <div class="fm-info">
                        <p><strong>Host:</strong> ${fm.host}</p>
                        <p><strong>Description:</strong> ${fm.description}</p>
                    </div>
                    <div class="form-actions" style="margin-top: 1rem;">
                        <button class="btn btn-primary" onclick="viewFortiManagerDevices('${fm.name}')">
                            <i class="fas fa-router"></i>
                            View Devices
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Utility Functions
 */

// API call wrapper
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        });
        
        const data = await response.json();
        
        // Check if response is successful
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${data.error || response.statusText}`);
        }
        
        // Check if the API returned an error in the response body
        if (data.success === false) {
            throw new Error(data.error || 'API request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Show/hide loading overlay
function showLoading(show, text = 'Processing...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = overlay.querySelector('.loading-text');
    
    if (show) {
        loadingText.textContent = text;
        overlay.classList.add('show');
        
        // Voice feedback for loading states
        if (typeof announceLoading === 'function') {
            announceLoading(text);
        }
    } else {
        overlay.classList.remove('show');
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const iconMap = {
        success: 'fas fa-check-circle',
        warning: 'fas fa-exclamation-triangle',
        error: 'fas fa-times-circle',
        info: 'fas fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="${iconMap[type]}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Voice feedback for important toasts
    if (typeof announceToast === 'function') {
        announceToast(message, type);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (container.contains(toast)) {
            container.removeChild(toast);
        }
    }, 5000);
}

// Refresh current section data
function refreshCurrentSection() {
    if (connectionStatus === 'connected') {
        loadSectionData(currentSection);
    }
}

// Refresh all data
async function refreshData() {
    showToast('Refreshing data...', 'info');
    await loadSectionData(currentSection);
}

// Quick investigation helper
function quickInvestigation(brand) {
    showSection('investigation');
    document.getElementById('investigationBrand').value = brand;
}

// View FortiManager helper
function viewFortiManager(brand) {
    showSection('fortimanager');
}

// View FortiManager devices
async function viewFortiManagerDevices(fmName) {
    try {
        showLoading(true, `Loading ${fmName} devices...`);
        
        const response = await apiCall(`/api/fortimanager/${fmName}/devices`);
        
        if (response.success) {
            // Show devices in a modal or dedicated section
            showToast(`Loaded ${response.data.device_count || 0} devices from ${fmName}`, 'success');
        }
        
        showLoading(false);
    } catch (error) {
        showLoading(false);
        showToast(`Failed to load ${fmName} devices`, 'error');
        console.error(`Error loading ${fmName} devices:`, error);
    }
}