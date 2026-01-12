"""
Shared Schema - Pydantic models for consistent data flow between agents
Ensures type safety and data validation across the agentic workflow
"""

from typing import Dict, List, Any, Optional, Union, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid

# =============================================================================
# CORE DATA MODELS
# =============================================================================

class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class ToolStatus(str, Enum):
    """Tool execution status"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class LogLevel(str, Enum):
    """Logging levels for observability"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# =============================================================================
# AGENT MODELS
# =============================================================================

class AgentResponse(BaseModel):
    """Standard response format for all agent outputs"""
    success: bool = Field(description="Whether the agent succeeded")
    content: Any = Field(description="The main content/output")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (0-1)")
    reasoning: str = Field(description="Agent's reasoning process")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    agent_name: Optional[str] = Field(None, description="Name of the agent")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0 and 1')
        return v

class AgentThought(BaseModel):
    """Represents an agent's internal thought process"""
    thought_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    timestamp: datetime = Field(default_factory=datetime.now)
    thought_type: Literal["planning", "reasoning", "reflection", "decision"] = "reasoning"
    content: str = Field(description="The thought content")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    context: Dict[str, Any] = Field(default_factory=dict, description="Context for the thought")

class AgentState(BaseModel):
    """Represents the current state of an agent"""
    agent_name: str
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    thoughts: List[AgentThought] = Field(default_factory=list)
    last_response: Optional[AgentResponse] = None
    error_count: int = Field(default=0, ge=0)
    retry_count: int = Field(default=0, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# =============================================================================
# TOOL MODELS
# =============================================================================

class ToolRequest(BaseModel):
    """Standardized tool request format"""
    tool_name: str = Field(description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(description="Parameters for the tool")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = Field(description="Name of the requesting agent")
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    timeout: Optional[float] = Field(None, description="Timeout in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ToolResponse(BaseModel):
    """Standardized tool response format"""
    success: bool = Field(description="Whether the tool execution succeeded")
    result: Any = Field(description="The tool's output/result")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    execution_time: float = Field(description="Execution time in seconds")
    tool_name: str = Field(description="Name of the tool that was executed")
    request_id: str = Field(description="ID of the original request")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ToolDefinition(BaseModel):
    """Definition of an available tool"""
    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")
    parameters: Dict[str, Any] = Field(description="Parameter schema")
    agent_permissions: List[str] = Field(default_factory=list, description="Agents allowed to use this tool")
    timeout: float = Field(default=30.0, description="Default timeout in seconds")
    retry_count: int = Field(default=3, description="Default retry count")

# =============================================================================
# WORKFLOW MODELS
# =============================================================================

class WorkflowStep(BaseModel):
    """Represents a single step in the workflow"""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    step_name: str
    agent_name: str
    step_type: Literal["analysis", "synthesis", "verification", "tool_call"] = "analysis"
    dependencies: List[str] = Field(default_factory=list, description="Step dependencies")
    status: AgentStatus = AgentStatus.IDLE
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=0)
    execution_time: Optional[float] = None

class WorkflowState(BaseModel):
    """Overall workflow state"""
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_name: str
    status: AgentStatus = AgentStatus.IDLE
    current_step: Optional[str] = None
    steps: List[WorkflowStep] = Field(default_factory=list)
    global_context: Dict[str, Any] = Field(default_factory=dict)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_execution_time: Optional[float] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# =============================================================================
# CONTENT MODELS
# =============================================================================

class ContentAnalysis(BaseModel):
    """Content analysis results"""
    topics: List[str] = Field(default_factory=list)
    key_points: List[str] = Field(default_factory=list)
    sentiment: str = Field(default="neutral")
    target_audience: str = Field(default="")
    word_count: int = Field(default=0)
    estimated_reading_time: float = Field(default=0.0)
    confidence: float = Field(ge=0.0, le=1.0)
    detected_product: Optional[str] = Field(None)

class SocialMediaContent(BaseModel):
    """Social media content structure"""
    platform: Literal["linkedin", "twitter", "facebook", "instagram"]
    content_type: Literal["post", "thread", "story", "reel"]
    content: str
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    character_count: int = Field(default=0)
    estimated_engagement: Optional[float] = Field(None)

class NewsletterContent(BaseModel):
    """Newsletter content structure"""
    subject: str
    preview_text: str
    body_content: str
    call_to_action: Optional[str] = None
    sections: List[str] = Field(default_factory=list)
    estimated_open_rate: Optional[float] = Field(None)

class BlogPostContent(BaseModel):
    """Blog post content structure"""
    title: str
    slug: str
    content: str
    excerpt: str
    tags: List[str] = Field(default_factory=list)
    category: str
    estimated_reading_time: float
    seo_score: Optional[float] = Field(None, ge=0.0, le=100.0)

class ScriptContent(BaseModel):
    """Script content structure"""
    script_type: Literal["short_form", "long_form", "educational", "promotional"]
    content: str
    estimated_duration: str  # e.g., "45 seconds"
    platform_suggestions: List[str] = Field(default_factory=list)
    visual_cues: List[str] = Field(default_factory=list)

# =============================================================================
# OBSERVABILITY MODELS
# =============================================================================

class LogEntry(BaseModel):
    """Log entry for observability"""
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    level: LogLevel = LogLevel.INFO
    component: str = Field(description="Component that generated the log")
    agent_name: Optional[str] = Field(None, description="Agent name if applicable")
    message: str = Field(description="Log message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional log data")
    execution_context: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PerformanceMetrics(BaseModel):
    """Performance metrics for monitoring"""
    agent_name: str
    total_requests: int = Field(default=0, ge=0)
    successful_requests: int = Field(default=0, ge=0)
    failed_requests: int = Field(default=0, ge=0)
    average_response_time: float = Field(default=0.0, ge=0.0)
    average_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    last_execution: Optional[datetime] = None
    uptime_percentage: float = Field(default=100.0, ge=0.0, le=100.0)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

# =============================================================================
# CONFIGURATION MODELS
# =============================================================================

class LLMConfig(BaseModel):
    """LLM configuration"""
    provider: Literal["ollama", "openai", "anthropic", "local"] = "ollama"
    model_name: str = Field(default="llama2")
    api_key: Optional[str] = Field(None)
    base_url: Optional[str] = Field(None)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1)
    timeout: float = Field(default=30.0, ge=1.0)
    retry_attempts: int = Field(default=3, ge=0)

class AgentConfig(BaseModel):
    """Individual agent configuration"""
    name: str
    enabled: bool = Field(default=True)
    llm_config: Optional[LLMConfig] = Field(None)
    max_retries: int = Field(default=3, ge=0)
    timeout: float = Field(default=120.0, ge=1.0)  # Increased for enhanced prompts
    priority: Literal["low", "medium", "high"] = "medium"
    custom_settings: Dict[str, Any] = Field(default_factory=dict)

class SystemConfig(BaseModel):
    """Overall system configuration"""
    debug_mode: bool = Field(default=False)
    log_level: LogLevel = LogLevel.INFO
    max_concurrent_agents: int = Field(default=5, ge=1)
    default_timeout: float = Field(default=180.0, ge=1.0)  # Increased for enhanced prompts
    enable_metrics: bool = Field(default=True)
    enable_persistence: bool = Field(default=False)
    persistence_path: Optional[str] = Field(None)
    agents: Dict[str, AgentConfig] = Field(default_factory=dict)
    tools: Dict[str, ToolDefinition] = Field(default_factory=dict)

# =============================================================================
# RESULT MODELS
# =============================================================================

class ProcessingResult(BaseModel):
    """Final processing result"""
    success: bool
    workflow_id: str
    total_execution_time: float
    results: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metrics: Dict[str, PerformanceMetrics] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ContentRepurposingResult(BaseModel):
    """Specific result for content repurposing workflow"""
    transcript: Optional[str] = None
    analysis: Optional[ContentAnalysis] = None
    social_media: Dict[str, SocialMediaContent] = Field(default_factory=dict)
    newsletter: Optional[NewsletterContent] = None
    blog_post: Optional[BlogPostContent] = None
    scripts: Dict[str, ScriptContent] = Field(default_factory=dict)
    seo_analysis: Optional[Dict[str, Any]] = None
    quality_scores: Dict[str, float] = Field(default_factory=dict)
    detected_product: Optional[str] = None
    processing_metrics: Dict[str, PerformanceMetrics] = Field(default_factory=dict)

# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def validate_agent_response(response: Dict[str, Any]) -> AgentResponse:
    """Validate and convert dict to AgentResponse"""
    return AgentResponse(**response)

def validate_tool_request(request: Dict[str, Any]) -> ToolRequest:
    """Validate and convert dict to ToolRequest"""
    return ToolRequest(**request)

def is_valid_content_type(content: Any, expected_type: type) -> bool:
    """Check if content matches expected type"""
    try:
        if expected_type == dict:
            return isinstance(content, dict)
        elif expected_type == list:
            return isinstance(content, list)
        elif expected_type == str:
            return isinstance(content, str)
        else:
            return isinstance(content, expected_type)
    except:
        return False

# =============================================================================
# TYPE ALIASES
# =============================================================================

AgentID = str
ToolID = str
WorkflowID = str
LogID = str
ConfigID = str
