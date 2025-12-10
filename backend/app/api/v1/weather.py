from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import httpx
from app.core.config import settings
import logging
import asyncio
import json
from app.infra.redis import redis_client
from app.services.service_manager import get_llm_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Get LLM service singleton
llm_service = get_llm_service()

CACHE_EXPIRY = 600  # 10 minutes

async def get_cached_weather(city: str, country_code: str = None):
    """Get cached weather data"""
    try:
        key = f"weather:{city}:{country_code or ''}"
        cached = await redis_client.get(key)
        if cached:
            logger.info(f"Returning cached weather for {key}")
            return json.loads(cached)
        logger.info(f"No cache found for {key}")
        return None
    except Exception as e:
        logger.error(f"Error getting cached weather: {e}")
        return None

async def set_cached_weather(city: str, data: dict, country_code: str = None):
    """Set cached weather data"""
    try:
        key = f"weather:{city}:{country_code or ''}"
        await redis_client.setex(key, CACHE_EXPIRY, json.dumps(data))
        logger.info(f"Cached weather for {key}")
    except Exception as e:
        logger.error(f"Error setting cached weather: {e}")

async def fetch_and_cache_weather(city: str, country_code: str = None):
    """Fetch weather data and cache it"""
    try:
        # Fetch current weather
        weather_data = await fetch_openweather_data(city, country_code, "weather")

        # Fetch 5-day forecast
        forecast_data = await fetch_openweather_data(city, country_code, "forecast")

        # Generate AI insights
        ai_insights = await generate_ai_insights(weather_data, forecast_data)

        # Process current weather
        current_weather = {
            "city": weather_data["name"],
            "country": weather_data["sys"]["country"],
            "temperature": weather_data["main"]["temp"],
            "feels_like": weather_data["main"]["feels_like"],
            "temp_min": weather_data["main"]["temp_min"],
            "temp_max": weather_data["main"]["temp_max"],
            "description": weather_data["weather"][0]["description"],
            "humidity": weather_data["main"]["humidity"],
            "pressure": weather_data["main"]["pressure"],
            "wind_speed": weather_data["wind"]["speed"] * 3.6,  # Convert m/s to km/h
            "wind_deg": weather_data["wind"].get("deg", 0),
            "cloudiness": weather_data["clouds"]["all"],
            "visibility": weather_data.get("visibility", 10000) / 1000,  # Convert to km
            "sunrise": weather_data["sys"]["sunrise"],
            "sunset": weather_data["sys"]["sunset"],
            "timezone": weather_data["timezone"],
            "icon": weather_data["weather"][0]["main"],
        }

        # Process 5-day forecast (one entry per day)
        forecast_list = []
        seen_dates = set()

        for item in forecast_data["list"]:
            date = item["dt_txt"].split(" ")[0]
            if date not in seen_dates and len(forecast_list) < 5:
                seen_dates.add(date)
                forecast_list.append(
                    {
                        "date": date,
                        "temp_max": item["main"]["temp_max"],
                        "temp_min": item["main"]["temp_min"],
                        "description": item["weather"][0]["description"],
                        "icon": item["weather"][0]["main"],
                    }
                )

        data = {
            "weather": current_weather,
            "forecast": forecast_list,
            "ai_insights": ai_insights,
        }

        await set_cached_weather(city, data, country_code)
        return data

    except Exception as e:
        logger.error(f"Error fetching and caching weather: {e}")
        return None



async def fetch_openweather_data(city: str, country_code: str = None, endpoint: str = "weather"):
    """Fetch data from OpenWeatherMap API"""
    api_key = settings.OPENWEATHER_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=500, detail="OpenWeatherMap API key not configured"
        )

    base_url = "https://api.openweathermap.org/data/2.5"
    url = f"{base_url}/{endpoint}"
    
    # Build query string with optional country code
    query = f"{city},{country_code}" if country_code else city
    params = {"q": query, "appid": api_key, "units": "metric"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            
            # Check if response is JSON
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                logger.error(f"Non-JSON response from weather API: {response.text[:200]}")
                raise HTTPException(
                    status_code=500, 
                    detail="Weather API returned invalid response. Please check API key."
                )
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"City '{city}' not found")
            elif e.response.status_code == 401:
                raise HTTPException(status_code=500, detail="Invalid weather API key")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Weather API error: {e.response.text[:200]}",
            )
        except httpx.RequestError as e:
            logger.error(f"Request error fetching weather: {e}")
            raise HTTPException(
                status_code=503, detail="Unable to reach weather service"
            )
        except Exception as e:
            logger.error(f"Unexpected error in weather API: {e}")
            raise HTTPException(
                status_code=500, detail=f"Weather service error: {str(e)}"
            )


