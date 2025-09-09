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
        transcript_path = Path(__file__).parent.parent.parent / "test_transcript_10_turns.json"
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
        known_words_path = Path(__file__).parent.parent.parent / "test_known_words.json"
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
    async def test_complete_workflow_with_transcript(self, graph_workflow_service, test_transcript, test_user_session):
        """Test the complete workflow processing a real transcript."""
        
        # Initialize graph state with proper structure
        initial_state = GraphState(
            user_id="test_user_001",
            user_session=test_user_session,
            transcript=test_transcript,
            current_agent="FEEDBACK"
        )
        
        # Process the transcript through the workflow
        final_state = await graph_workflow_service.run_workflow(initial_state)
        
        # Verify the workflow completed successfully
        assert final_state is not None
        assert final_state.user_id == "test_user_001"
        assert final_state.user_session.session_id == "test_session_001"
        
        # Verify that the transcript was processed
        assert final_state.transcript is not None
        assert len(final_state.transcript.transcript) == len(test_transcript.transcript)
    
    @pytest.mark.asyncio
    async def test_workflow_state_transitions(self, graph_workflow_service, test_transcript, test_user_session):
        """Test that the workflow properly manages state transitions."""
        
        initial_state = GraphState(
            user_id="test_user_001",
            user_session=test_user_session,
            transcript=test_transcript,
            current_agent="FEEDBACK"
        )
        
        # Run the workflow
        final_state = await graph_workflow_service.run_workflow(initial_state)
        
        # Verify state transitions
        assert final_state is not None
        assert final_state.user_id == "test_user_001"
        assert final_state.transcript is not None
        
        # Verify that agents were called (check for agent outputs)
        assert final_state.last_feedback is not None or final_state.last_plan is not None
    
    @pytest.mark.asyncio
    async def test_agent_interactions(self, graph_workflow_service, test_transcript, test_user_session):
        """Test that all agents are properly called during workflow execution."""
        
        initial_state = GraphState(
            user_id="test_user_001",
            user_session=test_user_session,
            transcript=test_transcript,
            current_agent="FEEDBACK"
        )
        
        # Run the workflow
        final_state = await graph_workflow_service.run_workflow(initial_state)
        
        # Verify that the workflow completed successfully
        assert final_state is not None
        
        # Verify that agents produced outputs (indicating they were called)
        # At least one agent should have produced output
        agent_outputs = [
            final_state.last_feedback,
            final_state.last_plan,
            final_state.last_words,
            final_state.last_referee_decision
        ]
        assert any(output is not None for output in agent_outputs)
    
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
    
    @pytest.mark.asyncio
    async def test_transcript_validation(self, graph_workflow_service, test_user_session):
        """Test that the transcript is properly validated."""
        
        # Test with invalid transcript
        invalid_transcript = Transcript(transcript=[])
        
        initial_state = GraphState(
            user_id="test_user_001",
            user_session=test_user_session,
            transcript=invalid_transcript,
            current_agent="FEEDBACK"
        )
        
        # Should handle empty transcript gracefully
        result = await graph_workflow_service.run_workflow(initial_state)
        
        assert result is not None
        assert result.user_id == "test_user_001"
        assert result.transcript is not None
        assert len(result.transcript.transcript) == 0
    
    @pytest.mark.asyncio
    async def test_real_agent_calls_with_logging(self, graph_workflow_service, test_transcript, test_user_session):
        """Test the workflow with real agent calls and detailed logging."""
        import logging
        
        # Set up logging to see what's happening
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
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
            final_state = await graph_workflow_service.run_workflow(initial_state)
            
            logger.info(f"Workflow completed successfully!")
            logger.info(f"Final state: {final_state}")
            logger.info(f"Agent outputs:")
            logger.info(f"  - Feedback: {final_state.last_feedback}")
            logger.info(f"  - Plan: {final_state.last_plan}")
            logger.info(f"  - Words: {final_state.last_words}")
            logger.info(f"  - Referee: {final_state.last_referee_decision}")
            
            # Verify the workflow completed successfully
            assert final_state is not None
            assert final_state.user_id == "test_user_001"
            assert final_state.transcript is not None
            
            # Log the conversation history to see what was generated
            if final_state.transcript:
                logger.info(f"Transcript processed: {len(final_state.transcript.transcript)} turns")
            
        except Exception as e:
            logger.error(f"Workflow failed with error: {e}")
            raise
