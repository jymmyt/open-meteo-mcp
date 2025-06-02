from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

# 1) Initialize your FastMCP server with a unique name
mcp = FastMCP("open-meteo",
    stateless_http=True,          # <-- enable stateless HTTP
    host="127.0.0.1",             # bind address
    port=8000)

# 2) Define the Open-Meteo base URL
OPEN_METEO_API_BASE = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_HISTORICAL_API_BASE = "https://historical-forecast-api.open-meteo.com/v1/forecast"
OPEN_METEO_PREVIOUS_RUNS_API_BASE = "https://previous-runs-api.open-meteo.com/v1/forecast"

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

# Prompts for common weather queries
@mcp.prompt()
async def current_weather(location: str) -> str:
    """Get current weather for a location.
    
    Args:
        location: City name or coordinates (e.g., 'New York' or '40.7,-74.0')
    """
    return f"What's the current weather in {location}? Include temperature, precipitation, wind speed, and cloud cover. Use the get_forecast tool with latitude and longitude coordinates."

@mcp.prompt()
async def weather_forecast(location: str, days: int = 7) -> str:
    """Get weather forecast for next few days.
    
    Args:
        location: City name or coordinates
        days: Number of days to forecast (default: 7)
    """
    return f"Give me a {days}-day weather forecast for {location}. Include daily highs/lows, precipitation chances, and general conditions. Use appropriate hourly variables."

@mcp.prompt()
async def severe_weather_check(location: str) -> str:
    """Check for severe weather conditions.
    
    Args:
        location: City name or coordinates
    """
    return f"Check {location} for any severe weather warnings or extreme conditions in the next 48 hours. Look for high winds, heavy precipitation, or extreme temperatures using wind_gusts_10m, precipitation_probability, and temperature extremes."

@mcp.prompt()
async def compare_models(location: str, variable: str) -> str:
    """Compare forecasts from different weather models.
    
    Args:
        location: City name or coordinates
        variable: Weather variable to compare (e.g., temperature, precipitation)
    """
    return f"Compare {variable} forecasts for {location} using different weather models (GFS, ECMWF, ICON). Show the differences between models by requesting multiple models in the models parameter."

@mcp.prompt()
async def historical_weather(location: str, start_date: str, end_date: str) -> str:
    """Get historical weather data for a date range.
    
    Args:
        location: City name or coordinates
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    return f"Show me the historical weather data for {location} from {start_date} to {end_date}. Include temperature trends and precipitation totals using the get_historical_forecast tool."

@mcp.prompt()
async def agriculture_forecast(location: str) -> str:
    """Get agriculture-relevant weather data.
    
    Args:
        location: Farm location or coordinates
    """
    return f"Provide agriculture-focused weather data for {location} including soil moisture (soil_moisture_0_to_1cm), evapotranspiration, precipitation, and temperature for the next 7 days."

@mcp.prompt()
async def solar_radiation(location: str, days: int = 7) -> str:
    """Get solar radiation forecast for solar energy planning.
    
    Args:
        location: Location or coordinates
        days: Number of days to forecast (default: 7)
    """
    return f"Show solar radiation forecast for {location} for the next {days} days. Include direct_radiation, diffuse_radiation, and shortwave_radiation values for solar energy planning."

@mcp.prompt()
async def travel_weather(destination: str, date: str) -> str:
    """Get weather conditions for travel planning.
    
    Args:
        destination: Travel destination
        date: Travel date (YYYY-MM-DD)
    """
    return f"What will the weather be like in {destination} on {date}? Include temperature range, precipitation chances, visibility, and general conditions for travel planning."

@mcp.tool()
async def get_forecast(
    latitude: float,
    longitude: float,
    hourly: str = "temperature_2m",
    models: str = "gfs_seamless"
) -> dict[str, Any]:
    """Fetch hourly forecast for a location.

    Args:
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.
        hourly: Comma-separated list of hourly variables (e.g., 'temperature_2m,precipitation').
        models: Comma-separated list of models to use for the forecast.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": hourly
        # you can add 'timezone', 'daily', etc. as needed
    }
    if models:
        params["models"] = models
        
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPEN_METEO_API_BASE, params=params)
        resp.raise_for_status()
        return resp.json()  # returns raw JSON for client consumption

@mcp.tool()
async def get_historical_forecast(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    hourly: str = "temperature_2m",
    models: str = "gfs_seamless"
) -> dict[str, Any]:
    """Fetch historical hourly forecast for a location.

    Args:
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        hourly: Comma-separated list of hourly variables (e.g., 'temperature_2m,precipitation').
        models: Comma-separated list of models to use for the forecast.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": hourly
    }
    if models:
        params["models"] = models
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPEN_METEO_HISTORICAL_API_BASE, params=params)
        resp.raise_for_status()
        return resp.json()  # returns raw JSON for client consumption

@mcp.tool()
async def get_previous_model_runs(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    hourly: str = "temperature_2m",
    models: str = "ecmwf_ifs025,gem_seamless,icon_seamless",  # ✅ Better models
    previous_days: int = 5                                     # ✅ User-controlled
) -> dict[str, Any]:
    """Fetch previous model runs for a location.

    Args:
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        hourly: Comma-separated list of hourly variables (e.g., 'temperature_2m,precipitation').
        models: Comma-separated list of models to use for the forecast.
        previous_days: Number of previous days to retrieve (1-7, default: 5).
    """
    
    # Validate previous_days parameter
    if previous_days < 1 or previous_days > 7:
        raise ValueError("previous_days must be between 1 and 7")
    
    # Parse the hourly parameters to automatically add previous day variants
    hourly_params = []
    base_params = [param.strip() for param in hourly.split(',')]
    
    for param in base_params:
        # Add the base parameter
        hourly_params.append(param)
        
        # For temperature and precipitation, automatically add previous day variants
        # But only if they're not already included in the hourly string
        if param in ["temperature_2m", "precipitation"] and not any(f"{param}_previous_day" in h for h in base_params):
            for day in range(1, previous_days + 1):
                hourly_params.append(f"{param}_previous_day{day}")
    
    # Build parameters for the API call
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(hourly_params)
        # NOTE: forecast_days and past_days are NOT used in Previous Runs API
    }
    
    if models:
        params["models"] = models
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPEN_METEO_PREVIOUS_RUNS_API_BASE, params=params)
        resp.raise_for_status()
        return resp.json()

if __name__ == "__main__":
    # Run over stdio by default; clients can connect via CLI or any MCP transport
    mcp.run(transport="stdio")