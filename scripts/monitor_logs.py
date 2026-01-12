#!/usr/bin/env python3
"""
Real-time Log Monitor
Monitors backend logs for video processing activity
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def monitor_backend_log(log_file="backend.log"):
    """Monitor backend log file in real-time"""
    print(f"🔍 Monitoring Backend Logs: {log_file}")
    print("=" * 50)
    print("Waiting for video processing activity...")
    print("Press Ctrl+C to stop monitoring\n")
    
    try:
        # Use tail -f to follow the log file
        process = subprocess.Popen(
            ['tail', '-f', log_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True
        )
        
        # Filter for important log messages
        keywords = [
            "🎬 Video processing request",
            "🎙️ Transcription Details",
            "📝 Generated Content",
            "💰 Cost Metrics",
            "🎉 Video processing completed",
            "❌ Processing failed",
            "✅",
            "❌"
        ]
        
        for line in iter(process.stdout.readline, ''):
            if any(keyword in line for keyword in keywords):
                print(line.strip())
            
    except KeyboardInterrupt:
        print("\n👋 Log monitoring stopped")
        process.terminate()
    except FileNotFoundError:
        print(f"❌ Log file not found: {log_file}")
        print("Start the backend first with: python run_backend_with_logs.py")

def monitor_system_processes():
    """Monitor system processes for backend activity"""
    print("\n🔧 Monitoring System Processes")
    print("=" * 40)
    
    try:
        # Check if backend is running
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        backend_processes = [line for line in result.stdout.split('\n') if 'python' in line and ('main.py' in line or 'uvicorn' in line)]
        
        if backend_processes:
            print("✅ Backend processes found:")
            for process in backend_processes:
                print(f"   {process}")
        else:
            print("❌ No backend processes running")
            
        # Check Ollama
        ollama_processes = [line for line in result.stdout.split('\n') if 'ollama' in line]
        if ollama_processes:
            print("✅ Ollama processes found:")
            for process in ollama_processes[:3]:  # Show first 3
                print(f"   {process}")
        else:
            print("❌ No Ollama processes running")
            
    except Exception as e:
        print(f"❌ Error monitoring processes: {e}")

def check_recent_logs(log_file="backend.log", lines=50):
    """Show recent log entries"""
    print(f"\n📋 Recent Log Entries (last {lines} lines)")
    print("=" * 50)
    
    try:
        if os.path.exists(log_file):
            result = subprocess.run(['tail', f'-{lines}', log_file], capture_output=True, text=True)
            print(result.stdout)
        else:
            print(f"❌ Log file not found: {log_file}")
    except Exception as e:
        print(f"❌ Error reading logs: {e}")

def main():
    """Main log monitoring function"""
    print("🔍 Backend Log Monitor")
    print("=" * 40)
    
    # Check system processes
    monitor_system_processes()
    
    # Show recent logs
    check_recent_logs()
    
    # Start real-time monitoring
    monitor_backend_log()

if __name__ == "__main__":
    main()
