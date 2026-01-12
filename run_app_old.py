#!/usr/bin/env python3
"""
Enhanced Entry Point for Video Content Repurposing Agency
Primary interface: Next.js frontend in /frontend. directory
"""

import sys
import os
import subprocess
import socket
from pathlib import Path

def find_available_port(start_port=8501, max_port=8600):
    """Find an available port in the given range"""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def run_command_with_retry(cmd, cwd, max_retries=3, retry_delay=2):
    """Run a command with retry logic"""
    for attempt in range(max_retries):
        try:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Command succeeded: {' '.join(cmd)}")
                return result
            else:
                print(f"⚠️ Command failed (attempt {attempt + 1}/{max_retries}): {' '.join(cmd)}")
                if attempt < max_retries - 1:
                    print(f"🔄 Retrying in {retry_delay} seconds...")
                    import time
                    time.sleep(retry_delay)
        except Exception as e:
            print(f"❌ Error running command: {e}")
            return None
    return None

def main():
    """Main entry point with frontend selection"""
    
    # Get project root directory
    PROJECT_ROOT = Path(__file__).parent
    
    # Detect and activate virtual environment
    venv_python = None
    venv_paths = [
        PROJECT_ROOT / ".venv" / "bin" / "python",
        PROJECT_ROOT / ".venv" / "bin" / "python",
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe",  # Windows
    ]
    
    for path in venv_paths:
        if path.exists():
            venv_python = str(path)
            break
    
    if not venv_python:
        print("⚠️  No virtual environment found. Using system Python.")
        venv_python = sys.executable
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    
    # Find available port
    port = find_available_port()
    if not port:
        print("❌ No available ports found in range 8501-8600")
        sys.exit(1)
    
    # Frontend selection - default to Next.js (new professional frontend)
    frontend_choice = os.getenv("FRONTEND", "nextjs").lower()
    
    if frontend_choice == "nextjs":
        # Launch Next.js (new professional frontend)
        frontend_path = PROJECT_ROOT / "frontend"
        
        # Check if Next.js project exists
        if not (frontend_path / "package.json").exists():
            print("❌ Next.js frontend not found. Please ensure frontend. directory exists.")
            print("💡 Run 'npm install' in frontend. directory first.")
            sys.exit(1)
        
        # Check if node_modules exists
        if not (frontend_path / "node_modules").exists():
            print("📦 Installing Next.js dependencies...")
            install_cmd = ["npm", "install"]
            install_result = run_command_with_retry(install_cmd, cwd=str(frontend_path))
            
            if install_result and install_result.returncode == 0:
                print("✅ Dependencies installed successfully")
            else:
                print("⚠️ Dependency installation failed. Please check the logs above.")
                sys.exit(1)
        
        # Start Next.js development server
        cmd = [
            "npm", "run",
            "--", "dev"
        ]
        
        print(f"🚀 Starting Next.js development server with: npm")
        print(f"📁 Frontend: {frontend_path}")
        print(f"🌐 Next.js app will be available at: http://localhost:3000")
        
        # Keep server running
        try:
            subprocess.run(cmd, cwd=str(frontend_path), check=True)
        except KeyboardInterrupt:
            print("\n👋 Application stopped by user")
        except Exception as e:
            print(f"❌ Error running Next.js app: {e}")
        
    else:
        print(f"❌ Unknown frontend choice: {frontend_choice}")
        print("💡 Set FRONTEND environment variable to 'streamlit' or 'nextjs'")
        sys.exit(1)

if __name__ == "__main__":
    main()
