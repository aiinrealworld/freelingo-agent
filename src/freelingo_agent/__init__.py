"""
FreeLingo Agent - AI-powered language learning agent with LangGraph workflow
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main components for easy access
from .models.graph_state import GraphState
from .services.graph_workflow_service import GraphWorkflowService

__all__ = ["GraphState", "GraphWorkflowService"]
