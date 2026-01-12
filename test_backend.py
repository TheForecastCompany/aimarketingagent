#!/usr/bin/env python3
"""
Comprehensive test script for backend pipeline
Tests all agent methods and track_operation calls to ensure no more TypeError issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.core.pipeline import VideoContentRepurposer
from backend.core.optimized_product_detector import OptimizedProductDetector, SAMPLE_PRODUCT_CATALOG
from backend.services.brand_voice import BrandVoice

def test_product_detector():
    """Test the optimized product detector"""
    print("🧪 Testing Product Detector...")
    
    detector = OptimizedProductDetector(SAMPLE_PRODUCT_CATALOG)
    
    # Test cases
    test_cases = [
        "I'm using Sony WH-1000XM4 headphones",
        "My MacBook Pro is working great", 
        "Just got these new Sen High Zer headphones",
        "The Apple iPhone is amazing",
        "I have a Bose QuietComfort 45"
    ]
    
    for i, transcript in enumerate(test_cases):
        print(f"\n📝 Test Case {i+1}: {transcript}")
        try:
            detection = detector.detect_product(transcript)
            print(f"✅ Detection: {detection.mapped_product} (confidence: {detection.confidence}%)")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print("✅ Product Detector test passed")
    return True

def test_agent_signatures():
    """Test that all agent methods accept **kwargs"""
    print("\n🧪 Testing Agent Method Signatures...")
    
    from backend.core.agents import ContentAnalystAgent, SocialStrategistAgent, ScriptDoctorAgent
    from backend.integrations.seo import SEOKeywordExtractor
    from backend.core.content_creators import NewsletterAgent, BlogPostAgent
    
    # Test ContentAnalystAgent
    try:
        analyst = ContentAnalystAgent()
        result = analyst.process("test transcript", extra_param="should_not_break")
        print("✅ ContentAnalystAgent.process accepts **kwargs")
    except TypeError as e:
        print(f"❌ ContentAnalystAgent.process error: {e}")
        return False
    
    # Test SocialStrategistAgent methods
    try:
        strategist = SocialStrategistAgent(use_ollama=False)
        result1 = strategist.create_linkedin_post({"test": "data"}, "professional", extra_param="should_not_break")
        result2 = strategist.create_twitter_thread({"test": "data"}, "professional", extra_param="should_not_break")
        print("✅ SocialStrategistAgent methods accept **kwargs")
    except TypeError as e:
        print(f"❌ SocialStrategistAgent method error: {e}")
        return False
    
    # Test ScriptDoctorAgent
    try:
        doctor = ScriptDoctorAgent(use_ollama=False)
        result = doctor.process("test content", "general", extra_param="should_not_break")
        print("✅ ScriptDoctorAgent.process accepts **kwargs")
    except TypeError as e:
        print(f"❌ ScriptDoctorAgent.process error: {e}")
        return False
    
    # Test SEOKeywordExtractor
    try:
        seo = SEOKeywordExtractor()
        result = seo.extract_keywords("test transcript", ["test"], extra_param="should_not_break")
        print("✅ SEOKeywordExtractor.extract_keywords accepts **kwargs")
    except TypeError as e:
        print(f"❌ SEOKeywordExtractor.extract_keywords error: {e}")
        return False
    
    # Test content creators
    try:
        newsletter = NewsletterAgent(use_ollama=False)
        result1 = newsletter.generate_content({"test": "data"}, "test transcript", "professional", extra_param="should_not_break")
        
        blog = BlogPostAgent(use_ollama=False)
        result2 = blog.generate_content({"test": "data"}, "test transcript", "professional", extra_param="should_not_break")
        
        print("✅ Content creator methods accept **kwargs")
    except TypeError as e:
        print(f"❌ Content creator method error: {e}")
        return False
    
    print("✅ Agent signatures test passed")
    return True

def test_track_operation_calls():
    """Test track_operation method calls"""
    print("\n🧪 Testing track_operation Calls...")
    
    try:
        # Create a minimal repurposer for testing
        repurposer = VideoContentRepurposer(
            brand_voice=BrandVoice.PROFESSIONAL,
            target_keywords=["test"],
            enable_critique_loop=False,
            track_costs=True,
            enable_rag=False,
            use_ollama=False
        )
        
        # Test with a short transcript
        test_transcript = "I'm testing the Sony WH-1000XM4 headphones and they work great."
        
        print(f"📝 Testing with transcript: {test_transcript}")
        
        # This should trigger all the track_operation calls
        result = repurposer.process_video(test_transcript)
        
        if result and 'error' not in result:
            print("✅ track_operation calls work correctly")
            return True
        else:
            print(f"❌ track_operation failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ track_operation test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pipeline_integration():
    """Test full pipeline integration"""
    print("\n🧪 Testing Full Pipeline Integration...")
    
    try:
        repurposer = VideoContentRepurposer(
            brand_voice=BrandVoice.PROFESSIONAL,
            target_keywords=["AI", "technology", "headphones"],
            enable_critique_loop=False,
            track_costs=True,
            enable_rag=False,
            use_professional_transcription=False,
            use_ollama=False
        )
        
        # Test with different transcript types
        test_transcripts = [
            "Today I want to talk about the new Apple MacBook Pro that I've been using for work.",
            "Just unboxed the Sony WH-1000XM4 and the noise cancellation is incredible.",
            "My old Sennheiser headphones finally gave up, so I upgraded to Bose."
        ]
        
        for i, transcript in enumerate(test_transcripts):
            print(f"\n📝 Pipeline Test {i+1}: {transcript[:50]}...")
            
            try:
                result = repurposer.process_video(transcript)
                
                if result and 'error' not in result:
                    print(f"✅ Pipeline test {i+1} passed")
                else:
                    print(f"❌ Pipeline test {i+1} failed: {result}")
                    return False
                    
            except Exception as e:
                print(f"❌ Pipeline test {i+1} error: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print("✅ Pipeline integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline integration test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Backend Test Suite")
    print("=" * 50)
    
    tests = [
        ("Product Detector", test_product_detector),
        ("Agent Signatures", test_agent_signatures),
        ("Track Operation Calls", test_track_operation_calls),
        ("Pipeline Integration", test_pipeline_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test CRASHED: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Backend is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
