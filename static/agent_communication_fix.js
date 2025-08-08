// Quick fix for Agent Communication display
// Add this script to your dashboard.html or replace the existing WebSocket handler

document.addEventListener('DOMContentLoaded', function() {
    // Find the agent messages container
    const messagesContainer = document.querySelector('.agent-messages-container, #agent-messages-container, [id*="agent-messages"]');
    
    if (!messagesContainer) {
        console.error('Agent messages container not found');
        return;
    }
    
    // Function to add a message to the display
    function addAgentMessage(data) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'agent-message';
        messageDiv.style.cssText = `
            padding: 12px;
            margin: 8px 0;
            background: rgba(59, 130, 246, 0.1);
            border-left: 3px solid #3b82f6;
            border-radius: 4px;
            animation: slideIn 0.3s ease;
        `;
        
        const timestamp = new Date().toLocaleTimeString();
        messageDiv.innerHTML = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <strong style="color: #3b82f6;">${data.agent || 'Agent'}</strong>
                <span style="color: #6b7280; font-size: 0.85em;">${timestamp}</span>
            </div>
            <div style="color: #e5e7eb;">${data.content || data.topic || 'Message'}</div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // If analysis results are already available, display the conversation highlights
    if (window.analysisResults && window.analysisResults.conversation_highlights) {
        // Clear "waiting" message
        messagesContainer.innerHTML = '';
        
        // Display stored messages
        window.analysisResults.conversation_highlights.forEach((highlight, index) => {
            setTimeout(() => {
                let agent = 'Agent';
                let content = highlight;
                
                if (highlight.includes('🚨')) {
                    agent = highlight.split(':')[0].replace('🚨', '').trim();
                    content = highlight.split(':').slice(1).join(':').trim();
                } else if (highlight.includes('❓')) {
                    const match = highlight.match(/❓\s*(\w+)\s+asked:\s+(.+)/);
                    if (match) {
                        agent = match[1];
                        content = match[2];
                    }
                } else if (highlight.includes('🤝')) {
                    agent = 'Consensus';
                    content = highlight.replace('🤝', '').trim();
                }
                
                addAgentMessage({ agent, content });
            }, index * 200); // Stagger messages
        });
    }
    
    // WebSocket connection for real-time updates
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    try {
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            console.log('Agent communication WebSocket connected');
            // Clear waiting message
            if (messagesContainer.textContent.includes('Waiting')) {
                messagesContainer.innerHTML = '<div style="color: #10b981;">Connected - Agents are communicating...</div>';
            }
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'agent_message') {
                    addAgentMessage(data);
                }
            } catch (e) {
                console.error('Error parsing WebSocket message:', e);
            }
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
    } catch (error) {
        console.error('Failed to create WebSocket:', error);
    }
});

// CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(style);
