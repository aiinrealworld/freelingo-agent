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

$env:PYTHONPATH = "src"
uvicorn main:app --reload


cd src/streamlit_app
streamlit run main.py

find firebase config here - https://console.firebase.google.com/u/0/project/language-tutor-agent/settings/general/web:NDBmNWNmNWMtODdmYi00M2FjLTk2ZDQtOTZjODUwNjkwMmI0

cd public
python -m http.server 8080

http://localhost:8080/login.html