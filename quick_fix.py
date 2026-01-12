#!/usr/bin/env python3
"""
Quick Fix Script for Video Processing Issues
Addresses the most common problems found in the test
"""

import os
import sys
import subprocess
from pathlib import Path

def check_ollama():
    """Check and fix Ollama setup"""
    print("🤖 Checking Ollama Setup...")
    
    # Check if Ollama is running
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama is running")
            
            # Check if mistral model is available
            if 'mistral' in result.stdout.lower():
                print("✅ Mistral model is available")
            else:
                print("⚠️  Mistral model not found. Pulling now...")
                subprocess.run(['ollama', 'pull', 'mistral'], check=True)
                print("✅ Mistral model pulled successfully")
        else:
            print("❌ Ollama is not running")
            print("Start Ollama with: ollama serve")
            return False
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Ollama not found or not responding")
        print("Install Ollama from: https://ollama.ai")
        print("Then start with: ollama serve")
        return False
    
    return True

def check_env_vars():
    """Check and set environment variables"""
    print("\n🔧 Checking Environment Variables...")
    
    required_vars = {
        'OLLAMA_BASE_URL': 'http://localhost:11434',
        'OLLAMA_MODEL': 'mistral'
    }
    
    updated = False
    for var, default in required_vars.items():
        current = os.getenv(var)
        if not current:
            print(f"⚠️  {var} not set, using default: {default}")
            os.environ[var] = default
            updated = True
        else:
            print(f"✅ {var}: {current}")
    
    return updated

def test_simple_transcription():
    """Test transcription with a different video"""
    print("\n🎙️ Testing Alternative Video...")
    
    try:
        from backend.integrations.transcription import TranscriptExtractor
        
        # Try a different video that's known to have subtitles
        test_urls = [
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # "Me at the zoo" - first YouTube video
            "https://www.youtube.com/watch?v=9bZkp7q19f0",  # Gangnam Style - very popular
            "https://www.youtube.com/watch?v=kJQP7kiw5Fk"   # Lofi hip hop radio - streaming
        ]
        
        extractor = TranscriptExtractor()
        
        for url in test_urls:
            print(f"🎬 Trying: {url}")
            try:
                result = extractor.get_transcript(url)
                if result and result.get('transcript'):
                    print(f"✅ Success! Transcript length: {len(result['transcript'])}")
                    return url, result
                else:
                    print("❌ No transcript found")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("❌ All test videos failed")
        return None, None
        
    except Exception as e:
        print(f"❌ Transcription test failed: {e}")
        return None, None

def create_simple_test():
    """Create a simple test with mock data"""
    print("\n🧪 Creating Simple Test...")
    
    try:
        from backend.core.pipeline import VideoContentRepurposer
        from backend.services.brand_voice import BrandVoice
        
        # Create repurposer with minimal setup
        repurposer = VideoContentRepurposer(
            brand_voice=BrandVoice.PROFESSIONAL,
            target_keywords=["test", "video"],
            enable_critique_loop=False,
            track_costs=False,
            enable_rag=False,
            use_ollama=True
        )
        
        # Test with mock transcript
        mock_transcript = """
        This is a test video about artificial intelligence and machine learning. 
        In this video, we discuss how AI is transforming businesses and creating new opportunities.
        We cover topics like neural networks, deep learning, and practical applications.
        The video demonstrates various AI tools and their real-world use cases.
        """
        
        print("🧠 Testing content analysis with mock data...")
        
        # Test individual components
        analysis = repurposer.analyst.process(mock_transcript)
        print(f"✅ Analysis: {type(analysis)}")
        
        if hasattr(analysis, 'success'):
            print(f"   Success: {analysis.success}")
            print(f"   Confidence: {getattr(analysis, 'confidence', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run quick fixes and tests"""
    print("🔧 Video Processing Quick Fix Tool")
    print("=" * 50)
    
    # Step 1: Check environment
    check_env_vars()
    
    # Step 2: Check Ollama
    ollama_ok = check_ollama()
    
    # Step 3: Test transcription
    success_url, transcript_result = test_simple_transcription()
    
    # Step 4: Simple pipeline test
    simple_test_ok = create_simple_test()
    
    # Summary
    print("\n📊 Quick Fix Summary")
    print("=" * 30)
    print(f"Ollama: {'✅' if ollama_ok else '❌'}")
    print(f"Transcription: {'✅' if success_url else '❌'}")
    print(f"Pipeline: {'✅' if simple_test_ok else '❌'}")
    
    if success_url:
        print(f"\n✅ Working video URL found: {success_url}")
        print("You can use this URL for testing the frontend")
    
    if ollama_ok and simple_test_ok:
        print("\n✅ Core components are working!")
        print("The main issue was likely YouTube transcription")
        print("Try using a different video or AssemblyAI transcription")
    else:
        print("\n❌ Core issues found:")
        if not ollama_ok:
            print("• Ollama setup needs fixing")
        if not simple_test_ok:
            print("• Pipeline components have issues")

if __name__ == "__main__":
    main()
