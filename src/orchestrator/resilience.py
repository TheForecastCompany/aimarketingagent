"""
Error Resilience System - Handles hallucinations, failed tool calls, and provides fallback mechanisms
Implements retry logic, circuit breakers, and graceful degradation
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import random

from ..schema.models import (
    AgentResponse, ToolRequest, ToolResponse, AgentStatus, LogLevel,
    ProcessingResult, AgentState
)
from ..config.manager import config_manager
from ..orchestrator.observability import observability

class ErrorType(Enum):
    """Types of errors that can occur"""
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    HALTUCINATION = "hallucination"
    TOOL_FAILURE = "tool_failure"
    AGENT_FAILURE = "agent_failure"
    UNKNOWN_ERROR = "unknown_error"

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail immediately
    HALF_OPEN = "half_open" # Testing if service has recovered

@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on: List[ErrorType] = field(default_factory=lambda: [
        ErrorType.TIMEOUT, ErrorType.NETWORK_ERROR, ErrorType.TOOL_FAILURE
    ])

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: type = Exception
    success_threshold: int = 3  # Successes needed to close circuit

class CircuitBreaker:
    """Circuit breaker pattern for preventing cascading failures"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.recovery_start_time = None
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                observability.log(
                    LogLevel.INFO,
                    "circuit_breaker",
                    f"Circuit {self.name} transitioning to HALF_OPEN"
                )
            else:
                raise Exception(f"Circuit breaker {self.name} is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.config.expected_exception as e:
            self._on_failure()
            raise e
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt to reset"""
        if self.recovery_start_time is None:
            self.recovery_start_time = time.time()
        
        return time.time() - self.recovery_start_time >= self.config.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._reset()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.recovery_start_time = time.time()
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                self.recovery_start_time = time.time()
                
                observability.log(
                    LogLevel.WARNING,
                    "circuit_breaker",
                    f"Circuit {self.name} opened due to {self.failure_count} failures"
                )
    
    def _reset(self):
        """Reset circuit breaker to closed state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.recovery_start_time = None
        
        observability.log(
            LogLevel.INFO,
            "circuit_breaker",
            f"Circuit {self.name} reset to CLOSED"
        )

class HallucinationDetector:
    """Detects and handles AI hallucinations"""
    
    def __init__(self):
        self.suspicious_patterns = [
            r"I (?:am|is) (?:an? )?AI",
            r"As an? AI",
            r"I (?:do not|don't) have",
            r"I (?:cannot|can't)",
            r"This is (?:not|n't) real",
            r"I (?:am|is) (?:not|n't) sure",
            r"I (?:believe|think) (?:that )?this (?:might|may|could)",
            r"\b(?:obviously|clearly|obviously)\b",
            r"\b(?:certainly|definitely|absolutely)\b"
        ]
        
        self.contradiction_indicators = [
            "however", "but", "although", "despite", "on the other hand"
        ]
        
        self.uncertainty_indicators = [
            "maybe", "perhaps", "possibly", "might", "could", "may", "seems"
        ]
    
    def detect_hallucination(self, text: str, confidence: float = None) -> Dict[str, Any]:
        """Detect potential hallucinations in text"""
        
        import re
        
        hallucination_score = 0.0
        reasons = []
        
        # Check for AI self-reference patterns
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                hallucination_score += len(matches) * 0.2
                reasons.append(f"AI self-reference detected: {len(matches)} instances")
        
        # Check for excessive uncertainty
        uncertainty_count = sum(1 for indicator in self.uncertainty_indicators 
                             if indicator.lower() in text.lower())
        if uncertainty_count > 3:
            hallucination_score += 0.3
            reasons.append(f"Excessive uncertainty: {uncertainty_count} indicators")
        
        # Check for contradictions
        contradiction_count = sum(1 for indicator in self.contradiction_indicators 
                                if indicator.lower() in text.lower())
        if contradiction_count > 2:
            hallucination_score += 0.2
            reasons.append(f"Multiple contradictions: {contradiction_count} instances")
        
        # Check confidence mismatch
        if confidence is not None and confidence > 0.8 and hallucination_score > 0.5:
            hallucination_score += 0.3
            reasons.append("High confidence with suspicious content")
        
        # Normalize score
        hallucination_score = min(hallucination_score, 1.0)
        
        is_hallucination = hallucination_score > 0.6
        
        return {
            "is_hallucination": is_hallucination,
            "score": hallucination_score,
            "reasons": reasons,
            "confidence_mismatch": confidence is not None and confidence > 0.8 and hallucination_score > 0.5
        }
    
    def sanitize_response(self, response: AgentResponse) -> AgentResponse:
        """Sanitize a response that may contain hallucinations"""
        
        if not response.success or not isinstance(response.content, str):
            return response
        
        detection = self.detect_hallucination(response.content, response.confidence)
        
        if detection["is_hallucination"]:
            observability.log(
                LogLevel.WARNING,
                "hallucination_detector",
                f"Hallucination detected in {response.agent_name}",
                data={
                    "score": detection["score"],
                    "reasons": detection["reasons"]
                }
            )
            
            # Create sanitized response
            sanitized_content = self._sanitize_text(response.content)
            
            return AgentResponse(
                success=True,  # Still successful but with caveats
                content=sanitized_content,
                confidence=max(response.confidence - 0.2, 0.3),  # Reduce confidence
                reasoning=response.reasoning + " [Content sanitized due to potential hallucination]",
                suggestions=response.suggestions + [
                    "Some content was flagged as potentially unreliable",
                    "Consider verifying the information independently"
                ],
                metadata={
                    **response.metadata,
                    "hallucination_detected": True,
                    "original_confidence": response.confidence,
                    "hallucination_score": detection["score"]
                }
            )
        
        return response
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text to remove hallucinated content"""
        
        import re
        
        # Remove AI self-references
        sanitized = re.sub(r"(?i)As an? AI[^.]*\.", "", sanitized)
        sanitized = re.sub(r"(?i)I (?:am|is) (?:an? )?AI[^.]*\.", "", sanitized)
        
        # Add disclaimer for uncertain content
        if any(indicator in sanitized.lower() for indicator in self.uncertainty_indicators):
            sanitized += "\n\n[Note: Some information in this response may be uncertain]"
        
        return sanitized.strip()

class FallbackAgent:
    """Provides fallback responses when primary agents fail"""
    
    def __init__(self):
        self.fallback_responses = {
            "content_analyst": {
                "success": False,
                "content": {
                    "topics": ["General content"],
                    "key_points": ["Unable to extract specific points due to processing error"],
                    "sentiment": "neutral",
                    "target_audience": "General audience",
                    "word_count": 0,
                    "estimated_reading_time": 0,
                    "confidence": 0.3
                },
                "confidence": 0.3,
                "reasoning": "Fallback response due to primary agent failure",
                "suggestions": ["Please try again with different content", "Check content format"]
            },
            "social_strategist": {
                "success": False,
                "content": {
                    "linkedin": {
                        "platform": "linkedin",
                        "content_type": "post",
                        "content": "Unable to generate social media content at this time. Please try again.",
                        "hashtags": ["#Content", "#SocialMedia"],
                        "mentions": [],
                        "character_count": 89
                    }
                },
                "confidence": 0.2,
                "reasoning": "Fallback social media content due to processing error",
                "suggestions": ["Try again with different input", "Check content quality"]
            },
            "default": {
                "success": False,
                "content": "Processing failed. Please try again later.",
                "confidence": 0.1,
                "reasoning": "Fallback response due to system error",
                "suggestions": ["Try again", "Contact support if issue persists"]
            }
        }
    
    def get_fallback_response(self, agent_name: str, error: Exception) -> AgentResponse:
        """Get fallback response for a failed agent"""
        
        fallback_data = self.fallback_responses.get(agent_name, self.fallback_responses["default"])
        
        observability.log(
            LogLevel.WARNING,
            "fallback_agent",
            f"Using fallback for {agent_name}",
            data={"error": str(error)}
        )
        
        return AgentResponse(
            **fallback_data,
            metadata={"fallback_used": True, "original_error": str(error)}
        )

class ErrorResilienceManager:
    """Manages error resilience across the system"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.hallucination_detector = HallucinationDetector()
        self.fallback_agent = FallbackAgent()
        
        # Default configurations
        self.default_retry_config = RetryConfig()
        self.default_circuit_config = CircuitBreakerConfig()
        
        # Load configuration
        self.config = config_manager.get_system_config()
    
    def get_circuit_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get or create a circuit breaker"""
        
        if name not in self.circuit_breakers:
            breaker_config = config or self.default_circuit_config
            self.circuit_breakers[name] = CircuitBreaker(name, breaker_config)
        
        return self.circuit_breakers[name]
    
    async def execute_with_resilience(self, func: Callable, agent_name: str, 
                                    retry_config: Optional[RetryConfig] = None,
                                    circuit_breaker_name: Optional[str] = None,
                                    *args, **kwargs) -> Any:
        """Execute function with full error resilience"""
        
        retry_config = retry_config or self.default_retry_config
        circuit_breaker_name = circuit_breaker_name or f"{agent_name}_circuit"
        
        # Get circuit breaker
        circuit_breaker = self.get_circuit_breaker(circuit_breaker_name)
        
        # Execute with circuit breaker and retry logic
        return await self._execute_with_retry(
            circuit_breaker.call, func, retry_config, agent_name, *args, **kwargs
        )
    
    async def _execute_with_retry(self, circuit_func: Callable, func: Callable, 
                                 retry_config: RetryConfig, agent_name: str,
                                 *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        
        last_exception = None
        
        for attempt in range(retry_config.max_attempts):
            try:
                if attempt > 0:
                    delay = self._calculate_delay(attempt, retry_config)
                    await asyncio.sleep(delay)
                    
                    observability.log(
                        LogLevel.INFO,
                        "retry_manager",
                        f"Retry attempt {attempt + 1} for {agent_name}",
                        data={"delay": delay}
                    )
                
                result = await circuit_func(func, *args, **kwargs)
                
                # Check for hallucinations if it's an agent response
                if isinstance(result, AgentResponse):
                    result = self.hallucination_detector.sanitize_response(result)
                
                if attempt > 0:
                    observability.log(
                        LogLevel.INFO,
                        "retry_manager",
                        f"Retry successful for {agent_name} on attempt {attempt + 1}"
                    )
                
                return result
                
            except Exception as e:
                last_exception = e
                error_type = self._classify_error(e)
                
                observability.log(
                    LogLevel.WARNING,
                    "retry_manager",
                    f"Attempt {attempt + 1} failed for {agent_name}",
                    data={"error": str(e), "error_type": error_type.value}
                )
                
                # Check if we should retry on this error type
                if error_type not in retry_config.retry_on:
                    break
                
                # If this is the last attempt, don't continue
                if attempt == retry_config.max_attempts - 1:
                    break
        
        # All attempts failed, use fallback
        observability.log(
            LogLevel.ERROR,
            "error_resilience",
            f"All retry attempts failed for {agent_name}",
            data={"attempts": retry_config.max_attempts, "final_error": str(last_exception)}
        )
        
        return self.fallback_agent.get_fallback_response(agent_name, last_exception)
    
    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay for retry attempt"""
        
        delay = config.base_delay * (config.exponential_base ** (attempt - 1))
        delay = min(delay, config.max_delay)
        
        if config.jitter:
            # Add jitter to prevent thundering herd
            jitter_amount = delay * 0.1 * random.random()
            delay += jitter_amount
        
        return delay
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify error type for retry logic"""
        
        error_message = str(error).lower()
        error_type_name = type(error).__name__.lower()
        
        if "timeout" in error_message or "timed out" in error_message:
            return ErrorType.TIMEOUT
        elif "network" in error_message or "connection" in error_message or "http" in error_message:
            return ErrorType.NETWORK_ERROR
        elif "validation" in error_message or "invalid" in error_message:
            return ErrorType.VALIDATION_ERROR
        elif "tool" in error_message or "function" in error_type_name:
            return ErrorType.TOOL_FAILURE
        elif "agent" in error_message or "processing" in error_message:
            return ErrorType.AGENT_FAILURE
        else:
            return ErrorType.UNKNOWN_ERROR
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        
        circuit_status = {}
        for name, breaker in self.circuit_breakers.items():
            circuit_status[name] = {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "success_count": breaker.success_count,
                "last_failure_time": breaker.last_failure_time
            }
        
        return {
            "circuit_breakers": circuit_status,
            "active_circuits": len(self.circuit_breakers),
            "open_circuits": len([b for b in self.circuit_breakers.values() if b.state == CircuitState.OPEN]),
            "half_open_circuits": len([b for b in self.circuit_breakers.values() if b.state == CircuitState.HALF_OPEN])
        }

# Global error resilience manager
error_resilience = ErrorResilienceManager()
