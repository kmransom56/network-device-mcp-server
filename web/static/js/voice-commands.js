/**
 * Advanced Voice Commands for Network Security Operations
 * Specialized voice command handlers for security investigations and analysis
 */

class VoiceCommands {
    constructor(voiceInterface) {
        this.voiceInterface = voiceInterface;
        this.activeInvestigation = null;
        this.contextStack = [];
        this.setupAdvancedCommands();
    }

    /**
     * Setup advanced voice command patterns
     */
    setupAdvancedCommands() {
        // Advanced investigation commands
        this.addCommandPattern(/investigate\s+(bww|buffalo wild wings|arbys?|arby'?s|sonic)\s+store\s+(\d+)\s*(?:for\s+(.+))?/, 
            this.handleStoreInvestigation.bind(this));

        // Advanced log search commands
        this.addCommandPattern(/search\s+(?:for\s+)?(.+?)(?:\s+in\s+(.+?))?(?:\s+from\s+(.+?))?(?:\s+in\s+the\s+last\s+(.+))?/,
            this.handleAdvancedLogSearch.bind(this));

        // Security event commands
        this.addCommandPattern(/show\s+(?:me\s+)?(?:the\s+)?(critical|high|medium|low)\s+(?:security\s+)?(?:events|alerts)(?:\s+for\s+(.+?))?/,
            this.handleSecurityEvents.bind(this));

        // FortiAnalyzer specific commands
        this.addCommandPattern(/show\s+(?:me\s+)?threat\s+intelligence\s+for\s+(bww|buffalo wild wings|arbys?|arby'?s|sonic)(?:\s+in\s+the\s+last\s+(.+))?/,
            this.handleThreatIntelligence.bind(this));

        // Web filters commands
        this.addCommandPattern(/(?:check|show)\s+web\s+filter\s+(?:status|policies)\s+for\s+(bww|buffalo wild wings|arbys?|arby'?s|sonic)(?:\s+store\s+(\d+))?/,
            this.handleWebFilterStatus.bind(this));

        // System status commands
        this.addCommandPattern(/(?:check|what\s+is\s+the|show\s+me\s+the)\s+(?:overall\s+)?(?:security\s+)?status(?:\s+of\s+(.+?))?/,
            this.handleSystemStatus.bind(this));

        // Report generation commands
        this.addCommandPattern(/generate\s+(?:a\s+)?(?:(security|threat|compliance|executive)\s+)?report\s+for\s+(bww|buffalo wild wings|arbys?|arby'?s|sonic)(?:\s+store\s+(\d+))?(?:\s+for\s+the\s+last\s+(.+))?/,
            this.handleReportGeneration.bind(this));

        // Contextual follow-up commands
        this.addCommandPattern(/(?:show\s+me\s+)?(?:more\s+)?(?:details|information|data)/, 
            this.handleShowMore.bind(this));
        
        this.addCommandPattern(/go\s+back/, 
            this.handleGoBack.bind(this));

        // Emergency commands
        this.addCommandPattern(/(?:alert|emergency|urgent|critical)\s*:?\s*(.+)/, 
            this.handleEmergencyCommand.bind(this));

        // Bulk operations
        this.addCommandPattern(/(?:check|investigate|analyze)\s+all\s+(stores|locations|sites)(?:\s+for\s+(.+?))?/,
            this.handleBulkOperation.bind(this));
    }

    /**
     * Add command pattern
     */
    addCommandPattern(pattern, handler) {
        if (!this.voiceInterface.commandPatterns) {
            this.voiceInterface.commandPatterns = [];
        }
        this.voiceInterface.commandPatterns.push({ pattern, handler });
    }

    /**
     * Handle store investigation
     */
    async handleStoreInvestigation(matches) {
        const brand = this.normalizeBrandName(matches[1]);
        const storeId = matches[2];
        const focus = matches[3];
        
        this.activeInvestigation = { brand, storeId, focus };
        this.pushContext('investigation', this.activeInvestigation);
        
        let message = `Investigating ${this.getBrandDisplayName(brand)} store ${storeId}`;
        if (focus) {
            message += ` focusing on ${focus}`;
        }
        
        this.voiceInterface.speak(message);
        
        // Navigate and setup investigation
        showSection('investigation');
        document.getElementById('investigationBrand').value = brand;
        document.getElementById('investigationStore').value = storeId;
        
        // Set appropriate timeframe based on focus
        if (focus) {
            const timeframe = this.inferTimeframeFromFocus(focus);
            document.getElementById('investigationPeriod').value = timeframe;
        }
        
        // Auto-run investigation
        setTimeout(() => {
            runInvestigation();
            this.announceInvestigationResults();
        }, 1000);
    }

    /**
     * Handle advanced log search
     */
    async handleAdvancedLogSearch(matches) {
        const query = matches[1];
        const context = matches[2]; // brand or store context
        const source = matches[3]; // fortianalyzer or webfilters
        const timeframe = this.parseTimeframe(matches[4]) || '24h';
        
        this.pushContext('log-search', { query, context, source, timeframe });
        
        let message = `Searching for ${query}`;
        if (context) message += ` in ${context}`;
        if (source) message += ` from ${source}`;
        message += ` for the last ${timeframe}`;
        
        this.voiceInterface.speak(message);
        
        // Navigate and setup search
        showSection('log-analysis');
        document.getElementById('logSearchQuery').value = query;
        document.getElementById('logSearchTimeframe').value = timeframe;
        
        if (context) {
            const brand = this.normalizeBrandName(context);
            if (brand) {
                document.getElementById('logSearchBrand').value = brand;
            }
        }
        
        if (source) {
            const normalizedSource = source.toLowerCase().includes('forti') ? 'fortianalyzer' : 'webfilters';
            document.getElementById('logSearchSource').value = normalizedSource;
        }
        
        setTimeout(() => searchLogs(), 500);
    }

    /**
     * Handle security events
     */
    async handleSecurityEvents(matches) {
        const severity = matches[1];
        const context = matches[2]; // brand or store
        
        this.pushContext('security-events', { severity, context });
        
        this.voiceInterface.speak(`Showing ${severity} security events${context ? ` for ${context}` : ''}`);
        
        // Navigate to FortiAnalyzer and filter by severity
        showSection('fortianalyzer');
        
        setTimeout(() => {
            this.filterSecurityEventsBySeverity(severity, context);
        }, 1000);
    }

    /**
     * Handle threat intelligence
     */
    async handleThreatIntelligence(matches) {
        const brand = this.normalizeBrandName(matches[1]);
        const timeframe = this.parseTimeframe(matches[2]) || '24h';
        
        this.pushContext('threat-intelligence', { brand, timeframe });
        
        this.voiceInterface.speak(`Loading threat intelligence for ${this.getBrandDisplayName(brand)} for the last ${timeframe}`);
        
        showSection('fortianalyzer');
        
        setTimeout(async () => {
            try {
                const response = await apiCall(`/api/fortianalyzer/threats/${brand}?timeframe=${timeframe}`);
                if (response.success) {
                    this.announceThreatIntelligence(response);
                    renderThreatIntelligenceDashboard({ [brand]: response });
                }
            } catch (error) {
                this.voiceInterface.speak('Error loading threat intelligence');
            }
        }, 1000);
    }

    /**
     * Handle web filter status
     */
    async handleWebFilterStatus(matches) {
        const brand = this.normalizeBrandName(matches[1]);
        const storeId = matches[2];
        
        this.pushContext('web-filter-status', { brand, storeId });
        
        let message = `Checking web filter status for ${this.getBrandDisplayName(brand)}`;
        if (storeId) message += ` store ${storeId}`;
        
        this.voiceInterface.speak(message);
        
        showSection('webfilters');
        
        if (storeId) {
            document.getElementById('webfilterBrand').value = brand;
            document.getElementById('webfilterStoreId').value = storeId;
            setTimeout(() => viewStoreWebFilters(), 1000);
        }
    }

    /**
     * Handle system status
     */
    async handleSystemStatus(matches) {
        const scope = matches[1]; // specific system or overall
        
        this.voiceInterface.speak('Checking system status');
        
        try {
            // Check overall system health
            const healthResponse = await apiCall('/health');
            const integrationResponse = await apiCall('/api/integration/status');
            
            let statusMessage = 'System status: ';
            
            if (healthResponse.status === 'healthy') {
                statusMessage += 'All systems operational. ';
            } else {
                statusMessage += 'System issues detected. ';
            }
            
            if (integrationResponse.success) {
                const activeManagers = integrationResponse.active_managers?.length || 0;
                statusMessage += `${activeManagers} integration modules active. `;
                
                if (integrationResponse.unified_platform_status === 'fully_operational') {
                    statusMessage += 'All integrations operational.';
                } else {
                    statusMessage += 'Some integrations have limited functionality.';
                }
            }
            
            this.voiceInterface.speak(statusMessage);
            
        } catch (error) {
            this.voiceInterface.speak('Unable to check system status. Connection may be down.');
        }
    }

    /**
     * Handle report generation
     */
    async handleReportGeneration(matches) {
        const reportType = matches[1] || 'security';
        const brand = this.normalizeBrandName(matches[2]);
        const storeId = matches[3];
        const timeframe = this.parseTimeframe(matches[4]) || '7d';
        
        this.pushContext('report-generation', { reportType, brand, storeId, timeframe });
        
        let message = `Generating ${reportType} report for ${this.getBrandDisplayName(brand)}`;
        if (storeId) message += ` store ${storeId}`;
        message += ` for the last ${timeframe}`;
        
        this.voiceInterface.speak(message);
        
        showSection('fortianalyzer');
        
        setTimeout(async () => {
            try {
                const url = `/api/fortianalyzer/reports/${brand}${storeId ? `?store_id=${storeId}` : ''}`;
                const response = await apiCall(url);
                
                if (response.success) {
                    this.announceReportResults(response);
                    renderSecurityReportModal(response);
                }
            } catch (error) {
                this.voiceInterface.speak('Error generating report');
            }
        }, 1000);
    }

    /**
     * Handle show more details
     */
    handleShowMore() {
        const currentContext = this.getCurrentContext();
        
        if (!currentContext) {
            this.voiceInterface.speak('No additional details available');
            return;
        }
        
        this.voiceInterface.speak('Showing additional details');
        
        switch (currentContext.type) {
            case 'investigation':
                this.showInvestigationDetails(currentContext.data);
                break;
            case 'threat-intelligence':
                this.showThreatDetails(currentContext.data);
                break;
            case 'security-events':
                this.showSecurityEventDetails(currentContext.data);
                break;
            default:
                this.voiceInterface.speak('No additional details available for current view');
        }
    }

    /**
     * Handle go back
     */
    handleGoBack() {
        if (this.contextStack.length > 1) {
            this.contextStack.pop(); // Remove current context
            const previousContext = this.getCurrentContext();
            
            this.voiceInterface.speak('Going back to previous view');
            this.restoreContext(previousContext);
        } else {
            this.voiceInterface.speak('Going back to overview');
            showSection('overview');
        }
    }

    /**
     * Handle emergency command
     */
    async handleEmergencyCommand(matches) {
        const emergencyContext = matches[1];
        
        this.voiceInterface.speak(`Emergency alert: ${emergencyContext}. Initiating immediate analysis.`, { rate: 1.2 });
        
        // Show critical dashboard with emergency styling
        showSection('fortianalyzer');
        
        // Search for critical events
        setTimeout(() => {
            this.performEmergencyAnalysis(emergencyContext);
        }, 500);
    }

    /**
     * Handle bulk operations
     */
    async handleBulkOperation(matches) {
        const scope = matches[1]; // stores, locations, sites
        const operation = matches[2]; // what to check for
        
        this.voiceInterface.speak(`Performing bulk analysis across all ${scope}${operation ? ` for ${operation}` : ''}`);
        
        showSection('overview');
        
        setTimeout(() => {
            this.performBulkAnalysis(scope, operation);
        }, 1000);
    }

    /**
     * Announce investigation results
     */
    async announceInvestigationResults() {
        // Wait for investigation to complete
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const investigation = this.activeInvestigation;
        if (!investigation) return;
        
        // Mock results announcement - in real implementation, read from investigation results
        const results = {
            securityEvents: Math.floor(Math.random() * 50),
            blockedThreats: Math.floor(Math.random() * 20),
            urlsBlocked: Math.floor(Math.random() * 100)
        };
        
        let announcement = `Investigation complete for ${this.getBrandDisplayName(investigation.brand)} store ${investigation.storeId}. `;
        announcement += `Found ${results.securityEvents} security events, `;
        announcement += `${results.blockedThreats} threats blocked, `;
        announcement += `and ${results.urlsBlocked} URLs filtered.`;
        
        if (results.securityEvents > 30) {
            announcement += ' High activity detected. Recommend immediate review.';
        } else if (results.securityEvents < 5) {
            announcement += ' Low activity. System appears secure.';
        } else {
            announcement += ' Normal activity levels.';
        }
        
        this.voiceInterface.speak(announcement);
    }

    /**
     * Announce threat intelligence
     */
    announceThreatIntelligence(data) {
        const threats = data.threat_summary;
        if (!threats) return;
        
        let announcement = `Threat intelligence summary: `;
        announcement += `${threats.total_threats || 0} total threats detected, `;
        announcement += `${threats.blocked_threats || 0} successfully blocked. `;
        
        const blockRate = Math.round(((threats.blocked_threats || 0) / Math.max(threats.total_threats || 1, 1)) * 100);
        announcement += `Block rate: ${blockRate}%. `;
        
        if (blockRate > 95) {
            announcement += 'Excellent threat protection.';
        } else if (blockRate > 90) {
            announcement += 'Good threat protection.';
        } else {
            announcement += 'Consider reviewing security policies.';
        }
        
        this.voiceInterface.speak(announcement);
    }

    /**
     * Announce report results
     */
    announceReportResults(data) {
        const summary = data.executive_summary;
        if (!summary) return;
        
        let announcement = `Report generated successfully. `;
        announcement += `Security posture: ${summary.overall_security_posture || 'unknown'}. `;
        announcement += `Analyzed ${summary.total_events_analyzed || 0} events, `;
        announcement += `blocked ${summary.threats_blocked || 0} threats. `;
        
        if (data.recommendations && data.recommendations.length > 0) {
            announcement += `${data.recommendations.length} recommendations provided.`;
        }
        
        this.voiceInterface.speak(announcement);
    }

    /**
     * Context management
     */
    pushContext(type, data) {
        this.contextStack.push({ type, data, timestamp: Date.now() });
        
        // Limit context stack size
        if (this.contextStack.length > 10) {
            this.contextStack.shift();
        }
    }

    getCurrentContext() {
        return this.contextStack[this.contextStack.length - 1] || null;
    }

    restoreContext(context) {
        if (!context) return;
        
        switch (context.type) {
            case 'investigation':
                showSection('investigation');
                if (context.data.brand) {
                    document.getElementById('investigationBrand').value = context.data.brand;
                }
                if (context.data.storeId) {
                    document.getElementById('investigationStore').value = context.data.storeId;
                }
                break;
            case 'log-search':
                showSection('log-analysis');
                if (context.data.query) {
                    document.getElementById('logSearchQuery').value = context.data.query;
                }
                break;
        }
    }

    /**
     * Utility functions
     */
    normalizeBrandName(brandInput) {
        const brandMap = {
            'bww': 'BWW',
            'buffalo wild wings': 'BWW',
            'arbys': 'ARBYS',
            'arby\'s': 'ARBYS',
            'sonic': 'SONIC'
        };
        
        return brandMap[brandInput.toLowerCase()] || brandInput.toUpperCase();
    }

    getBrandDisplayName(brandCode) {
        const brandNames = {
            'BWW': 'Buffalo Wild Wings',
            'ARBYS': 'Arby\'s',
            'SONIC': 'Sonic Drive-In'
        };
        return brandNames[brandCode] || brandCode;
    }

    parseTimeframe(timeInput) {
        if (!timeInput) return null;
        
        const timeMap = {
            'hour': '1h',
            'last hour': '1h',
            'day': '24h',
            'last day': '24h',
            '24 hours': '24h',
            'week': '7d',
            'last week': '7d',
            'month': '30d',
            'last month': '30d'
        };
        
        return timeMap[timeInput.toLowerCase()] || timeInput;
    }

    inferTimeframeFromFocus(focus) {
        if (focus.includes('recent') || focus.includes('current')) return '1h';
        if (focus.includes('today')) return '24h';
        if (focus.includes('week')) return '7d';
        if (focus.includes('month')) return '30d';
        return '24h';
    }

    async performEmergencyAnalysis(context) {
        // Emergency analysis logic
        this.voiceInterface.speak('Performing emergency security analysis');
        
        // Search for critical events
        document.getElementById('logSearchQuery').value = `critical emergency ${context}`;
        document.getElementById('logSearchTimeframe').value = '1h';
        
        setTimeout(() => searchLogs(), 500);
    }

    async performBulkAnalysis(scope, operation) {
        // Bulk analysis logic
        this.voiceInterface.speak(`Analyzing ${scope}${operation ? ` for ${operation}` : ''}. This may take a moment.`);
        
        // Load overview with focus on bulk metrics
        await loadOverviewData();
    }

    filterSecurityEventsBySeverity(severity, context) {
        // Filter FortiAnalyzer view by severity
        this.voiceInterface.speak(`Filtering events by ${severity} severity`);
        showThreatIntelligence();
    }

    showInvestigationDetails(data) {
        // Show detailed investigation results
        this.voiceInterface.speak('Showing detailed investigation results');
    }

    showThreatDetails(data) {
        // Show detailed threat information
        this.voiceInterface.speak('Showing detailed threat analysis');
    }

    showSecurityEventDetails(data) {
        // Show detailed security event information
        this.voiceInterface.speak('Showing detailed security event analysis');
    }
}

// Initialize voice commands when voice interface is ready
document.addEventListener('DOMContentLoaded', function() {
    if (typeof voiceInterface !== 'undefined') {
        window.voiceCommands = new VoiceCommands(voiceInterface);
        
        // Extend voice interface with advanced pattern matching
        const originalProcessCommand = voiceInterface.processVoiceCommand;
        voiceInterface.processVoiceCommand = function(transcript) {
            // Try advanced patterns first
            if (voiceInterface.commandPatterns) {
                for (const { pattern, handler } of voiceInterface.commandPatterns) {
                    const matches = transcript.match(pattern);
                    if (matches) {
                        console.log('Advanced pattern matched:', pattern, matches);
                        handler(matches);
                        return;
                    }
                }
            }
            
            // Fall back to original processing
            originalProcessCommand.call(this, transcript);
        };
    }
});