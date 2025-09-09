"""
Test the Feedback Agent in isolation using fixtures.
"""
import json
import pytest
from pathlib import Path

from freelingo_agent.services.llm_service import get_feedback
from freelingo_agent.models.feedback_model import FeedbackAgentOutput, Mistake
from freelingo_agent.models.transcript_model import Transcript
from freelingo_agent.models.words_model import Word


class TestFeedbackAgent:
    """Test the Feedback Agent in isolation."""

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
    def sample_feedback_input(self, test_transcript, test_known_words):
        """Create sample input for the feedback agent."""
        return {
            "transcript": test_transcript,
            "known_words": test_known_words,
            "new_words": None,  # Optional parameter
            "referee_feedback": None  # Optional parameter
        }

    @pytest.mark.asyncio
    async def test_feedback_agent_output_structure(self, sample_feedback_input):
        """Test that the feedback agent returns the correct output structure."""
        # Run the actual feedback agent through llm_service
        result = await get_feedback(**sample_feedback_input)
        
        # Verify the result is a FeedbackAgentOutput
        assert isinstance(result, FeedbackAgentOutput)
        
        # Verify structure
        assert hasattr(result, 'strengths')
        assert hasattr(result, 'mistakes')
        assert hasattr(result, 'conversation_examples')
        
        # Verify types
        assert isinstance(result.strengths, list)
        assert isinstance(result.mistakes, list)
        assert isinstance(result.conversation_examples, list)
        
        # Verify content
        assert len(result.strengths) > 0
        assert len(result.conversation_examples) > 0
        
        # Verify mistake structure (if any mistakes found)
        for mistake in result.mistakes:
            assert isinstance(mistake, Mistake)
            assert hasattr(mistake, 'what_you_said')
            assert hasattr(mistake, 'simple_explanation')
            assert hasattr(mistake, 'better_way')
            assert isinstance(mistake.what_you_said, str)
            assert isinstance(mistake.simple_explanation, str)
            assert isinstance(mistake.better_way, str)

    @pytest.mark.asyncio
    async def test_feedback_agent_with_real_transcript(self, test_transcript, test_known_words):
        """Test the feedback agent with real transcript data."""
        # Create input
        input_data = {
            "transcript": test_transcript,
            "known_words": test_known_words,
            "new_words": None,
            "referee_feedback": None
        }
        
        # Run the actual feedback agent through llm_service
        result = await get_feedback(**input_data)
        
        # Verify the result
        assert isinstance(result, FeedbackAgentOutput)
        assert len(result.strengths) > 0
        assert len(result.conversation_examples) > 0
        
        # Print the actual result for debugging
        print(f"\nActual Feedback Agent Result:")
        print(f"Strengths: {result.strengths}")
        print(f"Mistakes: {[{'what_you_said': m.what_you_said, 'simple_explanation': m.simple_explanation, 'better_way': m.better_way} for m in result.mistakes]}")
        print(f"Conversation Examples: {result.conversation_examples}")
        
        # Verify the content is meaningful
        assert all(isinstance(strength, str) and len(strength) > 0 for strength in result.strengths)
        assert all(isinstance(example, str) and len(example) > 0 for example in result.conversation_examples)
        
        # If mistakes are found, verify they're relevant
        if result.mistakes:
            for mistake in result.mistakes:
                assert len(mistake.what_you_said) > 0
                assert len(mistake.simple_explanation) > 0
                assert len(mistake.better_way) > 0

    @pytest.mark.asyncio
    async def test_feedback_agent_no_mistakes_scenario(self, test_known_words):
        """Test the feedback agent when there are no mistakes."""
        # Create a perfect transcript using the Transcript model
        from freelingo_agent.models.dialogue_model import Rationale, AiReply
        from freelingo_agent.models.transcript_model import TranscriptTurn, AiTurn, UserTurn
        
        perfect_transcript = Transcript(
            transcript=[
                TranscriptTurn(
                    ai_turn=AiTurn(
                        rationale=Rationale(
                            reasoning_summary="Perfect greeting",
                            vocabulary_challenge={"description": "Basic greeting", "tags": ["short_vocab"]},
                            rule_checks={"used_only_allowed_vocabulary": True, "one_sentence": True, "max_eight_words": True, "no_corrections_or_translations": True}
                        ),
                        ai_reply=AiReply(text="Bonjour ! Comment allez-vous ?", word_count=4)
                    ),
                    user_turn=UserTurn(text="Bonjour")
                ),
                TranscriptTurn(
                    ai_turn=AiTurn(
                        rationale=Rationale(
                            reasoning_summary="Perfect response",
                            vocabulary_challenge={"description": "Basic response", "tags": ["short_vocab"]},
                            rule_checks={"used_only_allowed_vocabulary": True, "one_sentence": True, "max_eight_words": True, "no_corrections_or_translations": True}
                        ),
                        ai_reply=AiReply(text="Très bien, merci ! Et vous ?", word_count=5)
                    ),
                    user_turn=UserTurn(text="Très bien, merci ! Et vous ?")
                )
            ]
        )
        
        input_data = {
            "transcript": perfect_transcript,
            "known_words": test_known_words,
            "new_words": None,
            "referee_feedback": None
        }
        
        # Run the actual feedback agent through llm_service
        result = await get_feedback(**input_data)
        
        # Verify the result
        assert isinstance(result, FeedbackAgentOutput)
        assert len(result.strengths) > 0
        assert len(result.conversation_examples) > 0
        
        # Print the actual result for debugging
        print(f"\nPerfect Transcript Feedback Result:")
        print(f"Strengths: {result.strengths}")
        print(f"Mistakes: {len(result.mistakes)} found")
        print(f"Conversation Examples: {result.conversation_examples}")
        
        # Verify the content is meaningful
        assert all(isinstance(strength, str) and len(strength) > 0 for strength in result.strengths)
        assert all(isinstance(example, str) and len(example) > 0 for example in result.conversation_examples)

    @pytest.mark.asyncio
    async def test_feedback_agent_field_limits(self, sample_feedback_input):
        """Test that the feedback agent respects field limits."""
        # Run the actual feedback agent through llm_service
        result = await get_feedback(**sample_feedback_input)
        
        # Verify the result respects limits (Pydantic should enforce this)
        assert isinstance(result, FeedbackAgentOutput)
        assert len(result.strengths) <= 3
        assert len(result.mistakes) <= 3
        assert len(result.conversation_examples) <= 2
        
        # Print the actual result for debugging
        print(f"\nField Limits Test Result:")
        print(f"Strengths count: {len(result.strengths)} (max 3)")
        print(f"Mistakes count: {len(result.mistakes)} (max 3)")
        print(f"Conversation Examples count: {len(result.conversation_examples)} (max 2)")

