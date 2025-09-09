import logfire
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, UserPromptPart, ModelResponse, TextPart
from freelingo_agent.config import PLANNER_LLM_MODEL
from freelingo_agent.agents.agents_config import PLANNER_AGENT_PROMPT
from freelingo_agent.models.planner_model import PlannerAgentOutput

# Configure logging
logfire.configure(send_to_logfire="if-token-present")

planner_agent = Agent(
    model=PLANNER_LLM_MODEL,
    system_prompt=PLANNER_AGENT_PROMPT,
    temperature=0.2,
    output_type=PlannerAgentOutput,
    instrument=True,
)
