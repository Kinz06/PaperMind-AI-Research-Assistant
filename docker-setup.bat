@echo off
REM Docker setup script for PaperMind (Windows)

echo ================================
echo PaperMind Docker Setup
echo ================================
echo.

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running or not installed
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Create .env if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo WARNING: Please edit .env and configure your settings
    echo.
)

REM Build images
echo Building Docker images...
docker-compose build
if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo Starting PaperMind containers...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start containers
    pause
    exit /b 1
)

echo.
echo Waiting for Ollama to initialize...
timeout /t 15 /nobreak >nul

echo.
echo Downloading Llama model (this may take 5-10 minutes)...
docker exec papermind-ollama ollama pull llama3.2:3b

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Access PaperMind at: http://localhost:8501
echo.
echo Useful commands:
echo   View logs:     docker-compose logs -f papermind
echo   Stop:          docker-compose down
echo   Restart:       docker-compose restart
echo.
pause