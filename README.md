# language-tutor-agent


$env:PYTHONPATH = "src"
pytest tests/db/test_known_words.py -v
pytest tests/services/test_llm_service.py -v

pytest -m integration -s