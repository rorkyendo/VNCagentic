# Integration Guide

This document explains how to integrate VNCagentic with the existing Anthropic computer use agent stack.

## Overview

VNCagentic is designed to reuse the existing computer use agent components from the [Anthropic Computer Use Demo](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo) while replacing the Streamlit interface with a scalable FastAPI backend.

## Integration Steps

### 1. Copy Computer Use Components

You need to copy the following components from the original demo:

```bash
# From the original repo, copy these to backend/app/agent/:
computer_use_demo/
├── tools/          # → backend/app/agent/tools/
├── loop.py         # → backend/app/agent/loop.py (adapt as needed)
└── (other files)   # → backend/app/agent/
```

### 2. Required Files to Copy

#### Essential Files:
- `computer_use_demo/tools/`: All computer use tools
- `computer_use_demo/loop.py`: Main agent loop
- `computer_use_demo/Dockerfile`: Docker setup (adapt for our VNC container)

#### Key Components:
1. **Computer Tool**: Screenshot, click, type, scroll operations
2. **Bash Tool**: Command execution in the VM
3. **Edit Tool**: File editing capabilities
4. **Tool Collection**: Management of available tools

### 3. Adaptation Required

#### A. File Paths
Update import paths in copied files:
```python
# Original:
from computer_use_demo.tools import ToolCollection

# Updated:
from app.agent.tools import ToolCollection
```

#### B. Loop Integration
The `sampling_loop` function needs to be adapted to work with our callback system:

```python
# In app/agent/computer_use_loop.py
async def process_message(self, user_message: str):
    # Add message to conversation
    self.messages.append({
        "role": "user", 
        "content": [BetaTextBlockParam(type="text", text=user_message)]
    })
    
    # Run the adapted sampling loop
    self.messages = await sampling_loop(
        model=self.model,
        provider=self.api_provider,
        system_prompt_suffix="",
        messages=self.messages,
        output_callback=self._output_callback,
        tool_output_callback=self._tool_output_callback,
        api_response_callback=self._api_response_callback,
        api_key=self.api_key
    )
```

#### C. Docker Environment
The VNC container (`Dockerfile.vnc`) should be based on the original computer use demo image:

```dockerfile
FROM ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest

# Add our backend integration
COPY app/agent/ /home/computeruse/agent_integration/
```

### 4. WebSocket Integration

The key innovation is the WebSocket integration that streams real-time updates:

```python
# In AgentService
async def _on_agent_output(self, session_id: str, content: Any):
    """Stream agent output via WebSocket"""
    message = WebSocketMessage(
        type=WebSocketMessageType.AGENT_MESSAGE,
        content=content,
        session_id=session_id
    )
    await self._broadcast_to_session(session_id, message)
```

### 5. Database Persistence

Unlike the original demo, we persist conversations:

```python
# Messages are stored in PostgreSQL
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), ForeignKey("sessions.id"))
    role = Column(String(20))  # user, assistant, tool
    content = Column(Text)
    tool_name = Column(String(50), nullable=True)
    # ... more fields
```

### 6. Session Management

Each session gets its own agent instance:

```python
class AgentService:
    def __init__(self):
        self.active_sessions: Dict[str, ComputerUseAgent] = {}
    
    async def initialize_session(self, session_id: str):
        agent = ComputerUseAgent(session_id=session_id, ...)
        self.active_sessions[session_id] = agent
```

## File Structure After Integration

```
backend/app/agent/
├── __init__.py
├── computer_use_loop.py     # Our wrapper
├── loop.py                  # Adapted from original
├── tools.py                 # Adapted from original
└── tools/                   # Copied from original
    ├── __init__.py
    ├── computer.py          # Computer interaction tool
    ├── bash.py              # Bash execution tool
    ├── edit.py              # File editing tool
    └── base.py              # Base tool classes
```

## Configuration

### Environment Variables

```env
# Agent Configuration
ANTHROPIC_API_KEY=your_key_here
API_PROVIDER=anthropic
DEFAULT_MODEL=claude-sonnet-4-20250514

# VNC Configuration  
VNC_PASSWORD=vncpassword
VNC_DISPLAY=:1
WIDTH=1024
HEIGHT=768
```

### System Prompt

The system prompt is adapted to work with our environment:

```python
def _build_system_prompt(self) -> str:
    return f"""<SYSTEM_CAPABILITY>
* You are utilising an Ubuntu virtual machine with internet access.
* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
* You can use bash, computer, and editing tools.
</SYSTEM_CAPABILITY>"""
```

## API Endpoints

The FastAPI backend provides these key endpoints:

- `POST /api/v1/sessions` - Create new session
- `GET /api/v1/sessions/{id}` - Get session details  
- `WS /api/v1/sessions/{id}/stream` - WebSocket for real-time updates
- `GET /api/v1/sessions/{id}/vnc` - VNC connection details

## Deployment

### Development
```bash
# Copy original components first
cp -r /path/to/computer-use-demo/computer_use_demo/tools backend/app/agent/
cp /path/to/computer-use-demo/computer_use_demo/loop.py backend/app/agent/

# Then start services
docker-compose up -d
```

### Production
Use the same approach but with production-ready configurations:
- Use managed PostgreSQL
- Use Redis cluster
- Add proper logging and monitoring
- Set up SSL/TLS

## Key Differences from Original

1. **Architecture**: FastAPI backend vs Streamlit app
2. **Session Management**: Multiple concurrent sessions vs single session
3. **Persistence**: Database storage vs in-memory
4. **Real-time Updates**: WebSocket streaming vs Streamlit rerun
5. **VNC Integration**: Embedded VNC access vs separate connection
6. **API-First**: RESTful API with OpenAPI docs vs web UI only

## Next Steps

1. Copy the required files from the original demo
2. Adapt the imports and integrate with our callback system  
3. Test the agent functionality
4. Deploy and configure VNC access
5. Add monitoring and logging
6. Implement additional features like file upload/download

This integration preserves all the computer use capabilities while providing a scalable, API-driven backend suitable for production use.
