"""
Configuration Management - Centralized system prompts, LLM parameters, and environment variables
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import json
import yaml
from dotenv import load_dotenv

from ..schema.models import LLMConfig, AgentConfig, SystemConfig, LogLevel
from .optimized_prompts import OptimizedSystemPrompts

load_dotenv()

class ConfigManager:
    """Centralized configuration management for the agentic system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv("CONFIG_PATH", "config/system.yaml")
        self.system_config: Optional[SystemConfig] = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment variables"""
        # Default configuration
        default_config = {
            "debug_mode": os.getenv("DEBUG_MODE", "false").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "info"),
            "max_concurrent_agents": int(os.getenv("MAX_CONCURRENT_AGENTS", "5")),
            "default_timeout": float(os.getenv("DEFAULT_TIMEOUT", "180.0")),  # Increased for enhanced prompts
            "enable_metrics": os.getenv("ENABLE_METRICS", "true").lower() == "true",
            "enable_persistence": os.getenv("ENABLE_PERSISTENCE", "false").lower() == "true",
            "persistence_path": os.getenv("PERSISTENCE_PATH", "data/state.json"),
            "agents": {},
            "tools": {}
        }
        
        # Load from file if exists
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        file_config = yaml.safe_load(f)
                    else:
                        file_config = json.load(f)
                
                # Merge with defaults
                default_config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_path}: {e}")
        
        # Create system config
        self.system_config = SystemConfig(**default_config)
    
    def get_system_config(self) -> SystemConfig:
        """Get the system configuration"""
        return self.system_config
    
    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """Get configuration for a specific agent"""
        if agent_name in self.system_config.agents:
            return self.system_config.agents[agent_name]
        
        # Return default config
        return AgentConfig(
            name=agent_name,
            llm_config=self.get_default_llm_config()
        )
    
    def get_default_llm_config(self) -> LLMConfig:
        """Get default LLM configuration"""
        return LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "ollama"),
            model_name=os.getenv("LLM_MODEL", "llama2"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
            timeout=float(os.getenv("LLM_TIMEOUT", "180.0")),  # Increased for enhanced prompts
            retry_attempts=int(os.getenv("LLM_RETRY_ATTEMPTS", "3"))
        )
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration dynamically"""
        if self.system_config:
            config_dict = self.system_config.dict()
            config_dict.update(updates)
            self.system_config = SystemConfig(**config_dict)
    
    def save_config(self, path: Optional[str] = None):
        """Save current configuration to file"""
        save_path = path or self.config_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'w') as f:
            if save_path.endswith('.yaml') or save_path.endswith('.yml'):
                yaml.dump(self.system_config.dict(), f, default_flow_style=False)
            else:
                json.dump(self.system_config.dict(), f, indent=2)

