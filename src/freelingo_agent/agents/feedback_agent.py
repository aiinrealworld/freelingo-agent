import logfire
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, UserPromptPart, ModelResponse, TextPart
from freelingo_agent.config import FEEDBACK_LLM_MODEL
from freelingo_agent.agents.agents_config import FEEDBACK_AGENT_PROMPT
from freelingo_agent.models.feedback_model import FeedbackAgentOutput

# Configure logging
logfire.configure(send_to_logfire="if-token-present")

feedback_agent = Agent(
    model=FEEDBACK_LLM_MODEL,
    system_prompt=FEEDBACK_AGENT_PROMPT,
    temperature=0.2,
    output_type=FeedbackAgentOutput,
    instrument=True,
)


