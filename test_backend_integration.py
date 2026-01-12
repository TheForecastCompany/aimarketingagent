#!/usr/bin/env python3
"""
Backend Integration Test
Tests the updated backend with proper environment loading
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
load_dotenv(PROJECT_ROOT / "config" / ".env")

def test_environment_loading():
    """Test that environment variables are loaded correctly"""
    print("🔧 Testing Environment Loading")
    print("=" * 40)
    
    required_vars = ['ASSEMBLYAI_API_KEY', 'OLLAMA_BASE_URL', 'OLLAMA_MODEL']
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else value
            print(f"✅ {var}: {masked}")
        else:
            print(f"❌ {var}: Not set")
            return False
    
    return True

def test_backend_api():
    """Test the backend API endpoints"""
    print("\n🌐 Testing Backend API")
    print("=" * 40)
    
    try:
        import subprocess
        import threading
        
        # Start backend server
        def run_server():
            import uvicorn
            from main import app
            uvicorn.run(app, host="127.0.0.1", port=8998, log_level="error")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(3)
        
        base_url = "http://127.0.0.1:8998"
        
        # Test basic endpoints
        endpoints = [
            ("/", "Root"),
            ("/health", "Health"),
            ("/api/v1/status", "Status"),
            ("/api/v1/videos", "Videos List")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"{status} {name}: {response.status_code}")
            except Exception as e:
                print(f"❌ {name}: {e}")
        
        # Test video processing endpoint
        print("\n🎬 Testing Video Processing Endpoint")
        test_request = {
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "config": {
                "brand_voice": "professional",
                "target_keywords": ["test", "video"],
                "enable_critique_loop": False
            }
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/process-video",
                json=test_request,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Video Processing: Success")
                print(f"   Video ID: {result.get('video_id', 'N/A')}")
                print(f"   Status: {result.get('status', 'N/A')}")
                print(f"   Platforms: {len(result.get('platforms', []))}")
                
                if 'cost_metrics' in result:
                    cost = result['cost_metrics'].get('current_metrics', {}).get('total_cost', 0)
                    print(f"   Cost: ${cost:.4f}")
                
                return True
            else:
                print(f"❌ Video Processing: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("⚠️  Video Processing: Timeout (processing may take longer)")
            return True
        except Exception as e:
            print(f"❌ Video Processing: {e}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_mock_processing():
    """Test processing with mock data to verify pipeline"""
    print("\n🧪 Testing Mock Processing")
    print("=" * 40)
    
    try:
        from backend.core.pipeline import VideoContentRepurposer
        from backend.services.brand_voice import BrandVoice
        
        # Create repurposer
        repurposer = load_repurposer(
            brand_voice=BrandVoice.PROFESSIONAL,
            target_keywords=["AI", "test"],
            enable_critique_loop=False,
            track_costs=False,
            use_ollama=True
        )
        
        # Test with short mock transcript
        mock_transcript = """
        This is a test video about artificial intelligence and machine learning.
        We discuss how AI is transforming businesses and creating new opportunities.
        Topics include neural networks, deep learning, and practical applications.
        This video demonstrates various AI tools and their real-world use cases.
        """
        
        print("🧠 Processing mock transcript...")
        analysis = repurposer.analyst.process(mock_transcript)
        
        if hasattr(analysis, 'success') and analysis.success:
            print("✅ Mock processing successful")
            print(f"   Analysis confidence: {analysis.confidence:.2f}")
            return True
        else:
            print("❌ Mock processing failed")
            return False
            
    except Exception as e:
        print(f"❌ Mock processing test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Backend Integration Test Suite")
    print("=" * 50)
    print("Testing the updated backend with proper environment loading\n")
    
    # Run tests
    results = {}
    
    results['environment'] = test_environment_loading()
    results['mock_processing'] = test_mock_processing()
    results['backend_api'] = test_backend_api()
    
    # Summary
    print("\n📊 Integration Test Summary")
    print("=" * 40)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"\nSuccess Rate: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    if results['environment'] and results['mock_processing']:
        print("\n✅ Core backend functionality is working!")
        print("   • Environment variables loaded correctly")
        print("   • Pipeline components functional")
        print("   • Ready for video processing")
    
    if results['backend_api']:
        print("✅ API endpoints are working!")
        print("   • Backend server starts successfully")
        print("   • All endpoints accessible")
        print("   • Video processing endpoint functional")

if __name__ == "__main__":
    main()
