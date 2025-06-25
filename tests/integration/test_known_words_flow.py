import pytest
from db.known_words import get_known_words
from services.llm_service import suggest_new_words
from models.words_model import WordSuggestion
import re

@pytest.mark.integration
@pytest.mark.asyncio
async def test_known_words_llm_integration():
    TEST_USER_ID = "00000000-0000-0000-0000-000000000999"

    # Step 1: Get known words
    known_words = get_known_words(TEST_USER_ID)
    assert isinstance(known_words, list)
    assert len(known_words) >= 3

    # Step 2: Run the agent
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

