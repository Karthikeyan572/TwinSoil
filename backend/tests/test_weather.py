import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings

client = TestClient(app)

def test_weather_missing_location():
    res = client.get("/api/weather/current")
    assert res.status_code == 200
    data = res.json()
    assert data["available"] is False
    assert "required" in data["message"].lower()

def test_weather_api_key_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "OPENWEATHER_API_KEY", "")
    res = client.get("/api/weather/current?lat=11.0&lon=77.0")
    assert res.status_code == 200
    data = res.json()
    assert data["available"] is False
    assert "not configured" in data["message"].lower()

def test_weather_live_mocked(monkeypatch):
    monkeypatch.setattr(settings, "OPENWEATHER_API_KEY", "test_key_123")
    
    mock_weather_response = {
        "name": "Coimbatore",
        "sys": {"country": "IN"},
        "main": {
            "temp": 28.5,
            "humidity": 65
        },
        "rain": {
            "1h": 2.4
        },
        "dt": 1727280000
    }
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"content-type": "application/json"}
    mock_resp.json.return_value = mock_weather_response

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        res = client.get("/api/weather/current?lat=11.0168&lon=76.9558")
        assert res.status_code == 200
        data = res.json()
        assert data["available"] is True
        assert data["temperature"] == 28.5
        assert data["humidity"] == 65
        assert data["rainfall"] == 2.4
        assert "Coimbatore" in data["location"]
        assert "OpenWeather" in data["source"]
