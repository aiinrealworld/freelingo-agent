"""
Test the Planner Agent in isolation using fixtures.
"""
import json
import pytest
from pathlib import Path

from freelingo_agent.services.llm_service import get_plan
from freelingo_agent.models.planner_model import PlannerAgentOutput
from freelingo_agent.models.transcript_model import Transcript
from freelingo_agent.models.words_model import Word
from freelingo_agent.models.feedback_model import FeedbackAgentOutput, Mistake


class TestPlannerAgent:
    """Test the Planner Agent in isolation."""

    @pytest.fixture
    def test_transcript(self):
        """Load the test transcript from fixtures."""
        transcript_path = Path(__file__).parent.parent / "fixtures" / "transcript_10_turns.json"
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)
        return Transcript(**transcript_data)

    @pytest.fixture
    def test_known_words(self):
        """Load the test known words from fixtures."""
        known_words_path = Path(__file__).parent.parent / "fixtures" / "known_words.json"
        with open(known_words_path, 'r', encoding='utf-8') as f:
            known_words_data = json.load(f)
        return [Word(**word_data) for word_data in known_words_data["known_words"]]

    @pytest.fixture
    def sample_feedback(self):
        """Create sample feedback for the planner agent."""
        return FeedbackAgentOutput(
            strengths=[
                "Great use of greetings to start the conversation",
                "Responded well with basic vocabulary",
                "Used food vocabulary effectively"
            ],
            mistakes=[
                Mistake(
                    what_you_said="Je bois de l'eau",
                    simple_explanation="Missing partitive article for drinks",
                    better_way="je bois de l'eau (I drink some water)"
                )
            ],
            conversation_examples=[
                "You could say: 'Je bois de l'eau avec une pomme' (I drink water with an apple)",
                "Try asking: 'Que buvez-vous d'habitude ?' (What do you usually drink ?)"
            ]
        )

    @pytest.fixture
    def sample_planner_input(self, test_known_words, sample_feedback):
        """Create sample input for the planner agent."""
        return {
            "known_words": test_known_words,
            "feedback": sample_feedback,
            "new_words": None,  # Optional parameter
            "referee_feedback": None  # Optional parameter
        }

    @pytest.mark.asyncio
    async def test_planner_agent_output_structure(self, sample_planner_input):
        """Test that the planner agent returns the correct output structure."""
        # Run the actual planner agent through llm_service
        result = await get_plan(**sample_planner_input)
        
        # Verify the result is a PlannerAgentOutput
        assert isinstance(result, PlannerAgentOutput)
        
        # Verify structure
        assert hasattr(result, 'session_objectives')
        assert hasattr(result, 'vocab_gaps')
        
        # Verify types
        assert isinstance(result.session_objectives, list)
        assert isinstance(result.vocab_gaps, list)
        
        # Verify content
        assert len(result.session_objectives) > 0
        assert len(result.vocab_gaps) > 0
        
        # Verify content types
        assert all(isinstance(obj, str) for obj in result.session_objectives)
        assert all(isinstance(gap, str) for gap in result.vocab_gaps)

    @pytest.mark.asyncio
    async def test_planner_agent_with_real_feedback(self, test_known_words, sample_feedback):
        """Test the planner agent with real feedback data."""
        # Create input
        input_data = {
            "known_words": test_known_words,
            "feedback": sample_feedback,
            "new_words": None,
            "referee_feedback": None
        }
        
        # Run the actual planner agent through llm_service
        result = await get_plan(**input_data)
        
        # Verify the result
        assert isinstance(result, PlannerAgentOutput)
        assert len(result.session_objectives) > 0
        assert len(result.vocab_gaps) > 0
        
        # Print the actual result for debugging
        print(f"\nActual Planner Agent Result:")
        print(f"Session Objectives: {result.session_objectives}")
        print(f"Vocab Gaps: {result.vocab_gaps}")
        
        # Verify the content is meaningful
        assert all(isinstance(obj, str) and len(obj) > 0 for obj in result.session_objectives)
        assert all(isinstance(gap, str) and len(gap) > 0 for gap in result.vocab_gaps)
        
        # Verify the objectives are substantial and meaningful
        for objective in result.session_objectives:
            assert len(objective) > 10  # Should be substantial
            assert len(objective.strip()) > 0  # Should not be empty
        
        # Verify vocab gaps are substantial and meaningful
        for gap in result.vocab_gaps:
            assert len(gap) > 10  # Should be substantial
            assert len(gap.strip()) > 0  # Should not be empty

    @pytest.mark.asyncio
    async def test_planner_agent_no_feedback_scenario(self, test_known_words):
        """Test the planner agent when there's no feedback (new user scenario)."""
        # Create input without feedback
        input_data = {
            "known_words": test_known_words,
            "feedback": None,
            "new_words": None,
            "referee_feedback": None
        }
        
        # Run the actual planner agent through llm_service
        result = await get_plan(**input_data)
        
        # Verify the result
        assert isinstance(result, PlannerAgentOutput)
        assert len(result.session_objectives) > 0
        assert len(result.vocab_gaps) > 0
        
        # Print the actual result for debugging
        print(f"\nNo Feedback Scenario Result:")
        print(f"Session Objectives: {result.session_objectives}")
        print(f"Vocab Gaps: {result.vocab_gaps}")
        
        # Verify the content is meaningful
        assert all(isinstance(obj, str) and len(obj) > 0 for obj in result.session_objectives)
        assert all(isinstance(gap, str) and len(gap) > 0 for gap in result.vocab_gaps)

    @pytest.mark.asyncio
    async def test_planner_agent_field_limits(self, sample_planner_input):
        """Test that the planner agent respects field limits."""
        # Run the actual planner agent through llm_service
        result = await get_plan(**sample_planner_input)
        
        # Verify the result respects limits (Pydantic should enforce this)
        assert isinstance(result, PlannerAgentOutput)
        assert len(result.session_objectives) <= 3
        assert len(result.vocab_gaps) <= 3
        
        # Print the actual result for debugging
        print(f"\nField Limits Test Result:")
        print(f"Session Objectives count: {len(result.session_objectives)} (max 3)")
        print(f"Vocab Gaps count: {len(result.vocab_gaps)} (max 3)")

    @pytest.mark.asyncio
    async def test_planner_agent_feedback_integration(self, test_known_words):
        """Test that the planner agent properly integrates feedback into planning."""
        # Create feedback with specific mistakes
        specific_feedback = FeedbackAgentOutput(
            strengths=[
                "Good basic conversation flow"
            ],
            mistakes=[
                Mistake(
                    what_you_said="je mange pomme",
                    simple_explanation="Missing article before noun",
                    better_way="je mange une pomme (I eat an apple)"
                ),
                Mistake(
                    what_you_said="je bois café",
                    simple_explanation="Need partitive article for drinks",
                    better_way="je bois du café (I drink some coffee)"
                )
            ],
            conversation_examples=[
                "Try: 'Je mange une pomme et je bois du café' (I eat an apple and drink some coffee)",
                "Ask back: 'Et vous, que mangez-vous ?' (And you, what do you eat?)"
            ]
        )
        
        input_data = {
            "known_words": test_known_words,
            "feedback": specific_feedback,
            "new_words": None,
            "referee_feedback": None
        }
        
        # Run the actual planner agent through llm_service
        result = await get_plan(**input_data)
        
        # Verify the result
        assert isinstance(result, PlannerAgentOutput)
        assert len(result.session_objectives) > 0
        assert len(result.vocab_gaps) > 0
        
        # Print the actual result for debugging
        print(f"\nFeedback Integration Test Result:")
        print(f"Session Objectives: {result.session_objectives}")
        print(f"Vocab Gaps: {result.vocab_gaps}")
        
        # Verify that the planner addresses the feedback issues
        objectives_text = " ".join(result.session_objectives).lower()
        gaps_text = " ".join(result.vocab_gaps).lower()
        
        # Should mention articles (from the mistakes)
        assert "article" in objectives_text or "article" in gaps_text
        
        # Should mention food/drink vocabulary (from the context)
        food_drink_words = ["food", "drink", "eat", "mange", "bois", "nourriture", "boisson"]
        assert any(word in objectives_text or word in gaps_text for word in food_drink_words)

    @pytest.mark.asyncio
    async def test_planner_agent_conversation_focus(self, test_known_words, sample_feedback):
        """Test that the planner agent focuses on conversation-building vocabulary."""
        input_data = {
            "known_words": test_known_words,
            "feedback": sample_feedback,
            "new_words": None,
            "referee_feedback": None
        }
        
        # Run the actual planner agent through llm_service
        result = await get_plan(**input_data)
        
        # Verify the result
        assert isinstance(result, PlannerAgentOutput)
        
        # Print the actual result for debugging
        print(f"\nConversation Focus Test Result:")
        print(f"Session Objectives: {result.session_objectives}")
        print(f"Vocab Gaps: {result.vocab_gaps}")
        
        # Verify conversation-building focus (more flexible)
        all_text = " ".join(result.session_objectives + result.vocab_gaps).lower()
        
        # Should mention conversation-related terms or vocabulary building
        conversation_words = ["conversation", "dialogue", "talk", "speak", "ask", "question", "response", "extend", "continue", "vocabulary", "words", "learn", "practice"]
        assert any(word in all_text for word in conversation_words)
