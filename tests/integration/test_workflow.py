import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
import asyncio

from freelingo_agent.services.graph_workflow_service import GraphWorkflowService
from freelingo_agent.models.graph_state import GraphState
from freelingo_agent.models.user_session import UserSession


@pytest.mark.asyncio
async def test_workflow_service_end_session_runs_agents():
    service = GraphWorkflowService()

    user_id = "test_user_workflow"
    # Create state directly (as the API does)
    initial_state = GraphState(
        user_id=user_id,
        user_session=UserSession(user_id=user_id)
    )

    # Simulate end of session, which should trigger the feedback -> planner -> words -> referee chain
    final_state = await service.trigger_feedback_loop(initial_state)

    assert final_state.last_feedback is not None
    assert final_state.last_plan is not None
    assert final_state.last_words is not None
    assert final_state.last_referee_decision is not None
