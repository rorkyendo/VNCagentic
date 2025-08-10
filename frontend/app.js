class VNCagenticClient {
    constructor() {
        this.apiUrl = 'http://localhost:8000/api/v1';
        this.currentSession = null;
        this.sessions = []; // Store session history
        this.isAgentProcessing = false;
        // Disable WebSocket, use REST API only
        this.useWebSocket = false;
        
        this.init();
    }
    
    async init() {
        this.setupEventListeners();
        this.loadVNC();
        
        // Set initial status to connected REST API mode
        this.updateStatus('connected', 'Connected (REST API)');
        this.enableInput();
        
        // Load session history 
        await this.loadSessionHistory();
        
        // If we have sessions, load the most recent one
        if (this.sessions.length > 0) {
            await this.loadSession(this.sessions[0]);
        } else {
            // Create a new session if none exist
            await this.createNewTask();
        }
    }
    
    setupEventListeners() {
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        const newTaskButton = document.getElementById('new-task-button');
        const clearHistoryButton = document.getElementById('clear-history-button');
        const scrollToBottomButton = document.getElementById('scroll-to-bottom');
        const messagesContainer = document.getElementById('messages');
        
    sendButton.addEventListener('click', () => this.sendMessage());
        newTaskButton.addEventListener('click', () => this.createNewTask());
        clearHistoryButton.addEventListener('click', () => this.clearHistory());
        scrollToBottomButton.addEventListener('click', () => this.scrollToBottom());
        
        // Setup scroll detection
        messagesContainer.addEventListener('scroll', () => this.handleScroll());
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }
    
    async loadSessionHistory() {
        try {
            const response = await fetch(`${this.apiUrl}/sessions`);
            if (response.ok) {
                const data = await response.json();
                this.sessions = data.sessions || [];
                this.updateTaskHistory();
            }
        } catch (error) {
            console.error('Error loading session history:', error);
        }
    }
    
    updateTaskHistory() {
        const historyContainer = document.getElementById('task-history');
        historyContainer.innerHTML = '';
        
        this.sessions.forEach(session => {
            const taskItem = document.createElement('div');
            taskItem.className = 'task-item';
            if (this.currentSession && session.id === this.currentSession.id) {
                taskItem.className += ' active';
            }
            
            taskItem.innerHTML = `
                <div><strong>${session.title || 'Untitled Task'}</strong></div>
                <div><small>${session.status} - ${new Date(session.created_at).toLocaleString()}</small></div>
            `;
            
            taskItem.addEventListener('click', () => this.loadSession(session));
            historyContainer.appendChild(taskItem);
        });
    }
    
    async createNewTask() {
        await this.createSession();
    }
    
    async clearHistory() {
        if (!confirm('Are you sure you want to clear all task history? This action cannot be undone.')) {
            return;
        }
        
        try {
            // Get all sessions first
            const response = await fetch(`${this.apiUrl}/sessions`);
            if (!response.ok) {
                throw new Error('Failed to fetch sessions');
            }
            
            const data = await response.json();
            const sessions = data.sessions || data;
            
            // Delete each session
            const deletePromises = sessions.map(session => 
                fetch(`${this.apiUrl}/sessions/${session.id}`, {
                    method: 'DELETE'
                })
            );
            
            await Promise.all(deletePromises);
            
            // Clear local state
            this.sessions = [];
            this.currentSession = null;
            
            // Close WebSocket if open
            if (this.websocket) {
                this.websocket.close();
                this.websocket = null;
            }
            
            // Clear UI
            document.getElementById('task-history').innerHTML = '<p>No tasks yet. Create a new task to get started.</p>';
            document.getElementById('messages').innerHTML = '';
            document.getElementById('session-id').textContent = 'None';
            document.getElementById('session-model').textContent = 'None';
            document.getElementById('session-status-text').textContent = 'No session';
            
            // Keep connected status - don't disconnect
            console.log('Task history cleared successfully');
            
            // Optionally create a new session right away
            setTimeout(() => {
                this.createNewTask();
            }, 500);
            
        } catch (error) {
            console.error('Error clearing history:', error);
            alert('Failed to clear history. Please try again.');
        }
    }
    
    async loadSession(session) {
        if (this.currentSession && this.currentSession.id === session.id) {
            return; // Already loaded
        }
        
        // Close current websocket
        if (this.websocket) {
            this.websocket.close();
        }
        
        this.currentSession = session;
        this.updateSessionInfo();
        this.connectWebSocket();
        
        // Load chat history
        await this.loadChatHistory();
        
        // Update UI
        this.updateTaskHistory();
    }
    
    async loadChatHistory() {
        if (!this.currentSession) return;
        
        // Skip loading if agent is processing to prevent flicker
        if (this.isAgentProcessing) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/sessions/${this.currentSession.id}/messages`);
            if (response.ok) {
                const data = await response.json();
                const messagesContainer = document.getElementById('messages');
                
                // Only reload if messages count has changed (avoid unnecessary reloads)
                const currentMessageCount = messagesContainer.children.length;
                if (currentMessageCount !== data.messages.length) {
                    messagesContainer.innerHTML = '';
                    
                    console.log(`Loading ${data.messages.length} messages for session ${this.currentSession.id}`);
                    
                    data.messages.forEach(msg => {
                        this.addMessage(msg.role, msg.content);
                    });
                    
                    // Scroll to bottom after loading all messages
                    setTimeout(() => {
                        this.scrollToBottom();
                    }, 100);
                }
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
    
    async createSession() {
        try {
            // Don't change status to connecting - keep it stable
            console.log('Creating new session...');
            
            const response = await fetch(`${this.apiUrl}/sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: `Task ${new Date().toLocaleString()}`,
                    model: 'claude-sonnet-4-20250514',
                    api_provider: 'anthropic',
                    user_id: 1
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            this.currentSession = await response.json();
            this.sessions.unshift(this.currentSession); // Add to beginning
            this.updateSessionInfo();
            this.updateTaskHistory();
            this.connectWebSocket();

            // Clear messages for new session
            document.getElementById('messages').innerHTML = '';

        } catch (error) {
            console.error('Error creating session:', error);
            this.updateStatus('error', `Failed to create session: ${error.message}`);
        }
    }    updateSessionInfo() {
        if (!this.currentSession) return;
        
        document.getElementById('session-id').textContent = this.currentSession.id.substring(0, 8);
        document.getElementById('session-model').textContent = this.currentSession.model;
        document.getElementById('session-status-text').textContent = this.currentSession.status;
    }
    
    connectWebSocket() {
        // WebSocket disabled - using REST API only
        console.log('WebSocket disabled, using REST API mode');
        // Only update status if not already connected to avoid flicker
        const statusElement = document.getElementById('session-status');
        if (!statusElement.textContent.includes('Connected (REST API)')) {
            this.updateStatus('connected', 'Connected (REST API)');
        }
        this.enableInput();
        return;
    }
    
    isWebSocketConnected() {
        // Always return false since WebSocket is disabled
        return false;
    }
    
    sendWebSocketMessage(message) {
        // WebSocket disabled - no action needed
        return;
    }
    
    handleWebSocketMessage(message) {
        // WebSocket disabled - no action needed
        return;
        
        switch (message.type) {
            case 'status':
                this.updateAgentStatus(message.status, message.details);
                break;
                
            case 'task_started':
                this.addMessage('system', `🚀 Task started: ${message.message}`);
                this.isAgentProcessing = true;
                this.disableInput();
                break;
                
            case 'agent_output':
                this.hadWSAgentOutput = true;
                this.awaitingWSResponse = false;
                this.addMessage('assistant', message.content);
                break;
                
            case 'tool_call':
                this.addMessage('system', `🔧 Using tool: ${message.tool_name}`, {
                    details: JSON.stringify(message.tool_input, null, 2),
                    tool_id: message.tool_id
                });
                break;
                
            case 'tool_result':
                this.addMessage('system', `✅ Tool completed`, {
                    details: message.result ? JSON.stringify(message.result).substring(0, 500) + '...' : 'No result',
                    error: message.error,
                    tool_id: message.tool_id
                });
                break;
                
            case 'screenshot':
                this.updateVNCScreenshot(message.image, message.context);
                break;
                
            case 'status_update':
                if (message.status === 'completed') {
                    this.addMessage('system', '✅ Task completed successfully');
                    this.isAgentProcessing = false;
                    this.enableInput();
                } else if (message.status === 'error') {
                    this.addMessage('system', `❌ Task failed: ${message.details?.error || 'Unknown error'}`);
                    this.isAgentProcessing = false;
                    this.enableInput();
                }
                break;
                
            case 'error':
                this.addMessage('system', `❌ Error: ${message.error}`);
                this.isAgentProcessing = false;
                this.enableInput();
                break;
                
            case 'pong':
                // Handle ping/pong for connection health
                break;
                
            default:
                console.log('Unknown message type:', message.type);
        }
    }
    
    updateVNCScreenshot(imageBase64, context) {
        // Update a screenshot overlay or indicator
        console.log(`VNC Screenshot updated - Context: ${context}`);
        
        // Could add a visual indicator showing the agent is viewing the screen
        const vncFrame = document.querySelector('#vnc-container iframe');
        if (vncFrame) {
            // Add a subtle border or indicator when agent is analyzing screen
            if (context.includes('before_') || context.includes('after_')) {
                vncFrame.style.border = '2px solid #4CAF50';
                setTimeout(() => {
                    vncFrame.style.border = '1px solid #ddd';
                }, 1000);
            }
        }
    }
    
    formatAgentContent(content) {
        if (typeof content === 'string') {
            return content;
        } else if (content && content.text) {
            return content.text;
        } else {
            return JSON.stringify(content);
        }
    }
    
    updateAgentStatus(status, details = {}) {
        const statusElement = document.getElementById('session-status-text');
        statusElement.textContent = status;
        
        if (details.message) {
            this.addMessage('system', details.message);
        }
    }
    
    async sendMessage() {
        const input = document.getElementById('message-input');
        const message = input.value.trim();
        
        if (!message) {
            return;
        }
        
        if (!this.currentSession) {
            console.error('No active session');
            return;
        }

        // Check if agent is already processing
        if (this.isAgentProcessing) {
            this.addMessage('system', '⏳ Agent is currently processing. Please wait...');
            return;
        }

        // Add user message to chat immediately
        this.addMessage('user', message);
        
        // Clear input and disable during processing
        input.value = '';
        this.isAgentProcessing = true;
        this.disableInput();
        
        try {
            // Use REST API for reliable chat
            console.log('Sending message via REST API');
            const response = await fetch(`${this.apiUrl}/simple/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message, session_id: this.currentSession.id })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.addMessage('assistant', data.response);
                // No need to refresh - response is already displayed
            } else {
                const errorText = await response.text();
                console.error('Failed to send message:', errorText);
                this.addMessage('system', `❌ Error: Failed to send message (${response.status})`);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('system', `❌ Error: ${error.message}`);
        } finally {
            // Re-enable input
            this.isAgentProcessing = false;
            this.enableInput();
        }
    }
    
    addMessage(role, content, options = {}) {
        const messagesContainer = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        // Create message content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        if (role === 'assistant') {
            contentDiv.innerHTML = this.renderAssistantContent(content);
        } else {
            contentDiv.textContent = content;
        }
        messageDiv.appendChild(contentDiv);
        
        // Add details if provided (for tool calls)
        if (options.details) {
            const detailsDiv = document.createElement('div');
            detailsDiv.className = 'message-details';
            detailsDiv.innerHTML = `<pre>${options.details}</pre>`;
            messageDiv.appendChild(detailsDiv);
        }
        
        // Add error if provided
        if (options.error) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message-error';
            errorDiv.textContent = `Error: ${options.error}`;
            messageDiv.appendChild(errorDiv);
        }
        
        // Add timestamp
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        timestampDiv.textContent = new Date().toLocaleTimeString();
        messageDiv.appendChild(timestampDiv);
        
        messagesContainer.appendChild(messageDiv);
        
        // Auto scroll to bottom for new messages
        setTimeout(() => {
            this.scrollToBottom();
        }, 100);
    }

    renderAssistantContent(content) {
        // Render assistant content and detect <xdotool> blocks
        const xdoRegex = /<xdotool>([\s\S]*?)<\/xdotool>/g;
        let html = content.replace(/\n/g, '<br/>');
        // Add execute buttons
        html = html.replace(xdoRegex, (match, cmd) => {
            const escaped = cmd.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            const btn = `<button class="exec-btn" data-cmd="${encodeURIComponent(cmd)}">Run in VNC</button>`;
            return `<div class="xdo-block"><pre>${escaped}</pre>${btn}</div>`;
        });
        // Attach delegated click after insert
        setTimeout(() => {
            document.querySelectorAll('.exec-btn').forEach(btn => {
                btn.onclick = async () => {
                    const raw = decodeURIComponent(btn.getAttribute('data-cmd'));
                    try {
                        const resp = await fetch(`${this.apiUrl}/vnc/execute`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ command: raw })
                        });
                        const result = await resp.json();
                        this.addMessage('system', `Executed: ${raw}`, { details: JSON.stringify(result, null, 2) });
                    } catch (e) {
                        this.addMessage('system', `Execution failed`, { error: String(e) });
                    }
                };
            });
        }, 0);
        return html;
    }
    
    updateStatus(status, message) {
        const statusElement = document.getElementById('session-status');
        statusElement.className = `status ${status}`;
        statusElement.textContent = message;
    }
    
    enableInput() {
        document.getElementById('message-input').disabled = false;
        document.getElementById('send-button').disabled = false;
    }
    
    disableInput() {
        document.getElementById('message-input').disabled = true;
        document.getElementById('send-button').disabled = true;
    }
    
    loadVNC() {
        const vncFrame = document.getElementById('vnc-frame');
        const vncStatus = document.getElementById('vnc-status');
        
        // Update status
        vncStatus.className = 'status connecting';
        vncStatus.textContent = 'Connecting to VNC...';
        
        // Load VNC web interface with appropriate parameters
        const vncUrl = `http://localhost:6080/vnc.html?host=localhost&port=5900&autoconnect=true&resize=scale`;
        vncFrame.src = vncUrl;
        
        vncFrame.onload = () => {
            vncStatus.className = 'status connected';
            vncStatus.textContent = 'VNC Connected';
            console.log('VNC loaded successfully');
        };
        
        vncFrame.onerror = () => {
            vncStatus.className = 'status error';
            vncStatus.textContent = 'VNC Connection Failed';
            console.log('VNC failed to load');
        };
        
        // Fallback check after 3 seconds
        setTimeout(() => {
            if (vncStatus.className === 'status connecting') {
                vncStatus.className = 'status connected';
                vncStatus.textContent = 'VNC Connected';
            }
        }, 3000);
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        this.hideScrollIndicator();
    }
    
    handleScroll() {
        const messagesContainer = document.getElementById('messages');
        const scrollIndicator = document.getElementById('scroll-to-bottom');
        
        // Check if user is near bottom (within 100px)
        const isNearBottom = messagesContainer.scrollTop + messagesContainer.clientHeight >= 
                            messagesContainer.scrollHeight - 100;
        
        if (isNearBottom) {
            this.hideScrollIndicator();
        } else {
            this.showScrollIndicator();
        }
    }
    
    showScrollIndicator() {
        const scrollIndicator = document.getElementById('scroll-to-bottom');
        scrollIndicator.style.display = 'flex';
    }
    
    hideScrollIndicator() {
        const scrollIndicator = document.getElementById('scroll-to-bottom');
        scrollIndicator.style.display = 'none';
    }
}

// Global functions for toolbar buttons
function refreshVNC() {
    const vncFrame = document.getElementById('vnc-frame');
    vncFrame.src = vncFrame.src;
}

function takeScreenshot() {
    // This would call the screenshot API
    console.log('Screenshot requested');
    if (window.vncagenticClient && window.vncagenticClient.currentSession) {
        fetch(`${window.vncagenticClient.apiUrl}/vnc/${window.vncagenticClient.currentSession.id}/screenshot`)
            .then(response => response.json())
            .then(data => {
                console.log('Screenshot data:', data);
                // Could display screenshot in a modal
            })
            .catch(error => console.error('Screenshot error:', error));
    }
}

function openVNCWindow() {
    window.open('http://localhost:6080/vnc.html', '_blank', 'width=1024,height=768');
}

function uploadFile() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file first');
        return;
    }
    
    // This would implement file upload to the session
    console.log('Uploading file:', file.name);
    
    // For demo purposes, just add to file list
    const fileList = document.getElementById('file-list');
    const fileItem = document.createElement('div');
    fileItem.innerHTML = `
        <div style="padding: 5px; border: 1px solid #ddd; margin: 5px 0; border-radius: 3px;">
            📄 ${file.name} (${(file.size / 1024).toFixed(1)} KB)
        </div>
    `;
    
    if (fileList.innerHTML.includes('No files uploaded')) {
        fileList.innerHTML = '';
    }
    fileList.appendChild(fileItem);
    
    // Clear input
    fileInput.value = '';
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.vncagenticClient = new VNCagenticClient();
});
