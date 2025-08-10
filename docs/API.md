# VNCagentic API Documentation

## Overview

VNCagentic provides a RESTful API for managing chat sessions and executing desktop commands through an AI agent. All endpoints return JSON responses and follow standard HTTP status codes.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required. For production deployment, implement API key authentication.

## Endpoints

### Chat Management

#### POST /api/simple/chat
Send a message to the AI agent for processing and command execution.

**Request Body:**
```json
{
  "message": "open firefox and search weather jakarta",
  "session_id": "optional-session-uuid"
}
```

**Response:**
```json
{
  "session_id": "fbec5be9-3876-47ea-ac5d-892573d5428e",
  "message": "open firefox and search weather jakarta",
  "response": "{\n  \"action\": \"Opening Firefox and searching for weather jakarta\",\n  \"commands\": [\n    \"DISPLAY=:1 firefox-esr &\",\n    \"sleep 5\",\n    \"xdotool key ctrl+l\",\n    \"sleep 1\",\n    \"xdotool type \\\"weather jakarta\\\"\",\n    \"xdotool key Return\"\n  ]\n}\n\n[REPORT]: Opening Firefox and searching for weather jakarta - 6 successful, 0 failed",
  "success": true,
  "actions_taken": [
    "DISPLAY=:1 firefox-esr &",
    "sleep 5", 
    "xdotool key ctrl+l",
    "sleep 1",
    "xdotool type \"weather jakarta\"",
    "xdotool key Return"
  ],
  "error": null
}
```

**Status Codes:**
- `200 OK` - Message processed successfully
- `400 Bad Request` - Invalid request format
- `500 Internal Server Error` - AI agent or execution error

---

### Session Management

#### GET /api/sessions
Retrieve all chat sessions.

**Response:**
```json
[
  {
    "id": "fbec5be9-3876-47ea-ac5d-892573d5428e",
    "created_at": "2024-01-10T10:30:00Z",
    "updated_at": "2024-01-10T11:45:00Z",
    "message_count": 5
  }
]
```

#### POST /api/sessions
Create a new chat session.

**Request Body:**
```json
{
  "name": "Optional session name"
}
```

**Response:**
```json
{
  "id": "new-session-uuid",
  "created_at": "2024-01-10T10:30:00Z",
  "updated_at": "2024-01-10T10:30:00Z",
  "message_count": 0
}
```

#### GET /api/sessions/{session_id}/messages
Retrieve all messages for a specific session.

**Response:**
```json
[
  {
    "id": "message-uuid",
    "session_id": "session-uuid", 
    "role": "user",
    "content": "open calculator",
    "timestamp": "2024-01-10T10:30:00Z"
  },
  {
    "id": "message-uuid-2",
    "session_id": "session-uuid",
    "role": "assistant", 
    "content": "Opening calculator application",
    "timestamp": "2024-01-10T10:30:05Z"
  }
]
```

#### DELETE /api/sessions/{session_id}/messages
Clear all messages from a session.

**Response:**
```json
{
  "success": true,
  "message": "Messages cleared successfully"
}
```

---

### VNC Control

#### POST /vnc/execute
Execute a command directly on the VNC desktop environment.

**Request Body:**
```json
{
  "command": "DISPLAY=:1 xcalc &"
}
```

**Response:**
```json
{
  "success": true,
  "return_code": 0,
  "output": "",
  "error": ""
}
```

#### POST /vnc/screenshot  
Take a screenshot of the current desktop.

**Response:**
```json
{
  "success": true,
  "image": "base64-encoded-png-data"
}
```

---

### System Health

#### GET /health
Check backend service health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-10T10:30:00Z",
  "version": "1.0.0"
}
```

---

## Error Handling

### Standard Error Response
```json
{
  "error": "Error description",
  "detail": "Detailed error message",
  "status_code": 400
}
```

### Common Error Codes
- `400` - Bad Request (invalid JSON, missing fields)
- `404` - Not Found (session not found) 
- `500` - Internal Server Error (AI agent failure, VNC connection issue)
- `503` - Service Unavailable (VNC agent down)

---

## Rate Limiting
Currently no rate limiting is implemented. For production:
- Implement per-IP rate limiting
- Add API key quotas
- Monitor usage patterns

---

## Examples

### Complete Workflow
```bash
# 1. Create new session
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"name":"My Desktop Session"}'

# 2. Send command to AI agent  
curl -X POST http://localhost:8000/api/simple/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message":"open calculator and firefox",
    "session_id":"your-session-id"
  }'

# 3. Check session messages
curl http://localhost:8000/api/sessions/your-session-id/messages

# 4. Take screenshot to verify
curl -X POST http://localhost:8090/screenshot
```

### Testing Commands
```bash
# Simple app launch
curl -X POST http://localhost:8000/api/simple/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"open calculator"}'

# Complex workflow
curl -X POST http://localhost:8000/api/simple/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"open firefox and search weather jakarta today"}'

# Text input
curl -X POST http://localhost:8000/api/simple/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"type hello world"}'

# Mouse control
curl -X POST http://localhost:8000/api/simple/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"klik di koordinat 300 200"}'
```

---

## WebSocket Support (Future)
Currently, the API uses REST endpoints. Future versions may include WebSocket support for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('AI Response:', data.response);
};
```

---

For more information, see the main [README.md](../README.md) documentation.
