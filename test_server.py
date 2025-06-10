#!/usr/bin/env python
"""Test script for Open-Meteo FastMCP server"""

import httpx
import json
import asyncio

async def test_server():
    """Test the server endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            print(f"Health check: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")
        print("Make sure the server is running: python open_meteo_server.py")
        return
    
    # Test get_forecast
    print("\nTesting get_forecast tool...")
    try:
        async with httpx.AsyncClient() as client:
            # FastMCP expects tool calls via specific endpoints
            payload = {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "hourly": "temperature_2m,precipitation",
                "models": "gfs_seamless"
            }
            # For FastMCP, we need to check the actual endpoint structure
            response = await client.post(f"{base_url}/tools/get_forecast", json=payload)
            print(f"Forecast response: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Location: lat={data.get('latitude')}, lon={data.get('longitude')}")
                print(f"Timezone: {data.get('timezone')}")
    except Exception as e:
        print(f"Forecast test failed: {e}")
    
    # Test get_historical_weather
    print("\nTesting get_historical_weather tool...")
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "start_date": "2023-01-01",
                "end_date": "2023-01-07",
                "hourly": "temperature_2m,precipitation",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "America/New_York"
            }
            response = await client.post(f"{base_url}/tools/get_historical_weather", json=payload)
            print(f"Historical weather response: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Location: lat={data.get('latitude')}, lon={data.get('longitude')}")
                print(f"Timezone: {data.get('timezone')}")
                if 'daily' in data:
                    print(f"Daily data points: {len(data['daily'].get('time', []))}")
    except Exception as e:
        print(f"Historical weather test failed: {e}")

if __name__ == "__main__":
    print("Open-Meteo FastMCP Server Test Script")
    print("=" * 40)
    asyncio.run(test_server())