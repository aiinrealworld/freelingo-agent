# FreeLingo Agent

AI-powered language learning agent with LangGraph workflow for managing multi-agent learning sessions.

## 🏗️ **Project Structure**

This project uses a proper Python package structure:

```
freelingo-agent/
├── pyproject.toml          # Package configuration
├── src/
│   └── freelingo_agent/   # Main package
│       ├── __init__.py     # Package initialization
│       ├── main.py         # FastAPI application entry point
│       ├── config.py       # Configuration settings
│       ├── api/            # FastAPI route handlers
│       ├── services/       # Business logic services
│       ├── models/         # Pydantic data models
│       ├── agents/         # AI agent implementations
│       ├── db/             # Database operations
│       └── utils/          # Utility functions
├── tests/                  # Test suite
└── requirements.txt        # Python dependencies
```

## 🚀 **Getting Started**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Install Package in Editable Mode**
```bash
pip install -e .
```

### **3. Run the Application**
```bash
# Run with Python module syntax (recommended)
python -m freelingo_agent.main

# Or run directly (not recommended)
python src/freelingo_agent/main.py
```

### **4. Run Tests**
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/integration/test_workflow.py -v
```

## 🔄 LangGraph Workflow

This app orchestrates a multi-agent learning workflow with LangGraph. The flow is:

```
User initiates → DIALOGUE
                    ↓
Session ends → FEEDBACK → PLANNER → NEW_WORDS → REFEREE
                                                  ↓
REFEREE routes to: PLANNER, NEW_WORDS, FEEDBACK, or END
```

### Key Components
- **DIALOGUE**: User-controlled conversation sessions
- **FEEDBACK**: Analyzes session performance and provides insights
- **PLANNER**: Creates learning plans based on feedback
- **NEW_WORDS**: Introduces appropriate vocabulary
- **REFEREE**: Evaluates and decides next learning steps

### Trigger Model
- The workflow is triggered when a dialogue session ends (i.e., after saving a transcript via the dialogue session endpoints). The dedicated workflow endpoints have been removed.

### Files
- `src/freelingo_agent/models/graph_state.py` — State models
- `src/freelingo_agent/services/graph_workflow_service.py` — Orchestration logic
- `src/freelingo_agent/api/dialogue.py` — Dialogue + session endpoints (triggers workflow after save)

### How It Works
1. Session start: User initiates dialogue
2. Dialogue active: User and AI converse
3. Session end: API saves transcript and triggers workflow
4. Feedback → Planning → New Words → Referee
5. Referee can route to any agent or end

### Agent Integration
Each agent node:
- Receives context from the state
- Processes using the appropriate agent in `services/llm_service.py`
- Updates the state with results
- Logs activities for monitoring (Logfire)

### Testing the Workflow
```python
from freelingo_agent.services.graph_workflow_service import GraphWorkflowService

service = GraphWorkflowService()
state = await service.start_session("test_user")
final_state = await service.end_session(state)
assert final_state.last_feedback is not None
```

## 📚 API Endpoints

- `POST /api/dialogue` — Run a dialogue turn
- `POST /api/dialogue-session` — Save a provided session (triggers workflow)
- `POST /api/dialogue-session/current/{user_id}` — Save current in-memory session (triggers workflow)
- `GET /api/dialogue-sessions/{user_id}` — List sessions
- `GET /api/dialogue-session/{session_id}` — Get one session
- `GET /api/health` — Health check

## 🧪 **Testing**

The project includes comprehensive tests:
- **Unit tests** for individual components
- **Integration tests** for API endpoints
- **Workflow tests** for LangGraph functionality

## 🚀 **Deployment**

The package structure makes deployment easy:
- **Local development**: `pip install -e .`
- **Production**: Install as regular package
- **Docker**: Build from package
- **Cloud platforms**: Render, AWS, etc.

## 📝 **Development**

### **Adding New Features**
1. Add code to appropriate package module
2. Use absolute imports: `from freelingo_agent.models import User`
3. Update tests
4. Test with `python -m freelingo_agent.main`

### **Import Best Practices**
- ✅ Use absolute imports: `from freelingo_agent.api.auth import router`
- ❌ Don't use relative imports: `from ..models import User`
- ❌ Don't use src prefixes: `from src.models import User`

## 🔧 **Configuration**

Set environment variables in `.env`:
- `SUPABASE_URL` - Database connection
- `SUPABASE_API_KEY` - Database authentication
- `FIREBASE_SERVICE_ACCOUNT_PATH` - Firebase configuration