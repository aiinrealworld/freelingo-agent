# LangGraph Workflow for FreeLingo Agents

This document describes the LangGraph workflow implementation that orchestrates the FreeLingo learning agents.

## 🏗️ Architecture Overview

The workflow follows this pattern:

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

## 📁 File Structure

```
src/
├── models/
│   └── graph_state.py              # State models for the workflow
├── services/
│   └── graph_workflow_service.py   # Main workflow orchestration
└── api/
    └── graph_workflow_api.py       # API endpoints for workflow
```

## 🚀 Getting Started

### 1. Install Dependencies

The workflow uses `pydantic-graph` which is already included in your requirements.txt.

### 2. Run the Test

```bash
python test_workflow.py
```

This will demonstrate the complete workflow flow.

### 3. Use the API

The workflow is exposed via FastAPI endpoints:

- `POST /api/workflow/start-session` - Start a new learning session
- `POST /api/workflow/process-dialogue` - Process user messages
- `POST /api/workflow/end-session` - End session and trigger workflow
- `GET /api/workflow/workflow-status/{user_id}` - Get current status
- `POST /api/workflow/test-workflow` - Test complete workflow

## 🔧 How It Works

### State Management

The `GraphState` class tracks:
- User progress and session information
- Current agent and workflow step
- Agent outputs and decisions
- Learning context and goals

### Workflow Flow

1. **Session Start**: User initiates dialogue
2. **Dialogue Active**: User and AI converse
3. **Session End**: User ends dialogue, triggers feedback flow
4. **Feedback**: Analyze session performance
5. **Planning**: Create next learning objectives
6. **New Words**: Introduce appropriate vocabulary
7. **Referee**: Evaluate and decide next steps
8. **Routing**: Referee can route to any agent or end

### Agent Integration

Each agent node:
- Receives context from the state
- Processes using the appropriate agent
- Updates the state with results
- Logs activities for monitoring

## 🎯 Customization

### Adding New Agents

1. Create the agent in `src/agents/`
2. Add a node in `_build_graph()`
3. Implement the node function
4. Add appropriate edges

### Modifying Routing Logic

The `_referee_router()` function controls agent transitions. Modify it to:
- Add new routing conditions
- Change routing priorities
- Implement learning-based routing

### State Extensions

Extend `GraphState` to include:
- Additional learning metrics
- User preferences
- Session history
- Performance analytics

## 🔍 Monitoring and Debugging

### Logging

The workflow uses Logfire for structured logging:
- Agent transitions
- State changes
- Error handling
- Performance metrics

### State Inspection

Use the API endpoints to:
- Monitor workflow progress
- Debug agent decisions
- Track user learning paths

## 🧪 Testing

### Unit Tests

Test individual components:
```python
from src.services.graph_workflow_service import GraphWorkflowService

# Test workflow creation
service = GraphWorkflowService()
assert service.graph is not None
```

### Integration Tests

Test complete workflows:
```python
# Test end-to-end workflow
state = await service.start_session("test_user")
final_state = await service.end_session(state)
assert final_state.last_feedback is not None
```

### API Tests

Test via HTTP endpoints:
```bash
curl -X POST "http://localhost:8000/api/workflow/test-workflow" \
     -H "Content-Type: application/json"
```

## 🚨 Common Issues

### Import Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### State Persistence

The current implementation uses in-memory state. For production:
- Add database persistence
- Implement state recovery
- Add session management

### Agent Failures

The workflow includes error handling:
- Fallback responses on agent failures
- Graceful degradation
- Error logging and monitoring

## 🔮 Future Enhancements

### Planned Features

1. **Persistent State**: Database storage for user progress
2. **Advanced Routing**: ML-based agent selection
3. **A/B Testing**: Different learning paths
4. **Analytics**: Learning effectiveness metrics
5. **Personalization**: User-specific adaptations

### Integration Opportunities

1. **Real-time Updates**: WebSocket connections
2. **External APIs**: Language learning services
3. **Mobile Apps**: Native app integration
4. **Analytics Platforms**: Learning analytics

## 📚 Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Pydantic Graph](https://github.com/langchain-ai/pydantic-graph)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Contributing

When modifying the workflow:

1. Update the state models if needed
2. Maintain backward compatibility
3. Add comprehensive logging
4. Include error handling
5. Update this documentation

## 📞 Support

For questions or issues:
1. Check the logs for error details
2. Review the state transitions
3. Test individual components
4. Consult the API documentation at `/docs`

