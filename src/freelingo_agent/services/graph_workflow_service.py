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
    validate_agent_chain,
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
        state.state_transitions.append("FEEDBACK")
        
        try:
            # Use transcript from GraphState (constructed once at workflow start)
            transcript = state.transcript
            
            # Call feedback agent; on failure, fall back to placeholder
            known_words = state.user_session.known_words or []
            new_words = state.last_words
            try:
                # Pass referee feedback history if this is a retry
                referee_feedback = state.referee_feedback_history if state.referee_feedback_history else None
                state.last_feedback = await get_feedback(
                    transcript=transcript,
                    known_words=known_words,
                    new_words=new_words,
                    referee_feedback=referee_feedback,
                )
            except Exception as agent_err:
                logger.error(f"feedback_agent failed, using fallback: {agent_err}")
                print(f"[ERROR] Feedback agent failed: {agent_err}")
                import traceback
                traceback.print_exc()
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
        state.state_transitions.append("PLANNER")
        
        try:
            # Call planner agent; on failure, fall back to placeholder
            known_words = state.user_session.known_words or []
            new_words = state.last_words
            # Use transcript from GraphState (constructed once at workflow start)
            transcript = state.transcript
            try:
                # Pass referee feedback history if this is a retry
                referee_feedback = state.referee_feedback_history if state.referee_feedback_history else None
                state.last_plan = await get_plan(
                    known_words=known_words,
                    feedback=state.last_feedback,
                    new_words=new_words,
                    referee_feedback=referee_feedback,
                )
            except Exception as agent_err:
                logger.warning(f"planner_agent failed, using fallback: {agent_err}")
                state.last_plan = PlannerAgentOutput(
                    session_objectives=["Expand vocabulary", "Practice conversation"],
                    practice_strategies=["Daily conversation practice"],
                )
            
        except Exception as e:
            logger.error(f"Error in planner node: {e}")
            state.last_plan = PlannerAgentOutput(
                session_objectives=["Continue learning"],
                practice_strategies=["Regular practice"]
            )
        
        return state
    
    async def _new_words_node(self, state: GraphState) -> GraphState:
        """Introduce new vocabulary - uses existing user progress"""
        logger.info(f"New Words node activated for user {state.user_id}")
        
        state.current_agent = "NEW_WORDS"
        state.updated_at = datetime.now()
        state.state_transitions.append("NEW_WORDS")
        
        try:
            # Call words agent; on failure, fall back to placeholder
            known_words = state.user_session.known_words or []
            try:
                # Pass referee feedback history if this is a retry
                referee_feedback = state.referee_feedback_history if state.referee_feedback_history else None
                state.last_words = await suggest_new_words(
                    known_words=known_words,
                    plan=state.last_plan,
                    feedback=state.last_feedback,
                    referee_feedback=referee_feedback,
                )
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
        state.state_transitions.append("REFEREE")
        
        # Print state transitions when reaching referee
        transitions_str = " → ".join(state.state_transitions)
        print(f"[REFEREE] State transitions: {transitions_str}")
        logger.info(f"State transitions when reaching referee: {transitions_str}")
        
        try:
            # Use transcript from GraphState (constructed once at workflow start)
            transcript = state.transcript
            
            # Call referee agent; on failure, fall back to permissive decision
            known_words = state.user_session.known_words or []
            new_words = state.last_words
            try:
                state.last_referee_decision = await validate_agent_chain(
                    transcript=transcript,
                    known_words=known_words,
                    feedback=state.last_feedback,
                    plan=state.last_plan,
                    new_words=new_words,
                )
            except Exception as agent_err:
                logger.warning(f"referee_agent failed, using conservative fallback: {agent_err}")
                state.last_referee_decision = RefereeAgentOutput(
                    is_valid=False,
                    violations=["referee_agent_failed"],
                    rationale={
                        "reasoning_summary": f"Referee agent failed to evaluate chain quality",
                        "rule_checks": {
                            "feedback_transcript_alignment": False,
                            "planner_feedback_incorporation": False,
                            "new_words_plan_alignment": False,
                            "overall_chain_coherence": False,
                        },
                    },
                )

            # Store referee decision in feedback history
            state.referee_feedback_history.append(state.last_referee_decision)
            
            # Set next agent based on referee evaluation
            state.next_agent = self._determine_next_agent_from_referee(state.last_referee_decision, state)
            
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
            # Store referee decision in feedback history
            state.referee_feedback_history.append(state.last_referee_decision)
            
            state.next_agent = self._determine_next_agent_from_referee(state.last_referee_decision, state)
        
        return state
    
    def _determine_next_agent_from_referee(self, referee_decision: RefereeAgentOutput, state: GraphState) -> str:
        """Determine next agent based on referee evaluation with circuit breaker"""
        if not referee_decision or not referee_decision.is_valid:
            # If invalid, check violations to determine where to route
            violations = referee_decision.violations if referee_decision else []
            
            # Determine target agent based on violations
            target_agent = None
            if "feedback_misaligned_with_transcript" in violations:
                target_agent = "FEEDBACK"
            elif "planner_ignored_feedback" in violations:
                target_agent = "PLANNER"
            elif "new_words_off_topic" in violations:
                target_agent = "NEW_WORDS"
            elif "chain_incoherent" in violations:
                target_agent = "FEEDBACK"  # Start over
            else:
                # Default to feedback for any other issues
                target_agent = "FEEDBACK"
            
            # Check retry count for circuit breaker
            retry_count = state.agent_retry_count.get(target_agent, 0)
            if retry_count >= state.max_retries:
                logger.warning(f"Circuit breaker triggered: {target_agent} has been retried {retry_count} times. Ending workflow.")
                return "END"
            
            return target_agent
        else:
            # Chain is valid, end the workflow
            return "END"
    
    def _referee_router(self, state: GraphState) -> str:
        """Route to next agent based on referee decision"""
        if not state.next_agent or state.next_agent == "END":
            return "END"
        
        # Check if we've been to referee 5 times - circuit breaker
        referee_count = state.state_transitions.count("REFEREE")
        if referee_count >= 5:
            logger.warning(f"Circuit breaker triggered: Referee has been called {referee_count} times. Ending workflow.")
            return "END"
        
        # Increment retry count for the target agent
        target_agent = state.next_agent
        state.agent_retry_count[target_agent] = state.agent_retry_count.get(target_agent, 0) + 1
        
        logger.info(f"Routing to {target_agent} (retry #{state.agent_retry_count[target_agent]})")
        self._log_state_transitions(state)
        return target_agent
    
    def _log_state_transitions(self, state: GraphState) -> None:
        """Log the current state transition history"""
        if state.state_transitions:
            transitions_str = " → ".join(state.state_transitions)
            logger.info(f"State transitions: {transitions_str}")
        else:
            logger.info("No state transitions recorded yet")
    
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
                final_state = GraphState(**result)
            else:
                final_state = result
            
            # Log final state transitions
            self._log_state_transitions(final_state)
            return final_state
        except Exception as e:
            logger.error(f"Error running workflow: {e}")
            return state

