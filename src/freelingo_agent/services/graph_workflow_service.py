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
from freelingo_agent.services.user_session_service import get_session, clear_dialogue_in_session
from freelingo_agent.services.dialogue_session_service import save_dialogue_session_service

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
        workflow.add_node("DIALOGUE", self._dialogue_node)
        workflow.add_node("FEEDBACK", self._feedback_node)
        workflow.add_node("PLANNER", self._planner_node)
        workflow.add_node("NEW_WORDS", self._new_words_node)
        workflow.add_node("REFEREE", self._referee_node)
        
        # Set entry point
        workflow.set_entry_point("DIALOGUE")
        
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
        
        # Add edge from DIALOGUE to END (user can end session)
        workflow.add_edge("DIALOGUE", END)
        
        return workflow
    
    async def _dialogue_node(self, state: GraphState) -> GraphState:
        """Handle dialogue interactions - uses existing UserSession"""
        logger.info(f"Dialogue node activated for user {state.user_id}")
        
        # Update state
        state.current_agent = "DIALOGUE"
        state.updated_at = datetime.now()
        
        # Get existing user session (don't create new one)
        existing_session = get_session(state.user_id)
        if existing_session:
            state.user_session = existing_session
        
        return state
    
    async def _feedback_node(self, state: GraphState) -> GraphState:
        """Generate feedback after dialogue session ends - uses existing session data"""
        logger.info(f"Feedback node activated for user {state.user_id}")
        
        state.current_agent = "FEEDBACK"
        state.updated_at = datetime.now()
        
        try:
            # Use existing session data for feedback
            context = self._prepare_feedback_context(state)
            
            # TODO: Call your existing feedback agent here
            # For now, create placeholder using existing session data
            state.last_feedback = FeedbackAgentOutput(
                strengths=[f"Completed session with {len(state.user_session.dialogue_history)} exchanges"],
                issues=[],
                next_focus_areas=["Continue practicing"],
                vocab_usage={}
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
            # Use existing user session data for planning
            context = self._prepare_planner_context(state)
            
            # TODO: Call your existing planner agent here
            # For now, create placeholder using existing session data
            state.last_plan = PlannerAgentOutput(
                session_objectives=["Expand vocabulary", "Practice conversation"],
                suggested_new_words=state.user_session.known_words[:3] if state.user_session.known_words else ["bonjour", "merci"],
                practice_strategies=["Daily conversation practice"],
                conversation_prompts=["Tell me about your day"]
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
            # Use existing user session data for new words
            context = self._prepare_words_context(state)
            
            # TODO: Call your existing words agent here
            # For now, create placeholder using existing session data
            state.last_words = WordSuggestion(
                new_words=["bonjour", "merci", "s'il vous plaît"],
                usages={
                    "bonjour": {"fr": "Bonjour, comment allez-vous?", "en": "Hello, how are you?"},
                    "merci": {"fr": "Merci beaucoup!", "en": "Thank you very much!"},
                    "s'il vous plaît": {"fr": "S'il vous plaît, aidez-moi.", "en": "Please help me."}
                }
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
            # Use existing session data for referee decision
            context = self._prepare_referee_context(state)
            
            # TODO: Call your existing referee agent here
            # For now, create placeholder decision using existing session data
            state.last_referee_decision = RefereeAgentOutput(
                is_valid=True,
                violations=[],
                rationale={
                    "reasoning_summary": f"Session completed with {len(state.user_session.dialogue_history)} exchanges",
                    "rule_checks": {
                        "used_only_allowed_vocabulary": True,
                        "one_sentence": True,
                        "max_eight_words": True,
                        "no_corrections_or_translations": True
                    }
                }
            )
            
            # Set next agent based on evaluation
            state.next_agent = "END"  # Default to ending
            
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
    
    def _prepare_feedback_context(self, state: GraphState) -> str:
        """Prepare context for feedback agent using existing session data"""
        context = f"""
        User ID: {state.user_id}
        Dialogue History: {len(state.user_session.dialogue_history)} exchanges
        Known Words: {', '.join(state.user_session.known_words)}
        Last Agent Response: {state.user_session.last_agent_response}
        """
        return context
    
    def _prepare_planner_context(self, state: GraphState) -> str:
        """Prepare context for planner agent using existing session data"""
        if not state.last_feedback:
            return "No feedback available"
        
        context = f"""
        User ID: {state.user_id}
        Known Words: {', '.join(state.user_session.known_words)}
        Feedback Strengths: {', '.join(state.last_feedback.strengths)}
        Areas for Improvement: {', '.join([issue.kind for issue in state.last_feedback.issues])}
        Next Focus Areas: {', '.join(state.last_feedback.next_focus_areas)}
        """
        return context
    
    def _prepare_words_context(self, state: GraphState) -> str:
        """Prepare context for words agent using existing session data"""
        context = f"""
        User ID: {state.user_id}
        Known Words: {', '.join(state.user_session.known_words)}
        Dialogue History Length: {len(state.user_session.dialogue_history)}
        """
        return context
    
    def _prepare_referee_context(self, state: GraphState) -> str:
        """Prepare context for referee agent using existing session data"""
        context = f"""
        User ID: {state.user_id}
        Known Words: {', '.join(state.user_session.known_words)}
        Session Goals: {', '.join(state.session_goals)}
        Feedback: {state.last_feedback.strengths if state.last_feedback else 'None'}
        Plan: {state.last_plan.session_objectives if state.last_plan else 'None'}
        New Words: {state.last_words.new_words if state.last_words else 'None'}
        """
        return context
    
    async def start_session(self, user_id: str, session_goals: List[str] = None) -> GraphState:
        """Start a new learning session using existing UserSession"""
        logger.info(f"Starting new session for user {user_id}")
        
        # Get existing user session (don't create new one)
        user_session = get_session(user_id)
        if not user_session:
            # Create minimal session if none exists
            user_session = UserSession(user_id=user_id)
        
        # Create initial state using existing session
        initial_state = GraphState(
            user_id=user_id,
            user_session=user_session,
            session_goals=session_goals or ["Practice conversation", "Learn new vocabulary"],
            current_agent="DIALOGUE"
        )
        
        return initial_state
    
    async def process_dialogue(self, state: GraphState, user_message: str) -> Dict[str, Any]:
        """Process a user message in dialogue mode - integrates with existing system"""
        logger.info(f"Processing dialogue for user {state.user_id}")
        
        # Update existing user session (this integrates with your existing dialogue flow)
        if state.user_session:
            # TODO: Integrate with your existing dialogue processing
            # For now, return a simple response
            response = {
                "message": "Bonjour! Comment allez-vous aujourd'hui?"
            }
        
        return response
    
    async def end_session(self, state: GraphState) -> GraphState:
        """End the current dialogue session and start the feedback flow"""
        logger.info(f"Ending session for user {state.user_id}")
        
        # Try to save the dialogue session using your existing service
        # But don't fail if it can't connect to database
        try:
            session_id = save_dialogue_session_service(
                user_id=state.user_id,
                started_at=None,
                ended_at=datetime.now().isoformat()
            )
            logger.info(f"Saved dialogue session: {session_id}")
        except Exception as e:
            logger.warning(f"Could not save dialogue session (this is OK for testing): {e}")
        
        # Transition to feedback flow
        state.current_agent = "FEEDBACK"
        
        # Run the workflow from feedback onwards
        try:
            # For now, let's manually run through the workflow steps to avoid return type issues
            logger.info("Running workflow manually to avoid return type issues")
            
            # Run feedback node
            state = await self._feedback_node(state)
            
            # Run planner node
            state = await self._planner_node(state)
            
            # Run new words node
            state = await self._new_words_node(state)
            
            # Run referee node
            state = await self._referee_node(state)
            
            return state
            
        except Exception as e:
            logger.error(f"Error running workflow: {e}")
            return state
    
    async def run_workflow(self, state: GraphState) -> GraphState:
        """Run the complete workflow from current state"""
        logger.info(f"Running workflow for user {state.user_id}")
        
        try:
            result = await self.app.ainvoke(state)
            return result
        except Exception as e:
            logger.error(f"Error running workflow: {e}")
            return state

