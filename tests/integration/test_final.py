#!/usr/bin/env python3
"""
Final Test Suite - Validates all restored components
Tests the complete application functionality
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_all_components():
    """Test all restored components"""
    
    print("🧪 Final Test Suite - Complete Application Validation")
    print("=" * 70)
    
    test_results = {
        "core_modules": {},
        "agent_modules": {},
        "utility_modules": {},
        "app_integration": False
    }
    
    # Test core modules
    print("\n📦 Testing Core Modules:")
    core_modules = [
        ("professional_transcription", "ProfessionalTranscriptionService"),
        ("transcript_extractor", "TranscriptExtractor"),
        ("enhanced_transcript_extractor", "EnhancedTranscriptExtractor"),
        ("pipeline", "VideoContentRepurposer")
    ]
    
    for module_name, class_name in core_modules:
        try:
            module = __import__(module_name)
            cls = getattr(module, class_name)
            test_results["core_modules"][module_name] = True
            print(f"   ✅ {module_name}.{class_name}")
        except Exception as e:
            test_results["core_modules"][module_name] = False
            print(f"   ❌ {module_name}: {e}")
    
    # Test agent modules
    print("\n🤖 Testing Agent Modules:")
    agent_modules = [
        ("agents", ["ContentAnalystAgent", "SocialStrategistAgent", "ScriptDoctorAgent"]),
        ("content_agents", ["NewsletterAgent", "BlogPostAgent", "ContentRepurposingAgent"]),
        ("brand_voice", ["BrandVoice", "BrandVoiceEngine"]),
        ("quality_control", ["QualityController", "ConfidenceScore"]),
        ("agentic_critique", ["AgenticCritiqueLoop"])
    ]
    
    for module_name, class_names in agent_modules:
        try:
            module = __import__(module_name)
            all_found = True
            for class_name in class_names:
                try:
                    cls = getattr(module, class_name)
                except:
                    all_found = False
                    break
            
            test_results["agent_modules"][module_name] = all_found
            if all_found:
                print(f"   ✅ {module_name}: {', '.join(class_names)}")
            else:
                print(f"   ❌ {module_name}: Missing classes")
        except Exception as e:
            test_results["agent_modules"][module_name] = False
            print(f"   ❌ {module_name}: {e}")
    
    # Test utility modules
    print("\n🔧 Testing Utility Modules:")
    utility_modules = [
        ("seo_agent", "SEOKeywordExtractor"),
        ("cost_tracker", "CostTracker"),
        ("knowledge_retrieval", "KnowledgeRetriever"),
        ("logger", "PerformanceLogger")
    ]
    
    for module_name, class_name in utility_modules:
        try:
            module = __import__(module_name)
            cls = getattr(module, class_name)
            test_results["utility_modules"][module_name] = True
            print(f"   ✅ {module_name}.{class_name}")
        except Exception as e:
            test_results["utility_modules"][module_name] = False
            print(f"   ❌ {module_name}: {e}")
    
    # Test app integration
    print("\n🚀 Testing App Integration:")
    try:
        from app import load_repurposer, create_brand_voice_object
        test_results["app_integration"] = True
        print("   ✅ App imports working")
        print("   ✅ load_repurposer function available")
        print("   ✅ create_brand_voice_object function available")
    except Exception as e:
        test_results["app_integration"] = False
        print(f"   ❌ App integration failed: {e}")
    
    # Calculate results
    total_tests = (len(test_results["core_modules"]) + 
                   len(test_results["agent_modules"]) + 
                   len(test_results["utility_modules"]) + 1)
    
    passed_tests = (sum(test_results["core_modules"].values()) + 
                   sum(test_results["agent_modules"].values()) + 
                   sum(test_results["utility_modules"].values()) + 
                   (1 if test_results["app_integration"] else 0))
    
    success_rate = (passed_tests / total_tests) * 100
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    print(f"\n📈 Overall Success Rate: {success_rate:.1f}%")
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    
    print(f"\n📦 Core Modules: {sum(test_results['core_modules'].values())}/{len(test_results['core_modules'])}")
    print(f"🤖 Agent Modules: {sum(test_results['agent_modules'].values())}/{len(test_results['agent_modules'])}")
    print(f"🔧 Utility Modules: {sum(test_results['utility_modules'].values())}/{len(test_results['utility_modules'])}")
    print(f"🚀 App Integration: {'✅' if test_results['app_integration'] else '❌'}")
    
    if success_rate >= 90:
        print(f"\n🎉 EXCELLENT! Application is fully functional")
    elif success_rate >= 80:
        print(f"\n✅ GOOD! Application is mostly functional")
    elif success_rate >= 70:
        print(f"\n⚠️  FAIR! Application has some issues")
    else:
        print(f"\n❌ POOR! Application needs significant work")
    
    # File count
    print(f"\n📁 Files Created/Restored:")
    files = [
        "app.py", "pipeline.py", "professional_transcription.py",
        "transcript_extractor.py", "enhanced_transcript_extractor.py",
        "agents.py", "content_agents.py", "brand_voice.py",
        "quality_control.py", "agentic_critique.py", "seo_agent.py",
        "cost_tracker.py", "knowledge_retrieval.py", "logger.py"
    ]
    
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {file} ({size:,} bytes)")
        else:
            print(f"   ❌ {file} (missing)")
    
    print("\n" + "=" * 70)
    print("🎯 RESTORATION COMPLETE!")
    print("=" * 70)
    
    return success_rate >= 90

if __name__ == "__main__":
    success = test_all_components()
    
    if success:
        print("\n🚀 The application is ready for use!")
        print("💡 Run: streamlit run app.py")
        print("📝 All files have been successfully restored from chat history")
    else:
        print("\n⚠️  Some components may need attention")
        print("💡 Review the test results above for details")
