@echo off
setlocal
title README.AI - Start Local App
cd /d "%~dp0"

where docker >nul 2>&1
if errorlevel 1 (
    echo Docker Desktop is required. Install it and start it, then double-click this file again.
    pause
    exit /b 1
)
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker Desktop is not running. Start Docker Desktop and try again.
    pause
    exit /b 1
)
docker compose version >nul 2>&1
if errorlevel 1 (
    echo Docker Compose is unavailable. Update Docker Desktop and try again.
    pause
    exit /b 1
)
if not exist "docker-compose.yml" (
    echo Run this launcher from the extracted Readme-Ai-Studio project folder.
    echo Download the source ZIP from the repository README and extract it first.
    pause
    exit /b 1
)
if not exist ".env" (
    if not exist ".env.example" (
        echo Missing .env.example. Download the complete project and try again.
        pause
        exit /b 1
    )
    copy /y ".env.example" ".env" >nul
    if errorlevel 1 (
        echo Could not create .env. Check folder write permissions.
        pause
        exit /b 1
    )
)
echo Starting README.AI...
echo The first launch downloads dependencies and builds the app. Keep this window open.
docker compose -p readme-ai-studio up -d --build
if errorlevel 1 (
    echo Startup failed. Review the Docker error above and try again.
    pause
    exit /b 1
)
echo Waiting for http://localhost:8080 ...
powershell -NoProfile -Command "$ready=$false; for($attempt=0; $attempt -lt 90; $attempt++){try{$response=Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:8080' -TimeoutSec 2; if($response.StatusCode -eq 200){$ready=$true; break}}catch{}; Start-Sleep -Seconds 2}; if(-not $ready){exit 1}"
if errorlevel 1 (
    echo The app did not become ready. Check Docker Desktop container logs.
    pause
    exit /b 1
)
start "" "http://localhost:8080"
echo README.AI is running at http://localhost:8080
echo The containers keep running after this window closes.
echo To stop them, run: docker compose -p readme-ai-studio stop
timeout /t 5 >nul
exit /b 0
