#!/usr/bin/env python3
"""
Cost Tracking System - Monitors API usage and costs
Provides detailed cost analysis and budget management
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import os

@dataclass
class CostMetrics:
    """Cost metrics for API usage"""
    tokens_used: int = 0
    api_calls: int = 0
    cost: float = 0.0
    model: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AgentCost:
    """Cost tracking for individual agents"""
    agent_name: str
    total_tokens: int = 0
    total_calls: int = 0
    total_cost: float = 0.0
    calls_history: List[CostMetrics] = field(default_factory=list)

class CostTracker:
    """Tracks API costs and usage across agents"""
    
    def __init__(self, use_ollama: bool = False):
        self.use_ollama = use_ollama
        self.agent_costs: Dict[str, AgentCost] = {}
        self.session_start = datetime.now()
        self.total_cost = 0.0
        self.total_tokens = 0
        self.total_calls = 0
        self.video_count = 0
        self.content_pieces_generated = 0
        
        # Create current_metrics for compatibility
        self.current_metrics = type('CurrentMetrics', (), {
            'video_count': 0,
            'content_pieces_generated': 0,
            'total_cost': 0.0,
            'total_tokens': 0,
            'total_calls': 0
        })()
        
        provider = "Ollama (Local)" if use_ollama else "OpenAI (Cloud)"
        print(f"💰 Cost Tracker Initialized")
        print(f"📊 Provider: {provider}")
        print(f"📊 Tracking API usage and costs")
    
    def track_api_call(self, agent_name: str, tokens_used: int, model: str = "gpt-3.5-turbo", cost_per_token: float = 0.000002):
        """Track an API call"""
        # Calculate cost (simplified pricing)
        if self.use_ollama:
            call_cost = 0.0  # Ollama is free
            model = "Ollama Local"
        else:
            call_cost = tokens_used * cost_per_token
        
        # Create metrics
        metrics = CostMetrics(
            tokens_used=tokens_used,
            api_calls=1,
            cost=call_cost,
            model=model
        )
        
        # Update agent costs
        if agent_name not in self.agent_costs:
            self.agent_costs[agent_name] = AgentCost(agent_name=agent_name)
        
        agent = self.agent_costs[agent_name]
        agent.total_tokens += tokens_used
        agent.total_calls += 1
        agent.total_cost += call_cost
        agent.calls_history.append(metrics)
        
        # Update totals
        self.total_tokens += tokens_used
        self.total_calls += 1
        self.total_cost += call_cost
        
        # Update current_metrics for compatibility
        self.current_metrics.total_tokens += tokens_used
        self.current_metrics.total_calls += 1
        self.current_metrics.total_cost += call_cost
        
        print(f"💰 Tracked {agent_name}: {tokens_used} tokens, ${call_cost:.6f}")
    
    def get_agent_cost(self, agent_name: str) -> Optional[AgentCost]:
        """Get cost information for a specific agent"""
        return self.agent_costs.get(agent_name)
    
    def get_total_cost(self) -> Dict[str, Any]:
        """Get total cost summary"""
        return {
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens,
            "total_calls": self.total_calls,
            "session_duration": (datetime.now() - self.session_start).total_seconds(),
            "agents_count": len(self.agent_costs)
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get complete session summary including all metrics"""
        return {
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens,
            "total_calls": self.total_calls,
            "session_duration": (datetime.now() - self.session_start).total_seconds(),
            "agents_count": len(self.agent_costs),
            "video_count": getattr(self, 'video_count', 0),
            "content_pieces_generated": getattr(self, 'content_pieces_generated', 0),
            "current_metrics": {
                "video_count": self.current_metrics.video_count,
                "content_pieces_generated": self.current_metrics.content_pieces_generated,
                "total_cost": self.current_metrics.total_cost,
                "total_tokens": self.current_metrics.total_tokens,
                "total_calls": self.current_metrics.total_calls
            },
            "cost_breakdown": self.get_cost_breakdown(),
            "provider": "Ollama (Local)" if self.use_ollama else "OpenAI (Cloud)"
        }
    
    def get_cost_breakdown(self) -> Dict[str, Any]:
        """Get detailed cost breakdown by agent"""
        breakdown = {}
        
        for agent_name, agent_cost in self.agent_costs.items():
            breakdown[agent_name] = {
                "total_tokens": agent_cost.total_tokens,
                "total_calls": agent_cost.total_calls,
                "total_cost": agent_cost.total_cost,
                "avg_cost_per_call": agent_cost.total_cost / agent_cost.total_calls if agent_cost.total_calls > 0 else 0,
                "avg_tokens_per_call": agent_cost.total_tokens / agent_cost.total_calls if agent_cost.total_calls > 0 else 0
            }
        
        return breakdown
    
    def export_cost_report(self) -> str:
        """Export detailed cost report"""
        report = {
            "session_summary": self.get_total_cost(),
            "agent_breakdown": self.get_cost_breakdown(),
            "session_start": self.session_start.isoformat(),
            "export_time": datetime.now().isoformat()
        }
        
        return json.dumps(report, indent=2)