# System Prompts
class SystemPrompts:
    """Centralized system prompts for different agent types"""
    
    # Base prompts
    BASE_SYSTEM_PROMPT = """You are an AI agent designed to assist with content analysis and repurposing. 
    You are knowledgeable, professional, and always provide thoughtful, well-reasoned responses.
    You should be honest about your limitations and ask for clarification when needed."""
    
    # Analysis agents
    CONTENT_ANALYST_PROMPT = """You are a Content Analyst specializing in analyzing video transcripts and multimedia content.
    Your expertise includes:
    - Topic identification and categorization
    - Sentiment analysis and emotional tone detection
    - Key point extraction and summarization
    - Target audience analysis
    - Content structure analysis
    
    Always provide detailed analysis with specific examples from the content.
    Rate your confidence in each analysis point."""
    
    SEO_ANALYST_PROMPT = """You are an SEO Specialist focused on keyword extraction and content optimization.
    Your responsibilities include:
    - Identifying primary and secondary keywords
    - Analyzing search intent
    - Suggesting content improvements for SEO
    - Evaluating keyword density and placement
    - Recommending meta descriptions and titles
    
    Provide keyword difficulty scores and search volume estimates when possible."""
    
    # Content creation agents
    SOCIAL_STRATEGIST_PROMPT = """You are a Social Media Strategist with expertise in creating platform-specific content.
    You understand:
    - LinkedIn: Professional tone, business focus, 1300-3000 characters
    - Twitter: Concise, engaging, 280 characters per tweet
    - Facebook: Conversational, community-focused
    - Instagram: Visual-first, storytelling approach
    
    Always adapt content to the specific platform's best practices and audience expectations."""
    
    SCRIPT_DOCTOR_PROMPT = """You are a Script Doctor specializing in creating engaging video scripts.
    Your skills include:
    - Writing hooks that capture attention immediately
    - Structuring content for optimal viewer retention
    - Creating clear calls-to-action
    - Adapting tone for different video formats (short-form, long-form, educational)
    - Adding visual and pacing cues
    
    Scripts should be conversational, engaging, and optimized for the target platform."""
    
    NEWSLETTER_WRITER_PROMPT = """You are a Newsletter Writer focused on creating engaging email content.
    You excel at:
    - Writing compelling subject lines with high open rates
    - Creating scannable content with clear hierarchy
    - Including strong calls-to-action
    - Balancing promotional and value-driven content
    - Personalizing content for subscriber segments
    
    Newsletters should feel personal, valuable, and drive desired actions."""
    
    BLOG_WRITER_PROMPT = """You are a Blog Writer specializing in SEO-optimized, long-form content.
    Your expertise includes:
    - Creating compelling headlines and introductions
    - Structuring articles for readability and SEO
    - Incorporating keywords naturally
    - Writing engaging meta descriptions
    - Creating internal and external linking strategies
    
    Blog posts should be informative, well-researched, and optimized for search engines."""
    
    # Quality control
    QUALITY_CONTROLLER_PROMPT = """You are a Quality Controller ensuring content meets high standards.
    You evaluate:
    - Accuracy and factual correctness
    - Clarity and readability
    - Brand voice consistency
    - Grammar and spelling
    - Appropriateness for target audience
    - SEO optimization
    - Engagement potential
    
    Provide specific, actionable feedback for improvement and confidence scores."""
    
    # Critique agents
    CRITIC_PROMPT = """You are a Content Critic providing constructive feedback on content quality.
    Your role is to:
    - Identify strengths and weaknesses in content
    - Suggest specific improvements
    - Evaluate alignment with objectives
    - Assess brand voice consistency
    - Check for factual accuracy
    - Recommend structural changes
    
    Be thorough, constructive, and always provide actionable suggestions."""
    
    EDITOR_PROMPT = """You are a Content Editor focused on refining and improving content.
    You specialize in:
    - Improving clarity and flow
    - Enhancing engagement and readability
    - Fixing grammar and style issues
    - Optimizing for specific platforms
    - Ensuring brand consistency
    - Strengthening calls-to-action
    
    Make content more compelling while preserving the original intent and key messages."""
    
    # Tool-specific prompts
    PRODUCT_DETECTION_PROMPT = """You are a Product Detection Specialist focused on identifying products, services, or brands mentioned in content.
    Your task is to:
    - Identify specific product names and brands
    - Distinguish between products and general concepts
    - Handle variations in product naming
    - Provide confidence scores for detections
    - Suggest alternative product names if uncertain
    
    Be precise and only identify actual products, not generic concepts."""
    
    @classmethod
    def get_prompt(cls, agent_type: str) -> str:
        """Get the appropriate system prompt for an agent type"""
        prompt_map = {
            "content_analyst": cls.CONTENT_ANALYST_PROMPT,
            "seo_analyst": cls.SEO_ANALYST_PROMPT,
            "social_strategist": cls.SOCIAL_STRATEGIST_PROMPT,
            "script_doctor": cls.SCRIPT_DOCTOR_PROMPT,
            "newsletter_writer": cls.NEWSLETTER_WRITER_PROMPT,
            "blog_writer": cls.BLOG_WRITER_PROMPT,
            "quality_controller": cls.QUALITY_CONTROLLER_PROMPT,
            "critic": cls.CRITIC_PROMPT,
            "editor": cls.EDITOR_PROMPT,
            "product_detector": cls.PRODUCT_DETECTION_PROMPT
        }
        
        return prompt_map.get(agent_type, cls.BASE_SYSTEM_PROMPT)

# Environment Variables Management
class EnvironmentManager:
    """Manage environment variables and secrets"""
    
    @staticmethod
    def get_required_env(key: str) -> str:
        """Get required environment variable or raise error"""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    @staticmethod
    def get_optional_env(key: str, default: Any = None) -> Any:
        """Get optional environment variable with default"""
        return os.getenv(key, default)
    
    @staticmethod
    def get_bool_env(key: str, default: bool = False) -> bool:
        """Get boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    @staticmethod
    def get_int_env(key: str, default: int = 0) -> int:
        """Get integer environment variable"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @staticmethod
    def get_float_env(key: str, default: float = 0.0) -> float:
        """Get float environment variable"""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @staticmethod
    def get_list_env(key: str, default: list = None, separator: str = ",") -> list:
        """Get list environment variable"""
        if default is None:
            default = []
        value = os.getenv(key)
        if value is None:
            return default
        return [item.strip() for item in value.split(separator) if item.strip()]

# Global configuration instance
config_manager = ConfigManager()
system_prompts = OptimizedSystemPrompts()
env_manager = EnvironmentManager()
