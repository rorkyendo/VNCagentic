class VNCagenticClient {
    constructor() {
        this.apiUrl = 'http://localhost:8000/api/v1';
        this.wsUrl = 'ws://localhost:8000/api/v1';
        this.currentSession = null;
        this.websocket = null;
        this.sessions = []; // Store session history
        
        this.init();
    }
    
    async init() {
        this.setupEventListeners();
        await this.loadSessionHistory();
        this.loadVNC();
    }
    
    setupEventListeners() {
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        const newTaskButton = document.getElementById('new-task-button');
        
        sendButton.addEventListener('click', () => this.sendMessage());
        newTaskButton.addEventListener('click', () => this.createNewTask());
        
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
        
        try {
            const response = await fetch(`${this.apiUrl}/messages/${this.currentSession.id}/messages`);
            if (response.ok) {
                const data = await response.json();
                const messagesContainer = document.getElementById('messages');
                messagesContainer.innerHTML = '';
                
                data.messages.forEach(msg => {
                    this.addMessage(msg.role, msg.content);
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
    
    async createSession() {
        try {
            this.updateStatus('connecting', 'Creating session...');
            
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
    }
    
    updateSessionInfo() {
        if (!this.currentSession) return;
        
        document.getElementById('session-id').textContent = this.currentSession.id.substring(0, 8);
        document.getElementById('session-model').textContent = this.currentSession.model;
        document.getElementById('session-status-text').textContent = this.currentSession.status;
    }
    
    connectWebSocket() {
        if (!this.currentSession) return;
        
        try {
            this.websocket = new WebSocket(`${this.wsUrl}/sessions/${this.currentSession.id}/stream`);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.updateStatus('connected', 'Connected');
                this.enableInput();
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleWebSocketMessage(message);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateStatus('error', 'Disconnected');
                this.disableInput();
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateStatus('error', 'Connection error');
            };
            
        } catch (error) {
            console.error('Error connecting WebSocket:', error);
            this.updateStatus('error', `WebSocket error: ${error.message}`);
        }
    }
    
    handleWebSocketMessage(message) {
        console.log('Received message:', message);
        
        switch (message.type) {
            case 'agent_message':
                this.addMessage('assistant', this.formatAgentContent(message.content));
                break;
            case 'tool_call':
                this.addMessage('system', `Tool call: ${message.content.tool_name}`);
                break;
            case 'tool_result':
                this.addMessage('system', `Tool result: ${JSON.stringify(message.content.result).substring(0, 100)}...`);
                break;
            case 'status':
                this.updateAgentStatus(message.content.status, message.content.details);
                break;
            case 'error':
                this.addMessage('system', `Error: ${message.content.error || 'Unknown error'}`);
                break;
            case 'pong':
                // Handle ping/pong
                break;
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
        
        if (!message || !this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
            return;
        }
        
        // Add user message to chat
        this.addMessage('user', message);
        
        // Send via WebSocket
        this.websocket.send(JSON.stringify({
            type: 'user_message',
            content: message
        }));
        
        // Clear input
        input.value = '';
    }
    
    addMessage(role, content) {
        const messagesContainer = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        messageDiv.textContent = content;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
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
        
        // Load VNC web interface
        vncFrame.src = 'http://localhost:6080/vnc.html';
        
        vncFrame.onload = () => {
            vncStatus.className = 'status connected';
            vncStatus.textContent = 'VNC Connected';
        };
        
        vncFrame.onerror = () => {
            vncStatus.className = 'status error';
            vncStatus.textContent = 'VNC Connection Failed';
        };
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
