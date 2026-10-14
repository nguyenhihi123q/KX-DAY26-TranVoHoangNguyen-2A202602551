# Weather Agent - Google ADK with MCP Server

AI agent built with **Google Agent Development Kit (ADK)** that uses tools from a local **MCP server** via Streamable HTTP transport.

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│   User Browser  │ ───> │  ADK Web UI      │ ───> │  Weather Agent      │
│   localhost:8000│      │  (Google ADK)    │      │  (Agent with MCP)   │
└─────────────────┘      └──────────────────┘      └─────────────────────┘
                                                             │
                                                             │ Streamable HTTP
                                                             ▼
                                                   ┌─────────────────────┐
                                                   │  MCP Server         │
                                                   │  localhost:8085/mcp │
                                                   │  FastMCP + Tools    │
                                                   └─────────────────────┘
                                                             │
                                                             ▼
                                                   ┌─────────────────────┐
                                                   │  WeatherAPI.com     │
                                                   └─────────────────────┘
```

## Features

- **Remote MCP Tools**: Connects to MCP server via Streamable HTTP
- **3 Weather Tools**:
  - `get_current_weather(city)` - Real-time weather conditions
  - `get_forecast(city, days)` - Weather forecast up to 3 days
  - `health_check()` - Server health verification
- **Web Interface**: UI via ADK web
- **Streaming Responses**: Real-time AI responses

## Quick Start

### 9router proxy (OpenAI-compatible)

Copy `.env.example` to `.env` and set your local proxy key. The agent uses
`LiteLlm` when `OPENAI_BASE_URL` is configured. `PROXY_MODEL` must match an ID
returned by the proxy's `/v1/models` endpoint; the local setup uses
`ag/gemini-3.8-flash` at `http://localhost:20128/v1`.

Run `uv sync --locked`, start the MCP server, then run `uv run adk web`.
With no `OPENAI_BASE_URL`, the agent uses direct Gemini and `GOOGLE_API_KEY`.
Keep `.env` private; `.env.example` contains placeholders only.

Run `uv run python verify_proxy.py` to verify the model returns a function call
through the proxy without requiring WeatherAPI credentials or a running MCP server.

### 1. Start the MCP Server

```bash
cd ../mcp-server
export WEATHERAPI_KEY="your_weatherapi_key"
uv run python weather.py
```

### 2. Setup Environment

```bash
cd mcp-client

# Create .env file with your Google API key
# Get free key from: https://aistudio.google.com/apikey
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Run the Agent

```bash
uv run adk web
```

### 5. Use the Agent

1. Open browser: http://localhost:8000
2. Select `weather_agent` from dropdown
3. Ask questions like:
   - "What's the weather in Brisbane?"
   - "Give me a 3-day forecast for Tokyo"
   - "How's the weather in New York?"

## Project Structure

```
mcp-client/
├── weather_agent/
│   ├── agent.py           # Main agent with MCP connection
│   └── __init__.py
├── pyproject.toml
├── .env                   # Environment variables (create this)
└── README.md
```

## Configuration

### Agent Configuration

In `weather_agent/agent.py`:

```python
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8085/mcp")

connection_params = StreamableHTTPConnectionParams(
    url=MCP_SERVER_URL,
    timeout=30.0,
)

root_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    tools=[weather_tools],
)
```

## Troubleshooting

### Agent won't connect to MCP server

1. **404 errors**: MCP server is not running or wrong port
   - Ensure the MCP server is running on port 8085
   - Check `MCP_SERVER_URL` (env var / `.env`, default `http://localhost:8085/mcp`)

2. **405 errors on a plain GET**: The endpoint may require MCP methods/headers
   - Use `verify_setup.py` for real MCP initialize/discovery/health checks.
   - A plain HTTP response does not prove the MCP protocol works.

3. **Timeout errors**: Server not started
   - Start the MCP server first, then the ADK client

### Safe failure handling

The agent checks MCP initialize/discovery before each request. If unavailable,
it returns a clear error rather than a tool-free fallback. Model/proxy failures
return a safe configuration message without changing provider. Weather tool
errors must not be turned into invented weather values.
After changing Python code on Windows, restart ADK Web (reload is disabled).
See `../README.md` for tool input validation and error handling.

## Environment Variables

Create `.env` file:
```bash
GOOGLE_API_KEY=your_gemini_api_key
```

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [WeatherAPI](https://www.weatherapi.com/)
