@echo off
echo ========================================
echo BiztelAI Docker Deployment Script
echo ========================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://desktop.docker.com/win/main/amd64/Docker%%20Desktop%%20Installer.exe
    echo After installation, restart your computer and try again.
    pause
    exit /b 1
)

echo [+] Docker is installed

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [+] Docker is running

REM Ask about ngrok
set /p "use_ngrok=Do you want to enable public sharing via ngrok? (y/n): "
if /i "%use_ngrok%"=="y" goto :deploy_with_ngrok
if /i "%use_ngrok%"=="yes" goto :deploy_with_ngrok

:deploy_local
echo [*] Deploying locally only...
docker compose down
docker compose up --build -d
goto :check_health

:deploy_with_ngrok
echo [*] Deploying with ngrok for public sharing...
echo [*] Configuring ngrok with auth token...

REM Update ngrok.yml with the auth token
(
echo version: "2"
echo authtoken: 2vfvoxYVYaI3VkTwd0pdkWqNAjm_78xAib8VKdMLKkxvJWJrd
echo tunnels:
echo   biztelai:
echo     addr: web:8000
echo     proto: http
echo     schemes: [https, http]
echo     host_header: localhost:8000
echo     inspect: true
echo web_addr: 0.0.0.0:4040
) > ngrok.yml

echo [+] Ngrok configured successfully
docker compose down
docker compose --profile sharing up --build -d

:check_health
echo [*] Waiting for services to start...
timeout /t 15 /nobreak >nul

echo [*] Checking application health...
for /l %%i in (1,1,10) do (
    curl -s http://localhost:8000/health >nul 2>&1
    if !errorlevel! equ 0 (
        echo [+] Application is healthy!
        goto :success
    )
    echo [*] Attempt %%i/10 - waiting...
    timeout /t 3 /nobreak >nul
)

echo [-] Application health check failed
goto :show_logs

:success
echo.
echo ========================================
echo   BiztelAI Deployment Successful!
echo ========================================
echo.
echo Access URLs:
echo   Local:     http://localhost:8000
if /i "%use_ngrok%"=="y" echo   Ngrok UI:  http://localhost:4040
echo.
echo Demo Credentials:
echo   Username: demo     ^| Password: demo123
echo   Username: admin    ^| Password: admin123
echo.
if /i "%use_ngrok%"=="y" (
    echo Check http://localhost:4040 for your public HTTPS URL
    echo Share that URL with others to let them use your tool!
)
echo.
echo Management Commands:
echo   View logs:    docker compose logs -f
echo   Stop:         docker compose down
echo   Restart:      docker compose restart
echo.
echo ========================================
goto :end

:show_logs
echo.
echo Showing recent logs (press Ctrl+C to exit):
docker compose logs --tail=50

:end
pause
