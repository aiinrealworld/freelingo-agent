import pytest
from unittest.mock import patch
from freelingo_agent.models.words_model import WordSuggestion
from freelingo_agent.services.words_service import suggest_new_words_for_user
from unittest.mock import patch, AsyncMock
import json

@pytest.mark.asyncio
@patch("freelingo_agent.services.words_service.fetch_known_words")
@patch("freelingo_agent.services.llm_service.words_agent")
async def test_suggest_new_words_for_user(mock_words_agent, mock_fetch_known_words):
    # Mock DB result
    mock_fetch_known_words.return_value = ["bonjour", "voyage", "train"]

    # Mock LLM result
    mock_words_agent.run = AsyncMock()
    mock_words_agent.run.return_value.output = json.dumps({
        "new_words": ["billet", "gare", "retard"],
        "usages": {
            "billet": {
                "fr": "J'ai acheté un billet pour Paris.",
                "en": "I bought a ticket to Paris."
            },
            "gare": {
                "fr": "Nous sommes arrivés à la gare à temps.",
                "en": "We arrived at the station on time."
            },
            "retard": {
                "fr": "Le train a eu un retard de 20 minutes.",
                "en": "The train was 20 minutes late."
            }
        }
    })


    # Call function under test
    result = await suggest_new_words_for_user("user123")

    # Assert correct structure
    assert isinstance(result, WordSuggestion)
    assert result.usages["gare"].fr.startswith("Nous sommes")
    assert result.usages["retard"].en.endswith("late.")
