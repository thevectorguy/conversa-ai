#!/usr/bin/env python3
"""
Setup script for BiztelAI project
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def setup_project():
    """Setup the BiztelAI project"""
    print("🚀 Setting up BiztelAI Project...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Check for dataset
    data_file = Path("data/BiztelAI_DS_Dataset_V1.json")
    if not data_file.exists():
        print("⚠️  Dataset file not found!")
        print(f"   Please place your dataset at: {data_file.absolute()}")
        print("   You can continue setup, but the app won't work without the dataset.")
        
        response = input("   Continue anyway? (y/N): ").lower().strip()
        if response != 'y':
            print("   Setup cancelled. Please add the dataset and run setup again.")
            return False
    else:
        print("✅ Dataset file found")
    
    # Create necessary directories
    directories = ["logs", "static/images"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Review and update .env file with your settings")
    print("   2. Run the application: python run.py")
    print("   3. Open http://localhost:8000 in your browser")
    print("   4. Login with demo/demo123")
    print("\n🐳 For Docker deployment:")
    print("   docker-compose up --build")
    
    return True

def main():
    """Main setup function"""
    try:
        success = setup_project()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
