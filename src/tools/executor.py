"""
Tool System - Standardized tool execution and management
Provides a clean interface for agents to request tool execution
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Callable, Union
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from dataclasses import dataclass
import inspect
import traceback

from ..schema.models import (
    ToolRequest, ToolResponse, ToolDefinition, ToolStatus, 
    AgentResponse, LogEntry, LogLevel
)
from ..config.manager import config_manager

class ToolRegistry:
    """Registry for managing available tools and their permissions"""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.implementations: Dict[str, Callable] = {}
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register built-in tools"""
        # Text processing tools
        self.register_tool(
            name="text_analysis",
            description="Analyze text for sentiment, topics, and key points",
            parameters={
                "text": {"type": "string", "required": True},
                "analysis_type": {"type": "string", "enum": ["sentiment", "topics", "key_points"], "required": True}
            },
            agent_permissions=["content_analyst", "quality_controller"],
            implementation=self._text_analysis_tool
        )
        
        # SEO tools
        self.register_tool(
            name="keyword_extraction",
            description="Extract keywords from text content",
            parameters={
                "text": {"type": "string", "required": True},
                "max_keywords": {"type": "integer", "default": 10}
            },
            agent_permissions=["seo_analyst", "content_analyst"],
            implementation=self._keyword_extraction_tool
        )
        
        # Content generation tools
        self.register_tool(
            name="generate_social_content",
            description="Generate social media content for specific platforms",
            parameters={
                "content": {"type": "string", "required": True},
                "platform": {"type": "string", "enum": ["linkedin", "twitter", "facebook"], "required": True},
                "tone": {"type": "string", "default": "professional"}
            },
            agent_permissions=["social_strategist"],
            implementation=self._generate_social_content_tool
        )
        
        # File operations
        self.register_tool(
            name="read_file",
            description="Read content from a file",
            parameters={
                "file_path": {"type": "string", "required": True},
                "encoding": {"type": "string", "default": "utf-8"}
            },
            agent_permissions=["all"],  # All agents can read files
            implementation=self._read_file_tool
        )
        
        self.register_tool(
            name="write_file",
            description="Write content to a file",
            parameters={
                "file_path": {"type": "string", "required": True},
                "content": {"type": "string", "required": True},
                "encoding": {"type": "string", "default": "utf-8"}
            },
            agent_permissions=["all"],
            implementation=self._write_file_tool
        )
        
        # Calculation tools
        self.register_tool(
            name="calculate_metrics",
            description="Calculate various content metrics",
            parameters={
                "content": {"type": "string", "required": True},
                "metrics": {"type": "array", "items": {"type": "string"}, "required": True}
            },
            agent_permissions=["quality_controller", "content_analyst"],
            implementation=self._calculate_metrics_tool
        )
        
        # Web tools
        self.register_tool(
            name="web_search",
            description="Search the web for information",
            parameters={
                "query": {"type": "string", "required": True},
                "max_results": {"type": "integer", "default": 5}
            },
            agent_permissions=["content_analyst", "seo_analyst"],
            implementation=self._web_search_tool
        )
    
    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], 
                     agent_permissions: List[str], implementation: Callable, 
                     timeout: float = 30.0, retry_count: int = 3):
        """Register a new tool"""
        tool_def = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            agent_permissions=agent_permissions,
            timeout=timeout,
            retry_count=retry_count
        )
        
        self.tools[name] = tool_def
        self.implementations[name] = implementation
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get tool definition by name"""
        return self.tools.get(name)
    
    def list_tools(self, agent_name: str = None) -> List[ToolDefinition]:
        """List available tools, optionally filtered by agent permissions"""
        if agent_name is None:
            return list(self.tools.values())
        
        return [
            tool for tool in self.tools.values()
            if agent_name in tool.agent_permissions or "all" in tool.agent_permissions
        ]
    
    def has_permission(self, agent_name: str, tool_name: str) -> bool:
        """Check if an agent has permission to use a tool"""
        tool = self.get_tool(tool_name)
        if not tool:
            return False
        
        return agent_name in tool.agent_permissions or "all" in tool.agent_permissions
    
    # Built-in tool implementations
    async def _text_analysis_tool(self, **kwargs) -> Dict[str, Any]:
        """Built-in text analysis tool"""
        text = kwargs.get("text", "")
        analysis_type = kwargs.get("analysis_type", "sentiment")
        
        # Simple implementation - in real system, would use NLP libraries
        if analysis_type == "sentiment":
            # Basic sentiment analysis
            positive_words = ["good", "great", "excellent", "amazing", "wonderful"]
            negative_words = ["bad", "terrible", "awful", "horrible", "poor"]
            
            words = text.lower().split()
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            if positive_count > negative_count:
                sentiment = "positive"
            elif negative_count > positive_count:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {"sentiment": sentiment, "confidence": 0.7}
        
        elif analysis_type == "topics":
            # Simple topic extraction based on common words
            words = text.lower().split()
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Ignore short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            return {"topics": [topic for topic, freq in topics]}
        
        elif analysis_type == "key_points":
            # Simple key point extraction - split by sentences
            sentences = text.split('.')
            key_points = [s.strip() for s in sentences if len(s.strip()) > 20][:3]
            return {"key_points": key_points}
        
        return {"error": "Unknown analysis type"}
    
    async def _keyword_extraction_tool(self, **kwargs) -> Dict[str, Any]:
        """Built-in keyword extraction tool"""
        text = kwargs.get("text", "")
        max_keywords = kwargs.get("max_keywords", 10)
        
        # Simple keyword extraction
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3 and word.isalpha():  # Ignore short words and punctuation
                word_freq[word] = word_freq.get(word, 0) + 1
        
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:max_keywords]
        return {"keywords": [keyword for keyword, freq in keywords]}
    
    async def _generate_social_content_tool(self, **kwargs) -> Dict[str, Any]:
        """Built-in social content generation tool"""
        content = kwargs.get("content", "")
        platform = kwargs.get("platform", "linkedin")
        tone = kwargs.get("tone", "professional")
        
        # Simple content adaptation
        if platform == "twitter":
            max_length = 280
            adapted_content = content[:max_length] + "..." if len(content) > max_length else content
        elif platform == "linkedin":
            adapted_content = f"🔹 {content}\n\n#Professional #Insights"
        else:  # facebook
            adapted_content = f"💡 {content}\n\nWhat are your thoughts?"
        
        return {"content": adapted_content, "platform": platform, "character_count": len(adapted_content)}
    
    async def _read_file_tool(self, **kwargs) -> Dict[str, Any]:
        """Built-in file reading tool"""
        file_path = kwargs.get("file_path", "")
        encoding = kwargs.get("encoding", "utf-8")
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return {"content": content, "file_path": file_path, "size": len(content)}
        except Exception as e:
            return {"error": str(e)}
    
    async def _write_file_tool(self, **kwargs) -> Dict[str, Any]:
        """Built-in file writing tool"""
        file_path = kwargs.get("file_path", "")
        content = kwargs.get("content", "")
        encoding = kwargs.get("encoding", "utf-8")
        
        try:
            # Create directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return {"success": True, "file_path": file_path, "bytes_written": len(content)}
        except Exception as e:
            return {"error": str(e)}
    
    async def _calculate_metrics_tool(self, **kwargs) -> Dict[str, Any]:
        """Built-in metrics calculation tool"""
        content = kwargs.get("content", "")
        metrics = kwargs.get("metrics", [])
        
        results = {}
        
        for metric in metrics:
            if metric == "word_count":
                results["word_count"] = len(content.split())
            elif metric == "character_count":
                results["character_count"] = len(content)
            elif metric == "sentence_count":
                results["sentence_count"] = len(content.split('.'))
            elif metric == "readability_score":
                # Simple readability calculation
                words = content.split()
                sentences = content.split('.')
                avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
                results["readability_score"] = min(100, max(0, 100 - (avg_words_per_sentence - 15) * 2))
            elif metric == "reading_time":
                word_count = len(content.split())
                results["reading_time"] = word_count / 200  # Average reading speed
        
        return {"metrics": results}
    
    async def _web_search_tool(self, **kwargs) -> Dict[str, Any]:
        """Built-in web search tool (placeholder)"""
        query = kwargs.get("query", "")
        max_results = kwargs.get("max_results", 5)
        
        # Placeholder implementation - in real system would use search API
        return {
            "query": query,
            "results": [
                {"title": f"Result {i+1} for '{query}'", "url": f"https://example.com/{i+1}", "snippet": f"Sample snippet {i+1}"}
                for i in range(min(max_results, 3))
            ],
            "total_results": min(max_results, 3)
        }

class ToolExecutor:
    """Executes tool requests with proper error handling and logging"""
    
    def __init__(self, registry: ToolRegistry, max_workers: int = 5):
        self.registry = registry
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.execution_history: List[ToolResponse] = []
    
    async def execute_tool(self, request: ToolRequest) -> ToolResponse:
        """Execute a tool request"""
        start_time = time.time()
        
        # Check permissions
        if not self.registry.has_permission(request.agent_name, request.tool_name):
            return ToolResponse(
                success=False,
                result=None,
                error_message=f"Agent {request.agent_name} does not have permission to use {request.tool_name}",
                execution_time=time.time() - start_time,
                tool_name=request.tool_name,
                request_id=request.request_id
            )
        
        # Get tool definition and implementation
        tool_def = self.registry.get_tool(request.tool_name)
        if not tool_def:
            return ToolResponse(
                success=False,
                result=None,
                error_message=f"Tool {request.tool_name} not found",
                execution_time=time.time() - start_time,
                tool_name=request.tool_name,
                request_id=request.request_id
            )
        
        implementation = self.registry.implementations.get(request.tool_name)
        if not implementation:
            return ToolResponse(
                success=False,
                result=None,
                error_message=f"Implementation for {request.tool_name} not found",
                execution_time=time.time() - start_time,
                tool_name=request.tool_name,
                request_id=request.request_id
            )
        
        # Execute with timeout and retry logic
        timeout = request.timeout or tool_def.timeout
        max_retries = tool_def.retry_count
        
        for attempt in range(max_retries + 1):
            try:
                # Check if implementation is async
                if inspect.iscoroutinefunction(implementation):
                    result = await asyncio.wait_for(implementation(**request.parameters), timeout=timeout)
                else:
                    # Run synchronous function in thread pool
                    result = await asyncio.get_event_loop().run_in_executor(
                        self.executor,
                        lambda: implementation(**request.parameters)
                    )
                
                execution_time = time.time() - start_time
                
                response = ToolResponse(
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    tool_name=request.tool_name,
                    request_id=request.request_id
                )
                
                self.execution_history.append(response)
                return response
                
            except asyncio.TimeoutError:
                if attempt == max_retries:
                    return ToolResponse(
                        success=False,
                        result=None,
                        error_message=f"Tool execution timed out after {timeout}s",
                        execution_time=time.time() - start_time,
                        tool_name=request.tool_name,
                        request_id=request.request_id
                    )
                continue
                
            except Exception as e:
                if attempt == max_retries:
                    return ToolResponse(
                        success=False,
                        result=None,
                        error_message=f"Tool execution failed: {str(e)}",
                        execution_time=time.time() - start_time,
                        tool_name=request.tool_name,
                        request_id=request.request_id
                    )
                continue
    
    def get_execution_history(self, agent_name: Optional[str] = None, 
                            tool_name: Optional[str] = None) -> List[ToolResponse]:
        """Get execution history, optionally filtered"""
        history = self.execution_history
        
        if agent_name:
            # Filter by agent (need to track this in requests)
            pass
        
        if tool_name:
            history = [resp for resp in history if resp.tool_name == tool_name]
        
        return history
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all executed tools"""
        if not self.execution_history:
            return {}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for resp in self.execution_history if resp.success)
        failed_executions = total_executions - successful_executions
        
        avg_execution_time = sum(resp.execution_time for resp in self.execution_history) / total_executions
        
        tool_stats = {}
        for response in self.execution_history:
            tool_name = response.tool_name
            if tool_name not in tool_stats:
                tool_stats[tool_name] = {"total": 0, "successful": 0, "total_time": 0.0}
            
            tool_stats[tool_name]["total"] += 1
            if response.success:
                tool_stats[tool_name]["successful"] += 1
            tool_stats[tool_name]["total_time"] += response.execution_time
        
        # Calculate averages per tool
        for tool_name, stats in tool_stats.items():
            stats["success_rate"] = (stats["successful"] / stats["total"]) * 100
            stats["avg_time"] = stats["total_time"] / stats["total"]
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "overall_success_rate": (successful_executions / total_executions) * 100,
            "average_execution_time": avg_execution_time,
            "tool_statistics": tool_stats
        }

# Global instances
tool_registry = ToolRegistry()
tool_executor = ToolExecutor(tool_registry)
