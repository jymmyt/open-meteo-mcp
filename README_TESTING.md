# Testing the Open-Meteo Server

This document explains how to run the tests for the Open-Meteo FastMCP server.

## Installing Test Dependencies

First, make sure you have the virtual environment activated and install the test dependencies:

```bash
source .venv/bin/activate
pip install -e ".[test]"
```

The test dependencies include:
- pytest: Test framework
- pytest-asyncio: Support for async tests
- pytest-cov: Code coverage reporting
- pytest-mock: Enhanced mocking capabilities
- respx: HTTP mocking for httpx

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests with verbose output
```bash
pytest -v
```

### Run tests without coverage
```bash
pytest --no-cov
```

### Run only unit tests (skip integration tests)
```bash
pytest -m "not integration"
```

### Run a specific test file
```bash
pytest test_open_meteo_server.py
```

### Run a specific test class or function
```bash
pytest test_open_meteo_server.py::TestGetForecastTool
pytest test_open_meteo_server.py::TestGetForecastTool::test_get_forecast_basic
```

## Test Structure

The test suite is organized into the following categories:

1. **TestHealthEndpoint**: Tests for the `/health` endpoint
2. **TestGetForecastTool**: Tests for the `get_forecast` tool
3. **TestGetHistoricalForecastTool**: Tests for the `get_historical_forecast` tool
4. **TestGetPreviousModelRunsTool**: Tests for the `get_previous_model_runs` tool
5. **TestGetHistoricalWeatherTool**: Tests for the `get_historical_weather` tool
6. **TestPrompts**: Tests for the predefined prompt functions

## Coverage Reports

After running tests with coverage, you can view the reports:

### Terminal report
The coverage summary is displayed automatically after running pytest.

### HTML report
```bash
open htmlcov/index.html
```

## Writing New Tests

When adding new features or fixing bugs, make sure to:

1. Add corresponding tests in the appropriate test class
2. Use async test functions with `@pytest.mark.asyncio` decorator
3. Mock external HTTP calls using `patch` or the provided fixtures
4. Test both success and error cases
5. Maintain at least 80% code coverage

## Integration Tests

Integration tests that make real API calls are marked with `@pytest.mark.integration`. These are skipped by default in CI but can be run locally:

```bash
pytest -m integration
```

Note: Integration tests require internet connectivity and may be rate-limited by the Open-Meteo API.