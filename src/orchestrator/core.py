"""
Orchestrator - Central logic that manages state and decides next steps
Implements decoupled agent communication through a centralized workflow system
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ..schema.models import (
    WorkflowState, WorkflowStep, AgentStatus, AgentResponse, ToolRequest,
    ToolResponse, ProcessingResult, AgentState, LogEntry, LogLevel
)
from ..tools.executor import tool_executor, tool_registry
from ..config.manager import config_manager, system_prompts
from .observability import observability, AgentLogger

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class OrchestratorMode(Enum):
    """Orchestrator execution modes"""
    SEQUENTIAL = "sequential"  # Execute steps one by one
    PARALLEL = "parallel"    # Execute independent steps in parallel
    ADAPTIVE = "adaptive"    # Dynamically choose execution strategy

@dataclass
class ExecutionPlan:
    """Execution plan for a workflow"""
    workflow_id: str
    steps: List[WorkflowStep]
    execution_mode: OrchestratorMode = OrchestratorMode.SEQUENTIAL
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    estimated_duration: Optional[float] = None
    retry_policy: Dict[str, Any] = field(default_factory=dict)

class AgentOrchestrator:
    """Central orchestrator for managing agent workflows"""
    
    def __init__(self):
        self.active_workflows: Dict[str, WorkflowState] = {}
        self.execution_plans: Dict[str, ExecutionPlan] = {}
        self.agent_registry: Dict[str, Any] = {}  # Will hold agent instances
        self.workflow_templates: Dict[str, List[WorkflowStep]] = {}
        self.execution_mode = OrchestratorMode.SEQUENTIAL
        self.max_concurrent_workflows = 5
        
        # Load configuration
        self.config = config_manager.get_system_config()
        
        # Register built-in workflow templates
        self._register_builtin_templates()
    
    def _register_builtin_templates(self):
        """Register built-in workflow templates"""
        
        # Content Repurposing Workflow
        content_repurposing_steps = [
            WorkflowStep(
                step_name="transcript_extraction",
                agent_name="transcript_extractor",
                step_type="tool_call",
                dependencies=[],
                input_data={"source": "video/audio"}
            ),
            WorkflowStep(
                step_name="content_analysis",
                agent_name="content_analyst",
                step_type="analysis",
                dependencies=["transcript_extraction"]
            ),
            WorkflowStep(
                step_name="product_detection",
                agent_name="product_detector",
                step_type="analysis",
                dependencies=["content_analysis"]
            ),
            WorkflowStep(
                step_name="seo_analysis",
                agent_name="seo_analyst",
                step_type="analysis",
                dependencies=["content_analysis"]
            ),
            WorkflowStep(
                step_name="social_content_creation",
                agent_name="social_strategist",
                step_type="synthesis",
                dependencies=["content_analysis", "product_detection", "seo_analysis"]
            ),
            WorkflowStep(
                step_name="script_creation",
                agent_name="script_doctor",
                step_type="synthesis",
                dependencies=["content_analysis", "product_detection"]
            ),
            WorkflowStep(
                step_name="newsletter_creation",
                agent_name="newsletter_writer",
                step_type="synthesis",
                dependencies=["content_analysis", "product_detection"]
            ),
            WorkflowStep(
                step_name="blog_creation",
                agent_name="blog_writer",
                step_type="synthesis",
                dependencies=["content_analysis", "product_detection", "seo_analysis"]
            ),
            WorkflowStep(
                step_name="quality_control",
                agent_name="quality_controller",
                step_type="verification",
                dependencies=["social_content_creation", "script_creation", 
                             "newsletter_creation", "blog_creation"]
            )
        ]
        
        self.workflow_templates["content_repurposing"] = content_repurposing_steps
    
    def register_agent(self, agent_name: str, agent_instance: Any):
        """Register an agent instance"""
        self.agent_registry[agent_name] = agent_instance
        
        # Create logger for the agent
        agent_logger = AgentLogger(agent_name, observability)
        
        # Initialize agent state
        agent_state = AgentState(agent_name=agent_name)
        observability.update_agent_state(agent_state)
        
        observability.log(
            LogLevel.INFO,
            "orchestrator",
            f"Agent registered: {agent_name}",
            data={"agent_type": type(agent_instance).__name__}
        )
    
    def create_workflow(self, workflow_name: str, template_name: Optional[str] = None,
                        steps: Optional[List[WorkflowStep]] = None, 
                        input_data: Optional[Dict[str, Any]] = None) -> str:
        """Create a new workflow instance"""
        
        workflow_id = str(uuid.uuid4())
        
        # Get steps from template or provided steps
        if template_name and template_name in self.workflow_templates:
            workflow_steps = self.workflow_templates[template_name].copy()
        elif steps:
            workflow_steps = steps.copy()
        else:
            raise ValueError("Must provide either template_name or steps")
        
        # Apply input data to steps
        if input_data:
            for step in workflow_steps:
                step.input_data.update(input_data)
        
        # Create workflow state
        workflow_state = WorkflowState(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            steps=workflow_steps,
            global_context=input_data or {}
        )
        
        self.active_workflows[workflow_id] = workflow_state
        
        # Create execution plan
        execution_plan = self._create_execution_plan(workflow_state)
        self.execution_plans[workflow_id] = execution_plan
        
        observability.log(
            LogLevel.INFO,
            "orchestrator",
            f"Workflow created: {workflow_name} ({workflow_id})",
            data={
                "template": template_name,
                "steps_count": len(workflow_steps),
                "execution_mode": execution_plan.execution_mode.value
            }
        )
        
        return workflow_id
    
    def _create_execution_plan(self, workflow_state: WorkflowState) -> ExecutionPlan:
        """Create execution plan for workflow"""
        # Analyze dependencies and determine execution order
        dependencies = {}
        for step in workflow_state.steps:
            dependencies[step.step_name] = step.dependencies
        
        # Determine execution mode based on dependencies
        has_dependencies = any(deps for deps in dependencies.values())
        execution_mode = OrchestratorMode.SEQUENTIAL if has_dependencies else OrchestratorMode.PARALLEL
        
        return ExecutionPlan(
            workflow_id=workflow_state.workflow_id,
            steps=workflow_state.steps,
            execution_mode=execution_mode,
            dependencies=dependencies
        )
    
    async def execute_workflow(self, workflow_id: str, 
                              progress_callback: Optional[Callable] = None) -> ProcessingResult:
        """Execute a workflow"""
        
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow_state = self.active_workflows[workflow_id]
        execution_plan = self.execution_plans[workflow_id]
        
        start_time = time.time()
        
        try:
            # Update workflow status
            workflow_state.status = AgentStatus.RUNNING
            workflow_state.start_time = datetime.now()
            
            observability.log(
                LogLevel.INFO,
                "orchestrator",
                f"Starting workflow execution: {workflow_state.workflow_name}",
                data={"workflow_id": workflow_id, "mode": execution_plan.execution_mode.value}
            )
            
            # Execute based on mode
            if execution_plan.execution_mode == OrchestratorMode.SEQUENTIAL:
                results = await self._execute_sequential(workflow_state, progress_callback)
            elif execution_plan.execution_mode == OrchestratorMode.PARALLEL:
                results = await self._execute_parallel(workflow_state, progress_callback)
            else:  # ADAPTIVE
                results = await self._execute_adaptive(workflow_state, progress_callback)
            
            # Update workflow completion
            workflow_state.status = AgentStatus.COMPLETED
            workflow_state.end_time = datetime.now()
            workflow_state.total_execution_time = time.time() - start_time
            
            # Update global context with results
            workflow_state.global_context.update(results)
            
            observability.log(
                LogLevel.INFO,
                "orchestrator",
                f"Workflow completed: {workflow_state.workflow_name}",
                data={
                    "workflow_id": workflow_id,
                    "execution_time": workflow_state.total_execution_time,
                    "steps_completed": len([s for s in workflow_state.steps if s.status == AgentStatus.COMPLETED])
                }
            )
            
            return ProcessingResult(
                success=True,
                workflow_id=workflow_id,
                total_execution_time=workflow_state.total_execution_time,
                results=results,
                metrics=self._collect_workflow_metrics(workflow_state)
            )
            
        except Exception as e:
            # Handle workflow failure
            workflow_state.status = AgentStatus.FAILED
            workflow_state.end_time = datetime.now()
            workflow_state.total_execution_time = time.time() - start_time
            
            observability.log_error("orchestrator", e, data={"workflow_id": workflow_id})
            
            return ProcessingResult(
                success=False,
                workflow_id=workflow_id,
                total_execution_time=workflow_state.total_execution_time,
                errors=[str(e)],
                metrics=self._collect_workflow_metrics(workflow_state)
            )
    
    async def _execute_sequential(self, workflow_state: WorkflowState, 
                                progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute workflow steps sequentially"""
        results = {}
        
        for step in workflow_state.steps:
            # Check dependencies
            if not self._check_dependencies(step, results):
                step.status = AgentStatus.FAILED
                step.error_message = "Dependencies not met"
                continue
            
            # Execute step
            step.status = AgentStatus.ACTING
            workflow_state.current_step = step.step_name
            
            if progress_callback:
                progress_callback(step.step_name, "executing")
            
            try:
                step_result = await self._execute_step(step, results)
                results[step.step_name] = step_result
                step.status = AgentStatus.COMPLETED
                step.output_data = step_result
                
                if progress_callback:
                    progress_callback(step.step_name, "completed")
                    
            except Exception as e:
                step.status = AgentStatus.FAILED
                step.error_message = str(e)
                step.retry_count += 1
                
                observability.log_error("orchestrator", e, 
                                       data={"workflow_id": workflow_state.workflow_id, "step": step.step_name})
                
                if progress_callback:
                    progress_callback(step.step_name, "failed")
                
                # Decide whether to continue or fail
                if step.retry_count >= step.max_retries:
                    raise e
        
        return results
    
    async def _execute_parallel(self, workflow_state: WorkflowState,
                               progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute independent steps in parallel"""
        results = {}
        
        # Group steps by dependency level
        dependency_levels = self._calculate_dependency_levels(workflow_state.steps)
        
        for level, steps in dependency_levels.items():
            # Execute steps at this level in parallel
            tasks = []
            for step in steps:
                if self._check_dependencies(step, results):
                    step.status = AgentStatus.ACTING
                    task = self._execute_step(step, results)
                    tasks.append((step, task))
            
            # Wait for all tasks at this level
            if tasks:
                step_results = await asyncio.gather(
                    *[task for _, task in tasks],
                    return_exceptions=True
                )
                
                for (step, _), result in zip(tasks, step_results):
                    if isinstance(result, Exception):
                        step.status = AgentStatus.FAILED
                        step.error_message = str(result)
                        step.retry_count += 1
                    else:
                        results[step.step_name] = result
                        step.status = AgentStatus.COMPLETED
                        step.output_data = result
        
        return results
    
    async def _execute_adaptive(self, workflow_state: WorkflowState,
                              progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute workflow with adaptive strategy selection"""
        # For now, default to sequential
        # In future, could analyze step characteristics and choose optimal strategy
        return await self._execute_sequential(workflow_state, progress_callback)
    
    async def _execute_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Any:
        """Execute a single workflow step"""
        
        # Get agent instance
        agent = self.agent_registry.get(step.agent_name)
        if not agent:
            raise ValueError(f"Agent {step.agent_name} not found")
        
        # Create agent logger
        logger = AgentLogger(step.agent_name, observability)
        
        # Update agent state
        agent_state = AgentState(
            agent_name=step.agent_name,
            status=AgentStatus.THINKING,
            current_task=step.step_name
        )
        observability.update_agent_state(agent_state)
        
        logger.info(f"Executing step: {step.step_name}")
        
        # Execute based on step type
        if step.step_type == "tool_call":
            return await self._execute_tool_step(step, logger)
        elif step.step_type == "analysis":
            return await self._execute_analysis_step(step, agent, logger, context)
        elif step.step_type == "synthesis":
            return await self._execute_synthesis_step(step, agent, logger, context)
        elif step.step_type == "verification":
            return await self._execute_verification_step(step, agent, logger, context)
        else:
            raise ValueError(f"Unknown step type: {step.step_type}")
    
    async def _execute_tool_step(self, step: WorkflowStep, logger: AgentLogger) -> Any:
        """Execute a tool call step"""
        
        # Create tool request
        tool_request = ToolRequest(
            tool_name=step.input_data.get("tool_name"),
            parameters=step.input_data.get("parameters", {}),
            agent_name=step.agent_name
        )
        
        logger.info(f"Calling tool: {tool_request.tool_name}")
        
        # Log tool request
        observability.log_tool_request(tool_request)
        
        # Execute tool
        tool_response = await tool_executor.execute_tool(tool_request)
        
        # Log tool response
        observability.log_tool_response(tool_response)
        
        if not tool_response.success:
            raise Exception(f"Tool execution failed: {tool_response.error_message}")
        
        logger.info(f"Tool execution completed: {tool_request.tool_name}")
        
        return tool_response.result
    
    async def _execute_analysis_step(self, step: WorkflowStep, agent: Any, 
                                   logger: AgentLogger, context: Dict[str, Any]) -> Any:
        """Execute an analysis step"""
        
        # Prepare input for agent
        input_data = {**step.input_data, **context}
        
        logger.reason(f"Starting analysis for {step.step_name}")
        
        # Call agent's analysis method
        if hasattr(agent, 'analyze'):
            result = await self._call_agent_method(agent, 'analyze', input_data, logger)
        elif hasattr(agent, 'process'):
            result = await self._call_agent_method(agent, 'process', input_data, logger)
        else:
            raise ValueError(f"Agent {step.agent_name} has no analysis method")
        
        logger.info(f"Analysis completed: {step.step_name}")
        
        return result
    
    async def _execute_synthesis_step(self, step: WorkflowStep, agent: Any,
                                    logger: AgentLogger, context: Dict[str, Any]) -> Any:
        """Execute a synthesis step"""
        
        # Prepare input for agent
        input_data = {**step.input_data, **context}
        
        logger.reason(f"Starting synthesis for {step.step_name}")
        
        # Call agent's synthesis method
        if hasattr(agent, 'synthesize'):
            result = await self._call_agent_method(agent, 'synthesize', input_data, logger)
        elif hasattr(agent, 'create'):
            result = await self._call_agent_method(agent, 'create', input_data, logger)
        elif hasattr(agent, 'process'):
            result = await self._call_agent_method(agent, 'process', input_data, logger)
        else:
            raise ValueError(f"Agent {step.agent_name} has no synthesis method")
        
        logger.info(f"Synthesis completed: {step.step_name}")
        
        return result
    
    async def _execute_verification_step(self, step: WorkflowStep, agent: Any,
                                      logger: AgentLogger, context: Dict[str, Any]) -> Any:
        """Execute a verification step"""
        
        # Prepare input for agent
        input_data = {**step.input_data, **context}
        
        logger.reason(f"Starting verification for {step.step_name}")
        
        # Call agent's verification method
        if hasattr(agent, 'verify'):
            result = await self._call_agent_method(agent, 'verify', input_data, logger)
        elif hasattr(agent, 'validate'):
            result = await self._call_agent_method(agent, 'validate', input_data, logger)
        elif hasattr(agent, 'process'):
            result = await self._call_agent_method(agent, 'process', input_data, logger)
        else:
            raise ValueError(f"Agent {step.agent_name} has no verification method")
        
        logger.info(f"Verification completed: {step.step_name}")
        
        return result
    
    async def _call_agent_method(self, agent: Any, method_name: str, 
                                input_data: Dict[str, Any], logger: AgentLogger) -> Any:
        """Call an agent method with proper error handling"""
        
        method = getattr(agent, method_name)
        
        # Update agent state to acting
        agent_state = observability.get_agent_state(agent.__class__.__name__.lower())
        if agent_state:
            agent_state.status = AgentStatus.ACTING
            observability.update_agent_state(agent_state)
        
        try:
            # Call method (handle both sync and async)
            if asyncio.iscoroutinefunction(method):
                result = await method(**input_data)
            else:
                result = method(**input_data)
            
            # Log agent response
            if hasattr(result, 'success') and hasattr(result, 'confidence'):
                observability.log_agent_response(agent.__class__.__name__.lower(), result)
            
            return result
            
        except Exception as e:
            # Update agent state to failed
            if agent_state:
                agent_state.status = AgentStatus.FAILED
                agent_state.error_count += 1
                observability.update_agent_state(agent_state)
            
            logger.error(f"Method {method_name} failed", e)
            raise
    
    def _check_dependencies(self, step: WorkflowStep, completed_results: Dict[str, Any]) -> bool:
        """Check if step dependencies are satisfied"""
        for dependency in step.dependencies:
            if dependency not in completed_results:
                return False
        return True
    
    def _calculate_dependency_levels(self, steps: List[WorkflowStep]) -> Dict[int, List[WorkflowStep]]:
        """Calculate dependency levels for parallel execution"""
        levels = {}
        remaining_steps = steps.copy()
        current_level = 0
        
        while remaining_steps:
            level_steps = []
            for step in remaining_steps[:]:
                # Check if all dependencies are in previous levels
                deps_satisfied = all(
                    any(dep_step.step_name == dep for dep_step in levels.get(level, []))
                    for dep in step.dependencies
                )
                
                if deps_satisfied or not step.dependencies:
                    level_steps.append(step)
                    remaining_steps.remove(step)
            
            if level_steps:
                levels[current_level] = level_steps
                current_level += 1
            else:
                # Circular dependency or missing dependency
                raise ValueError("Circular or missing dependencies detected")
        
        return levels
    
    def _collect_workflow_metrics(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Collect performance metrics for workflow"""
        metrics = {}
        
        for step in workflow_state.steps:
            agent_name = step.agent_name
            if agent_name not in metrics:
                agent_metrics = observability.get_performance_metrics(agent_name)
                if agent_name in agent_metrics:
                    metrics[agent_name] = agent_metrics[agent_name]
        
        return metrics
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get current status of a workflow"""
        return self.active_workflows.get(workflow_id)
    
    def list_active_workflows(self) -> List[WorkflowState]:
        """List all active workflows"""
        return list(self.active_workflows.values())
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.status = AgentStatus.FAILED
            workflow.end_time = datetime.now()
            
            observability.log(
                LogLevel.INFO,
                "orchestrator",
                f"Workflow cancelled: {workflow.workflow_name}",
                data={"workflow_id": workflow_id}
            )
            
            return True
        return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        active_workflows = self.list_active_workflows()
        
        return {
            "active_workflows": len(active_workflows),
            "registered_agents": len(self.agent_registry),
            "available_tools": len(tool_registry.tools),
            "workflow_templates": len(self.workflow_templates),
            "system_summary": observability.get_system_summary()
        }

# Global orchestrator instance
orchestrator = AgentOrchestrator()
