"""
Pipeline State Object - Centralized state management for the content repurposing pipeline
Ensures data flows correctly between all pipeline stages without information loss
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from ..schema.models import (
    AgentResponse, ContentAnalysis, SocialMediaContent, NewsletterContent,
    BlogPostContent, ScriptContent, ProcessingResult
)

@dataclass
class PipelineState:
    """
    Centralized state object that passes data from one stage to the next
    Ensures no information is lost during hand-offs between pipeline stages
    """
    
    # Pipeline metadata
    pipeline_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    current_stage: str = "initialized"
    status: str = "pending"  # pending, running, completed, failed
    
    # Input data
    input_url: Optional[str] = None
    input_transcript: Optional[str] = None
    target_keywords: List[str] = field(default_factory=list)
    brand_voice: Optional[str] = None
    
    # Configuration
    enable_critique_loop: bool = False
    track_costs: bool = False
    use_ollama: bool = False
    
    # Stage results
    transcription_metadata: Dict[str, Any] = field(default_factory=dict)
    detected_product: Optional[str] = None
    seo_analysis: Optional[Dict[str, Any]] = None
    content_analysis: Optional[Union[ContentAnalysis, Dict[str, Any]]] = None
    
    # Content generation results
    linkedin_post: Optional[AgentResponse] = None
    twitter_thread: Optional[AgentResponse] = None
    short_scripts: Optional[AgentResponse] = None
    newsletter: Optional[AgentResponse] = None
    blog_post: Optional[AgentResponse] = None
    repurposing_plan: Optional[AgentResponse] = None
    
    # Quality and metrics
    quality_scores: Dict[str, float] = field(default_factory=dict)
    cost_metrics: Optional[Dict[str, Any]] = None
    dashboard_data: Optional[Dict[str, Any]] = None
    
    # Critique loop results
    critique_loop: Optional[Dict[str, Any]] = None
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    debug_info: Dict[str, Any] = field(default_factory=dict)
    
    # Stage tracking
    completed_stages: List[str] = field(default_factory=list)
    stage_timings: Dict[str, float] = field(default_factory=dict)
    
    def update_stage(self, stage_name: str, status: str = "running"):
        """Update current stage and track timing"""
        if self.current_stage != stage_name:
            # Record timing for previous stage
            if self.current_stage in self.stage_timings:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                self.stage_timings[self.current_stage] = elapsed
            
            self.current_stage = stage_name
            self.status = status
            
            if stage_name not in self.completed_stages:
                self.completed_stages.append(stage_name)
    
    def add_error(self, error: str, stage: Optional[str] = None):
        """Add error with stage context"""
        error_msg = f"[{stage or self.current_stage}] {error}"
        self.errors.append(error_msg)
        self.status = "failed"
    
    def add_warning(self, warning: str, stage: Optional[str] = None):
        """Add warning with stage context"""
        warning_msg = f"[{stage or self.current_stage}] {warning}"
        self.warnings.append(warning_msg)
    
    def add_debug_info(self, key: str, value: Any):
        """Add debug information"""
        self.debug_info[key] = value
    
    def get_transcript_length(self) -> int:
        """Get transcript length safely"""
        if self.input_transcript:
            return len(self.input_transcript)
        return 0
    
    def has_transcript(self) -> bool:
        """Check if transcript is available"""
        return bool(self.input_transcript and len(self.input_transcript.strip()) > 0)
    
    def get_content_for_critique(self) -> str:
        """Get content for critique loop with fallbacks"""
        # Try LinkedIn content first
        if self.linkedin_post and hasattr(self.linkedin_post, 'content'):
            content = self.linkedin_post.content
            if isinstance(content, str):
                return content
            elif isinstance(content, dict):
                return str(content.get('content', ''))
        
        # Try Twitter content
        if self.twitter_thread and hasattr(self.twitter_thread, 'content'):
            content = self.twitter_thread.content
            if isinstance(content, str):
                return content
            elif isinstance(content, dict):
                return str(content.get('content', ''))
        
        # Fallback to transcript
        if self.input_transcript:
            return self.input_transcript
        
        # Last resort
        return "No content available for critique"
    
    def get_analysis_with_context(self) -> Dict[str, Any]:
        """Get analysis with transcript and product context"""
        analysis_data = {}
        
        if self.content_analysis:
            if hasattr(self.content_analysis, 'content'):
                analysis_data = self.content_analysis.content
            elif isinstance(self.content_analysis, dict):
                analysis_data = self.content_analysis
            else:
                analysis_data = {"content": str(self.content_analysis)}
        
        # Ensure transcript and product are included
        if self.input_transcript:
            analysis_data['transcript'] = self.input_transcript
        
        if self.detected_product:
            analysis_data['detected_product'] = self.detected_product
        
        return analysis_data
    
    def get_final_results(self) -> Dict[str, Any]:
        """Compile final results in legacy format"""
        results = {
            "transcript": self.input_transcript,
            "analysis": self.content_analysis,
            "seo_analysis": self.seo_analysis or {},
            "linkedin_post": self.linkedin_post,
            "twitter_thread": self.twitter_thread,
            "short_scripts": self.short_scripts,
            "newsletter": self.newsletter,
            "blog_post": self.blog_post,
            "repurposing_plan": self.repurposing_plan,
            "quality_scores": self.quality_scores,
            "transcription_metadata": self.transcription_metadata,
            "detected_product": self.detected_product
        }
        
        # Add optional results
        if self.critique_loop:
            results["critique_loop"] = self.critique_loop
        
        if self.cost_metrics:
            results["cost_metrics"] = self.cost_metrics
        
        if self.dashboard_data:
            results["dashboard_data"] = self.dashboard_data
        
        return results
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get pipeline execution summary"""
        return {
            "pipeline_id": self.pipeline_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            "status": self.status,
            "current_stage": self.current_stage,
            "completed_stages": self.completed_stages,
            "stage_timings": self.stage_timings,
            "errors": self.errors,
            "warnings": self.warnings,
            "transcript_length": self.get_transcript_length(),
            "detected_product": self.detected_product,
            "quality_scores": self.quality_scores
        }
    
    def mark_completed(self):
        """Mark pipeline as completed"""
        self.end_time = datetime.now()
        self.status = "completed"
        self.current_stage = "completed"
        
        # Record final timing
        total_duration = (self.end_time - self.start_time).total_seconds()
        self.stage_timings["total"] = total_duration
    
    def mark_failed(self, error: str):
        """Mark pipeline as failed"""
        self.end_time = datetime.now()
        self.status = "failed"
        self.current_stage = "failed"
        self.add_error(error)
    
    def clone(self) -> 'PipelineState':
        """Create a copy of the state for debugging or retry"""
        import copy
        return copy.deepcopy(self)

