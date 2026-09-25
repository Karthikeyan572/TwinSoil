import pytest
import time
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def demo_report_id():
    # Load demo report
    res = client.post("/api/reports/demo/duffy-rear")
    assert res.status_code == 200
    return res.json()["report_id"]

def test_chat_greeting_intent(demo_report_id):
    t0 = time.time()
    res = client.post(f"/api/reports/{demo_report_id}/ask", json={"question": "hi"})
    elapsed = time.time() - t0
    
    assert res.status_code == 200
    data = res.json()
    assert "SoilTwin AI" in data["answer"]
    assert len(data["citations"]) == 0
    assert data["provider"] == "SoilTwin Assistant"
    assert elapsed < 0.2  # Instant response (<200ms)

def test_chat_off_topic_intent(demo_report_id):
    t0 = time.time()
    res = client.post(f"/api/reports/{demo_report_id}/ask", json={"question": "who won the world cup?"})
    elapsed = time.time() - t0
    
    assert res.status_code == 200
    data = res.json()
    assert "specialized strictly in soil health" in data["answer"]
    assert len(data["citations"]) == 0
    assert data["provider"] == "SoilTwin Assistant"
    assert elapsed < 0.2  # Instant response (<200ms)

def test_chat_report_lookup(demo_report_id):
    res = client.post(f"/api/reports/{demo_report_id}/ask", json={"question": "what is my soil pH?"})
    assert res.status_code == 200
    data = res.json()
    assert "4.5" in data["answer"]  # Exact measured value from Duffy Rear
    assert "pH" in data["answer"]
    assert "BELOW OPTIMUM" in data["answer"] or "below optimum" in data["answer"].lower()
    assert data["provider"] == "SoilTwin Report Database"

def test_chat_interpretation(demo_report_id):
    res = client.post(f"/api/reports/{demo_report_id}/ask", json={"question": "how do I raise my pH from 4.5?"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["answer"]) > 20
    assert len(data["citations"]) > 0
    for cit in data["citations"]:
        assert len(cit["text"]) <= 250  # Concise snippet, not a 1000-char dump
        assert cit["source"]
