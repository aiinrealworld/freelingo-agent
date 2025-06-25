import pytest
from unittest.mock import patch
from models.words_model import WordSuggestion
from services.words_service import suggest_new_words_for_user

@patch("services.llm_service.fetch_known_words")
@patch("services.llm_service.words_agent")
def test_suggest_new_words_for_user(mock_words_agent, mock_fetch_known_words):
    # Mock DB result
    mock_fetch_known_words.return_value = ["bonjour", "voyage", "train"]

    # Mock LLM result
    mock_words_agent.run.return_value = {
        "new_words": ["billet", "gare", "retard"],
        "examples": {
            "billet": "J'ai acheté un billet pour Paris.",
            "gare": "Nous sommes arrivés à la gare à temps.",
            "retard": "Le train a eu un retard de 20 minutes."
        }
    }

    # Call function under test
    result: WordSuggestion = suggest_new_words_for_user("user123")

    # Assert correct structure
    assert isinstance(result, WordSuggestion)
    assert result.new_words == ["billet", "gare", "retard"]
    assert "billet" in result.examples
    assert "retard" in result.examples
