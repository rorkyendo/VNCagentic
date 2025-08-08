@echo off
REM VNCagentic Setup Script for Windows

echo 🚀 Setting up VNCagentic...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file and add your ANTHROPIC_API_KEY
)

REM Create necessary directories
echo 📁 Creating directories...
mkdir backend\logs 2>nul
mkdir frontend\dist 2>nul
mkdir data\postgres 2>nul
mkdir data\redis 2>nul

echo ✅ Setup completed!
echo.
echo Next steps:
echo 1. Edit .env file and add your ANTHROPIC_API_KEY
echo 2. Run: docker-compose up -d
echo 3. Access the application at http://localhost:8080
echo.
echo Useful commands:
echo - View logs: docker-compose logs -f
echo - Stop services: docker-compose down
echo - Rebuild: docker-compose build --no-cache

pause
