#!/usr/bin/env python3
"""
Performance Logger - Tracks agent performance and system metrics
Provides detailed logging for debugging and optimization
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import os

@dataclass
class LogEntry:
    """Individual log entry"""
    timestamp: datetime
    agent_name: str
    action: str
    duration: float
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

@dataclass
class PerformanceMetrics:
    """Performance metrics for an agent"""
    agent_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    success_rate: float = 0.0
    last_call: Optional[datetime] = None

class PerformanceLogger:
    """Logs performance metrics for agents and system operations"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_entries: List[LogEntry] = []
        self.agent_metrics: Dict[str, PerformanceMetrics] = {}
        self.session_start = datetime.now()
        self.log_file = log_file or "performance_logs.json"
        
        print("📊 Performance Logger Initialized")
        print(f"📁 Log file: {self.log_file}")
    
    def log_action(self, agent_name: str, action: str, duration: float, 
                   success: bool = True, details: Dict[str, Any] = None, 
                   error_message: Optional[str] = None):
        """Log an agent action"""
        entry = LogEntry(
            timestamp=datetime.now(),
            agent_name=agent_name,
            action=action,
            duration=duration,
            success=success,
            details=details or {},
            error_message=error_message
        )
        
        self.log_entries.append(entry)
        self._update_agent_metrics(entry)
        
        # Log to console
        status = "✅" if success else "❌"
        print(f"{status} {agent_name}: {action} ({duration:.3f}s)")
        
        if error_message:
            print(f"   ❌ Error: {error_message}")
    
    def _update_agent_metrics(self, entry: LogEntry):
        """Update agent performance metrics"""
        agent_name = entry.agent_name
        
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = PerformanceMetrics(agent_name=agent_name)
        
        metrics = self.agent_metrics[agent_name]
        metrics.total_calls += 1
        metrics.total_duration += entry.duration
        metrics.last_call = entry.timestamp
        
        if entry.success:
            metrics.successful_calls += 1
        else:
            metrics.failed_calls += 1
        
        # Calculate averages and rates
        metrics.avg_duration = metrics.total_duration / metrics.total_calls
        metrics.success_rate = metrics.successful_calls / metrics.total_calls
    
    def get_agent_metrics(self, agent_name: str) -> Optional[PerformanceMetrics]:
        """Get performance metrics for a specific agent"""
        return self.agent_metrics.get(agent_name)
    
    def get_all_metrics(self) -> Dict[str, PerformanceMetrics]:
        """Get performance metrics for all agents"""
        return self.agent_metrics
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session performance summary"""
        total_calls = len(self.log_entries)
        successful_calls = sum(1 for entry in self.log_entries if entry.success)
        failed_calls = total_calls - successful_calls
        
        total_duration = sum(entry.duration for entry in self.log_entries)
        avg_duration = total_duration / total_calls if total_calls > 0 else 0
        
        return {
            "session_start": self.session_start.isoformat(),
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
            "total_duration": total_duration,
            "avg_duration": avg_duration,
            "agents_active": len(self.agent_metrics)
        }
    
    def get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get performance summary for specified days"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_entries = [entry for entry in self.log_entries 
                         if entry.timestamp >= cutoff_date]
        
        total_calls = len(recent_entries)
        successful_calls = sum(1 for entry in recent_entries if entry.success)
        failed_calls = total_calls - successful_calls
        
        total_duration = sum(entry.duration for entry in recent_entries)
        avg_duration = total_duration / total_calls if total_calls > 0 else 0
        
        # Get agent performance
        agent_performance = {}
        for agent_name, metrics in self.agent_metrics.items():
            agent_performance[agent_name] = {
                "total_calls": metrics.total_calls,
                "successful_calls": metrics.successful_calls,
                "success_rate": metrics.success_rate,
                "avg_duration": metrics.avg_duration
            }
        
        return {
            "period_days": days,
            "period_start": cutoff_date.isoformat(),
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
            "total_duration": total_duration,
            "avg_duration": avg_duration,
            "agents_active": len(self.agent_metrics),
            "agent_performance": agent_performance,
            "slow_operations": self.get_slow_operations(threshold=1.0),
            "error_summary": self.get_error_summary()
        }
    
    def export_logs(self) -> str:
        """Export logs to JSON format"""
        export_data = {
            "session_summary": self.get_session_summary(),
            "agent_metrics": {
                name: {
                    "agent_name": metrics.agent_name,
                    "total_calls": metrics.total_calls,
                    "successful_calls": metrics.successful_calls,
                    "failed_calls": metrics.failed_calls,
                    "total_duration": metrics.total_duration,
                    "avg_duration": metrics.avg_duration,
                    "success_rate": metrics.success_rate,
                    "last_call": metrics.last_call.isoformat() if metrics.last_call else None
                }
                for name, metrics in self.agent_metrics.items()
            },
            "log_entries": [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "agent_name": entry.agent_name,
                    "action": entry.action,
                    "duration": entry.duration,
                    "success": entry.success,
                    "details": entry.details,
                    "error_message": entry.error_message
                }
                for entry in self.log_entries
            ]
        }
        
        # Save to file
        with open(self.log_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return json.dumps(export_data, indent=2)
    
    def get_slow_operations(self, threshold: float = 1.0) -> List[LogEntry]:
        """Get operations slower than threshold"""
        return [entry for entry in self.log_entries if entry.duration > threshold]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors"""
        error_entries = [entry for entry in self.log_entries if not entry.success]
        
        if not error_entries:
            return {"total_errors": 0, "error_types": {}, "error_agents": {}}
        
        error_types = {}
        error_agents = {}
        
        for entry in error_entries:
            # Count by error type
            error_type = entry.error_message or "Unknown error"
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Count by agent
            agent = entry.agent_name
            error_agents[agent] = error_agents.get(agent, 0) + 1
        
        return {
            "total_errors": len(error_entries),
            "error_types": error_types,
            "error_agents": error_agents,
            "error_rate": len(error_entries) / len(self.log_entries)
        }

