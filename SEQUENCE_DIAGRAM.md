# Sequence Diagram

This document shows the sequence of interactions in the VNCagentic system.

## User Session Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant A as Agent Service
    participant VNC as VNC Container
    participant C as Claude API

    %% Session Creation
    U->>F: Click "Start New Agent Task"
    F->>API: POST /api/v1/sessions
    API->>DB: Create session record
    API->>A: Initialize agent for session
    API-->>F: Return session details
    F->>F: Update task history
    F->>API: Connect WebSocket
    API->>A: Register WebSocket

    %% Message Processing
    U->>F: Type message: "Search weather in Dubai"
    F->>API: WebSocket: user_message
    API->>A: Process user message
    A->>DB: Store user message
    A->>C: Send to Claude API
    C-->>A: Return with tool calls
    A->>VNC: Execute computer tools
    VNC-->>A: Tool results
    A->>API: Broadcast tool_call via WebSocket
    API-->>F: Stream tool_call
    F->>F: Display "Tool call: computer"
    A->>API: Broadcast tool_result via WebSocket
    API-->>F: Stream tool_result
    F->>F: Display tool result
    A->>C: Continue with tool results
    C-->>A: Final response
    A->>DB: Store agent response
    A->>API: Broadcast agent_message via WebSocket
    API-->>F: Stream agent_message
    F->>F: Display agent response

    %% VNC Integration
    U->>F: View VNC panel
    F->>VNC: Load VNC web interface
    VNC-->>F: Display desktop
    U->>F: Click "Take Screenshot"
    F->>API: GET /api/v1/vnc/{session_id}/screenshot
    API->>VNC: Capture screenshot
    VNC-->>API: Return screenshot data
    API-->>F: Return screenshot

    %% Session History
    U->>F: View task history
    F->>API: GET /api/v1/sessions
    API->>DB: Query sessions
    DB-->>API: Return session list
    API-->>F: Return sessions
    F->>F: Update task history panel

    %% Load Previous Session
    U->>F: Click on previous task
    F->>API: GET /api/v1/messages/{session_id}/messages
    API->>DB: Query message history
    DB-->>API: Return messages
    API-->>F: Return chat history
    F->>F: Display previous conversation
```

## Real-time Streaming Flow

```mermaid
sequenceDiagram
    participant F as Frontend
    participant WS as WebSocket
    participant A as Agent Service
    participant C as Computer Use Agent

    F->>WS: Connect to /sessions/{id}/stream
    WS->>A: Register WebSocket
    
    loop Real-time Updates
        C->>A: Agent output
        A->>WS: Broadcast message
        WS->>F: Stream update
        F->>F: Update UI in real-time
        
        C->>A: Tool call
        A->>WS: Broadcast tool_call
        WS->>F: Stream tool call
        F->>F: Show "Tool: screenshot"
        
        C->>A: Tool result
        A->>WS: Broadcast tool_result
        WS->>F: Stream tool result
        F->>F: Show tool output
    end
```

## Architecture Components

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[HTML/JS Interface]
        VNC_UI[VNC Web Interface]
    end
    
    subgraph "API Layer"
        FastAPI[FastAPI Backend]
        WS[WebSocket Handler]
        REST[REST Endpoints]
    end
    
    subgraph "Service Layer"
        SS[Session Service]
        MS[Message Service]
        AS[Agent Service]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL)]
        Redis[(Redis)]
    end
    
    subgraph "Agent Layer"
        CUA[Computer Use Agent]
        Tools[Computer Tools]
        Loop[Agent Loop]
    end
    
    subgraph "VNC Layer"
        VNC[VNC Server]
        Desktop[Ubuntu Desktop]
        noVNC[noVNC Gateway]
    end
    
    subgraph "External"
        Claude[Claude API]
    end

    UI --> FastAPI
    VNC_UI --> noVNC
    FastAPI --> WS
    FastAPI --> REST
    REST --> SS
    REST --> MS
    WS --> AS
    SS --> PG
    MS --> PG
    AS --> Redis
    AS --> CUA
    CUA --> Tools
    CUA --> Loop
    Loop --> Claude
    Tools --> VNC
    VNC --> Desktop
    noVNC --> VNC
```

## Key Features Demonstrated

1. **Session Management**: Multiple concurrent sessions with persistent history
2. **Real-time Streaming**: WebSocket-based live updates from agent
3. **VNC Integration**: Embedded desktop view and screenshot capabilities
4. **Database Persistence**: All conversations and sessions stored
5. **Computer Use Tools**: Full integration with existing Anthropic tools
6. **REST API**: Complete CRUD operations for sessions and messages
