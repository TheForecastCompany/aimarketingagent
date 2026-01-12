"""
Agentic Workflow System - Main integration and entry point
Provides the new modular, decoupled agentic workflow architecture
"""

import asyncio
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# Import all the new modular components
from .schema.models import (
    AgentResponse, ProcessingResult, ContentRepurposingResult,
    WorkflowState, AgentStatus
)
from .orchestrator.core import orchestrator, OrchestratorMode
from .orchestrator.observability import observability, LogLevel
from .orchestrator.resilience import error_resilience
from .orchestrator.unified_pipeline import UnifiedPipelineOrchestrator, VideoContentRepurposer
from .orchestrator.state import state_manager
from .agents.content_analyst import ContentAnalystAgent
from .agents.social_strategist import SocialStrategistAgent
from .agents.seo_analyst import SEOAnalystAgent
from .agents.content_creators import ScriptDoctorAgent, NewsletterWriterAgent, BlogPostAgent
from .tools.executor import tool_executor, tool_registry
from .config.manager import config_manager

class AgenticWorkflowSystem:
    """
    Main interface for the new agentic workflow system
    Replaces the old linear pipeline with modular, decoupled architecture
    """
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the agentic workflow system"""
        
        # Load configuration
        if config_path:
            config_manager.config_path = config_path
            config_manager._load_config()
        
        self.config = config_manager.get_system_config()
        
        # Initialize unified pipeline orchestrator
        self.unified_orchestrator = UnifiedPipelineOrchestrator()
        
        observability.log(
            LogLevel.INFO,
            "agentic_system",
            "Agentic Workflow System initialized with unified pipeline",
            data={
                "agents_registered": len(orchestrator.agent_registry),
                "tools_available": len(tool_registry.tools),
                "workflow_templates": len(orchestrator.workflow_templates)
            }
        )
    
    async def process_content(self, input_data: Dict[str, Any], 
                           workflow_template: str = "content_repurposing",
                           progress_callback: Optional[callable] = None) -> ProcessingResult:
        """
        Process content using the new agentic workflow
        
        Args:
            input_data: Input data containing transcript, content, etc.
            workflow_template: Name of workflow template to use
            progress_callback: Optional callback for progress updates
        
        Returns:
            ProcessingResult with all outputs and metadata
        """
        
        try:
            # Check if this is a YouTube URL processing request
            if 'youtube_url' in input_data or 'url' in input_data:
                youtube_url = input_data.get('youtube_url') or input_data.get('url')
                
                # Use unified pipeline for YouTube video processing
                result = await self.unified_orchestrator.process_video(youtube_url)
                
                # Convert to ProcessingResult format
                if 'error' in result:
                    return ProcessingResult(
                        success=False,
                        workflow_id="unified_pipeline",
                        total_execution_time=0.0,
                        errors=[result['error']],
                        metrics={}
                    )
                
                # Convert to domain-specific result format
                domain_result = self._convert_to_content_result(result)
                
                return ProcessingResult(
                    success=True,
                    workflow_id="unified_pipeline",
                    total_execution_time=0.0,
                    results=domain_result,
                    metrics=self._collect_performance_metrics()
                )
            
            # For other content types, use the original orchestrator
            workflow_id = orchestrator.create_workflow(
                workflow_name=f"content_processing_{workflow_template}",
                template_name=workflow_template,
                input_data=input_data
            )
            
            observability.log(
                LogLevel.INFO,
                "agentic_system",
                f"Created workflow: {workflow_id}",
                data={"template": workflow_template}
            )
            
            # Execute workflow
            result = await orchestrator.execute_workflow(workflow_id, progress_callback)
            
            # Convert to domain-specific result format
            if result.success and workflow_template == "content_repurposing":
                domain_result = self._convert_to_content_result(result.results)
                result.results = domain_result
            
            return result
            
        except Exception as e:
            observability.log_error("agentic_system", e)
            return ProcessingResult(
                success=False,
                workflow_id="unknown",
                total_execution_time=0.0,
                errors=[str(e)],
                metrics={}
            )
    
    def _convert_to_content_result(self, workflow_results: Dict[str, Any]) -> ContentRepurposingResult:
        """Convert generic workflow results to domain-specific content result"""
        
        result = ContentRepurposingResult()
        
        # Extract analysis results
        if "analysis" in workflow_results:
            analysis = workflow_results["analysis"]
            if hasattr(analysis, 'content'):
                result.analysis = analysis.content
            elif isinstance(analysis, dict):
                from .schema.models import ContentAnalysis
                result.analysis = ContentAnalysis(**analysis)
        
        # Extract social media content
        if "social_media" in workflow_results:
            social_content = workflow_results["social_media"]
            if hasattr(social_content, 'content'):
                result.social_media = social_content.content
            elif isinstance(social_content, dict):
                from .schema.models import SocialMediaContent
                for platform, content in social_content.items():
                    if isinstance(content, dict):
                        result.social_media[platform] = SocialMediaContent(**content)
        
        # Extract other content types as needed
        if "short_scripts" in workflow_results:
            result.scripts = workflow_results["short_scripts"]
        
        if "newsletter" in workflow_results:
            result.newsletter = workflow_results["newsletter"]
        
        if "blog_post" in workflow_results:
            result.blog_post = workflow_results["blog_post"]
        
        if "seo_analysis" in workflow_results:
            result.seo_analysis = workflow_results["seo_analysis"]
        
        if "quality_scores" in workflow_results:
            result.quality_scores = workflow_results["quality_scores"]
        
        if "detected_product" in workflow_results:
            result.detected_product = workflow_results["detected_product"]
        
        # Extract metrics
        result.processing_metrics = result.metrics
        
        return result
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics from all components"""
        metrics = {}
        
        # Get orchestrator metrics
        orchestrator_metrics = orchestrator.get_system_status()
        metrics["orchestrator"] = orchestrator_metrics
        
        # Get error resilience metrics
        resilience_metrics = error_resilience.get_system_health()
        metrics["error_resilience"] = resilience_metrics
        
        # Get state manager metrics
        active_pipelines = state_manager.list_active_states()
        metrics["active_pipelines"] = len(active_pipelines)
        
        return metrics
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return orchestrator.get_system_status()
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get status of a specific workflow"""
        return orchestrator.get_workflow_status(workflow_id)
    
    def list_active_workflows(self) -> List[WorkflowState]:
        """List all active workflows"""
        return orchestrator.list_active_workflows()
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        return orchestrator.cancel_workflow(workflow_id)
    
    def get_logs(self, level: Optional[str] = None, component: Optional[str] = None,
                agent_name: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Get system logs"""
        logs = observability.get_logs(
            level=LogLevel(level) if level else None,
            component=component,
            agent_name=agent_name,
            limit=limit
        )
        return [log.dict() for log in logs]
    
    def get_performance_metrics(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics"""
        metrics = observability.get_performance_metrics(agent_name)
        return {name: metric.dict() for name, metric in metrics.items()}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health including circuit breakers"""
        return error_resilience.get_system_health()
    
    def export_logs(self, file_path: str, format: str = "json"):
        """Export system logs"""
        observability.export_logs(file_path, format)

# Backward compatibility layer
class VideoContentRepurposer:
    """
    Backward compatibility wrapper for the old VideoContentRepurposer
    Allows existing code to work with minimal changes
    """
    
    def __init__(self, brand_voice=None, target_keywords=None, enable_critique_loop=False,
                 track_costs=True, enable_rag=False, use_ollama=False):
        """Initialize with backward-compatible parameters"""
        
        # Store configuration for compatibility
        self.brand_voice = brand_voice
        self.target_keywords = target_keywords or []
        self.enable_critique_loop = enable_critique_loop
        self.track_costs = track_costs
        self.enable_rag = enable_rag
        self.use_ollama = use_ollama
        
        # Initialize new system
        self.agentic_system = AgenticWorkflowSystem()
        
        observability.log(
            LogLevel.INFO,
            "backward_compatibility",
            "VideoContentRepurposer initialized with agentic system"
        )
    
    async def process_content(self, transcript: str, **kwargs) -> Dict[str, Any]:
        """
        Process content using the new agentic system
        Maintains backward compatibility with old interface
        """
        
        # Prepare input data in expected format
        input_data = {
            "transcript": transcript,
            "brand_voice": self.brand_voice,
            "target_keywords": self.target_keywords,
            "enable_critique_loop": self.enable_critique_loop,
            "track_costs": self.track_costs,
            **kwargs
        }
        
        # Process with new system
        result = await self.agentic_system.process_content(
            input_data,
            workflow_template="content_repurposing"
        )
        
        # Convert to old format for compatibility
        if result.success:
            return self._convert_to_legacy_format(result.results)
        else:
            return {
                "success": False,
                "errors": result.errors,
                "warnings": result.warnings
            }
    
    def _convert_to_legacy_format(self, results: ContentRepurposingResult) -> Dict[str, Any]:
        """Convert new results to legacy format"""
        
        legacy_result = {
            "success": True,
            "transcript": results.transcript,
            "analysis": results.analysis,
            "social_media": {},
            "newsletter": results.newsletter,
            "blog_post": results.blog_post,
            "scripts": results.scripts,
            "seo_analysis": results.seo_analysis,
            "quality_scores": results.quality_scores,
            "detected_product": results.detected_product
        }
        
        # Convert social media to legacy format
        for platform, content in results.social_media.items():
            if hasattr(content, 'content'):
                legacy_result["social_media"][platform] = content.content
            else:
                legacy_result["social_media"][platform] = content
        
        return legacy_result

# Factory functions for easy instantiation
def create_agentic_system(config_path: Optional[str] = None) -> AgenticWorkflowSystem:
    """Create a new agentic workflow system"""
    return AgenticWorkflowSystem(config_path)

def create_legacy_repurposer(**kwargs) -> VideoContentRepurposer:
    """Create a legacy-compatible repurposer"""
    return VideoContentRepurposer(**kwargs)

# Main entry point
async def main():
    """Example usage of the new agentic system"""
    
    # Create the system
    system = create_agentic_system()
    
    # Sample input data
    input_data = {
        "transcript": "This is a sample transcript about GPT-5 and its capabilities...",
        "target_keywords": ["AI", "GPT-5", "technology"],
        "brand_voice": "professional"
    }
    
    # Process content
    def progress_callback(step_name, status):
        print(f"Step {step_name}: {status}")
    
    result = await system.process_content(
        input_data,
        workflow_template="content_repurposing",
        progress_callback=progress_callback
    )
    
    # Display results
    if result.success:
        print("✅ Processing completed successfully!")
        print(f"Execution time: {result.total_execution_time:.2f}s")
        
        if isinstance(result.results, ContentRepurposingResult):
            print(f"Analysis topics: {result.results.analysis.topics if result.results.analysis else 'N/A'}")
            print(f"Social platforms: {list(result.results.social_media.keys())}")
    else:
        print("❌ Processing failed:")
        for error in result.errors:
            print(f"  - {error}")
    
    # Show system status
    status = system.get_system_status()
    print(f"\nSystem Status: {status['active_workflows']} active workflows")

if __name__ == "__main__":
    asyncio.run(main())
