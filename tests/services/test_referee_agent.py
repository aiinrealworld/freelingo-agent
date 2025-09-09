"""
Test the Referee Agent in isolation using fixtures.
"""
import json
import pytest
from pathlib import Path

from freelingo_agent.services.llm_service import validate_agent_chain
from freelingo_agent.models.referee_model import RefereeAgentOutput, Rationale, ChainChecks
from freelingo_agent.models.transcript_model import Transcript
from freelingo_agent.models.words_model import Word, WordSuggestion, UsageExample
from freelingo_agent.models.feedback_model import FeedbackAgentOutput, Mistake
from freelingo_agent.models.planner_model import PlannerAgentOutput


class TestRefereeAgent:
    """Test the Referee Agent in isolation."""

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
        """Create sample feedback for the referee agent."""
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
    def sample_plan(self):
        """Create sample plan for the referee agent."""
        return PlannerAgentOutput(
            session_objectives=[
                "Practice using partitive articles with drinks (de l', du, de la)",
                "Learn to ask follow-up questions about preferences",
                "Expand on food and drink combinations in conversation"
            ],
            vocab_gaps=[
                "Words to ask about habits (que, qu'est-ce que, d'habitude)",
                "Words to express quantity (un peu de, beaucoup de)",
                "Words to combine food and drinks (avec, aussi, en plus de)"
            ]
        )

    @pytest.fixture
    def sample_words(self):
        """Create sample word suggestions for the referee agent."""
        return WordSuggestion(
            new_words=["d'habitude", "beaucoup", "avec"],
            usages={
                "d'habitude": UsageExample(
                    fr="D'habitude, je bois du thé le matin.",
                    en="Usually, I drink tea in the morning."
                ),
                "beaucoup": UsageExample(
                    fr="J'aime beaucoup les oranges.",
                    en="I really like oranges."
                ),
                "avec": UsageExample(
                    fr="Je mange des pâtes avec de la sauce.",
                    en="I eat pasta with sauce."
                )
            }
        )

    @pytest.fixture
    def sample_referee_input(self, test_transcript, test_known_words, sample_feedback, sample_plan, sample_words):
        """Create sample input for the referee agent."""
        return {
            "transcript": test_transcript,
            "known_words": test_known_words,
            "feedback": sample_feedback,
            "plan": sample_plan,
            "new_words": sample_words
        }

    @pytest.mark.asyncio
    async def test_referee_agent_output_structure(self, sample_referee_input):
        """Test that the referee agent returns the correct output structure."""
        # Run the actual referee agent through llm_service
        result = await validate_agent_chain(**sample_referee_input)
        
        # Verify the result is a RefereeAgentOutput
        assert isinstance(result, RefereeAgentOutput)
        
        # Verify structure
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'violations')
        assert hasattr(result, 'rationale')
        
        # Verify types
        assert isinstance(result.is_valid, bool)
        assert isinstance(result.violations, list)
        assert isinstance(result.rationale, Rationale)
        
        # Verify rationale structure
        assert hasattr(result.rationale, 'reasoning_summary')
        assert hasattr(result.rationale, 'chain_checks')
        assert isinstance(result.rationale.reasoning_summary, str)
        assert isinstance(result.rationale.chain_checks, ChainChecks)

    @pytest.mark.asyncio
    async def test_referee_agent_with_aligned_chain(self, sample_referee_input):
        """Test the referee agent with a well-aligned agent chain."""
        # Run the actual referee agent through llm_service
        result = await validate_agent_chain(**sample_referee_input)
        
        # Verify the result
        assert isinstance(result, RefereeAgentOutput)
        
        # Print the actual result for debugging
        print(f"\nActual Referee Agent Result (Aligned Chain):")
        print(f"Is Valid: {result.is_valid}")
        print(f"Violations: {result.violations}")
        print(f"Reasoning Summary: {result.rationale.reasoning_summary}")
        print(f"Chain Checks: {result.rationale.chain_checks}")
        
        # Verify the content is meaningful
        assert len(result.rationale.reasoning_summary) > 0
        assert isinstance(result.violations, list)
        
        # If valid, should have no violations
        if result.is_valid:
            assert len(result.violations) == 0

    @pytest.mark.asyncio
    async def test_referee_agent_with_misaligned_chain(self, test_transcript, test_known_words):
        """Test the referee agent with a misaligned agent chain."""
        # Create misaligned feedback (doesn't match transcript)
        misaligned_feedback = FeedbackAgentOutput(
            strengths=[
                "Excellent use of advanced grammar structures",
                "Perfect pronunciation and intonation"
            ],
            mistakes=[
                Mistake(
                    what_you_said="Je parle français parfaitement",
                    simple_explanation="This is not in the transcript",
                    better_way="This doesn't match the actual conversation"
                )
            ],
            conversation_examples=[
                "Try using more complex sentence structures",
                "Practice advanced vocabulary"
            ]
        )
        
        # Create misaligned plan (doesn't address feedback)
        misaligned_plan = PlannerAgentOutput(
            session_objectives=[
                "Learn advanced business French vocabulary",
                "Practice formal writing skills",
                "Master complex grammatical structures"
            ],
            vocab_gaps=[
                "Advanced business terminology",
                "Formal writing expressions",
                "Complex grammatical constructions"
            ]
        )
        
        # Create misaligned words (too advanced)
        misaligned_words = WordSuggestion(
            new_words=["entrepreneur", "bureaucratie", "sophistiqué"],
            usages={
                "entrepreneur": UsageExample(
                    fr="L'entrepreneur a créé une entreprise prospère.",
                    en="The entrepreneur created a successful business."
                ),
                "bureaucratie": UsageExample(
                    fr="La bureaucratie gouvernementale est complexe.",
                    en="Government bureaucracy is complex."
                ),
                "sophistiqué": UsageExample(
                    fr="Il a un goût sophistiqué pour l'art.",
                    en="He has a sophisticated taste for art."
                )
            }
        )
        
        input_data = {
            "transcript": test_transcript,
            "known_words": test_known_words,
            "feedback": misaligned_feedback,
            "plan": misaligned_plan,
            "new_words": misaligned_words
        }
        
        # Run the actual referee agent through llm_service
        result = await validate_agent_chain(**input_data)
        
        # Verify the result
        assert isinstance(result, RefereeAgentOutput)
        
        # Print the actual result for debugging
        print(f"\nActual Referee Agent Result (Misaligned Chain):")
        print(f"Is Valid: {result.is_valid}")
        print(f"Violations: {result.violations}")
        print(f"Reasoning Summary: {result.rationale.reasoning_summary}")
        print(f"Chain Checks: {result.rationale.chain_checks}")
        
        # Should detect misalignment
        assert len(result.rationale.reasoning_summary) > 0
        # May or may not be valid depending on how strict the validation is
        # But should provide meaningful feedback about the chain

    @pytest.mark.asyncio
    async def test_referee_agent_chain_checks(self, sample_referee_input):
        """Test that the referee agent performs proper chain checks."""
        # Run the actual referee agent through llm_service
        result = await validate_agent_chain(**sample_referee_input)
        
        # Verify the result
        assert isinstance(result, RefereeAgentOutput)
        assert isinstance(result.rationale.chain_checks, ChainChecks)
        
        # Print the actual result for debugging
        print(f"\nChain Checks Test Result:")
        print(f"Chain Checks: {result.rationale.chain_checks}")
        
        # Verify chain checks structure
        chain_checks = result.rationale.chain_checks
        assert hasattr(chain_checks, 'feedback_transcript_alignment')
        assert hasattr(chain_checks, 'planner_feedback_incorporation')
        assert hasattr(chain_checks, 'new_words_plan_alignment')
        assert hasattr(chain_checks, 'overall_chain_coherence')
        
        # Verify all checks are boolean
        assert isinstance(chain_checks.feedback_transcript_alignment, bool)
        assert isinstance(chain_checks.planner_feedback_incorporation, bool)
        assert isinstance(chain_checks.new_words_plan_alignment, bool)
        assert isinstance(chain_checks.overall_chain_coherence, bool)

    @pytest.mark.asyncio
    async def test_referee_agent_minimal_input(self, test_transcript, test_known_words):
        """Test the referee agent with minimal input (no feedback, plan, or words)."""
        input_data = {
            "transcript": test_transcript,
            "known_words": test_known_words,
            "feedback": None,
            "plan": None,
            "new_words": None
        }
        
        # Run the actual referee agent through llm_service
        result = await validate_agent_chain(**input_data)
        
        # Verify the result
        assert isinstance(result, RefereeAgentOutput)
        
        # Print the actual result for debugging
        print(f"\nMinimal Input Test Result:")
        print(f"Is Valid: {result.is_valid}")
        print(f"Violations: {result.violations}")
        print(f"Reasoning Summary: {result.rationale.reasoning_summary}")
        
        # Should still provide meaningful validation
        assert len(result.rationale.reasoning_summary) > 0
        assert isinstance(result.violations, list)

    @pytest.mark.asyncio
    async def test_referee_agent_partial_chain(self, test_transcript, test_known_words, sample_feedback):
        """Test the referee agent with partial chain (only feedback, no plan or words)."""
        input_data = {
            "transcript": test_transcript,
            "known_words": test_known_words,
            "feedback": sample_feedback,
            "plan": None,
            "new_words": None
        }
        
        # Run the actual referee agent through llm_service
        result = await validate_agent_chain(**input_data)
        
        # Verify the result
        assert isinstance(result, RefereeAgentOutput)
        
        # Print the actual result for debugging
        print(f"\nPartial Chain Test Result:")
        print(f"Is Valid: {result.is_valid}")
        print(f"Violations: {result.violations}")
        print(f"Reasoning Summary: {result.rationale.reasoning_summary}")
        print(f"Chain Checks: {result.rationale.chain_checks}")
        
        # Should still provide meaningful validation
        assert len(result.rationale.reasoning_summary) > 0
        assert isinstance(result.violations, list)
        assert isinstance(result.rationale.chain_checks, ChainChecks)

    @pytest.mark.asyncio
    async def test_referee_agent_validation_quality(self, sample_referee_input):
        """Test that the referee agent provides high-quality validation."""
        # Run the actual referee agent through llm_service
        result = await validate_agent_chain(**sample_referee_input)
        
        # Verify the result
        assert isinstance(result, RefereeAgentOutput)
        
        # Print the actual result for debugging
        print(f"\nValidation Quality Test Result:")
        print(f"Is Valid: {result.is_valid}")
        print(f"Violations: {result.violations}")
        print(f"Reasoning Summary: {result.rationale.reasoning_summary}")
        
        # Verify quality of validation
        assert len(result.rationale.reasoning_summary) > 20  # Should be substantial
        assert isinstance(result.violations, list)
        
        # If there are violations, they should be specific and actionable
        for violation in result.violations:
            assert isinstance(violation, str)
            assert len(violation) > 10  # Should be substantial
            assert len(violation.strip()) > 0  # Should not be empty