class LoggedAgent:
    """Base class for agents with performance logging"""
    
    def __init__(self, name: str, logger: Optional[PerformanceLogger] = None):
        self.name = name
        self.logger = logger
        self.action_count = 0
    
    def _log_start(self, action: str) -> datetime:
        """Log the start of an action"""
        self.action_count += 1
        return datetime.now()
    
    def _log_end(self, action: str, start_time: datetime, success: bool = True, 
                  details: Dict[str, Any] = None, error_message: Optional[str] = None):
        """Log the end of an action"""
        if self.logger:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.log_action(
                agent_name=self.name,
                action=action,
                duration=duration,
                success=success,
                details=details,
                error_message=error_message
            )
    
    def logged_execute(self, action: str, func, *args, **kwargs):
        """Execute a function with logging"""
        start_time = self._log_start(action)
        
        try:
            result = func(*args, **kwargs)
            self._log_end(action, start_time, success=True)
            return result
        except Exception as e:
            self._log_end(action, start_time, success=False, error_message=str(e))
            raise
    
    def logged_operation(self, action: str, func, *args, **kwargs):
        """Execute a logged operation - this is the method that was missing"""
        return self.logged_execute(action, func, *args, **kwargs)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this agent"""
        if self.logger:
            metrics = self.logger.get_agent_metrics(self.name)
            if metrics:
                return {
                    "agent_name": self.name,
                    "total_calls": metrics.total_calls,
                    "success_rate": metrics.success_rate,
                    "avg_duration": metrics.avg_duration,
                    "action_count": self.action_count
                }
        
        return {
            "agent_name": self.name,
            "total_calls": 0,
            "success_rate": 0.0,
            "avg_duration": 0.0,
            "action_count": self.action_count
        }

class LoggedAgentWrapper:
    """Wrapper class for adding performance logging to existing agents"""
    
    def __init__(self, agent, logger: PerformanceLogger):
        self.agent = agent
        self.logger = logger
        self.name = getattr(agent, 'name', agent.__class__.__name__)
        self.action_count = 0
    
    def _log_start(self, action: str) -> datetime:
        """Log the start of an action"""
        self.action_count += 1
        return datetime.now()
    
    def _log_end(self, action: str, start_time: datetime, success: bool = True, 
                  details: Dict[str, Any] = None, error_message: Optional[str] = None):
        """Log the end of an action"""
        if self.logger:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.log_action(
                agent_name=self.name,
                action=action,
                duration=duration,
                success=success,
                details=details,
                error_message=error_message
            )
    
    def logged_execute(self, action: str, func, *args, **kwargs):
        """Execute a function with logging"""
        start_time = self._log_start(action)
        
        try:
            result = func(*args, **kwargs)
            self._log_end(action, start_time, success=True)
            return result
        except Exception as e:
            self._log_end(action, start_time, success=False, error_message=str(e))
            raise
    
    def logged_operation(self, action: str, func, *args, **kwargs):
        """Execute a logged operation - this is the method that was missing"""
        return self.logged_execute(action, func, *args, **kwargs)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this agent"""
        if self.logger:
            metrics = self.logger.get_agent_metrics(self.name)
            if metrics:
                return {
                    "agent_name": self.name,
                    "total_calls": metrics.total_calls,
                    "success_rate": metrics.success_rate,
                    "avg_duration": metrics.avg_duration,
                    "action_count": self.action_count
                }
        
        return {
            "agent_name": self.name,
            "total_calls": 0,
            "success_rate": 0.0,
            "avg_duration": 0.0,
            "action_count": self.action_count
        }
    
    def __getattr__(self, name):
        """Delegate attribute access to the wrapped agent"""
        attr = getattr(self.agent, name)
        
        # If it's a method, wrap it with logging
        if callable(attr):
            def wrapped_method(*args, **kwargs):
                return self.logged_execute(name, attr, *args, **kwargs)
            return wrapped_method
        
        return attr
    
    def track_operation(self, operation_name: str, method, *args, **kwargs):
        """Track an operation with logging - delegate to wrapped agent if it has the method"""
        if hasattr(self.agent, 'track_operation'):
            return self.agent.track_operation(operation_name, method, *args, **kwargs)
        else:
            # Fallback to logged_execute
            return self.logged_execute(operation_name, method, *args, **kwargs)

