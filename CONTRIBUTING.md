# Contributing to VNCagentic

Thank you for your interest in contributing to VNCagentic! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Code Standards](#code-standards)

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Python 3.11+ (for local development)
- Node.js (optional, for frontend tooling)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone https://github.com/your-username/VNCagentic.git
cd VNCagentic
```

3. Add the original repository as upstream:
```bash
git remote add upstream https://github.com/original-owner/VNCagentic.git
```

## Development Setup

### Environment Setup

1. Copy environment template:
```bash
cp .env.example .env
```

2. Configure your API keys and settings in `.env`

3. Start development environment:
```bash
docker-compose up --build -d
```

### Development Workflow

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes following our [code standards](#code-standards)

3. Test your changes:
```bash
# Run backend tests
docker-compose exec backend python -m pytest

# Test API endpoints
curl -X POST http://localhost:8000/api/simple/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test command"}'
```

4. Commit your changes:
```bash
git add .
git commit -m "feat: add new feature description"
```

## Contributing Guidelines

### What We Welcome

- Bug fixes and improvements
- New desktop applications support
- Performance optimizations
- Documentation improvements
- Test coverage enhancements
- Security improvements
- UI/UX enhancements

### Areas for Contribution

#### Backend Development
- AI agent improvements
- New LLM provider integrations
- API endpoint enhancements
- Database optimization
- Error handling improvements

#### Frontend Development
- UI/UX improvements
- Mobile responsiveness
- Accessibility features
- Performance optimizations
- New interface features

#### VNC Agent Development
- New application integrations
- Command execution improvements
- Desktop environment enhancements
- Screenshot functionality
- Performance optimizations

#### Documentation
- README improvements
- API documentation
- Architecture documentation
- Deployment guides
- Tutorial creation

#### Infrastructure
- Docker improvements
- CI/CD pipeline setup
- Monitoring and logging
- Security enhancements
- Performance monitoring

## Pull Request Process

### Before Submitting

1. Ensure your code follows our [code standards](#code-standards)
2. Add tests for new functionality
3. Update documentation as needed
4. Verify all tests pass
5. Check that your changes don't break existing functionality

### PR Guidelines

1. **Title**: Use conventional commit format
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `refactor:` for code refactoring
   - `test:` for adding tests

2. **Description**: Provide clear description of:
   - What changes were made
   - Why the changes were necessary
   - How to test the changes
   - Any breaking changes

3. **Testing**: Include evidence that your changes work:
   - Screenshots for UI changes
   - Test results for backend changes
   - API testing examples

### Review Process

1. Automated checks must pass
2. At least one maintainer review required
3. All conversations must be resolved
4. Documentation must be updated if needed
5. Changes must be tested in development environment

## Issue Reporting

### Bug Reports

Use the bug report template and include:

- **Environment**: OS, Docker version, browser
- **Steps to Reproduce**: Detailed step-by-step instructions
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Screenshots**: If applicable
- **Logs**: Relevant error messages or logs

### Feature Requests

Use the feature request template and include:

- **Problem**: What problem does this solve?
- **Solution**: Describe your proposed solution
- **Alternatives**: Other solutions you've considered
- **Use Case**: Real-world usage scenarios

### Questions

For questions:
- Check existing documentation first
- Search existing issues
- Use discussions for general questions
- Create issue only for specific problems

## Code Standards

### Python (Backend)

```python
# Use type hints
def process_message(self, user_message: str) -> Dict[str, Any]:
    pass

# Use async/await for I/O operations
async def execute_command(self, command: str) -> Dict[str, Any]:
    pass

# Use descriptive variable names
user_input = message.strip().lower()
execution_results = []

# Use docstrings for functions
def extract_commands(self, response: str) -> List[str]:
    """Extract xdotool commands from AI response.
    
    Args:
        response: AI response containing commands
        
    Returns:
        List of extracted commands
    """
    pass
```

### JavaScript (Frontend)

```javascript
// Use const/let instead of var
const apiEndpoint = '/api/simple/chat';
let sessionId = localStorage.getItem('sessionId');

// Use descriptive function names
function sendMessageToAgent(message) {
    // Implementation
}

// Use promises/async-await
async function loadChatHistory() {
    try {
        const response = await fetch(`/api/sessions/${sessionId}/messages`);
        return await response.json();
    } catch (error) {
        console.error('Failed to load chat history:', error);
    }
}
```

### Docker

```dockerfile
# Use multi-stage builds
FROM python:3.11-slim as builder
# Build stage

FROM python:3.11-slim as runtime
# Runtime stage

# Use non-root user
RUN useradd -m appuser
USER appuser

# Set proper labels
LABEL maintainer="your-email@example.com"
LABEL version="1.0.0"
```

### Documentation

- Use clear, concise language
- Include code examples
- Keep README up to date
- Document API changes
- Add inline comments for complex logic

### Git Commits

Follow conventional commit format:

```bash
feat: add new desktop application support
fix: resolve VNC connection timeout issue
docs: update API documentation
refactor: improve AI agent response parsing
test: add unit tests for command execution
```

### Testing

```python
# Write unit tests for new functions
def test_extract_commands():
    agent = AIGenerativeAgent("test-session")
    response = '{"commands": ["echo test"]}'
    commands = agent._extract_xdotool_commands(response)
    assert commands == ["echo test"]

# Write integration tests for API endpoints
async def test_chat_endpoint():
    response = await client.post("/api/simple/chat", 
                               json={"message": "test"})
    assert response.status_code == 200
```

## Development Environment

### Local Backend Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r backend/requirements.txt

# Run backend locally
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Serve frontend locally
cd frontend
python -m http.server 3000

# Or with live reload (if using Node.js tools)
npm install -g live-server
live-server --port=3000
```

### Database Development

```bash
# Run PostgreSQL in Docker
docker run -d \
  --name postgres-dev \
  -e POSTGRES_PASSWORD=dev_password \
  -e POSTGRES_DB=vncagentic \
  -p 5432:5432 \
  postgres:15

# Connect to database
psql -h localhost -U postgres -d vncagentic
```

## Release Process

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create release branch
4. Test release candidate
5. Create GitHub release
6. Deploy to production

## Getting Help

- **Documentation**: Check docs/ directory
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub discussions for questions
- **Contact**: Create issue for specific problems

Thank you for contributing to VNCagentic! 🚀
