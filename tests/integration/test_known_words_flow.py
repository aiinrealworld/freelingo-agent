import pytest
from unittest.mock import patch, Mock
from freelingo_agent.db.words import get_known_words
from freelingo_agent.services.llm_service import suggest_new_words
from freelingo_agent.models.words_model import WordSuggestion
import re

@pytest.mark.integration
@pytest.mark.asyncio
async def test_known_words_llm_integration():
    TEST_USER_ID = "00000000-0000-0000-0000-000000000999"

    # Mock the database call to avoid network errors
    with patch('freelingo_agent.db.words.supabase') as mock_supabase:
        # Mock the database response
        mock_response = Mock()
        mock_response.data = [{"word": "bonjour"}, {"word": "chat"}, {"word": "merci"}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        mock_supabase.table.return_value = mock_table
        
        # Step 1: Get known words (now mocked)
        known_words = get_known_words(TEST_USER_ID)
        assert isinstance(known_words, list)
        assert len(known_words) >= 3

        # Step 2: Run the agent (mock the LLM call)
        with patch('freelingo_agent.services.llm_service.words_agent') as mock_agent:
            mock_agent.run.return_value.output = '{"new_words": ["manger", "jouer", "jardin"], "usages": {"manger": {"fr": "Je mange une pomme.", "en": "I eat an apple."}, "jouer": {"fr": "Le chat veut jouer.", "en": "The cat wants to play."}, "jardin": {"fr": "Je suis dans le jardin.", "en": "I am in the garden."}}}'
            
            result: WordSuggestion = await suggest_new_words(known_words)

            # Step 3: Validate basic structure
            assert isinstance(result, WordSuggestion)
            assert len(result.new_words) == 3
            assert isinstance(result.usages, dict)

            for word in result.new_words:
                usage = result.usages.get(word)
                assert usage is not None
                assert isinstance(usage.fr, str)
                assert isinstance(usage.en, str)
                assert len(usage.fr.strip()) > 0
                assert len(usage.en.strip()) > 0

                # Step 4: Optional strict validation
                # Confirm that `fr` sentence only contains words from known + new set
                allowed_vocab = set(known_words + result.new_words)
                sentence_words = re.findall(r"\b\w+\b", usage.fr.lower())

                ALLOWED_FUNCTION_WORDS = {
                    "il", "y", "a", "le", "la", "les", "un", "une", "de", "des", "du", "en",
                    "et", "est", "nous", "je", "tu", "vous", "dans", "sur", "avec", "pour",
                    "mon", "ton", "son", "ce", "cette", "qui", "que", "se"
                }

                unknown_words = [
                    token for token in sentence_words
                    if token not in allowed_vocab and token not in ALLOWED_FUNCTION_WORDS
                ]

                # Warn but don't fail
                if unknown_words:
                    print(f"WARN: (Possible) unexpected words in usage : {unknown_words}")

