"""
Base Agent Class - Foundation for all modular agents
Provides common functionality and standardized interfaces
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
import time

from ..schema.models import (
    AgentResponse, AgentState, AgentStatus, ToolRequest, ToolResponse,
    LogLevel, ContentAnalysis
)
from ..tools.executor import tool_executor
from ..config.manager import config_manager, system_prompts
from ..orchestrator.observability import observability, AgentLogger

class BaseModularAgent(ABC):
    """Base class for all modular agents with standardized interfaces"""
    
    def __init__(self, agent_name: str, description: str):
        self.agent_name = agent_name
        self.description = description
        
        # Get configuration
        self.config = config_manager.get_agent_config(agent_name)
        self.llm_config = self.config.llm_config or config_manager.get_default_llm_config()
        
        # Create logger
        self.logger = AgentLogger(agent_name, observability)
        
        # Initialize state
        self.state = AgentState(agent_name=agent_name)
        observability.update_agent_state(self.state)
        
        # Initialize LLM client
        self.llm_client = self._initialize_llm_client()
        
        self.logger.info(f"Agent initialized: {agent_name}")
        self.logger.info(f"Description: {description}")
    
    def _initialize_llm_client(self):
        """Initialize LLM client based on configuration"""
        if self.llm_config.provider == "ollama":
            from ollama import Client as OllamaClient
            import os
            client = OllamaClient(
                host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").replace("http://", "")
            )
            # Store model separately for use in generate calls
            self.model = os.getenv("OLLAMA_MODEL", "mistral:latest")
            return client
        else:
            # Add other LLM providers as needed
            raise ValueError(f"Unsupported LLM provider: {self.llm_config.provider}")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Main processing method - must be implemented by subclasses"""
        pass
    
    async def think(self, thought_type: str, content: str, 
                   confidence: Optional[float] = None, context: Optional[Dict[str, Any]] = None):
        """Log an internal thought"""
        self.logger.think(thought_type, content, confidence, context)
    
    async def plan(self, content: str, confidence: Optional[float] = None, 
                  context: Optional[Dict[str, Any]] = None):
        """Log planning thoughts"""
        await self.think("planning", content, confidence, context)
    
    async def reason(self, content: str, confidence: Optional[float] = None, 
                    context: Optional[Dict[str, Any]] = None):
        """Log reasoning thoughts"""
        await self.think("reasoning", content, confidence, context)
    
    async def reflect(self, content: str, confidence: Optional[float] = None, 
                     context: Optional[Dict[str, Any]] = None):
        """Log reflection thoughts"""
        await self.think("reflection", content, confidence, context)
    
    async def decide(self, content: str, confidence: Optional[float] = None, 
                    context: Optional[Dict[str, Any]] = None):
        """Log decision thoughts"""
        await self.think("decision", content, confidence, context)
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any], 
                       priority: str = "medium", timeout: Optional[float] = None) -> ToolResponse:
        """Call a tool through the standardized tool system"""
        
        await self.reason(f"Calling tool: {tool_name}", context={"parameters": parameters})
        
        # Create tool request
        tool_request = ToolRequest(
            tool_name=tool_name,
            parameters=parameters,
            agent_name=self.agent_name,
            priority=priority,
            timeout=timeout
        )
        
        # Execute tool
        response = await tool_executor.execute_tool(tool_request)
        
        if response.success:
            await self.reason(f"Tool {tool_name} completed successfully", 
                            context={"result_type": type(response.result).__name__})
        else:
            await self.reason(f"Tool {tool_name} failed: {response.error_message}")
        
        return response
    
    async def generate_with_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate content using LLM"""
        
        await self.reason("Generating content with LLM", context={"prompt_length": len(prompt)})
        
        # Use agent-specific system prompt if provided
        if not system_prompt:
            system_prompt = system_prompts.get_prompt(self.agent_name.replace("_", ""))
        
        try:
            # Generate with LLM
            if hasattr(self.llm_client, 'generate'):
                result = self.llm_client.generate(prompt=prompt, model=self.model)
            elif hasattr(self.llm_client, 'chat'):
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
                result = self.llm_client.chat(messages)
                result = result.get('content', str(result))
            else:
                raise ValueError("LLM client has no compatible generation method")
            
            await self.reason("LLM generation completed", context={"result_length": len(result)})
            return result
            
        except Exception as e:
            await self.logger.error("LLM generation failed", e)
            raise
    
    def create_response(self, success: bool, content: Any, confidence: float, 
                       reasoning: str, suggestions: Optional[List[str]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Create a standardized agent response"""
        
        response = AgentResponse(
            success=success,
            content=content,
            confidence=confidence,
            reasoning=reasoning,
            suggestions=suggestions or [],
            metadata=metadata or {},
            execution_time=self.state.metadata.get("execution_time"),
            agent_name=self.agent_name
        )
        
        # Log response
        observability.log_agent_response(self.agent_name, response)
        
        return response
    
    def update_state(self, status: AgentStatus, current_task: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None):
        """Update agent state"""
        self.state.status = status
        if current_task:
            self.state.current_task = current_task
        if metadata:
            self.state.metadata.update(metadata)
        
        observability.update_agent_state(self.state)
    
    async def execute_with_retry(self, func, *args, max_retries: Optional[int] = None, **kwargs):
        """Execute a function with retry logic"""
        
        max_retries = max_retries or self.config.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    await self.plan(f"Retry attempt {attempt + 1}")
                    self.state.retry_count += 1
                
                result = await func(*args, **kwargs)
                
                if attempt > 0:
                    await self.reflect(f"Retry successful on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                if attempt == max_retries:
                    await self.logger.error(f"Function failed after {max_retries + 1} attempts", e)
                    raise
                else:
                    await self.logger.warning(f"Attempt {attempt + 1} failed, retrying", data={"error": str(e)})
                    await asyncio.sleep(1)  # Brief delay before retry
    
    async def measure_execution_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            self.state.metadata["execution_time"] = execution_time
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            self.state.metadata["execution_time"] = execution_time
            raise

class AnalysisAgent(BaseModularAgent):
    """Base class for analysis agents"""
    
    @abstractmethod
    async def analyze(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Analyze input data and return insights"""
        pass
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Default process method calls analyze"""
        return await self.analyze(input_data)

class SynthesisAgent(BaseModularAgent):
    """Base class for synthesis/content creation agents"""
    
    @abstractmethod
    async def synthesize(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Synthesize new content from input data"""
        pass
    
    @abstractmethod
    async def create(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Create content - alternative to synthesize"""
        pass
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Default process method calls synthesize or create"""
        if hasattr(self, 'synthesize'):
            return await self.synthesize(input_data)
        elif hasattr(self, 'create'):
            return await self.create(input_data)
        else:
            raise ValueError(f"Synthesis agent {self.agent_name} must implement synthesize or create")

class VerificationAgent(BaseModularAgent):
    """Base class for verification/quality control agents"""
    
    @abstractmethod
    async def verify(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Verify content quality and accuracy"""
        pass
    
    @abstractmethod
    async def validate(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Validate content against requirements"""
        pass
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Default process method calls verify"""
        return await self.verify(input_data)

class ToolAgent(BaseModularAgent):
    """Base class for tool-based agents"""
    
    @abstractmethod
    async def execute_tool_workflow(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Execute a workflow using tools"""
        pass
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Default process method calls execute_tool_workflow"""
        return await self.execute_tool_workflow(input_data)