async def generate_ai_insights(weather_data: dict, forecast_data: dict) -> dict:
    """Generate AI insights based on weather data"""
    try:
        # Get LLM instance
        llm, _ = llm_service.get_llm(temperature=0.7)

        # Prepare weather summary for LLM
        current = weather_data["main"]
        weather_desc = weather_data["weather"][0]["description"]
        temp = current["temp"]
        feels_like = current["feels_like"]
        humidity = current["humidity"]
        wind_speed = weather_data["wind"]["speed"]

        # Create prompt for AI insights
        prompt = f"""Based on the following weather conditions, provide helpful insights:

Current Weather:
- Temperature: {temp}°C (feels like {feels_like}°C)
- Conditions: {weather_desc}
- Humidity: {humidity}%
- Wind Speed: {wind_speed} km/h

Please provide:
1. A brief weather analysis (2-3 sentences)
2. Three recommended outdoor activities suitable for this weather
3. Three health and safety tips
4. Three outfit/clothing suggestions

Format your response as JSON with the following structure:
{{
  "analysis": "your analysis here",
  "activities": ["activity 1", "activity 2", "activity 3"],
  "health_tips": ["tip 1", "tip 2", "tip 3"],
  "outfit_suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"]
}}"""

        # Invoke LLM
        response = await llm.ainvoke(prompt)
        
        # Parse response
        import json
        
        # Try to extract JSON from response
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Find JSON in response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            insights = json.loads(json_str)
        else:
            # Fallback if JSON parsing fails
            insights = {
                "analysis": f"The weather is {weather_desc} with a temperature of {temp}°C. {_get_generic_analysis(temp, weather_desc)}",
                "activities": _get_generic_activities(temp, weather_desc),
                "health_tips": _get_generic_health_tips(temp, weather_desc),
                "outfit_suggestions": _get_generic_outfit_suggestions(temp, weather_desc),
            }

        return insights

    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        # Return generic insights as fallback
        return {
            "analysis": f"Current conditions show {weather_desc} with a temperature of {temp}°C.",
            "activities": _get_generic_activities(temp, weather_desc),
            "health_tips": _get_generic_health_tips(temp, weather_desc),
            "outfit_suggestions": _get_generic_outfit_suggestions(temp, weather_desc),
        }


def _get_generic_analysis(temp: float, desc: str) -> str:
    """Generate generic weather analysis"""
    if temp < 10:
        return "It's quite cold outside. Bundle up and stay warm!"
    elif temp < 20:
        return "Pleasant moderate temperatures. Great for outdoor activities!"
    else:
        return "Warm weather conditions. Stay hydrated and protect yourself from the sun!"


def _get_generic_activities(temp: float, desc: str) -> list:
    """Generate generic activity suggestions"""
    if temp < 10:
        return [
            "Visit indoor museums or galleries",
            "Enjoy hot beverages at a cozy café",
            "Indoor sports or gym activities",
        ]
    elif temp < 20:
        return [
            "Go for a nature walk or hike",
            "Outdoor photography session",
            "Visit local parks or gardens",
        ]
    else:
        return [
            "Swimming or water sports",
            "Outdoor picnic in the shade",
            "Early morning or evening jogging",
        ]


def _get_generic_health_tips(temp: float, desc: str) -> list:
    """Generate generic health tips"""
    if temp < 10:
        return [
            "Dress in layers to maintain body warmth",
            "Protect extremities with gloves and warm socks",
            "Stay active to keep circulation going",
        ]
    elif temp < 20:
        return [
            "Stay hydrated throughout the day",
            "Light layers for temperature changes",
            "Good time for outdoor exercise",
        ]
    else:
        return [
            "Drink plenty of water to stay hydrated",
            "Use sunscreen with SPF 30 or higher",
            "Avoid prolonged sun exposure during peak hours",
        ]


def _get_generic_outfit_suggestions(temp: float, desc: str) -> list:
    """Generate generic outfit suggestions"""
    if temp < 10:
        return [
            "Heavy winter coat or jacket",
            "Warm sweater and thermal layers",
            "Boots and warm accessories (scarf, hat, gloves)",
        ]
    elif temp < 20:
        return [
            "Light jacket or cardigan",
            "Long sleeves with comfortable pants",
            "Comfortable walking shoes",
        ]
    else:
        return [
            "Light, breathable fabrics",
            "Shorts or light pants with t-shirt",
            "Sunglasses and sun hat recommended",
        ]


@router.get("/current")
async def get_current_weather(
    city: str = Query(..., description="City name"),
    country_code: str = Query(None, description="ISO 3166 country code (e.g., US, IN, GB)")
):
    """Get current weather with AI insights for a city"""
    try:
        # Try to get cached data
        cached_data = await get_cached_weather(city, country_code)
        if cached_data:
            return cached_data

        # No cache, fetch and cache
        data = await fetch_and_cache_weather(city, country_code)
        if data:
            return data
        else:
            raise HTTPException(status_code=503, detail="Unable to fetch weather data")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_weather: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/forecast")
async def get_forecast(
    city: str = Query(..., description="City name"),
    country_code: str = Query(None, description="ISO 3166 country code (e.g., US, IN, GB)")
):
    """Get 5-day weather forecast for a city"""
    try:
        forecast_data = await fetch_openweather_data(city, country_code, "forecast")

        # Process forecast data
        forecast_list = []
        seen_dates = set()

        for item in forecast_data["list"]:
            date = item["dt_txt"].split(" ")[0]
            if date not in seen_dates:
                seen_dates.add(date)
                forecast_list.append(
                    {
                        "date": date,
                        "temp_max": item["main"]["temp_max"],
                        "temp_min": item["main"]["temp_min"],
                        "description": item["weather"][0]["description"],
                        "icon": item["weather"][0]["main"],
                        "humidity": item["main"]["humidity"],
                        "wind_speed": item["wind"]["speed"] * 3.6,
                    }
                )

        return {"city": forecast_data["city"]["name"], "forecast": forecast_list}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_forecast: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