class TrackedAgent:
    """Base class for agents with cost tracking"""
    
    def __init__(self, name: str, cost_tracker: Optional[CostTracker] = None):
        self.name = name
        self.cost_tracker = cost_tracker
        self.tokens_used = 0
        self.api_calls = 0
    
    def _track_usage(self, tokens: int, model: str = "gpt-3.5-turbo"):
        """Track API usage"""
        self.tokens_used += tokens
        self.api_calls += 1
        
        if self.cost_tracker:
            self.cost_tracker.track_api_call(self.name, tokens, model)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "agent_name": self.name,
            "tokens_used": self.tokens_used,
            "api_calls": self.api_calls,
            "avg_tokens_per_call": self.tokens_used / self.api_calls if self.api_calls > 0 else 0
        }

class TrackedAgentWrapper:
    """Wrapper class for adding cost tracking to existing agents"""
    
    def __init__(self, agent, cost_tracker: CostTracker):
        self.agent = agent
        self.cost_tracker = cost_tracker
        self.name = getattr(agent, 'name', agent.__class__.__name__)
        
    def __getattr__(self, name):
        """Delegate attribute access to the wrapped agent"""
        attr = getattr(self.agent, name)
        
        # If it's a method, wrap it with cost tracking
        if callable(attr):
            def wrapped_method(*args, **kwargs):
                # Track the call (estimate tokens)
                estimated_tokens = len(str(args) + str(kwargs)) // 4  # Rough estimate
                self.cost_tracker.track_api_call(self.name, estimated_tokens)
                return attr(*args, **kwargs)
            return wrapped_method
        
        return attr
    
    def track_operation(self, operation_name: str, method, *args, **kwargs):
        """Track an operation with cost tracking"""
        # Track the call (estimate tokens)
        estimated_tokens = len(str(args) + str(kwargs)) // 4  # Rough estimate
        self.cost_tracker.track_api_call(f"{self.name}_{operation_name}", estimated_tokens)
        
        # Call the method
        result = method(*args, **kwargs)
        
        # If result is an AgentResponse and has content with detected_product, preserve it
        if hasattr(result, 'content') and hasattr(result.content, 'get'):
            # Check if we're in the pipeline's analysis step
            if 'content_analysis' in operation_name or 'analysis' in operation_name:
                # Get the original analysis from args to preserve detected_product
                if len(args) > 0 and hasattr(args[0], 'content'):
                    original_analysis = args[0]
                    if hasattr(original_analysis, 'content') and isinstance(original_analysis.content, dict):
                        detected_product = original_analysis.content.get('detected_product', 'Unknown product')
                        # Ensure the result's content has the detected_product
                        if isinstance(result.content, dict):
                            result.content['detected_product'] = detected_product
                        elif hasattr(result.content, '__dict__'):
                            # Handle dataclass-like objects
                            setattr(result.content, 'detected_product', detected_product)
        
        return result
    
    def logged_operation(self, action: str, func, *args, **kwargs):
        """Execute a logged operation with cost tracking - delegate to track_operation"""
        return self.track_operation(action, func, *args, **kwargs)

