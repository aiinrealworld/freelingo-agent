import uuid
from typing import Dict, Any, List
from datetime import datetime
import logging
import logfire
from langgraph.graph import StateGraph, END, START

from freelingo_agent.models.graph_state import GraphState
from freelingo_agent.models.dialogue_model import DialogueResponse
from freelingo_agent.models.feedback_model import FeedbackAgentOutput
from freelingo_agent.models.planner_model import PlannerAgentOutput
from freelingo_agent.models.words_model import WordSuggestion
from freelingo_agent.models.referee_model import RefereeAgentOutput
from freelingo_agent.models.user_session import UserSession

# Import your existing services
from freelingo_agent.services.user_session_service import get_session
from freelingo_agent.services.llm_service import (
    get_feedback,
    get_plan,
    suggest_new_words,
    referee_utterance,
)
from freelingo_agent.services.dialogue_session_service import construct_transcript_from_dialogue_history

# Configure logging
logfire.configure(send_to_logfire="if-token-present")
logger = logging.getLogger(__name__)


class GraphWorkflowService:
    """Service for managing the LangGraph learning workflow - integrates with existing system"""
    
    def __init__(self):
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(GraphState)
        
        # Add nodes for each agent
        workflow.add_node("FEEDBACK", self._feedback_node)
        workflow.add_node("PLANNER", self._planner_node)
        workflow.add_node("NEW_WORDS", self._new_words_node)
        workflow.add_node("REFEREE", self._referee_node)
        
        # Set entry point
        workflow.set_entry_point("FEEDBACK")
        
        # Add edges for the session end flow
        workflow.add_edge("FEEDBACK", "PLANNER")
        workflow.add_edge("PLANNER", "NEW_WORDS")
        workflow.add_edge("NEW_WORDS", "REFEREE")
        
        # Add conditional edges from REFEREE
        workflow.add_conditional_edges(
            "REFEREE",
            self._referee_router,
            {
                "PLANNER": "PLANNER",
                "NEW_WORDS": "NEW_WORDS", 
                "FEEDBACK": "FEEDBACK",
                "END": END
            }
        )
        
        
        return workflow
    
    async def _feedback_node(self, state: GraphState) -> GraphState:
        """Generate feedback after dialogue session ends - uses existing session data"""
        logger.info(f"Feedback node activated for user {state.user_id}")
        
        state.current_agent = "FEEDBACK"
        state.updated_at = datetime.now()
        
        try:
            # Use transcript from GraphState (constructed once at workflow start)
            transcript = state.transcript
            
            # Call feedback agent; on failure, fall back to placeholder
            known_words = state.user_session.known_words or []
            new_words = state.last_words
            try:
                state.last_feedback = await get_feedback(
                    transcript=transcript,
                    known_words=known_words,
                    new_words=new_words,
                )
            except Exception as agent_err:
                logger.warning(f"feedback_agent failed, using fallback: {agent_err}")
                state.last_feedback = FeedbackAgentOutput(
                    strengths=[f"Completed session with {len(state.user_session.dialogue_history)} exchanges"],
                    issues=[],
                    next_focus_areas=["Continue practicing"],
                    vocab_usage={},
                )
            
        except Exception as e:
            logger.error(f"Error in feedback node: {e}")
            state.last_feedback = FeedbackAgentOutput(
                strengths=["Completed the session"],
                issues=[],
                next_focus_areas=["Continue practicing"],
                vocab_usage={}
            )
        
        return state
    
    async def _planner_node(self, state: GraphState) -> GraphState:
        """Create learning plan based on feedback - uses existing user data"""
        logger.info(f"Planner node activated for user {state.user_id}")
        
        state.current_agent = "PLANNER"
        state.updated_at = datetime.now()
        
        try:
            # Call planner agent; on failure, fall back to placeholder
            known_words = state.user_session.known_words or []
            new_words = state.last_words
            # Use transcript from GraphState (constructed once at workflow start)
            transcript = state.transcript
            try:
                state.last_plan = await get_plan(
                    known_words=known_words,
                    new_words=new_words,
                    transcript=transcript,
                )
            except Exception as agent_err:
                logger.warning(f"planner_agent failed, using fallback: {agent_err}")
                state.last_plan = PlannerAgentOutput(
                    session_objectives=["Expand vocabulary", "Practice conversation"],
                    suggested_new_words=known_words[:3] if known_words else ["bonjour", "merci"],
                    practice_strategies=["Daily conversation practice"],
                    conversation_prompts=["Tell me about your day"],
                )
            
        except Exception as e:
            logger.error(f"Error in planner node: {e}")
            state.last_plan = PlannerAgentOutput(
                session_objectives=["Continue learning"],
                suggested_new_words=[],
                practice_strategies=["Regular practice"],
                conversation_prompts=[]
            )
        
        return state
    
    async def _new_words_node(self, state: GraphState) -> GraphState:
        """Introduce new vocabulary - uses existing user progress"""
        logger.info(f"New Words node activated for user {state.user_id}")
        
        state.current_agent = "NEW_WORDS"
        state.updated_at = datetime.now()
        
        try:
            # Call words agent; on failure, fall back to placeholder
            known_words = state.user_session.known_words or []
            try:
                state.last_words = await suggest_new_words(known_words)
            except Exception as agent_err:
                logger.warning(f"words_agent failed, using fallback: {agent_err}")
                state.last_words = WordSuggestion(
                    new_words=["bonjour", "merci", "s'il vous plaît"],
                    usages={
                        "bonjour": {"fr": "Bonjour, comment allez-vous?", "en": "Hello, how are you?"},
                        "merci": {"fr": "Merci beaucoup!", "en": "Thank you very much!"},
                        "s'il vous plaît": {"fr": "S'il vous plaît, aidez-moi.", "en": "Please help me."},
                    },
                )
            
        except Exception as e:
            logger.error(f"Error in new words node: {e}")
            state.last_words = WordSuggestion(
                new_words=[],
                usages={}
            )
        
        return state
    
    async def _referee_node(self, state: GraphState) -> GraphState:
        """Evaluate and decide next steps - uses existing session data"""
        logger.info(f"Referee node activated for user {state.user_id}")
        
        state.current_agent = "REFEREE"
        state.updated_at = datetime.now()
        
        try:
            # Determine last learner utterance from history (fallback to empty)
            learner_utterance = ""
            try:
                for msg in reversed(state.user_session.dialogue_history or []):
                    if type(msg).__name__ == "ModelRequest":
                        for part in getattr(msg, "parts", []):
                            if type(part).__name__ == "UserPromptPart" and part.content and part.content.strip():
                                learner_utterance = part.content
                                raise StopIteration
            except StopIteration:
                pass

            # Call referee agent; on failure, fall back to permissive decision
            known_words = state.user_session.known_words or []
            new_words = state.last_words
            try:
                state.last_referee_decision = await referee_utterance(
                    learner_utterance=learner_utterance,
                    known_words=known_words,
                    new_words=new_words,
                )
            except Exception as agent_err:
                logger.warning(f"referee_agent failed, using fallback: {agent_err}")
                state.last_referee_decision = RefereeAgentOutput(
                    is_valid=True,
                    violations=[],
                    rationale={
                        "reasoning_summary": f"Session completed with {len(state.user_session.dialogue_history)} exchanges",
                        "rule_checks": {
                            "used_only_allowed_vocabulary": True,
                            "one_sentence": True,
                            "max_eight_words": True,
                            "no_corrections_or_translations": True,
                        },
                    },
                )

            # Set next agent based on evaluation (simple policy for now)
            state.next_agent = "END"
            
        except Exception as e:
            logger.error(f"Error in referee node: {e}")
            state.last_referee_decision = RefereeAgentOutput(
                is_valid=False,
                violations=["Error occurred"],
                rationale={
                    "reasoning_summary": "Error in evaluation",
                    "rule_checks": {
                        "used_only_allowed_vocabulary": False,
                        "one_sentence": False,
                        "max_eight_words": False,
                        "no_corrections_or_translations": False
                    }
                }
            )
            state.next_agent = "END"
        
        return state
    
    def _referee_router(self, state: GraphState) -> str:
        """Route to next agent based on referee decision"""
        if not state.next_agent or state.next_agent == "END":
            return "END"
        return state.next_agent
    
    
    async def trigger_feedback_loop(self, state: GraphState) -> GraphState:
        """Trigger the post-session learning workflow: feedback → planner → words → referee"""
        logger.info(f"Triggering feedback loop for user {state.user_id}")
        
        # Transition to feedback flow
        state.current_agent = "FEEDBACK"
        
        # Prefer running the compiled graph; fall back to manual sequence on error
        try:
            logger.info("Running workflow via compiled graph")
            final_state = await self.run_workflow(state)
            return final_state
        except Exception as e:
            logger.warning(f"Graph execution failed, falling back to manual sequence: {e}")
            try:
                # Run feedback node
                state = await self._feedback_node(state)
                # Run planner node
                state = await self._planner_node(state)
                # Run new words node
                state = await self._new_words_node(state)
                # Run referee node
                state = await self._referee_node(state)
                return state
            except Exception as inner:
                logger.error(f"Error running manual workflow sequence: {inner}")
                return state
    
    async def run_workflow(self, state: GraphState) -> GraphState:
        """Run the complete workflow from current state"""
        logger.info(f"Running workflow for user {state.user_id}")
        
        try:
            result = await self.app.ainvoke(state)
            # Convert dict result back to GraphState if needed
            if isinstance(result, dict):
                return GraphState(**result)
            return result
        except Exception as e:
            logger.error(f"Error running workflow: {e}")
            return state

