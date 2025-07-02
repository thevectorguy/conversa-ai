#!/usr/bin/env python3
"""
BiztelAI Docker Deployment Script with Ngrok Sharing
Simple one-command deployment with public URL
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def run_command(command, description, capture_output=True):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print(f"✅ {description} completed")
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=True)
            print(f"✅ {description} completed")
            return ""
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        if capture_output and e.stderr:
            print(f"   Error output: {e.stderr}")
        return None

def check_docker():
    """Check if Docker is installed and running"""
    print("🐳 Checking Docker installation...")
    
    # Check if docker command exists
    result = run_command("docker --version", "Checking Docker version")
    if result is None:
        print("❌ Docker is not installed. Please install Docker first.")
        return False
    
    # Check if Docker daemon is running
    result = run_command("docker info", "Checking Docker daemon", capture_output=True)
    if result is None:
        print("❌ Docker daemon is not running. Please start Docker.")
        return False
    
    print("✅ Docker is ready")
    return True

def check_docker_compose():
    """Check if Docker Compose is available"""
    print("🔧 Checking Docker Compose...")
    
    # Try docker compose (newer version)
    result = run_command("docker compose version", "Checking Docker Compose", capture_output=True)
    if result is not None:
        print("✅ Docker Compose (plugin) is available")
        return "docker compose"
    
    # Try docker-compose (older version)
    result = run_command("docker-compose --version", "Checking docker-compose", capture_output=True)
    if result is not None:
        print("✅ docker-compose is available")
        return "docker-compose"
    
    print("❌ Docker Compose is not available")
    return None

def build_and_deploy(compose_command, with_ngrok=False):
    """Build and deploy the application"""
    print("🚀 Building and deploying BiztelAI...")
    
    # Stop any existing containers
    run_command(f"{compose_command} down", "Stopping existing containers")
    
    # Build and start containers
    if with_ngrok:
        cmd = f"{compose_command} --profile sharing up --build -d"
        description = "Building and starting containers with ngrok"
    else:
        cmd = f"{compose_command} up --build -d"
        description = "Building and starting containers"
    
    result = run_command(cmd, description, capture_output=False)
    if result is None:
        return False
    
    print("⏳ Waiting for services to start...")
    time.sleep(10)
    
    return True

def check_health():
    """Check if the application is healthy"""
    print("🏥 Checking application health...")
    
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Application is healthy and ready!")
                return True
        except requests.RequestException:
            pass
        
        if i < max_retries - 1:
            print(f"   Attempt {i+1}/{max_retries} - waiting...")
            time.sleep(2)
    
    print("❌ Application health check failed")
    return False

def get_ngrok_url():
    """Get the ngrok public URL"""
    print("🌐 Getting ngrok public URL...")
    
    max_retries = 15
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get("tunnels", [])
                
                for tunnel in tunnels:
                    if tunnel.get("name") == "biztelai":
                        public_url = tunnel.get("public_url")
                        if public_url and public_url.startswith("https://"):
                            return public_url
                
                # Fallback: get any HTTPS tunnel
                for tunnel in tunnels:
                    public_url = tunnel.get("public_url")
                    if public_url and public_url.startswith("https://"):
                        return public_url
        except requests.RequestException:
            pass
        
        if i < max_retries - 1:
            print(f"   Attempt {i+1}/{max_retries} - waiting for ngrok...")
            time.sleep(2)
    
    return None

def show_deployment_info(with_ngrok=False, ngrok_url=None):
    """Show deployment information"""
    print("\n" + "="*60)
    print("🎉 BiztelAI Deployment Successful!")
    print("="*60)
    
    print("\n📍 Access URLs:")
    print(f"   🏠 Local:     http://localhost:8000")
    
    if with_ngrok and ngrok_url:
        print(f"   🌐 Public:    {ngrok_url}")
        print(f"   📊 Ngrok UI:  http://localhost:4040")
    elif with_ngrok:
        print("   ⚠️  Ngrok URL not available - check ngrok configuration")
        print("   📊 Ngrok UI:  http://localhost:4040")
    
    print("\n🔐 Demo Credentials:")
    print("   Username: demo     | Password: demo123")
    print("   Username: admin    | Password: admin123")
    
    print("\n🛠️  Management Commands:")
    print("   View logs:    docker-compose logs -f")
    print("   Stop:         docker-compose down")
    print("   Restart:      docker-compose restart")
    
    if with_ngrok and ngrok_url:
        print(f"\n📤 Share this URL with others: {ngrok_url}")
    
    print("\n" + "="*60)

def main():
    """Main deployment function"""
    print("BiztelAI Docker Deployment Script")
    print("="*40)
    
    # Check prerequisites
    if not check_docker():
        sys.exit(1)
    
    compose_command = check_docker_compose()
    if not compose_command:
        sys.exit(1)
    
    # Ask user about ngrok
    while True:
        choice = input("\nDo you want to enable public sharing via ngrok? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            with_ngrok = True
            break
        elif choice in ['n', 'no']:
            with_ngrok = False
            break
        else:
            print("Please enter 'y' or 'n'")
    
    if with_ngrok:
        print("\nNote: You need to configure ngrok.yml with your auth token")
        print("Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken")
        
        # Check if ngrok.yml has been configured
        ngrok_file = Path("ngrok.yml")
        if ngrok_file.exists():
            content = ngrok_file.read_text()
            if "YOUR_NGROK_AUTH_TOKEN_HERE" in content:
                print("\nWARNING: Please update ngrok.yml with your actual auth token!")
                choice = input("Continue anyway? (y/n): ").lower().strip()
                if choice not in ['y', 'yes']:
                    print("Please update ngrok.yml and run again.")
                    sys.exit(1)
    
    # Deploy
    if not build_and_deploy(compose_command, with_ngrok):
        print("Deployment failed!")
        sys.exit(1)
    
    # Check health
    if not check_health():
        print("Application is not responding!")
        sys.exit(1)
    
    # Get ngrok URL if enabled
    ngrok_url = None
    if with_ngrok:
        ngrok_url = get_ngrok_url()
    
    # Show success info
    show_deployment_info(with_ngrok, ngrok_url)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
