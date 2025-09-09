"""
Test the Words Agent in isolation using fixtures.
"""
import json
import pytest
from pathlib import Path

from freelingo_agent.services.llm_service import suggest_new_words
from freelingo_agent.models.words_model import WordSuggestion, Word, UsageExample
from freelingo_agent.models.transcript_model import Transcript
from freelingo_agent.models.feedback_model import FeedbackAgentOutput, Mistake
from freelingo_agent.models.planner_model import PlannerAgentOutput


class TestWordsAgent:
    """Test the Words Agent in isolation."""

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
        """Create sample feedback for the words agent."""
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
        """Create sample plan for the words agent."""
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
    def sample_words_input(self, test_known_words, sample_plan, sample_feedback):
        """Create sample input for the words agent."""
        return {
            "known_words": test_known_words,
            "plan": sample_plan,
            "feedback": sample_feedback,
            "referee_feedback": None  # Optional parameter
        }

    @pytest.mark.asyncio
    async def test_words_agent_output_structure(self, sample_words_input):
        """Test that the words agent returns the correct output structure."""
        # Run the actual words agent through llm_service
        result = await suggest_new_words(**sample_words_input)
        
        # Verify the result is a WordSuggestion
        assert isinstance(result, WordSuggestion)
        
        # Verify structure
        assert hasattr(result, 'new_words')
        assert hasattr(result, 'usages')
        
        # Verify types
        assert isinstance(result.new_words, list)
        assert isinstance(result.usages, dict)
        
        # Verify content
        assert len(result.new_words) > 0
        assert len(result.usages) > 0
        
        # Verify content types
        assert all(isinstance(word, str) for word in result.new_words)
        assert all(isinstance(usage, UsageExample) for usage in result.usages.values())

    @pytest.mark.asyncio
    async def test_words_agent_with_real_plan(self, test_known_words, sample_plan, sample_feedback):
        """Test the words agent with real plan and feedback data."""
        # Create input
        input_data = {
            "known_words": test_known_words,
            "plan": sample_plan,
            "feedback": sample_feedback,
            "referee_feedback": None
        }
        
        # Run the actual words agent through llm_service
        result = await suggest_new_words(**input_data)
        
        # Verify the result
        assert isinstance(result, WordSuggestion)
        assert len(result.new_words) > 0
        assert len(result.usages) > 0
        
        # Print the actual result for debugging
        print(f"\nActual Words Agent Result:")
        print(f"New Words: {result.new_words}")
        print(f"Usages: {[(word, usage.fr, usage.en) for word, usage in result.usages.items()]}")
        
        # Verify the content is meaningful
        assert all(isinstance(word, str) and len(word) > 0 for word in result.new_words)
        assert all(isinstance(usage, UsageExample) for usage in result.usages.values())
        
        # Verify each word has a usage example
        for word in result.new_words:
            assert word in result.usages
            usage = result.usages[word]
            assert isinstance(usage.fr, str) and len(usage.fr) > 0
            assert isinstance(usage.en, str) and len(usage.en) > 0

    @pytest.mark.asyncio
    async def test_words_agent_no_plan_scenario(self, test_known_words):
        """Test the words agent when there's no plan (basic scenario)."""
        # Create input without plan
        input_data = {
            "known_words": test_known_words,
            "plan": None,
            "feedback": None,
            "referee_feedback": None
        }
        
        # Run the actual words agent through llm_service
        result = await suggest_new_words(**input_data)
        
        # Verify the result
        assert isinstance(result, WordSuggestion)
        assert len(result.new_words) > 0
        assert len(result.usages) > 0
        
        # Print the actual result for debugging
        print(f"\nNo Plan Scenario Result:")
        print(f"New Words: {result.new_words}")
        print(f"Usages: {[(word, usage.fr, usage.en) for word, usage in result.usages.items()]}")
        
        # Verify the content is meaningful
        assert all(isinstance(word, str) and len(word) > 0 for word in result.new_words)
        assert all(isinstance(usage, UsageExample) for usage in result.usages.values())

    @pytest.mark.asyncio
    async def test_words_agent_field_limits(self, sample_words_input):
        """Test that the words agent respects field limits."""
        # Run the actual words agent through llm_service
        result = await suggest_new_words(**sample_words_input)
        
        # Verify the result respects limits (Pydantic should enforce this)
        assert isinstance(result, WordSuggestion)
        assert len(result.new_words) <= 8  # Max 8 words as per prompt
        
        # Print the actual result for debugging
        print(f"\nField Limits Test Result:")
        print(f"New Words count: {len(result.new_words)} (max 8)")
        print(f"Usages count: {len(result.usages)} (should match new_words)")

    @pytest.mark.asyncio
    async def test_words_agent_plan_integration(self, test_known_words):
        """Test that the words agent properly integrates plan into word suggestions."""
        # Create a specific plan focused on articles and questions
        specific_plan = PlannerAgentOutput(
            session_objectives=[
                "Master partitive articles with food and drinks",
                "Learn to ask questions about preferences",
                "Practice combining food and drink vocabulary"
            ],
            vocab_gaps=[
                "Partitive articles (du, de la, de l')",
                "Question words (que, qu'est-ce que, comment)",
                "Food and drink combinations (avec, aussi, et)"
            ]
        )
        
        input_data = {
            "known_words": test_known_words,
            "plan": specific_plan,
            "feedback": None,
            "referee_feedback": None
        }
        
        # Run the actual words agent through llm_service
        result = await suggest_new_words(**input_data)
        
        # Verify the result
        assert isinstance(result, WordSuggestion)
        assert len(result.new_words) > 0
        assert len(result.usages) > 0
        
        # Print the actual result for debugging
        print(f"\nPlan Integration Test Result:")
        print(f"New Words: {result.new_words}")
        print(f"Usages: {[(word, usage.fr, usage.en) for word, usage in result.usages.items()]}")
        
        # Verify that the words align with the plan
        all_words_text = " ".join(result.new_words).lower()
        all_usages_text = " ".join([usage.fr.lower() + " " + usage.en.lower() for usage in result.usages.values()])
        combined_text = all_words_text + " " + all_usages_text
        
        # Should mention articles, questions, or food/drink related terms
        plan_related_terms = ["du", "de", "que", "qu'est-ce", "comment", "avec", "aussi", "et", "article", "question", "food", "drink", "mange", "bois"]
        assert any(term in combined_text for term in plan_related_terms)

    @pytest.mark.asyncio
    async def test_words_agent_conversation_focus(self, test_known_words, sample_plan):
        """Test that the words agent focuses on conversation-enabling vocabulary."""
        input_data = {
            "known_words": test_known_words,
            "plan": sample_plan,
            "feedback": None,
            "referee_feedback": None
        }
        
        # Run the actual words agent through llm_service
        result = await suggest_new_words(**input_data)
        
        # Verify the result
        assert isinstance(result, WordSuggestion)
        
        # Print the actual result for debugging
        print(f"\nConversation Focus Test Result:")
        print(f"New Words: {result.new_words}")
        print(f"Usages: {[(word, usage.fr, usage.en) for word, usage in result.usages.items()]}")
        
        # Verify conversation-enabling focus
        all_usages_text = " ".join([usage.fr.lower() + " " + usage.en.lower() for usage in result.usages.values()])
        
        # Should mention conversation-related terms or vocabulary that enables dialogue
        # Updated to include more flexible conversation patterns
        conversation_words = [
            "conversation", "dialogue", "talk", "speak", "ask", "question", "response", 
            "et vous", "qu'est-ce que", "comment", "pourquoi", "où", "quand",
            "d'habitude", "souvent", "parfois", "toujours", "beaucoup", "en plus",
            "préférer", "aimer", "boire", "manger", "avec", "et", "ou"
        ]
        assert any(word in all_usages_text for word in conversation_words), f"No conversation-enabling words found in: {all_usages_text}"

    @pytest.mark.asyncio
    async def test_words_agent_level_appropriateness(self, test_known_words, sample_plan):
        """Test that the words agent suggests level-appropriate vocabulary."""
        input_data = {
            "known_words": test_known_words,
            "plan": sample_plan,
            "feedback": None,
            "referee_feedback": None
        }
        
        # Run the actual words agent through llm_service
        result = await suggest_new_words(**input_data)
        
        # Verify the result
        assert isinstance(result, WordSuggestion)
        
        # Print the actual result for debugging
        print(f"\nLevel Appropriateness Test Result:")
        print(f"New Words: {result.new_words}")
        print(f"Usages: {[(word, usage.fr, usage.en) for word, usage in result.usages.items()]}")
        
        # Verify that suggested words are not too complex
        for word in result.new_words:
            # Should not be overly complex (basic heuristic)
            assert len(word) <= 15  # Not extremely long
            # Should be basic French characters (allow spaces for phrases like "un peu")
            assert all(c.isalpha() or c in "'- " for c in word)  # Should be basic French characters
        
        # Verify that usage examples are simple and clear
        for usage in result.usages.values():
            assert len(usage.fr) <= 100  # Not overly complex sentences
            assert len(usage.en) <= 100  # Not overly complex translations
            assert len(usage.fr.split()) <= 10  # Not overly long sentences
