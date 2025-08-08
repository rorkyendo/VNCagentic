**Author: Taufiq Rorkyendo**

# VNCagentic - Scalable Computer Use Agent Backend

A scalable FastAPI backend for computer use agent session management that replaces the experimental Streamlit interface with a production-ready API and session management system.

This implementation reuses the existing computer use agent stack from the [Anthropic Computer Use Demo](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo) while removing the experimental Streamlit layer and adding missing backend API, database, and session management layers.

## Demo Video

📹 **[5-Minute Demo Video](demo_video_link_here)**

The demo video demonstrates:

### Repository and Codebase Overview
- Complete project structure walkthrough
- FastAPI backend architecture
- Database schema and models
- Agent integration components

### Service Launch and Endpoint Functionality
- Docker compose startup process
- API endpoint testing via Swagger UI
- WebSocket connection establishment
- VNC integration demonstration

### Usage Case Demonstrations

#### Usage Case 1: Search Weather in Dubai
1. ✅ Start a new chat session
2. ✅ Send prompt: "Search the weather in Dubai"
3. ✅ Verify system opens Firefox, conducts Google search
4. ✅ Agent provides summarized result in real-time
5. ✅ All interactions streamed via WebSocket

#### Usage Case 2: Search Weather in San Francisco
1. ✅ Start another new chat session
2. ✅ Send prompt: "Search the weather in San Francisco"
3. ✅ Verify system opens Firefox, conducts Google search
4. ✅ Agent provides summarized result in real-time
5. ✅ All interactions streamed via WebSocket

#### History Verification
- ✅ Both sessions properly stored in database
- ✅ Session history accessible via task history panel
- ✅ Complete message history preserved
- ✅ Users can switch between sessions

### Streamlit-like UI Behavior Simulation
- ✅ Real-time progress streaming for each intermediate step
- ✅ Tool calls displayed as they happen
- ✅ Tool results shown immediately
- ✅ UI prompts for new tasks after completion

## Quick Demo Test

Run the automated demo script to test both usage cases:

```bash
# Install demo dependencies
pip install aiohttp

# Run demo test
python demo.py
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
│   (HTML/JS)     │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Computer Use  │
                       │   Agent Stack   │
                       │   (VNC + Tools) │
                       └─────────────────┘
```

## Quick Start

### Using Docker (Recommended)

1. **Clone and setup**:
```bash
git clone <your-repo>
cd VNCagentic
cp .env.example .env
# Edit .env with your API keys and provider settings
```

2. **Configure API Provider**:
```bash
# For Anthropic (default)
API_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-anthropic-key

# OR for CometAPI (Anthropic-compatible, often more cost-effective)
API_PROVIDER=comet
COMET_API_BASE_URL=https://api.cometapi.com
ANTHROPIC_API_KEY=your-cometapi-key
```

3. **Run with Docker Compose**:
```bash
docker-compose up -d
```

4. **Test API connection**:
```bash
# Test your API provider setup
python quick_test.py
```

5. **Access the application**:
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- VNC Web Interface: http://localhost:6080/vnc.html

### Local Development

1. **Prerequisites**:
- Python 3.11+
- PostgreSQL
- Node.js (for frontend)

2. **Backend setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Database setup**:
```bash
createdb vncagentic
alembic upgrade head
```

4. **Run the backend**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Frontend setup**:
```bash
cd frontend
npm install
npm start
```

## API Documentation

### Complete API Reference

Once running, visit **http://localhost:8000/docs** for the interactive OpenAPI documentation.

#### Core Session Management Endpoints

```http
POST /api/v1/sessions
Content-Type: application/json

{
  "title": "Weather Search Task",
  "model": "claude-sonnet-4-20250514",
  "api_provider": "anthropic",
  "user_id": 1
}
```

```http
GET /api/v1/sessions
# Returns: List of all sessions with pagination

GET /api/v1/sessions/{session_id}
# Returns: Detailed session information

PATCH /api/v1/sessions/{session_id}
# Update session title, status, etc.

DELETE /api/v1/sessions/{session_id}
# Delete session and cleanup resources
```

#### Message Management

```http
POST /api/v1/messages/{session_id}/messages
Content-Type: application/json

{
  "content": "Search the weather in Dubai",
  "role": "user"
}
```

```http
GET /api/v1/messages/{session_id}/messages
# Returns: Complete chat history for session
```

#### VNC Integration

```http
GET /api/v1/vnc/{session_id}
# Returns: VNC connection details and web URL

GET /api/v1/vnc/{session_id}/screenshot
# Returns: Current desktop screenshot
```

#### Real-time WebSocket

```javascript
// Connect to session stream
const ws = new WebSocket('ws://localhost:8000/api/v1/sessions/{session_id}/stream');

// Send user message
ws.send(JSON.stringify({
  type: 'user_message',
  content: 'Search the weather in Dubai'
}));

// Receive real-time updates
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  // Handle: agent_message, tool_call, tool_result, status, error
};
```

### Architecture Documentation

See [SEQUENCE_DIAGRAM.md](SEQUENCE_DIAGRAM.md) for detailed sequence diagrams showing:
- Session creation and management flow
- Real-time message processing
- VNC integration patterns
- Database interaction patterns

## API Provider Support

### CometAPI Integration (Recommended)

VNCagentic supports **CometAPI** as an Anthropic-compatible provider, offering:

✅ **Cost-effective alternative** to direct Anthropic API  
✅ **Drop-in replacement** - same interface, same functionality  
✅ **Multiple Claude models** available  
✅ **Enterprise-grade reliability**  

#### Quick Setup with CometAPI

1. **Get CometAPI Key**: Visit [CometAPI](https://api.cometapi.com) and get your API key
2. **Configure**: Set `API_PROVIDER=comet` in your `.env` file
3. **Test**: Run `python quick_test.py` to validate connection

```bash
# .env configuration for CometAPI
API_PROVIDER=comet
COMET_API_BASE_URL=https://api.cometapi.com
ANTHROPIC_API_KEY=sk-your-cometapi-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**📖 Full Documentation**: See [docs/COMETAPI.md](docs/COMETAPI.md) for comprehensive setup guide.

### Anthropic Direct API

For direct Anthropic API usage:

```bash
# .env configuration for Anthropic
API_PROVIDER=anthropic
ANTHROPIC_API_URL=https://api.anthropic.com
ANTHROPIC_API_KEY=your-anthropic-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/vncagentic

# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key

# VNC Configuration
VNC_PASSWORD=your_vnc_password
VNC_DISPLAY=:1

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your_secret_key

# Agent Configuration
MAX_SESSIONS=10
SESSION_TIMEOUT_MINUTES=60
```

## Project Structure

```
VNCagentic/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Core configuration
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic
│   │   ├── agent/             # Computer use agent
│   │   └── main.py            # FastAPI app
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Simple HTML/JS frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml          # Docker orchestration
├── .env.example               # Environment template
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
