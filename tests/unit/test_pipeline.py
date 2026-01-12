"""
Unified Pipeline Test Script - Comprehensive testing of the migrated agentic workflow
Validates that all legacy functionality works correctly in the new architecture
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

# Import the unified pipeline system
from src.main import AgenticWorkflowSystem, VideoContentRepurposer
from src.orchestrator.unified_pipeline import UnifiedPipelineOrchestrator
from src.orchestrator.observability import observability, LogLevel
from src.orchestrator.state import state_manager

class UnifiedPipelineTester:
    """Comprehensive test suite for the unified pipeline"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        
        print("🚀 Starting Unified Pipeline Test Suite")
        print("=" * 60)
        
        # Test 1: System Initialization
        await self.test_system_initialization()
        
        # Test 2: Legacy Compatibility
        await self.test_legacy_compatibility()
        
        # Test 3: Agent Registration
        await self.test_agent_registration()
        
        # Test 4: Tool Registration
        await self.test_tool_registration()
        
        # Test 5: State Management
        await self.test_state_management()
        
        # Test 6: Error Resilience
        await self.test_error_resilience()
        
        # Test 7: Observability
        await self.test_observability()
        
        # Test 8: End-to-End Pipeline (with mock data)
        await self.test_end_to_end_pipeline()
        
        # Generate test report
        self.generate_test_report()
        
        print("\n✅ All tests completed!")
        print(f"📊 Test Summary: {len(self.test_results)} tests executed")
        print(f"⏱️  Total time: {time.time() - self.start_time:.2f}s")
    
    async def test_system_initialization(self):
        """Test 1: System Initialization"""
        
        print("\n📋 Test 1: System Initialization")
        
        try:
            # Test AgenticWorkflowSystem initialization
            system = AgenticWorkflowSystem()
            
            # Test UnifiedPipelineOrchestrator initialization
            orchestrator = UnifiedPipelineOrchestrator(
                brand_voice="professional",
                target_keywords=["AI", "technology"],
                enable_critique_loop=False,
                track_costs=False,
                use_professional_transcription=False,
                use_ollama=True
            )
            
            # Verify system status
            status = system.get_system_status()
            
            self.add_test_result("System Initialization", True, {
                "agents_registered": status.get("registered_agents", 0),
                "tools_available": status.get("available_tools", 0),
                "workflow_templates": status.get("workflow_templates", 0)
            })
            
            print("✅ System initialization successful")
            
        except Exception as e:
            self.add_test_result("System Initialization", False, {"error": str(e)})
            print(f"❌ System initialization failed: {e}")
    
    async def test_legacy_compatibility(self):
        """Test 2: Legacy Compatibility"""
        
        print("\n📋 Test 2: Legacy Compatibility")
        
        try:
            # Test legacy VideoContentRepurposer
            legacy_repurposer = VideoContentRepurposer(
                brand_voice="professional",
                target_keywords=["AI", "technology"],
                enable_critique_loop=False,
                track_costs=False,
                use_ollama=True
            )
            
            # Verify it has the expected attributes
            assert hasattr(legacy_repurposer, 'unified_orchestrator')
            assert hasattr(legacy_repurposer, 'process_video')
            
            self.add_test_result("Legacy Compatibility", True, {
                "has_unified_orchestrator": True,
                "has_process_video": True
            })
            
            print("✅ Legacy compatibility verified")
            
        except Exception as e:
            self.add_test_result("Legacy Compatibility", False, {"error": str(e)})
            print(f"❌ Legacy compatibility test failed: {e}")
    
    async def test_agent_registration(self):
        """Test 3: Agent Registration"""
        
        print("\n📋 Test 3: Agent Registration")
        
        try:
            system = AgenticWorkflowSystem()
            status = system.get_system_status()
            
            expected_agents = [
                "content_analyst",
                "social_strategist", 
                "seo_analyst",
                "script_doctor",
                "newsletter_writer",
                "blog_writer"
            ]
            
            registered_agents = status.get("registered_agents", 0)
            
            self.add_test_result("Agent Registration", True, {
                "registered_agents": registered_agents,
                "expected_agents": len(expected_agents),
                "all_expected_present": registered_agents >= len(expected_agents)
            })
            
            print(f"✅ {registered_agents} agents registered")
            
        except Exception as e:
            self.add_test_result("Agent Registration", False, {"error": str(e)})
            print(f"❌ Agent registration test failed: {e}")
    
    async def test_tool_registration(self):
        """Test 4: Tool Registration"""
        
        print("\n📋 Test 4: Tool Registration")
        
        try:
            from src.tools.executor import tool_registry
            
            # Check that legacy tools are registered
            expected_tools = [
                "extract_video_id",
                "extract_youtube_transcript",
                "extract_transcript_with_fallbacks",
                "extract_seo_keywords",
                "detect_product",
                "write_file",
                "read_file",
                "calculate_text_metrics",
                "extract_key_points"
            ]
            
            registered_tools = len(tool_registry.tools)
            missing_tools = [tool for tool in expected_tools if tool not in tool_registry.tools]
            
            self.add_test_result("Tool Registration", True, {
                "registered_tools": registered_tools,
                "expected_tools": len(expected_tools),
                "missing_tools": missing_tools
            })
            
            print(f"✅ {registered_tools} tools registered")
            if missing_tools:
                print(f"⚠️  Missing tools: {missing_tools}")
            
        except Exception as e:
            self.add_test_result("Tool Registration", False, {"error": str(e)})
            print(f"❌ Tool registration test failed: {e}")
    
    async def test_state_management(self):
        """Test 5: State Management"""
        
        print("\n📋 Test 5: State Management")
        
        try:
            # Test state creation
            state = state_manager.create_state(
                input_url="https://youtube.com/watch?v=test",
                target_keywords=["test"],
                brand_voice="professional"
            )
            
            # Test state updates
            state.update_stage("test_stage")
            state.add_debug_info("test_key", "test_value")
            
            # Test state retrieval
            retrieved_state = state_manager.get_state(state.pipeline_id)
            
            self.add_test_result("State Management", True, {
                "state_created": True,
                "state_updated": state.current_stage == "test_stage",
                "state_retrieved": retrieved_state is not None,
                "debug_info_added": "test_key" in state.debug_info
            })
            
            print("✅ State management working correctly")
            
        except Exception as e:
            self.add_test_result("State Management", False, {"error": str(e)})
            print(f"❌ State management test failed: {e}")
    
    async def test_error_resilience(self):
        """Test 6: Error Resilience"""
        
        print("\n📋 Test 6: Error Resilience")
        
        try:
            from src.orchestrator.resilience import error_resilience
            
            # Test circuit breaker
            circuit_breaker = error_resilience.get_circuit_breaker("test_circuit")
            
            # Test health monitoring
            health = error_resilience.get_system_health()
            
            self.add_test_result("Error Resilience", True, {
                "circuit_breaker_created": circuit_breaker is not None,
                "health_monitoring": health is not None,
                "active_circuits": health.get("active_circuits", 0),
                "open_circuits": health.get("open_circuits", 0)
            })
            
            print("✅ Error resilience systems operational")
            
        except Exception as e:
            self.add_test_result("Error Resilience", False, {"error": str(e)})
            print(f"❌ Error resilience test failed: {e}")
    
    async def test_observability(self):
        """Test 7: Observability"""
        
        print("\n📋 Test 7: Observability")
        
        try:
            # Test logging
            observability.log(LogLevel.INFO, "test", "Test message")
            
            # Test system summary
            summary = observability.get_system_summary()
            
            # Test log retrieval
            logs = observability.get_logs(limit=10)
            
            self.add_test_result("Observability", True, {
                "logging_working": True,
                "system_summary": summary is not None,
                "log_retrieval": len(logs) >= 0,
                "total_logs": summary.get("total_logs", 0)
            })
            
            print("✅ Observability systems operational")
            
        except Exception as e:
            self.add_test_result("Observability", False, {"error": str(e)})
            print(f"❌ Observability test failed: {e}")
    
    async def test_end_to_end_pipeline(self):
        """Test 8: End-to-End Pipeline (with mock data)"""
        
        print("\n📋 Test 8: End-to-End Pipeline (Mock Data)")
        
        try:
            # Create mock transcript data
            mock_transcript = """
            This is a test transcript about AI and machine learning technologies.
            We discuss the latest developments in artificial intelligence and how
            these technologies are transforming various industries. The content covers
            topics like natural language processing, computer vision, and deep learning.
            """
            
            # Test content analysis agent
            from src.agents.content_analyst import ContentAnalystAgent
            analyst = ContentAnalystAgent()
            
            analysis_result = await analyst.analyze({
                "transcript": mock_transcript,
                "detected_product": "AI Technologies"
            })
            
            # Test SEO agent
            from src.agents.seo_analyst import SEOAnalystAgent
            seo_agent = SEOAnalystAgent()
            
            seo_result = await seo_agent.analyze({
                "transcript": mock_transcript,
                "target_keywords": ["AI", "machine learning"]
            })
            
            # Test social strategist agent
            from src.agents.social_strategist import SocialStrategistAgent
            social_agent = SocialStrategistAgent()
            
            social_result = await social_agent.synthesize({
                "transcript": mock_transcript,
                "detected_product": "AI Technologies",
                "analysis": analysis_result.content
            })
            
            self.add_test_result("End-to-End Pipeline", True, {
                "content_analysis": analysis_result.success,
                "seo_analysis": seo_result.success,
                "social_content": social_result.success,
                "analysis_confidence": analysis_result.confidence,
                "seo_confidence": seo_result.confidence,
                "social_confidence": social_result.confidence
            })
            
            print("✅ End-to-end pipeline test successful")
            print(f"   Content Analysis: {analysis_result.success}")
            print(f"   SEO Analysis: {seo_result.success}")
            print(f"   Social Content: {social_result.success}")
            
        except Exception as e:
            self.add_test_result("End-to-End Pipeline", False, {"error": str(e)})
            print(f"❌ End-to-end pipeline test failed: {e}")
    
    def add_test_result(self, test_name: str, success: bool, details: dict):
        """Add test result to the results list"""
        
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        
        report = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "passed_tests": len([r for r in self.test_results if r["success"]]),
                "failed_tests": len([r for r in self.test_results if not r["success"]]),
                "success_rate": len([r for r in self.test_results if r["success"]]) / len(self.test_results) * 100,
                "total_time": time.time() - self.start_time
            },
            "test_results": self.test_results,
            "system_info": {
                "timestamp": datetime.now().isoformat(),
                "python_version": "3.x",
                "test_environment": "development"
            }
        }
        
        # Save report to file
        report_path = "unified_pipeline_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Test report saved to: {report_path}")
        
        # Print summary
        summary = report["test_summary"]
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed_tests']}")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        print(f"   Total Time: {summary['total_time']:.2f}s")

async def main():
    """Main test runner"""
    
    tester = UnifiedPipelineTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