class StateManager:
    """Manages pipeline state with persistence and recovery capabilities"""
    
    def __init__(self, enable_persistence: bool = False, persistence_path: Optional[str] = None):
        self.enable_persistence = enable_persistence
        self.persistence_path = persistence_path or "data/pipeline_states.json"
        self.active_states: Dict[str, PipelineState] = {}
        
        # Load persisted states if enabled
        if enable_persistence:
            self._load_persisted_states()
    
    def create_state(self, **kwargs) -> PipelineState:
        """Create a new pipeline state"""
        state = PipelineState(**kwargs)
        self.active_states[state.pipeline_id] = state
        
        if self.enable_persistence:
            self._persist_state(state)
        
        return state
    
    def get_state(self, pipeline_id: str) -> Optional[PipelineState]:
        """Get a pipeline state by ID"""
        return self.active_states.get(pipeline_id)
    
    def update_state(self, pipeline_id: str, **updates):
        """Update a pipeline state"""
        if pipeline_id in self.active_states:
            state = self.active_states[pipeline_id]
            for key, value in updates.items():
                setattr(state, key, value)
            
            if self.enable_persistence:
                self._persist_state(state)
    
    def remove_state(self, pipeline_id: str):
        """Remove a pipeline state"""
        if pipeline_id in self.active_states:
            del self.active_states[pipeline_id]
            
            if self.enable_persistence:
                self._persist_all_states()
    
    def list_active_states(self) -> List[PipelineState]:
        """List all active states"""
        return list(self.active_states.values())
    
    def get_state_summary(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get state summary"""
        state = self.get_state(pipeline_id)
        return state.get_pipeline_summary() if state else None
    
    def _persist_state(self, state: PipelineState):
        """Persist a single state to storage"""
        import json
        import os
        
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            
            # Load existing states
            states_data = {}
            if os.path.exists(self.persistence_path):
                with open(self.persistence_path, 'r') as f:
                    states_data = json.load(f)
            
            # Update with current state
            states_data[state.pipeline_id] = state.get_pipeline_summary()
            
            # Save back
            with open(self.persistence_path, 'w') as f:
                json.dump(states_data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Warning: Failed to persist state {state.pipeline_id}: {e}")
    
    def _persist_all_states(self):
        """Persist all active states"""
        import json
        import os
        
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            
            states_data = {}
            for state in self.active_states.values():
                states_data[state.pipeline_id] = state.get_pipeline_summary()
            
            with open(self.persistence_path, 'w') as f:
                json.dump(states_data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Warning: Failed to persist states: {e}")
    
    def _load_persisted_states(self):
        """Load persisted states from storage"""
        import json
        import os
        
        try:
            if os.path.exists(self.persistence_path):
                with open(self.persistence_path, 'r') as f:
                    states_data = json.load(f)
                
                # Note: We only load summaries, not full states
                # Full state reconstruction would require more complex logic
                print(f"Loaded {len(states_data)} persisted state summaries")
                
        except Exception as e:
            print(f"Warning: Failed to load persisted states: {e}")

# Global state manager instance
state_manager = StateManager()
