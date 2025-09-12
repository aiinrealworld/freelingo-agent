import os
import json
from typing import List, Dict, Any, Optional, Tuple
from openai import AsyncOpenAI
from freelingo_agent.models.words_model import WordSuggestion, Word
from freelingo_agent.models.feedback_model import FeedbackAgentOutput
from freelingo_agent.models.planner_model import PlannerAgentOutput
from freelingo_agent.models.referee_model import RefereeAgentOutput
from freelingo_agent.models.transcript_model import Transcript
from freelingo_agent.services.user_session_service import get_session
from freelingo_agent.agents.words_agent import words_agent
from freelingo_agent.agents.agents_config import DIALOGUE_AGENT_PROMPT
from freelingo_agent.agents.dialogue_agent import create_dialogue_agent
from freelingo_agent.agents.feedback_agent import feedback_agent
from freelingo_agent.agents.planner_agent import planner_agent
from freelingo_agent.agents.referee_agent import referee_agent
from pydantic_ai.messages import ModelMessage, UserPromptPart, ModelResponse, TextPart

async def suggest_new_words(
    known_words: List[Word],
    plan: Optional[PlannerAgentOutput] = None,
    feedback: Optional[FeedbackAgentOutput] = None,
    referee_feedback: Optional[List[RefereeAgentOutput]] = None,
) -> WordSuggestion:
    """
    Calls the words_agent to suggest 3 new words that pair well with known words.

    Args:
        known_words (List[Word]): The user's known French words.

    Returns:
        WordSuggestion: new words + example sentences
    """

    try:
        # Build INPUT block with complete plan and feedback outputs
        word_strings = [word.word for word in known_words]
        parts: List[str] = []
        parts.append(f"known_words: {json.dumps(word_strings, ensure_ascii=False)}")
        if plan is not None:
            # Pass complete plan output
            plan_json = json.dumps(plan.model_dump(), indent=2, ensure_ascii=False)
            parts.append("Plan:")
            parts.append(plan_json)
        if feedback is not None:
            # Pass complete feedback output as fallback/context
            feedback_json = json.dumps(feedback.model_dump(), indent=2, ensure_ascii=False)
            parts.append("Feedback:")
            parts.append(feedback_json)
        
        # Add referee feedback if this is a retry
        if referee_feedback:
            parts.append("Referee Feedback (from previous attempts):")
            for i, feedback in enumerate(referee_feedback):
                parts.append(f"Attempt {i+1}: {feedback.rationale.reasoning_summary}")
                if feedback.violations:
                    parts.append(f"  Violations: {', '.join(feedback.violations)}")
            parts.append("Please address the referee's concerns in your word suggestions.")
        
        parts.append("END")
        user_prompt = "\n".join(parts)

        result = await words_agent.run(user_prompt=user_prompt)
        parsed_output = json.loads(result.output)
        
        return WordSuggestion(**parsed_output)
    
    except Exception as e:
        raise RuntimeError(f"words_agent failed: {e}")


async def get_dialogue_response(
    user_id: str,
    known_words: List[Word],
    student_response: str,
    dialogue_history: List[ModelMessage],
) -> Tuple[str, List[ModelMessage], Dict[str, Any]]:
    """
    Calls the dialogue_agent to generate the next AI message in French.

    Args:
        known_words (List[Word]): Words the user already knows.
        dialogue_history (List[ModelMessage]): List of previous ModelMessage objects.

    Returns:
        str: The next AI message in French (clean text for UI).
        List[ModelMessage]: Updated dialogue history with new turn.
        Dict: Full agent response (for storage and feedback agent).
    """

    try:
        session = get_session(user_id=user_id)
        dialogue_agent = session.dialogue_agent

        if dialogue_agent is None:
            # Extract just the word strings for the agent
            word_strings = [word.word for word in known_words]
            updated_dialogue_agent_prompt = DIALOGUE_AGENT_PROMPT.format(
                known_words=json.dumps(word_strings, ensure_ascii=False)
            )
            dialogue_agent = create_dialogue_agent(updated_dialogue_agent_prompt)
            session.dialogue_agent = dialogue_agent
      
        result = await dialogue_agent.run(
            user_prompt=student_response,
            message_history=dialogue_history
        )
        
        # Extract the actual reply text from the structured response
        if hasattr(result.output, 'ai_reply') and hasattr(result.output.ai_reply, 'text'):
            ai_message = result.output.ai_reply.text
        else:
            # Fallback: try to use the output directly if it's a string
            ai_message = str(result.output)
        
        # Extract full response for storage
        full_response = extract_full_agent_response(result.output)
        
        return ai_message, result.all_messages(), full_response

    except Exception as e:
        raise RuntimeError(f"dialogue_agent failed: {e}")

def extract_full_agent_response(result_output) -> Dict[str, Any]:
    """Extract the full agent response including rationale, rule_checks, etc."""
    if hasattr(result_output, '__dict__'):
        return result_output.__dict__
    elif hasattr(result_output, 'model_dump'):
        return result_output.model_dump()
    else:
        return {"raw_response": str(result_output)}


def truncate_transcript_for_logging(transcript_text: str, max_lines: int = 3) -> str:
    """Truncate transcript text for cleaner logging output."""
    lines = transcript_text.split('\n')
    if len(lines) <= max_lines:
        return transcript_text
    
    truncated_lines = lines[:max_lines]
    truncated_text = '\n'.join(truncated_lines)
    return f"{truncated_text}\n... (+{len(lines) - max_lines} more lines)"



