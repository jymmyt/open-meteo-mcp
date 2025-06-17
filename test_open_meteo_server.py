"""Tests for the Open-Meteo FastMCP Server."""

import pytest
from unittest.mock import AsyncMock, patch
import json
from datetime import datetime, timedelta

# Test imports
from open_meteo_server import (
    mcp,
    get_forecast,
    get_historical_forecast,
    get_previous_model_runs,
    get_historical_weather,
    health_check,
    OPEN_METEO_API_BASE,
    OPEN_METEO_HISTORICAL_API_BASE,
    OPEN_METEO_PREVIOUS_RUNS_API_BASE,
    OPEN_METEO_ARCHIVE_API_BASE
)


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check_returns_ok(self):
        """Test that health check returns OK."""
        # Mock request object
        mock_request = AsyncMock()
        
        response = await health_check(mock_request)
        
        assert response.body == b"OK"
        assert response.status_code == 200


class TestGetForecastTool:
    """Tests for the get_forecast tool."""
    
    @pytest.mark.asyncio
    async def test_get_forecast_basic(self):
        """Test basic forecast request with minimal parameters."""
        mock_response = {
            "latitude": 52.52,
            "longitude": 13.419,
            "hourly": {
                "time": ["2024-01-01T00:00", "2024-01-01T01:00"],
                "temperature_2m": [10.5, 11.2]
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get = AsyncMock(return_value=AsyncMock(
                json=lambda: mock_response,
                raise_for_status=lambda: None
            ))
            
            result = await get_forecast(
                latitude=52.52,
                longitude=13.419
            )
            
            assert result == mock_response
            mock_instance.get.assert_called_once_with(
                OPEN_METEO_API_BASE,
                params={
                    "latitude": 52.52,
                    "longitude": 13.419,
                    "hourly": "temperature_2m",
                    "models": "gfs_seamless"
                }
            )
    
    @pytest.mark.asyncio
    async def test_get_forecast_with_multiple_variables(self):
        """Test forecast with multiple hourly variables and models."""
        mock_response = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "hourly": {
                "time": ["2024-01-01T00:00"],
                "temperature_2m": [5.5],
                "precipitation": [0.2],
                "wind_speed_10m": [15.5]
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get = AsyncMock(return_value=AsyncMock(
                json=lambda: mock_response,
                raise_for_status=lambda: None
            ))
            
            result = await get_forecast(
                latitude=40.7128,
                longitude=-74.0060,
                hourly="temperature_2m,precipitation,wind_speed_10m",
                models="gfs_seamless,ecmwf_ifs04"
            )
            
            assert result == mock_response
            mock_instance.get.assert_called_once_with(
                OPEN_METEO_API_BASE,
                params={
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "hourly": "temperature_2m,precipitation,wind_speed_10m",
                    "models": "gfs_seamless,ecmwf_ifs04"
                }
            )
    
    @pytest.mark.asyncio
    async def test_get_forecast_handles_api_error(self):
        """Test that forecast properly handles API errors."""
        from httpx import HTTPStatusError, Response, Request
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            
            # Create a mock response that will raise an error
            mock_request = Request("GET", "https://api.open-meteo.com/v1/forecast")
            mock_response = Response(500, request=mock_request)
            mock_instance.get = AsyncMock(return_value=mock_response)
            
            with pytest.raises(HTTPStatusError):
                await get_forecast(latitude=52.52, longitude=13.419)


class TestGetHistoricalForecastTool:
    """Tests for the get_historical_forecast tool."""
    
    @pytest.mark.asyncio
    async def test_get_historical_forecast_basic(self):
        """Test basic historical forecast request."""
        mock_response = {
            "latitude": 52.52,
            "longitude": 13.419,
            "hourly": {
                "time": ["2023-01-01T00:00", "2023-01-01T01:00"],
                "temperature_2m": [0.5, 1.2]
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get = AsyncMock(return_value=AsyncMock(
                json=lambda: mock_response,
                raise_for_status=lambda: None
            ))
            
            result = await get_historical_forecast(
                latitude=52.52,
                longitude=13.419,
                start_date="2023-01-01",
                end_date="2023-01-02"
            )
            
            assert result == mock_response
            mock_instance.get.assert_called_once_with(
                OPEN_METEO_HISTORICAL_API_BASE,
                params={
                    "latitude": 52.52,
                    "longitude": 13.419,
                    "start_date": "2023-01-01",
                    "end_date": "2023-01-02",
                    "hourly": "temperature_2m",
                    "models": "gfs_seamless"
                }
            )
    
    @pytest.mark.asyncio
    async def test_get_historical_forecast_with_custom_params(self):
        """Test historical forecast with custom parameters."""
        mock_response = {"data": "historical"}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get = AsyncMock(return_value=AsyncMock(
                json=lambda: mock_response,
                raise_for_status=lambda: None
            ))
            
            result = await get_historical_forecast(
                latitude=35.6762,
                longitude=139.6503,
                start_date="2023-06-01",
                end_date="2023-06-30",
                hourly="temperature_2m,precipitation,relative_humidity_2m",
                models="icon_seamless,jma_seamless"
            )
            
            assert result == mock_response
            mock_instance.get.assert_called_once_with(
                OPEN_METEO_HISTORICAL_API_BASE,
                params={
                    "latitude": 35.6762,
                    "longitude": 139.6503,
                    "start_date": "2023-06-01",
                    "end_date": "2023-06-30",
                    "hourly": "temperature_2m,precipitation,relative_humidity_2m",
                    "models": "icon_seamless,jma_seamless"
                }
            )


class TestGetPreviousModelRunsTool:
    """Tests for the get_previous_model_runs tool."""
    
    @pytest.mark.asyncio
    async def test_get_previous_model_runs_basic(self):
        """Test basic previous model runs request."""
        mock_response = {
            "latitude": 52.52,
            "longitude": 13.419,
            "hourly": {
                "time": ["2024-01-01T00:00"],
                "temperature_2m": [10.5],
                "temperature_2m_previous_day1": [9.8],
                "temperature_2m_previous_day2": [9.2]
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get = AsyncMock(return_value=AsyncMock(
                json=lambda: mock_response,
                raise_for_status=lambda: None
            ))
            
            result = await get_previous_model_runs(
                latitude=52.52,
                longitude=13.419,
                start_date="2024-01-01",
                end_date="2024-01-02"
            )
            
            assert result == mock_response
            # Check that previous day variants were added automatically
            call_args = mock_instance.get.call_args
            params = call_args[1]['params']
            assert "temperature_2m_previous_day1" in params['hourly']
            assert "temperature_2m_previous_day5" in params['hourly']
    
    @pytest.mark.asyncio
    async def test_get_previous_model_runs_with_precipitation(self):
        """Test that precipitation previous days are added automatically."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get = AsyncMock(return_value=AsyncMock(
                json=lambda: {"data": "test"},
                raise_for_status=lambda: None
            ))
            
            await get_previous_model_runs(
                latitude=40.7,
                longitude=-74.0,
                start_date="2024-01-01",
                end_date="2024-01-02",
                hourly="temperature_2m,precipitation,wind_speed_10m",
                previous_days=3
            )
            
            call_args = mock_instance.get.call_args
            params = call_args[1]['params']
            hourly_params = params['hourly']
            
            # Check base parameters are present
            assert "temperature_2m" in hourly_params
            assert "precipitation" in hourly_params
            assert "wind_speed_10m" in hourly_params
            
            # Check previous day variants for temperature and precipitation
            assert "temperature_2m_previous_day1" in hourly_params
            assert "temperature_2m_previous_day2" in hourly_params
            assert "temperature_2m_previous_day3" in hourly_params
            assert "precipitation_previous_day1" in hourly_params
            assert "precipitation_previous_day2" in hourly_params
            assert "precipitation_previous_day3" in hourly_params
            
            # Wind speed should not have previous day variants
            assert "wind_speed_10m_previous_day1" not in hourly_params
    
    @pytest.mark.asyncio
    async def test_get_previous_model_runs_invalid_days(self):
        """Test that invalid previous_days raises ValueError."""
        with pytest.raises(ValueError, match="previous_days must be between 1 and 7"):
            await get_previous_model_runs(
                latitude=52.52,
                longitude=13.419,
                start_date="2024-01-01",
                end_date="2024-01-02",
                previous_days=8
            )
        
        with pytest.raises(ValueError, match="previous_days must be between 1 and 7"):
            await get_previous_model_runs(
                latitude=52.52,
                longitude=13.419,
                start_date="2024-01-01",
                end_date="2024-01-02",
                previous_days=0
            )
    
    @pytest.mark.asyncio
    async def test_get_previous_model_runs_no_duplicate_params(self):
        """Test that already included previous day params aren't duplicated."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get = AsyncMock(return_value=AsyncMock(
                json=lambda: {"data": "test"},
                raise_for_status=lambda: None
            ))
            
            # Include some previous day params manually
            await get_previous_model_runs(
                latitude=40.7,
                longitude=-74.0,
                start_date="2024-01-01",
                end_date="2024-01-02",
                hourly="temperature_2m,temperature_2m_previous_day1,precipitation",
                previous_days=2
            )
            
            call_args = mock_instance.get.call_args
            params = call_args[1]['params']
            hourly_params = params['hourly']
            
            # Count occurrences of temperature_2m_previous_day1
            count = hourly_params.count("temperature_2m_previous_day1")
            assert count == 1  # Should appear only once


class TestGetHistoricalWeatherTool:
    """Tests for the get_historical_weather tool."""
    
    @pytest.mark.asyncio
    async def test_get_historical_weather_basic(self):
        """Test basic historical weather request."""
        mock_response = {
            "latitude": 52.52,
            "longitude": 13.419,
            "hourly": {
                "time": ["1980-01-01T00:00", "1980-01-01T01:00"],
                "temperature_2m": [-5.5, -5.2]
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get = AsyncMock(return_value=AsyncMock(
                json=lambda: mock_response,
                raise_for_status=lambda: None
            ))
            
            result = await get_historical_weather(
                latitude=52.52,
                longitude=13.419,
                start_date="1980-01-01",
                end_date="1980-01-02",
                hourly="temperature_2m"
            )
            
            assert result == mock_response
            mock_instance.get.assert_called_once_with(
                OPEN_METEO_ARCHIVE_API_BASE,
                params={
                    "latitude": 52.52,
                    "longitude": 13.419,
                    "start_date": "1980-01-01",
                    "end_date": "1980-01-02",
                    "hourly": "temperature_2m",
                    "temperature_unit": "celsius",
                    "wind_speed_unit": "kmh",
                    "precipitation_unit": "mm",
                    "timezone": "GMT"
                }
            )
    
    @pytest.mark.asyncio
    async def test_get_historical_weather_with_daily_data(self):
        """Test historical weather with daily aggregated data."""
        mock_response = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "daily": {
                "time": ["2000-06-01", "2000-06-02"],
                "temperature_2m_max": [28.5, 30.2],
                "precipitation_sum": [0.0, 5.5]
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get = AsyncMock(return_value=AsyncMock(
                json=lambda: mock_response,
                raise_for_status=lambda: None
            ))
            
            result = await get_historical_weather(
                latitude=40.7128,
                longitude=-74.0060,
                start_date="2000-06-01",
                end_date="2000-06-30",
                daily="temperature_2m_max,precipitation_sum",
                temperature_unit="celsius",
                timezone="America/New_York"
            )
            
            assert result == mock_response
            call_args = mock_instance.get.call_args
            params = call_args[1]['params']
            assert params["daily"] == "temperature_2m_max,precipitation_sum"
            assert params["timezone"] == "America/New_York"
            assert "hourly" not in params  # Should not include hourly when not specified
    
    @pytest.mark.asyncio
    async def test_get_historical_weather_with_custom_units(self):
        """Test historical weather with custom units."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get = AsyncMock(return_value=AsyncMock(
                json=lambda: {"data": "test"},
                raise_for_status=lambda: None
            ))
            
            await get_historical_weather(
                latitude=51.5074,
                longitude=-0.1278,
                start_date="2010-01-01",
                end_date="2010-12-31",
                hourly="temperature_2m,wind_speed_10m",
                temperature_unit="fahrenheit",
                wind_speed_unit="mph",
                precipitation_unit="inch"
            )
            
            call_args = mock_instance.get.call_args
            params = call_args[1]['params']
            assert params["temperature_unit"] == "fahrenheit"
            assert params["wind_speed_unit"] == "mph"
            assert params["precipitation_unit"] == "inch"


class TestPrompts:
    """Tests for the predefined prompts."""
    
    @pytest.mark.asyncio
    async def test_current_weather_prompt(self):
        """Test current weather prompt generation."""
        from open_meteo_server import current_weather
        
        prompt = await current_weather("New York")
        assert "New York" in prompt
        assert "temperature" in prompt
        assert "get_forecast" in prompt
    
    @pytest.mark.asyncio
    async def test_weather_forecast_prompt(self):
        """Test weather forecast prompt generation."""
        from open_meteo_server import weather_forecast
        
        prompt = await weather_forecast("London", days=5)
        assert "London" in prompt
        assert "5-day" in prompt
        assert "highs/lows" in prompt
    
    @pytest.mark.asyncio
    async def test_climate_analysis_prompt(self):
        """Test climate analysis prompt generation."""
        from open_meteo_server import climate_analysis
        
        prompt = await climate_analysis("Tokyo", 2000, 2020, 7)
        assert "Tokyo" in prompt
        assert "2000" in prompt
        assert "2020" in prompt
        assert "month 7" in prompt
        assert "get_historical_weather" in prompt


# Integration test example (requires actual API connection)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_forecast():
    """Integration test with real Open-Meteo API (skip in CI)."""
    try:
        result = await get_forecast(
            latitude=52.52,
            longitude=13.419,
            hourly="temperature_2m"
        )
        
        assert "latitude" in result
        assert "longitude" in result
        assert "hourly" in result
        assert "time" in result["hourly"]
        assert "temperature_2m" in result["hourly"]
    except Exception:
        pytest.skip("Open-Meteo API not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])