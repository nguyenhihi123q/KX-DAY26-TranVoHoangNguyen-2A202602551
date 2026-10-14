"""Verify real WeatherAPI results through MCP Streamable HTTP (SDK v1)."""
import asyncio
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def text_result(result):
    if result.isError:
        raise RuntimeError("MCP returned a tool error")
    return "\n".join(block.text for block in result.content if block.type == "text")


async def main():
    load_dotenv(Path(__file__).resolve().parent / ".env")
    url = os.getenv("MCP_SERVER_URL", "http://localhost:8085/mcp")
    print("MCP endpoint:", url)
    print("Transport: Streamable HTTP; data source: WeatherAPI (real)")
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            initialized = await session.initialize()
            print("Initialize PASS; server:", initialized.serverInfo.name)
            tools = (await session.list_tools()).tools
            names = {tool.name for tool in tools}
            expected = {"health_check", "get_current_weather", "get_forecast"}
            if names != expected:
                raise RuntimeError(f"Unexpected tools: {sorted(names)}")
            for tool in tools:
                print("Tool:", tool.name, "schema:", tool.inputSchema)
            print("Discovery PASS: all 3 tools found")

            health = text_result(await session.call_tool("health_check", {}))
            if "Weather MCP Server is running" not in health:
                raise RuntimeError("Unexpected health result")
            print("\n=== health_check ===\n" + health)
            print("PASS: MCP tool reachable (WeatherAPI verified separately below)")

            current = text_result(await session.call_tool("get_current_weather", {"city": "Hanoi"}))
            for field in ["Hanoi", "Vietnam", "Temperature:", "Condition:", "Humidity:", "Last updated:"]:
                if field not in current:
                    raise RuntimeError(f"Missing weather field: {field}")
            if not re.search(r"Temperature: [-\d.]+°C", current):
                raise RuntimeError("Missing numeric temperature")
            print("\n=== get_current_weather(Hanoi) ===\n" + current)
            print("PASS: real current weather and update timestamp")

            for days in (1, 2, 3):
                forecast = text_result(await session.call_tool("get_forecast", {"city": "Tokyo", "days": days}))
                dates = re.findall(r"^\d{4}-\d{2}-\d{2}:$", forecast, re.MULTILINE)
                if "Tokyo" not in forecast or len(dates) != days:
                    raise RuntimeError(f"Expected Tokyo/{days} days, got {len(dates)}")
                if len(set(dates)) != days or dates != sorted(dates):
                    raise RuntimeError("Forecast dates are duplicated or unordered")
                for field in ("High:", "Low:", "Chance of Rain:"):
                    if forecast.count(field) != days:
                        raise RuntimeError(f"Unexpected forecast field count: {field}")
                print(f"\n=== get_forecast(Tokyo, days={days}) ===\n" + forecast)
                print(f"PASS: {days} forecast day(s), expected fields present")
    print("\nALL STAGE 3 MCP CHECKS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
