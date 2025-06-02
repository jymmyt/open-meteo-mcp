# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation
```bash
# Create and activate virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install .
```

### Running the Server
```bash
# Run FastMCP server in HTTP mode
fastmcp run open_meteo_server.py --transport streamable-http

# The server will be available at http://127.0.0.1:8000
```

### Testing the Server

1. **Using MCP Inspector (Recommended):**
   ```bash
   mcp dev open_meteo_server.py:mcp
   ```
   This opens an interactive inspector where you can test all tools.

2. **Using HTTP endpoints:**
   After starting the server with `fastmcp run`, you can test:
   ```bash
   # Health check
   curl http://127.0.0.1:8000/health
   
   # Use the test script for testing tools
   python test_server.py
   ```

## Architecture Overview

This is a FastMCP server that provides weather forecast data from the Open-Meteo API. The architecture is straightforward:

1. **FastMCP Server (`open_meteo_server.py`)**: The main server implementation using FastMCP framework
   - Configured for stateless HTTP mode on `127.0.0.1:8000`
   - Exposes three main tools:
     - `get_forecast`: Fetches current weather forecasts
     - `get_historical_forecast`: Retrieves historical forecast data
     - `get_previous_model_runs`: Gets previous model run comparisons
   - Custom endpoints:
     - `/health`: Health check endpoint
   - Pre-defined prompts (accessible via MCP prompt system) for common weather queries

2. **API Integration**: The server acts as a proxy to three Open-Meteo API endpoints:
   - Standard forecast API: `https://api.open-meteo.com/v1/forecast`
   - Historical forecast API: `https://historical-forecast-api.open-meteo.com/v1/forecast`
   - Previous runs API: `https://previous-runs-api.open-meteo.com/v1/forecast`

3. **Tool Parameters**:
   - All tools require `latitude` and `longitude`
   - Historical and previous runs additionally require `start_date` and `end_date`
   - Optional parameters include `hourly` (weather variables) and `models` (forecast models)
   - Previous runs tool automatically adds previous day variants for temperature and precipitation

The server uses `httpx` for async HTTP requests and returns raw JSON responses from the Open-Meteo API to clients.

## Available Hourly Variables

The following hourly weather variables can be requested (comma-separated in the `hourly` parameter):

### Basic Weather
- `temperature_2m` - Air temperature at 2 meters (°C)
- `relative_humidity_2m` - Relative humidity at 2 meters (%)
- `dew_point_2m` - Dew point temperature at 2 meters (°C)
- `apparent_temperature` - Apparent "feels like" temperature (°C)
- `weather_code` - WMO weather interpretation code

### Precipitation
- `precipitation` - Total precipitation (rain + snow) (mm)
- `rain` - Rain (mm)
- `showers` - Showers (mm)
- `snowfall` - Snowfall (cm)
- `precipitation_probability` - Precipitation probability (%)
- `snow_depth` - Snow depth on ground (m)

### Wind
- `wind_speed_10m`, `wind_speed_80m`, `wind_speed_120m`, `wind_speed_180m` - Wind speed at heights (km/h)
- `wind_direction_10m`, `wind_direction_80m`, `wind_direction_120m`, `wind_direction_180m` - Wind direction (°)
- `wind_gusts_10m` - Wind gusts at 10 meters (km/h)

### Pressure & Clouds
- `pressure_msl` - Mean sea level pressure (hPa)
- `surface_pressure` - Surface pressure (hPa)
- `cloud_cover` - Total cloud cover (%)
- `cloud_cover_low`, `cloud_cover_mid`, `cloud_cover_high` - Cloud cover by altitude (%)

### Radiation & Energy
- `shortwave_radiation` - Shortwave solar radiation (W/m²)
- `direct_radiation` - Direct solar radiation (W/m²)
- `diffuse_radiation` - Diffuse solar radiation (W/m²)
- `global_tilted_irradiance` - Global tilted irradiance (W/m²)

### Soil & Agriculture
- `soil_temperature_0cm`, `soil_temperature_6cm`, `soil_temperature_18cm`, `soil_temperature_54cm` - Soil temperature (°C)
- `soil_moisture_0_to_1cm`, `soil_moisture_1_to_3cm`, `soil_moisture_3_to_9cm`, `soil_moisture_9_to_27cm`, `soil_moisture_27_to_81cm` - Volumetric soil moisture (m³/m³)
- `evapotranspiration` - Evapotranspiration (mm)
- `et0_fao_evapotranspiration` - Reference evapotranspiration (mm)
- `vapour_pressure_deficit` - Vapor pressure deficit (kPa)

### Other
- `cape` - Convective available potential energy (J/kg)
- `freezing_level_height` - Altitude of 0°C isotherm (m)
- `visibility` - Visibility (m)
- `is_day` - Daylight indicator (0 or 1)

## Available Weather Models

The following weather models can be requested (comma-separated in the `models` parameter):

### Global Models
- `gfs_seamless`, `gfs_global` - NCEP GFS
- `ecmwf_ifs04` - ECMWF IFS 0.4°
- `ecmwf_aifs025` - ECMWF AIFS 0.25°
- `cma_grapes_global` - CMA GRAPES Global
- `bom_access_global` - BOM ACCESS-G
- `gem_seamless`, `gem_global` - Canadian GEM Global
- `icon_seamless`, `icon_global` - DWD ICON Global
- `jma_seamless`, `jma_gsm` - JMA GSM
- `ncep_gfs_graphcast025` - GFS GraphCast

### Regional Models
- `ncep_hrrr` - NCEP HRRR (US)
- `ncep_nbm` - NCEP NBM (US)
- `icon_eu`, `icon_d2` - DWD ICON Europe/Germany
- `gem_regional`, `gem_hrdps` - Canadian GEM Regional/HRDPS
- `meteo_france_seamless`, `meteo_france_arpege_world`, `meteo_france_arpege_europe`, `meteo_france_arome_france` - Météo-France models
- `arpae_cosmo_seamless`, `arpae_cosmo_2i`, `arpae_cosmo_5m` - ARPAE COSMO (Italy)
- `metno_nordic` - MET Norway Nordic
- `knmi_harmonie_arome_netherlands` - KNMI Harmonie (Netherlands)
- `dmi_harmonie_arome_europe` - DMI Harmonie (Europe)
- `jma_msm` - JMA MSM (Japan)
- `kma_seamless`, `kma_ldps`, `kma_gdps` - KMA models (Korea)

### Specialized
- `ukmo_seamless`, `ukmo_global_deterministic_10km`, `ukmo_uk_deterministic_2km` - UK Met Office models

Note: Not all variables are available for all models. Check the Open-Meteo documentation for specific model capabilities.

## Available Prompts

The server provides pre-defined prompts via the MCP prompt system for common weather queries:

- **current_weather(location)**: Get current weather conditions for any location
- **weather_forecast(location, days)**: Multi-day weather forecast with highs/lows and conditions
- **severe_weather_check(location)**: Check for extreme weather warnings
- **compare_models(location, variable)**: Compare forecasts from different weather models
- **historical_weather(location, start_date, end_date)**: Retrieve historical weather data for a date range
- **agriculture_forecast(location)**: Agriculture-focused weather data (soil moisture, evapotranspiration)
- **solar_radiation(location, days)**: Solar radiation forecast for energy planning
- **travel_weather(destination, date)**: Weather conditions for travel planning

These prompts automatically generate appropriate queries that utilize the server's tools with the correct parameters. They can be accessed through any MCP client that supports the prompt system.