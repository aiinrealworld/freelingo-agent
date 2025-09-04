import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi.testclient import TestClient
from freelingo_agent.main import app

client = TestClient(app)


def test_workflow_test_endpoint():
    response = client.post("/api/workflow/test-workflow")
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["test_completed"] is True

    final = data["final_state"]
    assert final["feedback_generated"] is True
    assert final["plan_generated"] is True
    assert final["words_generated"] is True
    assert final["referee_decision"] is True


def test_workflow_end_session():
    response = client.post(
        "/api/workflow/end-session",
        params={"user_id": "test_user", "session_id": "dummy"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["session_ended"] is True
    assert data["final_agent"] == "REFEREE"


    assert data["feedback"] is not None
    assert data["plan"] is not None
    assert data["new_words"] is not None
    assert data["referee_decision"] is not None
