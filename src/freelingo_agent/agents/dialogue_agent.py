import logfire
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, UserPromptPart, ModelResponse, TextPart
from freelingo_agent.config import DIALOGUE_LLM_MODEL
from freelingo_agent.models.dialogue_model import DialogueResponse

# Configure logging
logfire.configure(send_to_logfire="if-token-present")

def create_dialogue_agent(system_prompt: str) -> Agent:
    return Agent(
        model=DIALOGUE_LLM_MODEL,
        system_prompt=system_prompt,
        temperature=0.3,
        output_type=DialogueResponse,
        instrument=True,
    )