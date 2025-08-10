# VNCagentic Quick Start Guide

Get VNCagentic up and running in 5 minutes with this step-by-step guide.

## 🚀 Prerequisites Check

Before starting, ensure you have:

- ✅ **Docker** & **Docker Compose** installed
- ✅ **4GB RAM** available
- ✅ **Comet API Key** (for LLM integration)
- ✅ **Ports available**: 3000, 6080, 8000, 8090

## 📥 Step 1: Download & Setup

```bash
# Clone the repository
git clone <repository-url>
cd VNCagentic

# Copy environment template
cp .env.example .env
```

## ⚙️ Step 2: Configure Environment

Edit `.env` file with your settings:

```bash
# Required: Add your Comet API key
COMET_API_KEY=your_actual_comet_api_key_here
COMET_API_BASE_URL=https://api.comet.ml

# Database settings (keep defaults for quick start)
POSTGRES_PASSWORD=quickstart_password
DATABASE_URL=postgresql+asyncpg://postgres:quickstart_password@postgres:5432/vncagentic

# Other settings (defaults are fine)
LOG_LEVEL=INFO
```

**📝 Note**: Get your Comet API key from your Comet ML account dashboard.

## 🐳 Step 3: Launch Services

```bash
# Build and start all containers
docker-compose up --build -d

# This will start:
# - Backend API (FastAPI)
# - VNC Desktop Environment  
# - PostgreSQL Database
# - Redis Cache
# - Frontend Web Interface
```

## ⏳ Step 4: Wait for Startup

Monitor the startup process:

```bash
# Check all services are running
docker-compose ps

# Watch logs (optional)
docker-compose logs -f
```

Wait until you see:
- ✅ Backend: "Application startup complete"
- ✅ Database: "database system is ready to accept connections"
- ✅ VNC Agent: Container is healthy

## 🌐 Step 5: Access the Application

Open these URLs in your browser:

### Chat Interface
```
http://localhost:3000
```
- Main chat interface for sending commands
- Real-time conversation with AI agent
- Session and message history

### VNC Desktop
```
http://localhost:6080
```
- Live desktop view in your browser
- Visual confirmation of command execution
- Direct interaction with applications

### VNC API (Direct Command Execution)
```
http://localhost:8090/execute
```
- Direct HTTP API for command execution
- Used internally by the backend
- Test endpoint for debugging

### Backend API Documentation
```
http://localhost:8000/docs
```
- Interactive API documentation
- Test endpoints directly
- View request/response schemas
- Live desktop view in your browser
- See applications open and close in real-time
- Visual feedback for all commands

### API Documentation
```
http://localhost:8000/docs
```
- Interactive API documentation
- Test endpoints directly
- View request/response schemas

## 🎮 Step 6: Test Basic Commands

Try these commands in the chat interface at `http://localhost:3000`:

### Simple Application Launch
```
User: open calculator
Expected: Calculator opens in VNC desktop

User: open firefox  
Expected: Firefox browser opens
```

### Complex Multi-Step Commands
```
User: open firefox and search weather jakarta
Expected: Firefox opens, navigates to address bar, types search term, presses enter

User: open calculator and firefox
Expected: Both calculator and Firefox open
```

### Text Input Commands
```
User: type hello world
Expected: Types "hello world" in active window

User: tekan enter
Expected: Presses Enter key
```

## ✅ Verification Checklist

After setup, verify everything works:

### Backend Health Check
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}
```

### Chat API Test
```bash
curl -X POST http://localhost:8000/api/simple/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"open calculator"}'
# Should return JSON with commands and execution results
```

### VNC Agent Test
```bash
curl -X POST http://localhost:8090/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"echo test"}'
# Should return: {"success": true, ...}
```

### Visual Verification
1. Open chat interface: http://localhost:3000
2. Open VNC desktop: http://localhost:6080  
3. Send command: "open calculator"
4. Verify calculator appears in VNC desktop

## 🔧 Troubleshooting Quick Fixes

### Port Already in Use
```bash
# Check what's using the port
netstat -tlnp | grep 8000

# Kill the process or change port in docker-compose.yml
```

### Container Won't Start
```bash
# Check logs for specific service
docker-compose logs backend
docker-compose logs vnc-agent

# Restart specific service
docker-compose restart backend
```

### VNC API Not Responding
```bash
# Restart VNC API server
docker exec -d vncagentic-vnc-agent-1 bash -c "cd /home/computeruse && python3 vnc_api.py"

# Verify it's running
docker exec vncagentic-vnc-agent-1 ps aux | grep vnc_api
```

### Database Connection Error
```bash
# Check PostgreSQL is healthy
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

### AI Commands Not Working
1. Verify your Comet API key is correct in `.env`
2. Check backend logs: `docker-compose logs backend`
3. Ensure internet connection for API calls
4. Try simple fallback commands (should work without API)

## 🎯 Next Steps

Once you have the basic setup working:

1. **Read the Full Documentation**
   - [README.md](../README.md) - Complete project overview
   - [docs/API.md](../docs/API.md) - API reference
   - [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System design

2. **Explore More Commands**
   - Try complex workflows
   - Test different applications
   - Experiment with mouse and keyboard control

3. **Production Deployment**
   - See [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md) for production setup
   - Configure SSL/TLS
   - Set up monitoring and backups

4. **Customize and Extend**
   - Add new applications to VNC environment
   - Modify AI prompts for better responses
   - Integrate with other LLM providers

## 📞 Need Help?

- **Issues**: Create GitHub issue for bugs
- **Questions**: Check existing documentation first
- **Feature Requests**: Use GitHub discussions

---

**Congratulations!** 🎉 You now have VNCagentic running and can control desktop applications through natural language commands.
