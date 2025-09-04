import logfire
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, UserPromptPart, ModelResponse, TextPart
from freelingo_agent.config import WORDS_LLM_MODEL
from freelingo_agent.agents.agents_config import WORDS_AGENT_PROMPT
from freelingo_agent.models.words_model import WordSuggestion

# Configure logging
logfire.configure(send_to_logfire="if-token-present")

words_agent = Agent(
    model=WORDS_LLM_MODEL,
    system_prompt=WORDS_AGENT_PROMPT,
    temperature=0.3,
    output_type=str,
    instrument=True,
)