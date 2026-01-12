#!/usr/bin/env python3
"""
Run Backend with Detailed Logging
Starts the backend server with comprehensive logging for video processing
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
load_dotenv(PROJECT_ROOT / "config" / ".env")

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set specific logger levels
logging.getLogger('uvicorn').setLevel(logging.INFO)
logging.getLogger('fastapi').setLevel(logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)

def main():
    """Start backend with detailed logging"""
    print("🚀 Starting Backend with Detailed Logging")
    print("=" * 50)
    print("📝 Logs will be saved to: backend.log")
    print("🌐 Backend will run on: http://localhost:8000")
    print("🔍 Monitoring video processing requests...")
    print()
    
    import uvicorn
    from main import app
    
    # Run with detailed logging
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        access_log=True,
        use_colors=True
    )

if __name__ == "__main__":
    main()
