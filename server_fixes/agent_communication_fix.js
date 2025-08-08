"""
Fix for Agent Communication Display on Server
Add this to your dashboard.html or update existing JavaScript
"""

// Enhanced Agent Communication Handler
const AgentCommunication = {
    container: null,
    messages: [],
    isConnected: false,
    
    init() {
        this.container = document.getElementById('agent-messages-container');
        if (!this.container) {
            console.error('Agent messages container not found');
            return;
        }
        
        // Add connection status indicator
        this.addStatusIndicator();
        
        // Initialize WebSocket with fallback
        this.initWebSocket();
        
        // Also listen for messages from analysis results
        this.listenForAnalysisResults();
    },
    
    addStatusIndicator() {
        const statusHtml = `
            <div class="connection-status" id="ws-connection-status">
                <span class="status-icon">●</span>
                <span class="status-text">Connecting...</span>
            </div>
        `;
        this.container.insertAdjacentHTML('beforebegin', statusHtml);
    },
    
    updateStatus(connected) {
        const statusEl = document.getElementById('ws-connection-status');
        if (statusEl) {
            const icon = statusEl.querySelector('.status-icon');
            const text = statusEl.querySelector('.status-text');
            
            if (connected) {
                icon.style.color = '#10b981';
                text.textContent = 'Connected';
            } else {
                icon.style.color = '#ef4444';
                text.textContent = 'Disconnected';
            }
        }
    },
    
    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('Agent communication WebSocket connected');
                this.isConnected = true;
                this.updateStatus(true);
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'agent_message') {
                        this.addMessage(data);
                    }
                } catch (e) {
                    console.error('Error parsing WebSocket message:', e);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.handleWebSocketFailure();
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket closed');
                this.isConnected = false;
                this.updateStatus(false);
                
                // Try to reconnect after 5 seconds
                setTimeout(() => this.initWebSocket(), 5000);
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.handleWebSocketFailure();
        }
    },
    
    handleWebSocketFailure() {
        // Fallback: Load messages from analysis results if available
        console.log('WebSocket failed, using fallback message display');
        this.updateStatus(false);
        
        // Check if we have messages from the analysis
        if (window.analysisResults && window.analysisResults.conversation_highlights) {
            this.displayStoredMessages(window.analysisResults.conversation_highlights);
        }
    },
    
    listenForAnalysisResults() {
        // Listen for analysis completion
        document.addEventListener('analysisComplete', (event) => {
            if (event.detail && event.detail.conversation_highlights) {
                this.displayStoredMessages(event.detail.conversation_highlights);
            }
        });
    },
    
    displayStoredMessages(highlights) {
        console.log('Displaying stored agent messages:', highlights);
        
        // Clear existing messages
        this.container.innerHTML = '';
        
        // Add stored messages
        highlights.forEach((highlight, index) => {
            setTimeout(() => {
                this.addMessageFromHighlight(highlight);
            }, index * 100); // Stagger for effect
        });
    },
    
    addMessageFromHighlight(highlight) {
        let agent = 'Unknown';
        let message = highlight;
        let type = 'info';
        
        if (highlight.includes('🚨')) {
            type = 'alert';
            const parts = highlight.split(':');
            agent = parts[0].replace('🚨', '').trim();
            message = parts.slice(1).join(':').trim();
        } else if (highlight.includes('❓')) {
            type = 'question';
            const match = highlight.match(/❓\s*(\w+)\s+asked:\s+(.+)/);
            if (match) {
                agent = match[1];
                message = match[2];
            }
        } else if (highlight.includes('🤝')) {
            type = 'consensus';
            agent = 'ConsensusBuilder';
            message = highlight.replace('🤝', '').trim();
        }
        
        this.addMessage({
            agent: agent,
            content: message,
            type: type,
            timestamp: new Date().toISOString()
        });
    },
    
    addMessage(data) {
        const messageEl = document.createElement('div');
        messageEl.className = `agent-message ${data.type || 'info'}`;
        
        const timestamp = new Date(data.timestamp).toLocaleTimeString();
        
        messageEl.innerHTML = `
            <div class="message-header">
                <span class="agent-name">${data.agent}</span>
                <span class="timestamp">${timestamp}</span>
            </div>
            <div class="message-content">${data.content}</div>
        `;
        
        this.container.appendChild(messageEl);
        
        // Auto-scroll to bottom
        this.container.scrollTop = this.container.scrollHeight;
        
        // Animate in
        messageEl.style.opacity = '0';
        messageEl.style.transform = 'translateY(10px)';
        setTimeout(() => {
            messageEl.style.transition = 'all 0.3s ease';
            messageEl.style.opacity = '1';
            messageEl.style.transform = 'translateY(0)';
        }, 10);
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => AgentCommunication.init());
} else {
    AgentCommunication.init();
}

// Store analysis results globally when received
window.handleAnalysisResults = function(results) {
    window.analysisResults = results;
    
    // Dispatch event for agent communication
    const event = new CustomEvent('analysisComplete', { detail: results });
    document.dispatchEvent(event);
    
    // Update other UI elements...
};
