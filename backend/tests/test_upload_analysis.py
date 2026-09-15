from fastapi.testclient import TestClient
from backend.app.main import app

def test_upload_and_analyze_specific_content():
    client = TestClient(app)
    
    # 1. Upload balanced soil fixture
    with open("backend/tests/fixtures/balanced_soil.pdf", "rb") as f:
        up_res = client.post(
            "/api/reports/upload",
            files={"file": ("balanced_soil.pdf", f, "application/pdf")}
        )
    assert up_res.status_code == 200
    report_id = up_res.json()["report_id"]
    
    # 2. Analyze uploaded report
    ana_res = client.post(f"/api/reports/{report_id}/analyze")
    assert ana_res.status_code == 200
    data = ana_res.json()
    
    parameters = data.get("parameters", [])
    assert len(parameters) > 0
    
    print("\n--- ANALYZED UPLOADED PARAMETERS ---")
    for p in parameters:
        print(f"[{p['name']}] Status: {p['status']} | Value: {p['value']}")
        print(f"Explanation: {p['explanation']}")
        print(f"Why it matters: {p['why_it_matters']}\n")
        
        # Verify it is specific, not generic
        assert "this parameter reflects current soil nutrient availability" not in p["explanation"].lower()
        assert p["name"] in p["explanation"] or "pH" in p["explanation"]
        assert str(p["value"]) in p["explanation"]

if __name__ == "__main__":
    test_upload_and_analyze_specific_content()
