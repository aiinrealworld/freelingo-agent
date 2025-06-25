import logfire
from pydantic_ai import Agent

from config import DIALOGUE_LLM_MODEL
from agents.agents_config import DIALOGUE_AGENT_PROMPT

# Configure logging
logfire.configure(send_to_logfire="if-token-present")

def create_dialogue_agent(system_prompt: str) -> Agent:
    return Agent(
        model=DIALOGUE_LLM_MODEL,
        system_prompt=system_prompt,
        temperature=0.3,
        output_type=str,
        instrument=True,
    )