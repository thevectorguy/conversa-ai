#!/usr/bin/env python3
"""
Development runner script for BiztelAI
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run the development server"""
    
    # Check if data file exists
    data_file = project_root / "data" / "BiztelAI_DS_Dataset_V1.json"
    if not data_file.exists():
        print("⚠️  Warning: Dataset file not found!")
        print(f"   Please place your dataset at: {data_file}")
        print("   The application may not work properly without it.")
        print()
    
    # Use port 12000 for the runtime environment
    port = 12000
    
    print("🚀 Starting BiztelAI Development Server...")
    print(f"📊 Dashboard: http://localhost:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    print("🔐 Demo Login: demo/demo123")
    print()
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            reload_dirs=["app"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down BiztelAI...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
