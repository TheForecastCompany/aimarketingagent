#!/usr/bin/env python3
"""
Backend Video Processing Test Script
Diagnoses issues in the video processing pipeline
"""

import os
import sys
import json
import time
import traceback
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_environment():
    """Test environment setup and dependencies"""
    print("🔍 Testing Environment Setup")
    print("=" * 50)
    
    # Check Python version
    print(f"Python Version: {sys.version}")
    
    # Check required packages
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'requests',
        'ollama', 'python-dotenv', 'youtube-transcript-api'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    # Check environment variables
    print("\n🔍 Environment Variables:")
    env_vars = [
        'OLLAMA_BASE_URL', 'OLLAMA_MODEL', 
        'ASSEMBLYAI_API_KEY', 'OPENAI_API_KEY'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"✅ {var}: {masked_value}")
        else:
            print(f"⚠️  {var}: Not set")
    
    return True

def test_ollama_connection():
    """Test Ollama connection and model availability"""
    print("\n🤖 Testing Ollama Connection")
    print("=" * 50)
    
    try:
        from ollama import Client as OllamaClient
        
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "mistral:latest")
        
        print(f"🔗 Connecting to: {base_url}")
        print(f"📦 Model: {model}")
        
        # Test connection
        client = OllamaClient(host=base_url.replace("http://", ""))
        
        # List available models
        try:
            models = client.list()
            model_names = [m['name'] for m in models.get('models', [])]
            print(f"✅ Available models: {', '.join(model_names[:5])}")
            
            if model not in model_names:
                print(f"⚠️  Model '{model}' not found. Available: {', '.join(model_names)}")
                print(f"Pull with: ollama pull {model}")
                return False
        except Exception as e:
            print(f"❌ Failed to list models: {e}")
            return False
        
        # Test generation
        print("🧪 Testing generation...")
        start_time = time.time()
        
        response = client.generate(
            prompt="Respond with just: Ollama is working",
            model=model
        )
        
        elapsed = time.time() - start_time
        
        if response and response.get('response'):
            print(f"✅ Generation successful ({elapsed:.2f}s)")
            print(f"📝 Response: {response['response'][:50]}...")
            return True
        else:
            print("❌ Generation failed - no response")
            return False
            
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

def test_transcription():
    """Test transcription functionality"""
    print("\n🎙️ Testing Transcription")
    print("=" * 50)
    
    try:
        from backend.integrations.transcription import TranscriptExtractor
        from backend.integrations.transcription_enhanced import EnhancedTranscriptExtractor
        
        # Test standard transcription
        print("📹 Testing standard YouTube transcription...")
        standard_extractor = TranscriptExtractor()
        
        # Test video URL (short, accessible video)
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - always available
        
        print(f"🎬 Testing with: {test_url}")
        result = standard_extractor.get_transcript(test_url)
        
        if result and result.get('transcript'):
            transcript = result['transcript']
            print(f"✅ Standard transcription successful")
            print(f"📝 Length: {len(transcript)} characters")
            print(f"🔍 Preview: {transcript[:100]}...")
        else:
            print("❌ Standard transcription failed")
            print("💡 This could be due to:")
            print("   • Video has no subtitles")
            print("   • YouTube rate limiting")
            print("   • Network issues")
        
        # Test enhanced transcription if AssemblyAI key is available
        if os.getenv('ASSEMBLYAI_API_KEY'):
            print("\n🎙️ Testing enhanced transcription (AssemblyAI)...")
            enhanced_extractor = EnhancedTranscriptExtractor(use_professional=True)
            
            result = enhanced_extractor.get_transcript(test_url)
            
            if result and result.get('transcript'):
                transcript = result['transcript']
                metadata = result.get('transcription_metadata', {})
                print(f"✅ Enhanced transcription successful")
                print(f"📝 Length: {len(transcript)} characters")
                print(f"🎯 Confidence: {metadata.get('confidence_score', 'N/A')}")
                print(f"👥 Speakers: {metadata.get('speakers', 'N/A')}")
                print(f"⏱️  Duration: {metadata.get('audio_duration', 'N/A')}s")
            else:
                print("❌ Enhanced transcription failed")
        else:
            print("⚠️  AssemblyAI API key not set - skipping enhanced transcription")
        
        return True
        
    except Exception as e:
        print(f"❌ Transcription test failed: {e}")
        traceback.print_exc()
        return False

