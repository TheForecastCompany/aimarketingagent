"""
Observability System - Comprehensive logging and monitoring for agentic workflows
Captures internal monologue, tool calls, and system events
"""

import json
import time
import uuid
import random
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import threading
from collections import defaultdict, deque
import traceback

from ..schema.models import (
    LogEntry, LogLevel, AgentThought, AgentResponse, ToolRequest, 
    ToolResponse, AgentState, PerformanceMetrics
)
from ..config.manager import config_manager

class ObservabilitySystem:
    """Centralized observability system for logging and monitoring"""
    
    def __init__(self, log_file: Optional[str] = None, max_memory_logs: int = 10000):
        self.log_file = log_file or "logs/agent_system.log"
        self.max_memory_logs = max_memory_logs
        
        # In-memory storage
        self.logs: deque = deque(maxlen=max_memory_logs)
        self.agent_thoughts: Dict[str, List[AgentThought]] = defaultdict(list)
        self.agent_states: Dict[str, AgentState] = {}
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        self.tool_calls: List[Dict[str, Any]] = []
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Ensure log directory exists
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # System configuration
        self.config = config_manager.get_system_config()
    
    def log(self, level: LogLevel, component: str, message: str, 
            agent_name: Optional[str] = None, data: Optional[Dict[str, Any]] = None,
            execution_context: Optional[Dict[str, Any]] = None):
        """Log an event with full context"""
        
        log_entry = LogEntry(
            level=level,
            component=component,
            agent_name=agent_name,
            message=message,
            data=data or {},
            execution_context=execution_context or {}
        )
        
        with self._lock:
            self.logs.append(log_entry)
        
        # Write to file if above info level
        if level.value >= LogLevel.INFO.value or self.config.debug_mode:
            self._write_log_to_file(log_entry)
        
        # Print critical errors
        if level == LogLevel.CRITICAL:
            print(f"🚨 CRITICAL [{component}] {agent_name}: {message}")
    
    def log_agent_thought(self, agent_name: str, thought_type: str, content: str,
                         confidence: Optional[float] = None, context: Optional[Dict[str, Any]] = None):
        """Log an agent's internal thought process"""
        
        thought = AgentThought(
            agent_name=agent_name,
            thought_type=thought_type,
            content=content,
            confidence=confidence,
            context=context or {}
        )
        
        with self._lock:
            self.agent_thoughts[agent_name].append(thought)
        
        # Log as info level
        self.log(
            level=LogLevel.INFO,
            component="agent_thought",
            message=f"[{thought_type.upper()}] {content[:100]}...",
            agent_name=agent_name,
            data={"thought_type": thought_type, "confidence": confidence}
        )
    
    def log_tool_request(self, request: ToolRequest):
        """Log a tool request"""
        self.log(
            level=LogLevel.INFO,
            component="tool_call",
            message=f"Tool request: {request.tool_name}",
            agent_name=request.agent_name,
            data={
                "tool_name": request.tool_name,
                "parameters": request.parameters,
                "request_id": request.request_id,
                "priority": request.priority
            }
        )
        
        with self._lock:
            self.tool_calls.append({
                "type": "request",
                "timestamp": datetime.now().isoformat(),
                "request": request.dict()
            })
    
    def log_tool_response(self, response: ToolResponse):
        """Log a tool response"""
        level = LogLevel.INFO if response.success else LogLevel.WARNING
        message = f"Tool response: {response.tool_name} - {'SUCCESS' if response.success else 'FAILED'}"
        
        if not response.success:
            message += f" - {response.error_message}"
        
        self.log(
            level=level,
            component="tool_call",
            message=message,
            data={
                "tool_name": response.tool_name,
                "success": response.success,
                "execution_time": response.execution_time,
                "request_id": response.request_id,
                "error_message": response.error_message
            }
        )
        
        with self._lock:
            self.tool_calls.append({
                "type": "response",
                "timestamp": datetime.now().isoformat(),
                "response": response.dict()
            })
    
    def log_agent_response(self, agent_name: str, response: AgentResponse):
        """Log an agent response"""
        level = LogLevel.INFO if response.success else LogLevel.ERROR
        message = f"Agent response: {response.success} - {response.reasoning[:100]}..."
        
        self.log(
            level=level,
            component="agent_response",
            message=message,
            agent_name=agent_name,
            data={
                "success": response.success,
                "confidence": response.confidence,
                "execution_time": response.execution_time,
                "suggestions_count": len(response.suggestions)
            }
        )
        
        # Update performance metrics
        self._update_performance_metrics(agent_name, response)
    
    def update_agent_state(self, state: AgentState):
        """Update and log agent state"""
        with self._lock:
            self.agent_states[state.agent_name] = state
        
        self.log(
            level=LogLevel.DEBUG,
            component="agent_state",
            message=f"State updated: {state.status.value}",
            agent_name=state.agent_name,
            data={"status": state.status.value, "current_task": state.current_task}
        )
    
    def log_error(self, component: str, error: Exception, agent_name: Optional[str] = None,
                  context: Optional[Dict[str, Any]] = None):
        """Log an error with full traceback"""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        
        self.log(
            level=LogLevel.ERROR,
            component=component,
            message=f"Error in {component}: {str(error)}",
            agent_name=agent_name,
            data=error_data
        )
    
    def _write_log_to_file(self, log_entry: LogEntry):
        """Write log entry to file"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                log_dict = log_entry.dict()
                log_dict['timestamp'] = log_entry.timestamp.isoformat()
                f.write(json.dumps(log_dict) + '\n')
        except Exception as e:
            print(f"Warning: Failed to write log to file: {e}")
    
    def _update_performance_metrics(self, agent_name: str, response: AgentResponse):
        """Update performance metrics for an agent"""
        with self._lock:
            if agent_name not in self.performance_metrics:
                self.performance_metrics[agent_name] = PerformanceMetrics(agent_name=agent_name)
            
            metrics = self.performance_metrics[agent_name]
            metrics.total_requests += 1
            
            if response.success:
                metrics.successful_requests += 1
            else:
                metrics.failed_requests += 1
            
            if response.execution_time:
                # Update average response time
                total_time = metrics.average_response_time * (metrics.total_requests - 1) + response.execution_time
                metrics.average_response_time = total_time / metrics.total_requests
            
            # Update average confidence
            if response.confidence is not None:
                total_confidence = metrics.average_confidence * (metrics.total_requests - 1) + response.confidence
                metrics.average_confidence = total_confidence / metrics.total_requests
            
            metrics.last_execution = datetime.now()
    
    def get_agent_thoughts(self, agent_name: str, thought_type: Optional[str] = None,
                          limit: Optional[int] = None) -> List[AgentThought]:
        """Get thoughts for an agent, optionally filtered"""
        with self._lock:
            thoughts = self.agent_thoughts.get(agent_name, [])
            
            if thought_type:
                thoughts = [t for t in thoughts if t.thought_type == thought_type]
            
            if limit:
                thoughts = thoughts[-limit:]
            
            return thoughts
    
    def get_agent_state(self, agent_name: str) -> Optional[AgentState]:
        """Get current state of an agent"""
        with self._lock:
            return self.agent_states.get(agent_name)
    
    def get_logs(self, level: Optional[LogLevel] = None, component: Optional[str] = None,
                agent_name: Optional[str] = None, limit: Optional[int] = None) -> List[LogEntry]:
        """Get logs with optional filtering"""
        with self._lock:
            logs = list(self.logs)
        
        # Apply filters
        if level:
            logs = [log for log in logs if log.level == level]
        
        if component:
            logs = [log for log in logs if log.component == component]
        
        if agent_name:
            logs = [log for log in logs if log.agent_name == agent_name]
        
        if limit:
            logs = logs[-limit:]
        
        return logs
    
    def get_performance_metrics(self, agent_name: Optional[str] = None) -> Dict[str, PerformanceMetrics]:
        """Get performance metrics"""
        with self._lock:
            if agent_name:
                return {agent_name: self.performance_metrics.get(agent_name)}
            return self.performance_metrics.copy()
    
    def get_tool_call_history(self, agent_name: Optional[str] = None,
                            tool_name: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get tool call history"""
        with self._lock:
            calls = self.tool_calls.copy()
        
        # Apply filters
        if agent_name:
            calls = [call for call in calls if 
                    (call.get('request', {}).get('agent_name') == agent_name or
                     call.get('response', {}).get('agent_name') == agent_name)]
        
        if tool_name:
            calls = [call for call in calls if 
                    (call.get('request', {}).get('tool_name') == tool_name or
                     call.get('response', {}).get('tool_name') == tool_name)]
        
        if limit:
            calls = calls[-limit:]
        
        return calls
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get a summary of system activity"""
        with self._lock:
            total_logs = len(self.logs)
            total_thoughts = sum(len(thoughts) for thoughts in self.agent_thoughts.values())
            total_tool_calls = len(self.tool_calls)
            
            # Agent status summary
            agent_summary = {}
            for agent_name, state in self.agent_states.items():
                agent_summary[agent_name] = {
                    "status": state.status.value,
                    "current_task": state.current_task,
                    "error_count": state.error_count,
                    "retry_count": state.retry_count
                }
            
            # Performance summary
            performance_summary = {}
            for agent_name, metrics in self.performance_metrics.items():
                performance_summary[agent_name] = {
                    "total_requests": metrics.total_requests,
                    "success_rate": metrics.success_rate,
                    "average_response_time": metrics.average_response_time,
                    "average_confidence": metrics.average_confidence
                }
            
            return {
                "total_logs": total_logs,
                "total_thoughts": total_thoughts,
                "total_tool_calls": total_tool_calls,
                "active_agents": len(self.agent_states),
                "agent_summary": agent_summary,
                "performance_summary": performance_summary,
                "timestamp": datetime.now().isoformat()
            }
    
    def export_logs(self, file_path: str, format: str = "json"):
        """Export logs to file"""
        logs_data = [log.dict() for log in self.logs]
        
        if format.lower() == "json":
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(logs_data, f, indent=2, default=str)
        elif format.lower() == "csv":
            import csv
            if logs_data:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=logs_data[0].keys())
                    writer.writeheader()
                    writer.writerows(logs_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def clear_logs(self, older_than_hours: Optional[int] = None):
        """Clear logs, optionally only older than specified hours"""
        with self._lock:
            if older_than_hours is None:
                # Clear all logs
                self.logs.clear()
                self.agent_thoughts.clear()
                self.agent_states.clear()
                self.performance_metrics.clear()
                self.tool_calls.clear()
            else:
                # Clear only old logs
                cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
                
                # Clear old log entries
                self.logs = deque(
                    [log for log in self.logs if log.timestamp.timestamp() > cutoff_time],
                    maxlen=self.max_memory_logs
                )
                
                # Clear old thoughts
                for agent_name in self.agent_thoughts:
                    self.agent_thoughts[agent_name] = [
                        thought for thought in self.agent_thoughts[agent_name]
                        if thought.timestamp.timestamp() > cutoff_time
                    ]

class AgentLogger:
    """Logger wrapper specifically for agents"""
    
    def __init__(self, agent_name: str, observability: ObservabilitySystem):
        self.agent_name = agent_name
        self.observability = observability
    
    def think(self, thought_type: str, content: str, confidence: Optional[float] = None, context: Optional[Dict[str, Any]] = None):
        """Log an internal thought"""
        self.observability.log_agent_thought(self.agent_name, thought_type, content, confidence, context)
    
    def plan(self, content: str, confidence: Optional[float] = None, context: Optional[Dict[str, Any]] = None):
        """Log planning thoughts"""
        self.think("planning", content, confidence, context)
    
    def reason(self, content: str, confidence: Optional[float] = None, context: Optional[Dict[str, Any]] = None):
        """Log reasoning thoughts"""
        self.think("reasoning", content, confidence, context)
    
    def reflect(self, content: str, confidence: Optional[float] = None, context: Optional[Dict[str, Any]] = None):
        """Log reflection thoughts"""
        self.think("reflection", content, confidence, context)
    
    def decide(self, content: str, confidence: Optional[float] = None, context: Optional[Dict[str, Any]] = None):
        """Log decision thoughts"""
        self.think("decision", content, confidence, context)
    
    def info(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self.observability.log(LogLevel.INFO, "agent", message, self.agent_name, data)
    
    def warning(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self.observability.log(LogLevel.WARNING, "agent", message, self.agent_name, data)
    
    def error(self, message: str, error: Optional[Exception] = None, data: Optional[Dict[str, Any]] = None):
        """Log error message"""
        if error:
            self.observability.log_error("agent", error, self.agent_name, data)
        else:
            self.observability.log(LogLevel.ERROR, "agent", message, self.agent_name, data)
    
    def debug(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self.observability.log(LogLevel.DEBUG, "agent", message, self.agent_name, data)

# Global observability instance
observability = ObservabilitySystem()