async def get_feedback(
    transcript: Transcript,
    known_words: List[Word],
    new_words: Optional[WordSuggestion] = None,
    referee_feedback: Optional[List[RefereeAgentOutput]] = None,
) -> FeedbackAgentOutput:
    """
    Calls the feedback_agent with the provided transcript and vocabulary context.
    Returns a validated FeedbackAgentOutput.
    """

    try:
        # Convert Transcript model to rich JSON-style string format for the agent
        transcript_text = json.dumps(transcript.model_dump(), indent=2, ensure_ascii=False)

        # Build INPUT block as per few-shots
        parts = []
        # Extract just the word strings for the agent
        word_strings = [word.word for word in known_words]
        parts.append(f"known_words: {json.dumps(word_strings, ensure_ascii=False)}")
        if new_words and new_words.new_words:
            parts.append(f"new_words: {json.dumps(new_words.new_words, ensure_ascii=False)}")
        parts.append("Transcript:")
        parts.append(transcript_text)
        
        # Add referee feedback if this is a retry
        if referee_feedback:
            parts.append("Referee Feedback (from previous attempts):")
            for i, feedback in enumerate(referee_feedback):
                parts.append(f"Attempt {i+1}: {feedback.rationale.reasoning_summary}")
                if feedback.violations:
                    parts.append(f"  Violations: {', '.join(feedback.violations)}")
            parts.append("Please address the referee's concerns in your feedback.")
        
        parts.append("END")
        user_prompt = "\n".join(parts)

        result = await feedback_agent.run(user_prompt=user_prompt)
        
        # The agent now returns FeedbackAgentOutput directly
        if isinstance(result.output, FeedbackAgentOutput):
            return result.output
        else:
            # Fallback for string output (shouldn't happen with proper config)
            parsed_output = json.loads(result.output)
            return FeedbackAgentOutput(**parsed_output)
    except Exception as e:
        raise RuntimeError(f"feedback_agent failed: {e}")


async def get_plan(
    known_words: List[Word],
    feedback: Optional[FeedbackAgentOutput] = None,
    new_words: Optional[WordSuggestion] = None,
    referee_feedback: Optional[List[RefereeAgentOutput]] = None,
) -> PlannerAgentOutput:
    """
    Calls the planner_agent to create a practice plan for the next session.
    Returns a validated PlannerAgentOutput.
    """

    try:
        # Build INPUT block with complete feedback output
        parts: List[str] = []
        word_strings = [word.word for word in known_words]
        parts.append(f"known_words: {json.dumps(word_strings, ensure_ascii=False)}")
        if new_words and new_words.new_words:
            parts.append(f"new_words: {json.dumps(new_words.new_words, ensure_ascii=False)}")
        if feedback is not None:
            # Pass complete feedback output
            feedback_json = json.dumps(feedback.model_dump(), indent=2, ensure_ascii=False)
            parts.append("Feedback:")
            parts.append(feedback_json)
        
        # Add referee feedback if this is a retry
        if referee_feedback:
            parts.append("Referee Feedback (from previous attempts):")
            for i, feedback in enumerate(referee_feedback):
                parts.append(f"Attempt {i+1}: {feedback.rationale.reasoning_summary}")
                if feedback.violations:
                    parts.append(f"  Violations: {', '.join(feedback.violations)}")
            parts.append("Please address the referee's concerns in your plan.")
        
        parts.append("END")
        user_prompt = "\n".join(parts)
        
        result = await planner_agent.run(user_prompt=user_prompt)
        return result.output
    except Exception as e:
        raise RuntimeError(f"planner_agent failed: {e}")


async def validate_agent_chain(
    transcript: Transcript,
    known_words: List[Word],
    feedback: Optional[FeedbackAgentOutput] = None,
    plan: Optional[PlannerAgentOutput] = None,
    new_words: Optional[WordSuggestion] = None,
) -> RefereeAgentOutput:
    """
    Calls the referee_agent to validate the entire agent chain alignment.
    Returns a validated RefereeAgentOutput.
    """

    try:
        # Build allowed vocabulary list
        allowed_words = [word.word for word in known_words]
        if new_words and new_words.new_words:
            allowed_words.extend(new_words.new_words)
        
        # Build INPUT block with full transcript
        parts = []
        parts.append("Transcript:")
        parts.append(json.dumps(transcript.model_dump(), indent=2, ensure_ascii=False))
        parts.append(f"Known words: {json.dumps(allowed_words, ensure_ascii=False)}")
        
        # Add complete chain context for validation
        if feedback is not None:
            feedback_json = json.dumps(feedback.model_dump(), indent=2, ensure_ascii=False)
            parts.append("Feedback:")
            parts.append(feedback_json)
        if plan is not None:
            plan_json = json.dumps(plan.model_dump(), indent=2, ensure_ascii=False)
            parts.append("Plan:")
            parts.append(plan_json)
        
        parts.append("END")
        user_prompt = "\n".join(parts)

        result = await referee_agent.run(user_prompt=user_prompt)
        
        # The agent now returns RefereeAgentOutput directly
        if isinstance(result.output, RefereeAgentOutput):
            return result.output
        else:
            # Fallback for string output (shouldn't happen with correct config)
            parsed_output = json.loads(result.output)
            return RefereeAgentOutput(**parsed_output)
    except Exception as e:
        raise RuntimeError(f"referee_agent failed: {e}")
