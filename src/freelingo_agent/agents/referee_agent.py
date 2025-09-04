import logfire
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, UserPromptPart, ModelResponse, TextPart
from freelingo_agent.config import REFEREE_LLM_MODEL
from freelingo_agent.agents.agents_config import REFEREE_AGENT_PROMPT
from freelingo_agent.models.referee_model import RefereeAgentOutput

# Configure logging
logfire.configure(send_to_logfire="if-token-present")

referee_agent = Agent(
    model=REFEREE_LLM_MODEL,
    system_prompt=REFEREE_AGENT_PROMPT,
    temperature=0.2,
    output_type=str,
    instrument=True,
)
