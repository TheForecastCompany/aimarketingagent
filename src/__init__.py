"""
Agentic Workflow System - Root package
"""

from .main import AgenticWorkflowSystem, VideoContentRepurposer, create_agentic_system, create_legacy_repurposer

__version__ = "1.0.0"
__all__ = [
    "AgenticWorkflowSystem",
    "VideoContentRepurposer", 
    "create_agentic_system",
    "create_legacy_repurposer"
]
