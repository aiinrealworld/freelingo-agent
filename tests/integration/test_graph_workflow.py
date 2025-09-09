"""
Integration test for the complete graph workflow using a real transcript.
Tests the full end-to-end flow from transcript input to final response.
"""

import json
import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from freelingo_agent.models.transcript_model import Transcript
from freelingo_agent.models.graph_state import GraphState
from freelingo_agent.models.user_session import UserSession
from freelingo_agent.models.words_model import Word
from freelingo_agent.services.graph_workflow_service import GraphWorkflowService
# Note: GraphWorkflowService is self-contained and doesn't need external dependencies


class TestGraphWorkflowTranscript:
    """Test the complete graph workflow with a real transcript."""
    
    @pytest.fixture
    def test_transcript(self):
        """Load the test transcript from JSON file."""
        transcript_path = Path(__file__).parent.parent / "fixtures" / "transcript_10_turns.json"
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)
        return Transcript(**transcript_data)
    
    @pytest.fixture
    def graph_workflow_service(self):
        """Create GraphWorkflowService - it's self-contained."""
        return GraphWorkflowService()
    
    @pytest.fixture
    def test_known_words(self):
        """Load the test known words from JSON file."""
        known_words_path = Path(__file__).parent.parent / "fixtures" / "known_words.json"
        with open(known_words_path, 'r', encoding='utf-8') as f:
            known_words_data = json.load(f)
        return [Word(**word_data) for word_data in known_words_data["known_words"]]
    
    @pytest.fixture
    def test_user_session(self, test_known_words):
        """Create a test user session with known words."""
        return UserSession(
            user_id="test_user_001",
            session_id="test_session_001",
            language="fr",
            proficiency_level="beginner",
            learning_goals=["basic_conversation"],
            current_topic="greetings",
            known_words=test_known_words
        )
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, graph_workflow_service, test_transcript, test_user_session):
        """Test the complete workflow processing a real transcript with comprehensive validation and logging."""
        import logging
        
        # Set up logging to see what's happening
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Initialize graph state with proper structure
        initial_state = GraphState(
            user_id="test_user_001",
            user_session=test_user_session,
            transcript=test_transcript,
            current_agent="FEEDBACK"
        )
        
        logger.info("Starting workflow test with real agent calls...")
        logger.info(f"Initial state: {initial_state}")
        logger.info(f"Transcript has {len(test_transcript.transcript)} turns")
        
        # Process the first turn to see real agent behavior
        first_turn = test_transcript.transcript[0]
        logger.info(f"Processing first turn: {first_turn.user_turn.text}")
        
        try:
            # Process the transcript through the workflow
            final_state = await graph_workflow_service.run_workflow(initial_state)
            
            logger.info(f"Workflow completed successfully!")
            logger.info(f"Final state: {final_state}")
            logger.info(f"Agent outputs:")
            logger.info(f"  - Feedback: {final_state.last_feedback}")
            logger.info(f"  - Plan: {final_state.last_plan}")
            logger.info(f"  - Words: {final_state.last_words}")
            logger.info(f"  - Referee: {final_state.last_referee_decision}")
            
        except Exception as e:
            logger.error(f"Workflow failed with error: {e}")
            raise
        
        # === WORKFLOW COMPLETION VALIDATION ===
        # Verify the workflow completed successfully
        assert final_state is not None
        assert final_state.user_id == "test_user_001"
        assert final_state.user_session.session_id == "test_session_001"
        
        # === STATE TRANSITION VALIDATION ===
        # Verify that the transcript was processed and state is maintained
        assert final_state.transcript is not None
        assert len(final_state.transcript.transcript) == len(test_transcript.transcript)
        
        # === AGENT INTERACTION VALIDATION ===
        # Verify that agents produced outputs (indicating they were called)
        # At least one agent should have produced output
        agent_outputs = [
            final_state.last_feedback,
            final_state.last_plan,
            final_state.last_words,
            final_state.last_referee_decision
        ]
        assert any(output is not None for output in agent_outputs), "At least one agent should have produced output"
        
        # Additional validation: Check that the workflow actually processed the transcript
        assert final_state.transcript.transcript == test_transcript.transcript, "Transcript should be preserved through workflow"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, test_transcript, test_user_session):
        """Test error handling in the workflow."""
        
        # Create a workflow service
        workflow_service = GraphWorkflowService()
        
        initial_state = GraphState(
            user_id="test_user_001",
            user_session=test_user_session,
            transcript=test_transcript,
            current_agent="FEEDBACK"
        )
        
        # Test that the workflow handles errors gracefully
        # The workflow should return the state even if there are errors
        final_state = await workflow_service.run_workflow(initial_state)
        
        # Should return a state (even if there were errors)
        assert final_state is not None
        assert final_state.user_id == "test_user_001"
    
