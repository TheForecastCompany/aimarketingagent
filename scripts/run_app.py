#!/usr/bin/env python3
"""
Enhanced Entry Point for Video Content Repurposing Agency
Multi-process orchestrator: Python backend + Next.js frontend
"""

import sys
import os
import subprocess
import socket
import signal
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config/.env
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / "config" / ".env")

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

def check_dependencies():
    """Check if required dependencies are available"""
    PROJECT_ROOT = Path(__file__).parent.parent
    frontend_path = PROJECT_ROOT / "frontend"
    
    # Check if frontend directory exists
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if package.json exists
    if not (frontend_path / "package.json").exists():
        print("❌ package.json not found in frontend directory")
        return False
    
    # Check if node_modules exists
    if not (frontend_path / "node_modules").exists():
        print("📦 node_modules not found. Dependencies need to be installed.")
        return False
    
    return True

def install_frontend_dependencies():
    """Install frontend dependencies"""
    PROJECT_ROOT = Path(__file__).parent.parent
    frontend_path = PROJECT_ROOT / "frontend"
    
    print("📦 Installing Next.js dependencies...")
    install_cmd = ["npm", "install"]
    
    try:
        result = subprocess.run(install_cmd, cwd=str(frontend_path), capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Dependency installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def start_backend():
    """Start the Python backend server"""
    PROJECT_ROOT = Path(__file__).parent.parent
    BACKEND_ROOT = PROJECT_ROOT / "backend"
    
    # Find available port for backend
    backend_port = find_available_port(8000, 8100)
    if not backend_port:
        print("❌ No available ports found for backend")
        return None
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)  # Set to project root, not backend root
    env["BACKEND_PORT"] = str(backend_port)
    
    # Start backend using uvicorn
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "0.0.0.0",
        "--port", str(backend_port),
        "--reload",
        "--timeout-keep-alive", "600",  # 10 minutes keep-alive
        "--timeout-graceful-shutdown", "30"  # 30 seconds graceful shutdown
    ]
    
    print(f"🚀 Starting Python backend on port {backend_port}")
    print(f"📁 Backend: {BACKEND_ROOT}")
    
    try:
        process = subprocess.Popen(backend_cmd, cwd=str(BACKEND_ROOT), env=env)
        time.sleep(2)  # Give backend time to start
        if process.poll() is None:
            print(f"✅ Backend started successfully at http://localhost:{backend_port}")
            return process, backend_port
        else:
            print("❌ Backend failed to start")
            return None
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the Next.js frontend server"""
    PROJECT_ROOT = Path(__file__).parent.parent
    frontend_path = PROJECT_ROOT / "frontend"
    
    # Start Next.js development server
    frontend_cmd = ["npm", "run", "dev"]
    
    print(f"🚀 Starting Next.js development server")
    print(f"📁 Frontend: {frontend_path}")
    print(f"🌐 Next.js app will be available at: http://localhost:3000")
    
    try:
        process = subprocess.Popen(frontend_cmd, cwd=str(frontend_path))
        time.sleep(3)  # Give frontend time to start
        if process.poll() is None:
            print("✅ Frontend started successfully")
            return process
        else:
            print("❌ Frontend failed to start")
            return None
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def cleanup_processes(processes):
    """Clean up all child processes"""
    for process in processes:
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except:
                pass

def main():
    """Main entry point - orchestrates both backend and frontend"""
    
    print("🎬 Video Content Repurposing Agency - Full Stack Launcher")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n💡 Some dependencies are missing. Attempting to install...")
        if not install_frontend_dependencies():
            print("❌ Failed to install dependencies. Please run 'npm install' manually in the frontend directory.")
            sys.exit(1)
        
        # Check again after installation
        if not check_dependencies():
            print("❌ Dependencies still not available after installation.")
            sys.exit(1)
    
    # Store processes for cleanup
    processes = []
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Shutting down gracefully...")
        cleanup_processes(processes)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start backend
        backend_result = start_backend()
        if not backend_result:
            print("❌ Failed to start backend")
            sys.exit(1)
        
        backend_process, backend_port = backend_result
        processes.append(backend_process)
        
        # Start frontend
        frontend_process = start_frontend()
        if not frontend_process:
            print("❌ Failed to start frontend")
            cleanup_processes(processes)
            sys.exit(1)
        
        processes.append(frontend_process)
        
        print("\n✅ Full stack application is running!")
        print(f"🔗 Backend API: http://localhost:{backend_port}")
        print("🔗 Frontend: http://localhost:3000")
        print("\nPress Ctrl+C to stop all services")
        
        # Keep the main process alive and monitor child processes
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for i, process in enumerate(processes):
                if process and process.poll() is not None:
                    service_name = "Backend" if i == 0 else "Frontend"
                    print(f"❌ {service_name} process has stopped unexpectedly")
                    cleanup_processes(processes)
                    sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        cleanup_processes(processes)

if __name__ == "__main__":
    main()
