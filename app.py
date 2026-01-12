#!/usr/bin/env python3
"""
AI Marketing Agent - Main Entry Point
This is the main entry point for the application.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path (not just backend)
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

if __name__ == "__main__":
    # Import and run the main application
    from backend.main import app
    import uvicorn
    
    print("🎬 AI Marketing Agent - Starting Application")
    print("=" * 50)
    
    # Run the FastAPI application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
