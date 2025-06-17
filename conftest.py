"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient for testing API calls."""
    mock_response = AsyncMock()
    mock_response.json = lambda: {"test": "data"}
    mock_response.raise_for_status = lambda: None
    
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.post = AsyncMock(return_value=mock_response)
    
    return mock_client


@pytest.fixture
def sample_forecast_response():
    """Sample forecast API response."""
    return {
        "latitude": 52.52,
        "longitude": 13.419,
        "generationtime_ms": 0.123,
        "utc_offset_seconds": 0,
        "timezone": "GMT",
        "timezone_abbreviation": "GMT",
        "elevation": 38.0,
        "hourly_units": {
            "time": "iso8601",
            "temperature_2m": "°C",
            "precipitation": "mm"
        },
        "hourly": {
            "time": [
                "2024-01-01T00:00",
                "2024-01-01T01:00",
                "2024-01-01T02:00"
            ],
            "temperature_2m": [10.5, 10.8, 11.2],
            "precipitation": [0.0, 0.1, 0.0]
        }
    }


@pytest.fixture
def sample_historical_response():
    """Sample historical weather API response."""
    return {
        "latitude": 52.52,
        "longitude": 13.419,
        "generationtime_ms": 0.456,
        "utc_offset_seconds": 0,
        "timezone": "GMT",
        "timezone_abbreviation": "GMT",
        "elevation": 38.0,
        "daily_units": {
            "time": "iso8601",
            "temperature_2m_max": "°C",
            "temperature_2m_min": "°C",
            "precipitation_sum": "mm"
        },
        "daily": {
            "time": ["2000-01-01", "2000-01-02", "2000-01-03"],
            "temperature_2m_max": [2.5, 3.1, 1.8],
            "temperature_2m_min": [-2.1, -1.5, -3.2],
            "precipitation_sum": [0.0, 2.5, 0.8]
        }
    }


@pytest.fixture
def mock_starlette_request():
    """Mock Starlette Request object."""
    request = MagicMock()
    request.method = "GET"
    request.url = MagicMock()
    request.url.path = "/health"
    request.headers = {}
    return request