def test_pipeline_components():
    """Test individual pipeline components"""
    print("\n🔧 Testing Pipeline Components")
    print("=" * 50)
    
    try:
        # Import required components
        from backend.core.agents import ContentAnalystAgent, SocialStrategistAgent
        from backend.services.brand_voice import BrandVoice, BrandVoiceEngine
        from backend.integrations.seo import SEOKeywordExtractor
        
        # Test brand voice
        print("🎨 Testing brand voice...")
        brand_engine = BrandVoiceEngine()
        brand_voice = brand_engine.get_brand_voice("professional")
        print(f"✅ Brand voice: {brand_voice.value}")
        
        # Test SEO agent
        print("🔍 Testing SEO keyword extraction...")
        seo_agent = SEOKeywordExtractor(brand_voice)
        test_transcript = "This video discusses artificial intelligence, machine learning, and data science applications in business."
        
        seo_result = seo_agent.extract_keywords(test_transcript, ["AI", "technology"])
        print(f"✅ SEO analysis complete - {len(seo_result.keywords)} keywords found")
        for keyword in seo_result.keywords[:3]:
            print(f"   • {keyword.keyword} (relevance: {keyword.relevance_score:.2f})")
        
        # Test content analyst
        print("🧠 Testing content analysis...")
        analyst = ContentAnalystAgent()
        analysis_result = analyst.process(test_transcript)
        
        if hasattr(analysis_result, 'success') and analysis_result.success:
            print("✅ Content analysis successful")
            print(f"📊 Confidence: {analysis_result.confidence:.2f}")
        else:
            print("❌ Content analysis failed")
        
        # Test social strategist
        print("📱 Testing social media generation...")
        social_strategist = SocialStrategistAgent()
        
        # Create a mock analysis result
        class MockAnalysis:
            def __init__(self):
                self.content = {
                    'transcript': test_transcript,
                    'detected_product': 'AI tools',
                    'key_topics': ['artificial intelligence', 'machine learning'],
                    'sentiment': 'positive'
                }
                self.success = True
                self.confidence = 0.8
        
        mock_analysis = MockAnalysis()
        
        try:
            linkedin_post = social_strategist.create_linkedin_post(mock_analysis, "professional")
            if hasattr(linkedin_post, 'success') and linkedin_post.success:
                print("✅ LinkedIn post generation successful")
                print(f"📝 Length: {len(str(linkedin_post.content))} characters")
            else:
                print("❌ LinkedIn post generation failed")
        except Exception as e:
            print(f"❌ Social strategist error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline component test failed: {e}")
        traceback.print_exc()
        return False

def test_full_pipeline():
    """Test the complete video processing pipeline"""
    print("\n🚀 Testing Full Pipeline")
    print("=" * 50)
    
    try:
        from backend.core.pipeline import load_repurposer
        from backend.services.brand_voice import BrandVoice
        
        # Initialize repurposer
        print("⚙️ Initializing video repurposer...")
        brand_voice = BrandVoice.PROFESSIONAL
        target_keywords = ["AI", "technology", "business"]
        
        repurposer = load_repurposer(
            brand_voice=BrandVoice.PROFESSIONAL,
            target_keywords=target_keywords,
            enable_critique_loop=False,  # Disable for testing
            track_costs=True,
            _use_ollama=True
        )
        
        print("✅ Repurposer initialized")
        
        # Test with a short, accessible video
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        print(f"🎬 Processing video: {test_url}")
        
        start_time = time.time()
        results = repurposer.process_video(test_url)
        elapsed = time.time() - start_time
        
        if "error" in results:
            print(f"❌ Pipeline failed: {results['error']}")
            return False
        else:
            print(f"✅ Pipeline completed successfully ({elapsed:.2f}s)")
            
            # Check results
            content_types = ['linkedin_post', 'twitter_thread', 'newsletter', 'blog_post', 'short_scripts']
            for content_type in content_types:
                content = results.get(content_type)
                if content:
                    content_str = str(content.content if hasattr(content, 'content') else content)
                    print(f"✅ {content_type}: {len(content_str)} characters")
                else:
                    print(f"⚠️  {content_type}: Not generated")
            
            # Check cost tracking
            if 'cost_metrics' in results:
                cost_data = results['cost_metrics']
                print(f"💰 Total cost: ${cost_data.get('current_metrics', {}).get('total_cost', 0):.4f}")
                print(f"🪙 Total tokens: {cost_data.get('current_metrics', {}).get('total_tokens', 0)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    try:
        import requests
        import subprocess
        import threading
        import time
        
        # Start the API server in a background thread
        print("🚀 Starting API server...")
        
        def run_server():
            import uvicorn
            from main import app
            uvicorn.run(app, host="127.0.0.1", port=8999, log_level="error")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        base_url = "http://127.0.0.1:8999"
        
        # Test endpoints
        endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/api/v1/status", "Status endpoint"),
            ("/api/v1/videos", "Videos list")
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {description}: {response.status_code}")
                else:
                    print(f"❌ {description}: {response.status_code}")
            except Exception as e:
                print(f"❌ {description}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

def generate_test_report(results: Dict[str, bool]):
    """Generate a comprehensive test report"""
    print("\n📊 Test Report Summary")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n📋 Detailed Results:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    if not results.get('environment', False):
        print("   • Install missing Python packages")
        print("   • Set up required environment variables")
    
    if not results.get('ollama', False):
        print("   • Ensure Ollama is running: ollama serve")
        print("   • Pull required model: ollama pull mistral")
        print("   • Check OLLAMA_BASE_URL and OLLAMA_MODEL env vars")
    
    if not results.get('transcription', False):
        print("   • Try a different YouTube video")
        print("   • Check internet connection")
        print("   • Consider using AssemblyAI for professional transcription")
    
    if not results.get('pipeline', False):
        print("   • Check individual component tests above")
        print("   • Verify all dependencies are installed")
        print("   • Check logs for specific error messages")
    
    if not results.get('api', False):
        print("   • Check if port 8999 is available")
        print("   • Verify FastAPI installation")
        print("   • Check main.py for import errors")

def main():
    """Main test runner"""
    print("🧪 Video Processing Backend Test Suite")
    print("=" * 60)
    print("This script will test all components of the video processing pipeline")
    print("to help diagnose any issues you're experiencing.\n")
    
    # Run all tests
    test_results = {}
    
    test_results['environment'] = test_environment()
    test_results['ollama'] = test_ollama_connection()
    test_results['transcription'] = test_transcription()
    test_results['components'] = test_pipeline_components()
    test_results['pipeline'] = test_full_pipeline()
    test_results['api'] = test_api_endpoints()
    
    # Generate report
    generate_test_report(test_results)
    
    # Save results to file
    report_file = PROJECT_ROOT / "test_report.json"
    with open(report_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    all_passed = all(test_results.values())
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
