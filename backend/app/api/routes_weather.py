import os
import httpx
from typing import Optional
from fastapi import APIRouter, Query
from backend.app.config import settings

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/current")
async def get_current_weather(
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    city: Optional[str] = Query(None, description="City name")
):
    if (lat is None or lon is None) and not city:
        return {
            "available": False,
            "message": "Location coordinates or city name are required to fetch weather."
        }

    api_key = settings.OPENWEATHER_API_KEY.strip()
    if not api_key:
        return {
            "available": False,
            "message": "OpenWeather API key is not configured on the server. You can enter temperature, humidity, and rainfall manually."
        }

    query_params = {
        "appid": api_key,
        "units": "metric"
    }
    if lat is not None and lon is not None:
        query_params["lat"] = lat
        query_params["lon"] = lon
    elif city:
        query_params["q"] = city

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params=query_params
            )
            
            if resp.status_code != 200:
                err_data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                err_msg = err_data.get("message", f"OpenWeather returned HTTP {resp.status_code}")
                return {
                    "available": False,
                    "message": f"Weather lookup failed: {err_msg}"
                }
            
            data = resp.json()
            main = data.get("main", {})
            temp = main.get("temp")
            humidity = main.get("humidity")
            rain_obj = data.get("rain", {})
            # OpenWeather gives rainfall in mm for past 1h or 3h if raining
            rain_mm = rain_obj.get("1h", rain_obj.get("3h", 0.0))
            
            city_name = data.get("name", "")
            sys_obj = data.get("sys", {})
            country = sys_obj.get("country", "")
            location_str = f"{city_name}, {country}" if city_name and country else (city_name or "Detected Location")
            
            return {
                "available": True,
                "temperature": round(temp, 1) if temp is not None else None,
                "humidity": round(humidity, 1) if humidity is not None else None,
                "rainfall": round(float(rain_mm), 1) if rain_mm is not None else 0.0,
                "location": location_str,
                "timestamp": data.get("dt"),
                "source": "OpenWeather API",
                "disclaimer": "Live weather reflects current ambient conditions. Crop recommendations factor in seasonal growing conditions."
            }
    except Exception as exc:
        return {
            "available": False,
            "message": f"Could not reach weather service: {str(exc)}"
        }