def demonstrate_performance_logging():
    """Demonstrate performance logging system"""
    
    print("📊 Performance Logging Demo")
    print("=" * 60)
    
    # Initialize logger
    logger = PerformanceLogger()
    
    # Simulate agent actions
    print("\n🤖 Simulating Agent Actions:")
    
    # Create logged agents
    agent1 = LoggedAgent("ContentAnalyst", logger)
    agent2 = LoggedAgent("SocialStrategist", logger)
    agent3 = LoggedAgent("ScriptDoctor", logger)
    
    # Simulate actions
    def analyze_content():
        import time
        time.sleep(0.1)  # Simulate work
        return {"topics": ["AI", "technology"], "sentiment": "positive"}
    
    def create_strategy():
        import time
        time.sleep(0.15)  # Simulate work
        return {"platform": "twitter", "content": "strategy"}
    
    def improve_script():
        import time
        time.sleep(0.05)  # Simulate work
        return {"improved": True, "changes": 3}
    
    def failing_action():
        import time
        time.sleep(0.02)
        raise ValueError("Simulated error")
    
    # Execute logged actions
    agent1.logged_execute("content_analysis", analyze_content)
    agent2.logged_execute("strategy_creation", create_strategy)
    agent3.logged_execute("script_improvement", improve_script)
    
    # Simulate a failing action
    try:
        agent1.logged_execute("failing_action", failing_action)
    except:
        pass  # Expected to fail
    
    # More actions
    agent1.logged_execute("content_analysis", analyze_content)
    agent2.logged_execute("strategy_creation", create_strategy)
    
    # Show session summary
    summary = logger.get_session_summary()
    print(f"\n📊 Session Summary:")
    print(f"   📞 Total Calls: {summary['total_calls']}")
    print(f"   ✅ Successful: {summary['successful_calls']}")
    print(f"   ❌ Failed: {summary['failed_calls']}")
    print(f"   📈 Success Rate: {summary['success_rate']:.2%}")
    print(f"   ⏱️ Avg Duration: {summary['avg_duration']:.3f}s")
    print(f"   🤖 Agents Active: {summary['agents_active']}")
    
    # Show agent metrics
    metrics = logger.get_all_metrics()
    print(f"\n📈 Agent Performance:")
    for agent_name, agent_metrics in metrics.items():
        print(f"   🤖 {agent_name}:")
        print(f"      📞 Calls: {agent_metrics.total_calls}")
        print(f"      ✅ Success Rate: {agent_metrics.success_rate:.2%}")
        print(f"      ⏱️ Avg Duration: {agent_metrics.avg_duration:.3f}s")
    
    # Show error summary
    error_summary = logger.get_error_summary()
    if error_summary["total_errors"] > 0:
        print(f"\n❌ Error Summary:")
        print(f"   🚨 Total Errors: {error_summary['total_errors']}")
        print(f"   📊 Error Rate: {error_summary['error_rate']:.2%}")
        print(f"   🏷️ Error Types: {error_summary['error_types']}")
    
    # Show slow operations
    slow_ops = logger.get_slow_operations(threshold=0.1)
    if slow_ops:
        print(f"\n🐌 Slow Operations (>0.1s):")
        for op in slow_ops:
            print(f"   🤖 {op.agent_name}: {op.action} ({op.duration:.3f}s)")
    
    # Export logs
    logger.export_logs()
    print(f"\n💾 Logs exported to: {logger.log_file}")
    
    print("\n" + "=" * 60)
    print("\n📊 Performance Logging Benefits:")
    print("   ✅ Detailed performance tracking")
    print("   ✅ Agent-specific metrics")
    print("   ✅ Error monitoring and analysis")
    print("   ✅ Performance optimization insights")
    print("   ✅ Comprehensive logging and reporting")
    
    print("\n💼 Interview Points:")
    print("   🎯 'I implemented comprehensive performance logging for all agents'")
    print("   🎯 'Real-time monitoring of agent performance and success rates'")
    print("   🎯 'Error tracking and analysis for debugging'")
    print("   🎯 'Performance optimization through detailed metrics'")
    print("   🎯 'Exportable logs for analysis and reporting'")

if __name__ == "__main__":
    demonstrate_performance_logging()
