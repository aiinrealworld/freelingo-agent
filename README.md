# language-tutor-agent


$env:PYTHONPATH = "src"
pytest tests/db/test_known_words.py -v
pytest tests/services/test_llm_service.py -v

pytest -m integration -s

## Synthflow

Has widget functionality - for website embed
Don't think it supports dynamic prompt (also did not see GPT LLM options)
Agent types - inbound, outbound and widget
API only allows to work with inbout and outbound (GPT LLM options available here)

## VapI

Has voice embed script => tied to an assistant
API available to update assistant with prompt, model