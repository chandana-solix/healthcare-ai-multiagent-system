// WebSocket connection handler for production
// Add this to your dashboard.html or create a separate JS file

function initializeWebSocket() {
    // Determine protocol based on current page protocol
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    console.log('Connecting to WebSocket:', wsUrl);
    
    let ws;
    let reconnectInterval = 5000; // 5 seconds
    let reconnectTimer;
    
    function connect() {
        try {
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('WebSocket connected');
                clearTimeout(reconnectTimer);
                reconnectInterval = 5000; // Reset interval
                
                // Update UI to show connected status
                const statusElement = document.getElementById('ws-status');
                if (statusElement) {
                    statusElement.textContent = 'Connected';
                    statusElement.className = 'status-connected';
                }
            };
            
            ws.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    console.log('WebSocket message:', data);
                    
                    if (data.type === 'agent_message') {
                        addAgentMessage(data);
                    }
                } catch (e) {
                    console.error('Error parsing WebSocket message:', e);
                }
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
            
            ws.onclose = function(event) {
                console.log('WebSocket disconnected:', event.code, event.reason);
                
                // Update UI to show disconnected status
                const statusElement = document.getElementById('ws-status');
                if (statusElement) {
                    statusElement.textContent = 'Disconnected';
                    statusElement.className = 'status-disconnected';
                }
                
                // Attempt to reconnect
                reconnectTimer = setTimeout(() => {
                    console.log('Attempting to reconnect...');
                    connect();
                }, reconnectInterval);
                
                // Increase reconnect interval (max 30 seconds)
                reconnectInterval = Math.min(reconnectInterval * 1.5, 30000);
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
        }
    }
    
    // Initial connection
    connect();
    
    // Clean up on page unload
    window.addEventListener('beforeunload', () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.close();
        }
        clearTimeout(reconnectTimer);
    });
    
    return ws;
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initializeWebSocket);