class AgencyDashboard:
    """Dashboard for agency-wide cost and performance metrics"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        print("📊 Agency Dashboard Initialized")
        print(f"🔍 Debug: AgencyDashboard methods: {[m for m in dir(self) if not m.startswith('_')]}")
    
    def generate_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard"""
        return {
            "cost_summary": self.cost_tracker.get_total_cost(),
            "agent_performance": self.cost_tracker.get_cost_breakdown(),
            "efficiency_metrics": self._calculate_efficiency(),
            "budget_analysis": self._analyze_budget(),
            "recommendations": self._generate_recommendations()
        }
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate dashboard data - alias for generate_dashboard"""
        print("🔍 Debug: generate_dashboard_data() called!")
        return self.generate_dashboard()
    
    def _calculate_efficiency(self) -> Dict[str, Any]:
        """Calculate efficiency metrics"""
        total = self.cost_tracker.get_total_cost()
        
        return {
            "cost_per_token": total["total_cost"] / total["total_tokens"] if total["total_tokens"] > 0 else 0,
            "tokens_per_call": total["total_tokens"] / total["total_calls"] if total["total_calls"] > 0 else 0,
            "cost_per_call": total["total_cost"] / total["total_calls"] if total["total_calls"] > 0 else 0,
            "calls_per_minute": total["total_calls"] / (total["session_duration"] / 60) if total["session_duration"] > 0 else 0
        }
    
    def _analyze_budget(self) -> Dict[str, Any]:
        """Analyze budget usage"""
        total = self.cost_tracker.get_total_cost()
        
        # Simulated budget (in real implementation, this would be configurable)
        daily_budget = 10.0
        hourly_budget = daily_budget / 24
        
        return {
            "daily_budget": daily_budget,
            "hourly_budget": hourly_budget,
            "current_spend": total["total_cost"],
            "budget_remaining": daily_budget - total["total_cost"],
            "budget_usage_percentage": (total["total_cost"] / daily_budget) * 100,
            "on_track": total["total_cost"] <= hourly_budget
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        total = self.cost_tracker.get_total_cost()
        breakdown = self.cost_tracker.get_cost_breakdown()
        
        # Check for high-cost agents
        high_cost_agents = [name for name, data in breakdown.items() if data["total_cost"] > 1.0]
        if high_cost_agents:
            recommendations.append(f"Consider optimizing {', '.join(high_cost_agents)} for cost efficiency")
        
        # Check for low efficiency
        if total["total_calls"] > 0:
            avg_cost_per_call = total["total_cost"] / total["total_calls"]
            if avg_cost_per_call > 0.01:
                recommendations.append("Average cost per call is high - consider token optimization")
        
        # Budget recommendations
        budget = self._analyze_budget()
        if budget["budget_usage_percentage"] > 80:
            recommendations.append("Approaching daily budget limit - monitor usage closely")
        
        return recommendations
    
    def export_dashboard(self) -> str:
        """Export dashboard data"""
        dashboard = self.generate_dashboard()
        return json.dumps(dashboard, indent=2)

def demonstrate_cost_tracking():
    """Demonstrate cost tracking system"""
    
    print("💰 Cost Tracking Demo")
    print("=" * 60)
    
    # Initialize cost tracker
    tracker = CostTracker(use_ollama=False)  # Demo uses OpenAI pricing
    
    # Simulate API calls
    print("\n📊 Simulating API calls...")
    tracker.track_api_call("ContentAnalyst", 150, "gpt-3.5-turbo")
    tracker.track_api_call("SocialStrategist", 200, "gpt-3.5-turbo")
    tracker.track_api_call("ScriptDoctor", 100, "gpt-3.5-turbo")
    tracker.track_api_call("ContentAnalyst", 75, "gpt-3.5-turbo")
    
    # Show total cost
    total = tracker.get_total_cost()
    print(f"\n💰 Total Cost Summary:")
    print(f"   💵 Total Cost: ${total['total_cost']:.6f}")
    print(f"   🔢 Total Tokens: {total['total_tokens']}")
    print(f"   📞 Total Calls: {total['total_calls']}")
    print(f"   ⏱️ Session Duration: {total['session_duration']:.1f}s")
    
    # Show breakdown
    breakdown = tracker.get_cost_breakdown()
    print(f"\n📊 Cost Breakdown by Agent:")
    for agent, data in breakdown.items():
        print(f"   🤖 {agent}:")
        print(f"      💵 Cost: ${data['total_cost']:.6f}")
        print(f"      🔢 Tokens: {data['total_tokens']}")
        print(f"      📞 Calls: {data['total_calls']}")
    
    # Create dashboard
    dashboard = AgencyDashboard(tracker)
    dashboard_data = dashboard.generate_dashboard()
    
    print(f"\n📈 Agency Dashboard:")
    efficiency = dashboard_data["efficiency_metrics"]
    print(f"   💰 Cost per token: ${efficiency['cost_per_token']:.8f}")
    print(f"   🔢 Tokens per call: {efficiency['tokens_per_call']:.1f}")
    print(f"   💰 Cost per call: ${efficiency['cost_per_call']:.6f}")
    
    budget = dashboard_data["budget_analysis"]
    print(f"\n💼 Budget Analysis:")
    print(f"   💵 Daily Budget: ${budget['daily_budget']:.2f}")
    print(f"   💰 Current Spend: ${budget['current_spend']:.6f}")
    print(f"   📊 Usage: {budget['budget_usage_percentage']:.2f}%")
    
    recommendations = dashboard_data["recommendations"]
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    print("\n" + "=" * 60)
    print("\n💰 Cost Tracking Benefits:")
    print("   ✅ Real-time cost monitoring")
    print("   ✅ Agent-specific cost breakdown")
    print("   ✅ Budget management and alerts")
    print("   ✅ Efficiency metrics and optimization")
    print("   ✅ Comprehensive reporting")
    
    print("\n💼 Interview Points:")
    print("   🎯 'I implemented comprehensive cost tracking for AI agents'")
    print("   🎯 'Real-time monitoring of API usage and costs'")
    print("   🎯 'Agent-specific cost breakdown and optimization'")
    print("   🎯 'Budget management with automated recommendations'")
    print("   🎯 'Efficiency metrics for performance optimization'")

if __name__ == "__main__":
    demonstrate_cost_tracking()
