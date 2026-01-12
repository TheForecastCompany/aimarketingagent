"""
Unified Pipeline Orchestrator - Main pipeline that chains all agents and tools
Migrates all legacy pipeline logic into the new agentic workflow architecture
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from ..schema.models import ProcessingResult, AgentResponse, WorkflowStep, AgentStatus
from ..orchestrator.core import orchestrator, OrchestratorMode
from ..orchestrator.state import PipelineState, state_manager
from ..orchestrator.observability import observability, LogLevel
from ..orchestrator.resilience import error_resilience
from ..agents.content_analyst import ContentAnalystAgent
from ..agents.social_strategist import SocialStrategistAgent
from ..agents.seo_analyst import SEOAnalystAgent
from ..agents.content_creators import ScriptDoctorAgent, NewsletterWriterAgent, BlogPostAgent
from ..tools.legacy_tools import TranscriptTools, SEOTools, ProductDetectionTools

class UnifiedPipelineOrchestrator:
    """
    Main pipeline orchestrator that chains all agents and tools
    Migrates legacy VideoContentRepurposer logic into the new agentic architecture
    """
    
    def __init__(self, brand_voice: Optional[str] = None, target_keywords: Optional[List[str]] = None, 
                 enable_critique_loop: bool = False, track_costs: bool = False, 
                 enable_rag: bool = False, use_ollama: bool = False) -> None:
        """Initialize with legacy-compatible parameters"""
        
        # Store legacy configuration
        self.brand_voice = brand_voice
        self.target_keywords = target_keywords or []
        self.enable_critique_loop = enable_critique_loop
        self.track_costs = track_costs
        self.enable_rag = enable_rag
        self.use_professional_transcription = True  # Always enabled
        self.use_ollama = use_ollama
        
        # Initialize agents
        self._initialize_agents()
        
        # Initialize observability
        observability.log(
            LogLevel.INFO,
            "unified_orchestrator",
            "Unified Pipeline Orchestrator initialized with professional transcription",
            {
                "brand_voice": str(brand_voice),
                "target_keywords": len(target_keywords),
                "enable_critique_loop": enable_critique_loop,
                "use_professional_transcription": True,  # Always enabled
                "use_ollama": use_ollama
            }
        )
    
    def _initialize_agents(self):
        """Initialize all agents with the new architecture"""
        
        # Register agents with orchestrator
        agents = [
            ContentAnalystAgent(),
            SocialStrategistAgent(),
            SEOAnalystAgent(),
            ScriptDoctorAgent(),
            NewsletterWriterAgent(),
            BlogPostAgent()
        ]
        
        for agent in agents:
            orchestrator.register_agent(agent.agent_name, agent)
    
    async def process_video(self, youtube_url: str) -> Dict[str, Any]:
        """
        Process a YouTube video through the complete pipeline
        Legacy-compatible method that uses the new agentic architecture
        
        Args:
            youtube_url: YouTube video URL to process
            
        Returns:
            Dictionary containing all processing results
        """
        
        # Create pipeline state
        state = state_manager.create_state(
            input_url=youtube_url,
            target_keywords=self.target_keywords,
            brand_voice=str(self.brand_voice) if self.brand_voice else 'professional',
            enable_critique_loop=self.enable_critique_loop,
            track_costs=self.track_costs,
            use_ollama=self.use_ollama
        )
        
        try:
            # Step 1: Extract transcript
            state.update_stage("transcript_extraction")
            transcript_result = await self._extract_transcript(youtube_url, state)
            
            if not transcript_result["success"]:
                state.mark_failed("Transcript extraction failed")
                return {"error": transcript_result["error"]}
            
            state.input_transcript = transcript_result["transcript"]
            state.transcription_metadata = transcript_result["metadata"]
            
            # Step 2: SEO Analysis
            state.update_stage("seo_analysis")
            seo_result = await self._perform_seo_analysis(state)
            
            if not seo_result["success"]:
                state.add_warning("SEO analysis failed, continuing without SEO data")
                state.seo_analysis = {}
            else:
                state.seo_analysis = seo_result["seo_analysis"]
            
            # Step 3: Product Detection
            state.update_stage("product_detection")
            product_result = await self._detect_product(state)
            
            if product_result["success"]:
                state.detected_product = product_result["product"]
            else:
                state.detected_product = "Unknown product"
            
            # Step 4: Content Analysis
            state.update_stage("content_analysis")
            analysis_result = await self._perform_content_analysis(state)
            
            if not analysis_result["success"]:
                state.mark_failed("Content analysis failed")
                return {"error": "Content analysis failed"}
            
            state.content_analysis = analysis_result["content"]
            
            # Step 5: Social Media Content Creation
            state.update_stage("social_content_creation")
            social_result = await self._create_social_content(state)
            
            if social_result["success"]:
                state.linkedin_post = social_result["linkedin_post"]
                state.twitter_thread = social_result["twitter_thread"]
            else:
                state.add_warning("Social content creation failed")
            
            # Step 6: Script Creation
            state.update_stage("script_creation")
            script_result = await self._create_scripts(state)
            
            if script_result["success"]:
                state.short_scripts = script_result["scripts"]
            else:
                state.add_warning("Script creation failed")
            
            # Step 7: Newsletter Creation
            state.update_stage("newsletter_creation")
            newsletter_result = await self._create_newsletter(state)
            
            if newsletter_result["success"]:
                state.newsletter = newsletter_result["newsletter"]
            else:
                state.add_warning("Newsletter creation failed")
            
            # Step 8: Blog Post Creation
            state.update_stage("blog_creation")
            blog_result = await self._create_blog_post(state)
            
            if blog_result["success"]:
                state.blog_post = blog_result["blog_post"]
            else:
                state.add_warning("Blog post creation failed")
            
            # Step 9: Quality Control
            state.update_stage("quality_control")
            quality_result = await self._perform_quality_control(state)
            
            if quality_result["success"]:
                state.quality_scores = quality_result["quality_scores"]
            else:
                state.add_warning("Quality control failed")
            
            # Mark pipeline as completed
            state.mark_completed()
            
            # Return legacy-compatible results
            return state.get_final_results()
            
        except Exception as e:
            state.mark_failed(str(e))
            observability.log_error("unified_orchestrator", e, data={"pipeline_id": state.pipeline_id})
            return {"error": str(e)}
    
    async def _extract_transcript(self, youtube_url: str, state: PipelineState) -> Dict[str, Any]:
        """Extract transcript using tools with error resilience"""
        
        try:
            # Use tool for video ID extraction
            video_id_result = await error_resilience.execute_with_resilience(
                TranscriptTools.extract_video_id,
                "transcript_extractor",
                {"url": youtube_url}
            )
            
            if not video_id_result["success"]:
                return {"success": False, "error": video_id_result["error"]}
            
            # Use tool for transcript extraction
            transcript_result = await error_resilience.execute_with_resilience(
                TranscriptTools.extract_with_fallbacks,
                "transcript_extractor",
                {
                    "url": youtube_url,
                    "use_professional": True  # Always enabled
                }
            )
            
            return transcript_result
            
        except Exception as e:
            observability.log_error("transcript_extraction", e, data={"url": youtube_url})
            return {"success": False, "error": str(e)}
    
    async def _perform_seo_analysis(self, state: PipelineState) -> Dict[str, Any]:
        """Perform SEO analysis using the SEO agent"""
        
        try:
            # Get SEO agent
            seo_agent = orchestrator.agent_registry.get("seo_analyst")
            if not seo_agent:
                return {"success": False, "error": "SEO agent not available"}
            
            # Prepare input data
            input_data = {
                "transcript": state.input_transcript,
                "target_keywords": state.target_keywords
            }
            
            # Execute SEO analysis
            result = await error_resilience.execute_with_resilience(
                seo_agent.analyze,
                "seo_analyst",
                input_data
            )
            
            return {"success": True, "seo_analysis": result.content}
            
        except Exception as e:
            observability.log_error("seo_analysis", e)
            return {"success": False, "error": str(e)}
    
    async def _detect_product(self, state: PipelineState) -> Dict[str, Any]:
        """Detect product using tools"""
        
        try:
            # Use tool for product detection
            result = await error_resilience.execute_with_resilience(
                ProductDetectionTools.detect_product_from_text,
                "product_detector",
                {"text": state.input_transcript}
            )
            
            return result
            
        except Exception as e:
            observability.log_error("product_detection", e)
            return {"success": False, "error": str(e)}
    
    async def _perform_content_analysis(self, state: PipelineState) -> Dict[str, Any]:
        """Perform content analysis using the content analyst agent"""
        
        try:
            # Get content analyst agent
            analyst_agent = orchestrator.agent_registry.get("content_analyst")
            if not analyst_agent:
                return {"success": False, "error": "Content analyst agent not available"}
            
            # Prepare input data with transcript and product
            input_data = {
                "transcript": state.input_transcript,
                "detected_product": state.detected_product,
                "seo_analysis": state.seo_analysis
            }
            
            # Execute content analysis
            result = await error_resilience.execute_with_resilience(
                analyst_agent.analyze,
                "content_analyst",
                input_data
            )
            
            return {"success": True, "content": result.content}
            
        except Exception as e:
            observability.log_error("content_analysis", e)
            return {"success": False, "error": str(e)}
    
    async def _create_social_content(self, state: PipelineState) -> Dict[str, Any]:
        """Create social media content using the social strategist agent"""
        
        try:
            # Get social strategist agent
            social_agent = orchestrator.agent_registry.get("social_strategist")
            if not social_agent:
                return {"success": False, "error": "Social strategist agent not available"}
            
            # Prepare input data
            input_data = state.get_analysis_with_context()
            input_data["brand_voice"] = state.brand_voice
            
            # Execute social content creation
            result = await error_resilience.execute_with_resilience(
                social_agent.synthesize,
                "social_strategist",
                input_data
            )
            
            # Extract LinkedIn and Twitter content
            social_content = result.content if result.success else {}
            
            return {
                "success": True,
                "linkedin_post": social_content.get("linkedin"),
                "twitter_thread": social_content.get("twitter")
            }
            
        except Exception as e:
            observability.log_error("social_content_creation", e)
            return {"success": False, "error": str(e)}
    
    async def _create_scripts(self, state: PipelineState) -> Dict[str, Any]:
        """Create scripts using the script doctor agent"""
        
        try:
            # Get script doctor agent
            script_agent = orchestrator.agent_registry.get("script_doctor")
            if not script_agent:
                return {"success": False, "error": "Script doctor agent not available"}
            
            # Prepare input data
            input_data = state.get_analysis_with_context()
            
            # Execute script creation
            result = await error_resilience.execute_with_resilience(
                script_agent.synthesize,
                "script_doctor",
                input_data
            )
            
            return {"success": True, "scripts": result.content}
            
        except Exception as e:
            observability.log_error("script_creation", e)
            return {"success": False, "error": str(e)}
    
    async def _create_newsletter(self, state: PipelineState) -> Dict[str, Any]:
        """Create newsletter using the newsletter writer agent"""
        
        try:
            # Get newsletter writer agent
            newsletter_agent = orchestrator.agent_registry.get("newsletter_writer")
            if not newsletter_agent:
                return {"success": False, "error": "Newsletter writer agent not available"}
            
            # Prepare input data
            input_data = state.get_analysis_with_context()
            input_data["brand_voice"] = state.brand_voice
            
            # Execute newsletter creation
            result = await error_resilience.execute_with_resilience(
                newsletter_agent.create_newsletter,
                "newsletter_writer",
                input_data
            )
            
            return {"success": True, "newsletter": result.content}
            
        except Exception as e:
            observability.log_error("newsletter_creation", e)
            return {"success": False, "error": str(e)}
    
    async def _create_blog_post(self, state: PipelineState) -> Dict[str, Any]:
        """Create blog post using the blog writer agent"""
        
        try:
            # Get blog writer agent
            blog_agent = orchestrator.agent_registry.get("blog_writer")
            if not blog_agent:
                return {"success": False, "error": "Blog writer agent not available"}
            
            # Prepare input data
            input_data = state.get_analysis_with_context()
            input_data["brand_voice"] = state.brand_voice
            input_data["seo_analysis"] = state.seo_analysis
            
            # Execute blog post creation
            result = await error_resilience.execute_with_resilience(
                blog_agent.create_blog_post,
                "blog_writer",
                input_data
            )
            
            return {"success": True, "blog_post": result.content}
            
        except Exception as e:
            observability.log_error("blog_creation", e)
            return {"success": False, "error": str(e)}
    
    async def _perform_quality_control(self, state: PipelineState) -> Dict[str, Any]:
        """Perform quality control on all generated content"""
        
        try:
            # Collect all content for quality assessment
            content_items = {
                "linkedin_post": state.linkedin_post.content if state.linkedin_post else "",
                "twitter_thread": state.twitter_thread.content if state.twitter_thread else "",
                "short_scripts": state.short_scripts.content if state.short_scripts else "",
                "newsletter": state.newsletter.content if state.newsletter else "",
                "blog_post": state.blog_post.content if state.blog_post else ""
            }
            
            # Use tool for quality assessment
            quality_scores = {}
            for content_type, content in content_items.items():
                if content:
                    # Simple quality scoring based on content length and structure
                    if isinstance(content, str):
                        score = min(100, len(content.split()) / 10)  # Basic scoring
                    elif isinstance(content, dict):
                        score = min(100, len(str(content)) / 20)  # Basic scoring for dict content
                    else:
                        score = 50  # Default score
                    
                    quality_scores[content_type] = score
                else:
                    quality_scores[content_type] = 0
            
            return {"success": True, "quality_scores": quality_scores}
            
        except Exception as e:
            observability.log_error("quality_control", e)
            return {"success": False, "error": str(e)}
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific pipeline"""
        state = state_manager.get_state(pipeline_id)
        return state.get_pipeline_summary() if state else None
    
    def list_active_pipelines(self) -> List[Dict[str, Any]]:
        """List all active pipelines"""
        return [state.get_pipeline_summary() for state in state_manager.list_active_states()]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        return {
            "orchestrator_status": orchestrator.get_system_status(),
            "error_resilience": error_resilience.get_system_health(),
            "active_pipelines": len(state_manager.list_active_states())
        }

# Legacy compatibility wrapper
class VideoContentRepurposer:
    """Legacy compatibility wrapper for the new unified pipeline"""
    
    def __init__(self, brand_voice=None, target_keywords=None, enable_critique_loop=False,
                 track_costs=False, enable_rag=False, use_ollama=False):
        """Initialize with legacy parameters"""
        
        self.unified_orchestrator = UnifiedPipelineOrchestrator(
            brand_voice=brand_voice,
            target_keywords=target_keywords,
            enable_critique_loop=enable_critique_loop,
            track_costs=track_costs,
            enable_rag=enable_rag,
            use_ollama=use_ollama
        )
    
    async def process_video(self, youtube_url: str) -> Dict[str, Any]:
        """Legacy-compatible method"""
        return await self.unified_orchestrator.process_video(youtube_url)
