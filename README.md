# Open Meteo Server

A simple FastMCP server that provides weather forecasts and historical weather data using the [Open-Meteo API](https://open-meteo.com/). This project exposes tools to fetch weather forecasts, historical weather data, and model comparisons for any location, suitable for integration with MCP clients or CLI tools.

## Features

- Fetch hourly weather forecasts for any latitude/longitude.
- Access historical weather data (reanalysis) from 1940 onwards.
- Compare weather forecasts from previous model runs.
- Select weather models and variables (e.g., temperature, precipitation).
- FastMCP stateless HTTP server, easy to run locally or integrate.

## Requirements

- Python 3.12+
- [httpx](https://www.python-httpx.org/) (>=0.28.1)
- [mcp](https://github.com/multiprocessio/mcp) (>=1.9.0, with CLI support)

All dependencies are listed in `pyproject.toml`.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd open-meteo-server
   ```

2. **(Recommended) Create a virtual environment:**
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Or, if using PEP 621/pyproject.toml:
   ```bash
   pip install .
   ```

## Usage

### Run the FastMCP Server

To run the server in HTTP mode (available at `127.0.0.1:8000`):

```bash
fastmcp run open_meteo_server.py --transport streamable-http
```

Or use the MCP Inspector for interactive testing:

```bash
mcp dev open_meteo_server.py:mcp
```

### Example: Fetch a Forecast

You can use the `get_forecast` tool via MCP or by extending the server. Example parameters:

- `latitude`: Latitude in decimal degrees (e.g., `40.7128`)
- `longitude`: Longitude in decimal degrees (e.g., `-74.0060`)
- `hourly`: Comma-separated list of variables (default: `temperature_2m`)
- `models`: Comma-separated list of models (default: `gfs_seamless`)

#### Testing with HTTP endpoints

After starting the server with `fastmcp run`, test the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

For testing the forecast tools, use the provided test script:

```bash
python test_server.py
```

### Example: Fetch a Historical Forecast

The `get_historical_forecast` tool fetches archived high-resolution weather model data for a given location and time range, using the [Open-Meteo Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api).

- `latitude`: Latitude in decimal degrees (e.g., `40.7128`)
- `longitude`: Longitude in decimal degrees (e.g., `-74.0060`)
- `start_date`: Start date in `YYYY-MM-DD` format
- `end_date`: End date in `YYYY-MM-DD` format
- `hourly`: Comma-separated list of variables (default: `temperature_2m`)
- `models`: Comma-separated list of models (default: `gfs_seamless`)

### Example: Fetch Previous Model Runs

The `get_previous_model_runs` tool retrieves weather forecasts from previous days to compare run-to-run performance, using the [Open-Meteo Previous Model Runs API](https://open-meteo.com/en/docs/previous-runs-api).

- `latitude`: Latitude in decimal degrees (e.g., `40.7128`)
- `longitude`: Longitude in decimal degrees (e.g., `-74.0060`)
- `start_date`: Start date in `YYYY-MM-DD` format
- `end_date`: End date in `YYYY-MM-DD` format
- `hourly`: Comma-separated list of variables (default: `temperature_2m`)
- `models`: Comma-separated list of models (default: `ecmwf_ifs025,gem_seamless,icon_seamless`)
- `previous_days`: Number of previous days to retrieve (1-7, default: 5)

### Example: Fetch Historical Weather Data

The `get_historical_weather` tool retrieves actual historical weather data (reanalysis) from 1940 onwards, using the [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).

- `latitude`: Latitude in decimal degrees (e.g., `40.7128`)
- `longitude`: Longitude in decimal degrees (e.g., `-74.0060`)
- `start_date`: Start date in `YYYY-MM-DD` format
- `end_date`: End date in `YYYY-MM-DD` format
- `hourly`: Comma-separated list of hourly variables (default: `temperature_2m`)
- `daily`: Comma-separated list of daily aggregated variables (optional)
- `temperature_unit`: Temperature unit (`celsius` or `fahrenheit`, default: `celsius`)
- `wind_speed_unit`: Wind speed unit (`kmh`, `ms`, `mph`, or `kn`, default: `kmh`)
- `precipitation_unit`: Precipitation unit (`mm` or `inch`, default: `mm`)
- `timezone`: Timezone (e.g., `GMT`, `America/New_York`, default: `GMT`)

## Development

- The main server logic is in `open_meteo_server.py`.
- `main.py` is a simple hello-world stub.
- Dependencies are managed via `pyproject.toml`.

## License

MIT (or specify your license here)
