#!/bin/bash

echo "========================================"
echo "BiztelAI Docker Deployment Script"
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker first:"
    echo "  macOS: https://desktop.docker.com/mac/main/amd64/Docker.dmg"
    echo "  Linux: curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
    exit 1
fi

echo "[+] Docker is installed"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker is not running"
    echo "Please start Docker and try again."
    exit 1
fi

echo "[+] Docker is running"

# Check for Docker Compose
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "ERROR: Docker Compose is not available"
    exit 1
fi

echo "[+] Docker Compose is available"

# Ask about ngrok
read -p "Do you want to enable public sharing via ngrok? (y/n): " use_ngrok

if [[ $use_ngrok =~ ^[Yy]$ ]]; then
    echo "[*] Deploying with ngrok for public sharing..."
    echo "[!] Make sure you've configured your ngrok auth token in ngrok.yml"
    echo "[!] Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken"
    read -p "Press Enter to continue..."
    
    $COMPOSE_CMD down
    $COMPOSE_CMD --profile sharing up --build -d
else
    echo "[*] Deploying locally only..."
    $COMPOSE_CMD down
    $COMPOSE_CMD up --build -d
fi

echo "[*] Waiting for services to start..."
sleep 15

echo "[*] Checking application health..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "[+] Application is healthy!"
        break
    fi
    echo "[*] Attempt $i/10 - waiting..."
    sleep 3
done

if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "[-] Application health check failed"
    echo "Showing recent logs:"
    $COMPOSE_CMD logs --tail=50
    exit 1
fi

echo ""
echo "========================================"
echo "   BiztelAI Deployment Successful!"
echo "========================================"
echo ""
echo "Access URLs:"
echo "  Local:     http://localhost:8000"
if [[ $use_ngrok =~ ^[Yy]$ ]]; then
    echo "  Ngrok UI:  http://localhost:4040"
fi
echo ""
echo "Demo Credentials:"
echo "  Username: demo     | Password: demo123"
echo "  Username: admin    | Password: admin123"
echo ""
if [[ $use_ngrok =~ ^[Yy]$ ]]; then
    echo "Check http://localhost:4040 for your public HTTPS URL"
    echo "Share that URL with others to let them use your tool!"
fi
echo ""
echo "Management Commands:"
echo "  View logs:    $COMPOSE_CMD logs -f"
echo "  Stop:         $COMPOSE_CMD down"
echo "  Restart:      $COMPOSE_CMD restart"
echo ""
echo "========================================"
