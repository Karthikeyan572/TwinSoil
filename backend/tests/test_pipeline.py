import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.extraction.soil_schema import normalize_parameter_name, SoilProfile, SoilParameter
from backend.app.validation.numerical_validator import compute_numerical_status, validate_soil_profile_numerics
from backend.app.rag.retriever import parameter_retriever
from backend.app.agents.crop_agent import crop_agent
from backend.app.agents.critic_agent import critic_agent

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "SoilTwin AI"

def test_canonical_parameter_normalization():
    assert normalize_parameter_name("soil pH") == "pH"
    assert normalize_parameter_name("Organic Matter %") == "Organic Matter"
    assert normalize_parameter_name("Potassium") == "K"
    assert normalize_parameter_name("Cation Exchange Capacity") == "CEC"
    assert normalize_parameter_name("NonExistentXYZ") is None

def test_deterministic_numerical_validation():
    # Below optimum
    assert compute_numerical_status(4.5, 6.0, 6.8) == "BELOW_OPTIMUM"
    # Within optimum
    assert compute_numerical_status(6.5, 6.0, 6.8) == "WITHIN_RANGE"
    # Above optimum
    assert compute_numerical_status(7.5, 6.0, 6.8) == "ABOVE_OPTIMUM"
    # Single bounded range (>10)
    assert compute_numerical_status(15.0, 10.0, None) == "WITHIN_RANGE"
    assert compute_numerical_status(8.0, 10.0, None) == "BELOW_OPTIMUM"
    # Single bounded range (<75)
    assert compute_numerical_status(94.0, None, 75.0) == "ABOVE_OPTIMUM"
    assert compute_numerical_status(50.0, None, 75.0) == "WITHIN_RANGE"

def test_crop_agent_missing_inputs_safety():
    # When environmental inputs are missing, Crop Agent must return INSUFFICIENT_INPUTS and NEVER fabricate
    res = crop_agent.check_inputs_and_predict(
        provided_inputs={"N": 80, "P": 40, "K": 40},
        extracted_parameters={"pH": 6.5}
    )
    assert res["status"] == "INSUFFICIENT_INPUTS"
    assert "temperature" in res["missing_inputs"]
    assert "humidity" in res["missing_inputs"]
    assert "rainfall" in res["missing_inputs"]

def test_crop_agent_prediction_with_full_inputs():
    res = crop_agent.check_inputs_and_predict(
        provided_inputs={
            "N": 80, "P": 47, "K": 40,
            "temperature": 24.0, "humidity": 80.0,
            "ph": 6.5, "rainfall": 220.0
        }
    )
    assert res["status"] == "READY"
    assert len(res["predictions"]) > 0
    top = res["predictions"][0]
    assert "crop" in top
    assert "probability" in top
    assert "disclaimer" in top
    assert "not a guaranteed yield" in top["disclaimer"]

def test_critic_agent_validation():
    dummy_param = {
        "name": "pH",
        "value": 4.5,
        "status": "BELOW_OPTIMUM",
        "explanation": "Measured pH is below optimum laboratory range.",
        "evidence": [{"source": "Penn State Extension Soil Guide (2023)"}]
    }
    chunks = [{"source": "Penn State Extension Soil Guide (2023)", "content": "Soil pH ..."}]
    critic_res = critic_agent.validate_parameter_interpretation(dummy_param, chunks, retry_count=0)
    assert critic_res["status"] == "PASS"

def test_demo_endpoint_end_to_end():
    res = client.post("/api/reports/demo/duffy-rear")
    assert res.status_code == 200
    data = res.json()
    assert "report_id" in data
    assert data["summary"]["overall_observation"] == "Needs Attention"
    assert len(data["parameters"]) == 15
    assert len(data["pipeline_steps"]) > 0
