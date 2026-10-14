# Lab 04 — Weather Agent with Remote MCP Server

A weather agent built with Google ADK that connects to an MCP server via Streamable HTTP transport.

## Architecture

```
┌─────────────────┐   Streamable HTTP    ┌─────────────────┐      REST       ┌─────────────────┐
│   ADK Agent     │ ──────────────────── │   MCP Server    │ ─────────────── │  WeatherAPI.com │
│  (mcp-client)   │   localhost:8085/mcp │  (mcp-server)   │                 │                 │
└─────────────────┘                      └─────────────────┘                 └─────────────────┘
```

## Tools

| Tool | Description |
|------|-------------|
| `get_current_weather(city)` | Get current weather conditions for a city |
| `get_forecast(city, days)` | Get weather forecast (1–3 days) |
| `health_check()` | Verify server is running |

## ADK làm gì trong Lab này?

ADK (Agent Development Kit) đóng vai trò **MCP Client** 
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. KẾT NỐI tới MCP Server qua Streamable HTTP                  │
│     StreamableHTTPConnectionParams(url="localhost:8085/mcp")    │
│                                                                 │
│  2. KHÁM PHÁ tools tự động (list_tools)                         │
│     McpToolset → tự hỏi server "anh có tool gì?"                │
│     → nhận về: get_current_weather, get_forecast, health_check  │
│                                                                 │
│  3. TRUYỀN tools cho LLM (Gemini)                               │
│     Agent(model="gemini-2.5-flash", tools=[weather_tools])      │
│     → Gemini biết nó có thể gọi 3 tools trên                    │
│                                                                 │
│  4. ĐIỀU PHỐI vòng lặp Function Calling                         │
│     User hỏi → Gemini chọn tool → ADK gọi MCP Server            │
│     → nhận kết quả → đưa lại cho Gemini tổng hợp                │
│                                                                 │
│  5. CUNG CẤP giao diện web (adk web)                            │
│     → http://localhost:8000 để chat với agent                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

So với bài 02 (viết client thủ công bằng `mcp.ClientSession`), ADK giúp bạn **không phải viết vòng lặp function calling thủ công** nữa. Toàn bộ luồng list_tools → model quyết định → call_tool → model tổng hợp được ADK xử lý tự động.

## Setup

### 1. MCP Server

```bash
cd mcp-server
uv sync

# Set your WeatherAPI key (get one free at https://weatherapi.com)
export WEATHERAPI_KEY="your_weatherapi_key"

# Start the server (runs on port 8085 by default)
uv run python weather.py
```

The server will be available at `http://localhost:8085/mcp`.

### 2. ADK Agent (Client)

```bash
cd mcp-client
uv sync

# Create .env file with your Gemini API key
echo "GOOGLE_API_KEY=your_gemini_api_key" > .env

# Start ADK web interface
uv run adk web
```

Open http://localhost:8000 in your browser, select `weather_agent`, and ask about the weather.

## Configuration

### Local PowerShell configuration

You can store `WEATHERAPI_KEY` in `mcp-server/.env` (copy
`mcp-server/.env.example`; never commit real keys). From the repository root,
run `.\04-lab\mcp-server\start-server.ps1` to load this file through uv and
start the server using Streamable HTTP. Running `weather.py` directly does
not automatically load `.env`.

To verify WeatherAPI credentials independently of MCP, run from the root:

```powershell
& .\04-lab\mcp-client\.venv\Scripts\python.exe .\04-lab\mcp-client\verify_weatherapi.py
```

The check requests current weather for Hanoi and a three-day forecast for
Tokyo. It displays results without printing the API key or request URLs.

After starting the server, verify the MCP protocol and all three tools:

```powershell
$env:PYTHONIOENCODING = "utf-8"
& .\04-lab\mcp-client\.venv\Scripts\python.exe .\04-lab\mcp-client\verify_mcp_tools.py
```

This uses the client SDK v1 environment, performs initialize/discovery,
checks health and real current weather, then verifies forecasts for 1, 2,
and 3 days. A successful run ends with `ALL STAGE 3 MCP CHECKS PASSED`.

### Error handling

Blank cities and forecast days below 1 produce MCP errors. Requests above
3 days return at most 3 with an explicit limit notice. WeatherAPI failures
are translated to safe errors for unknown city, invalid/disabled key,
quota, plan restrictions or network failure; key-bearing request URLs are
not printed by the server.

`health_check(reason="")` accepts an optional caller explanation and only
confirms that MCP responds. It does not verify WeatherAPI access or long-term
stability. The agent checks actual MCP initialize/discovery before each
request, rejects unsupported tool arguments, and returns safe error messages
instead of a tool-free fallback or a different model provider.

| Variable | Where | Description |
|----------|-------|-------------|
| `WEATHERAPI_KEY` | mcp-server | API key from weatherapi.com |
| `GOOGLE_API_KEY` | mcp-client/.env | Gemini API key |
| `PORT` | mcp-server (env) | Override server port (default: 8085) |
| `MCP_SERVER_URL` | mcp-client/.env | MCP endpoint the agent connects to (default: `http://localhost:8085/mcp`; set to your Cloud Run URL + `/mcp` when deployed) |
