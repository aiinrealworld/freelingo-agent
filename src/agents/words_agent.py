import logfire
from pydantic_ai import Agent, RunContext

from config import WORDS_LLM_MODEL
from agents.agents_config import WORDS_AGENT_PROMPT
from models.words_model import WordSuggestion

# Configure logging
logfire.configure(send_to_logfire="if-token-present")

words_agent = Agent(
    model=WORDS_LLM_MODEL,
    system_prompt=WORDS_AGENT_PROMPT,
    temperature=0.3,
    output_type=str,
    instrument=True,
)