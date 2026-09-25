import pytest
import time
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def demo_report_id():
    res = client.post("/api/reports/demo/duffy-rear")
    assert res.status_code == 200
    return res.json()["report_id"]

def test_final_analysis_structure(demo_report_id):
    res = client.get(f"/api/reports/{demo_report_id}/final-analysis")
    assert res.status_code == 200
    data = res.json()

    # Module 7 required sections
    assert "report_metadata" in data
    assert "executive_summary" in data
    assert "parameters" in data
    assert "crop_suitability" in data
    assert "provenance_audit" in data

    # Metadata checks
    meta = data["report_metadata"]
    assert meta["report_id"] == demo_report_id
    assert meta["report_name"]

    # Executive summary checks
    exec_summary = data["executive_summary"]
    assert exec_summary["overall_health_status"]
    assert len(exec_summary["key_findings"]) > 0
    assert len(exec_summary["priority_actions"]) > 0

    # Parameters checks
    params = data["parameters"]
    assert len(params) == 15
    for p in params:
        assert p["name"]
        assert p["status"]
        assert p["interpretation"]
        # Verify no undefined / placeholder text
        assert "undefined" not in p["name"].lower()
        assert "[object object]" not in p["interpretation"].lower()

    # Provenance audit checks
    prov = data["provenance_audit"]
    assert prov["total_grounded_citations"] > 0
    assert len(prov["guidelines_referenced"]) > 0

def test_pdf_generation_endpoint(demo_report_id):
    t0 = time.time()
    res = client.get(f"/api/reports/{demo_report_id}/pdf")
    elapsed = time.time() - t0

    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert "attachment; filename=" in res.headers.get("content-disposition", "")
    assert res.content.startswith(b"%PDF-")
    assert len(res.content) > 5000  # Valid ReportLab PDF
    assert elapsed < 3.0  # Must generate in under 3 seconds per Module 9
