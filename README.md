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

## 🔄 **LangGraph Workflow**

The application implements a learning workflow using LangGraph:

1. **DIALOGUE** → User initiates conversation
2. **FEEDBACK** → Generate feedback after session
3. **PLANNER** → Create learning plan
4. **NEW_WORDS** → Introduce vocabulary
5. **REFEREE** → Evaluate and route to next step

## 📚 **API Endpoints**

- `POST /api/workflow/start-session` - Start learning session
- `POST /api/workflow/end-session` - End session and trigger workflow
- `POST /api/workflow/test-workflow` - Test complete workflow
- `GET /api/health` - Health check

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