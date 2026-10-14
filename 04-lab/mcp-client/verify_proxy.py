"""Verify the configured proxy supports chat and function calling, without MCP."""
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from litellm import acompletion


async def main():
    load_dotenv(Path(__file__).resolve().parent / ".env")
    tool = {
        "type": "function",
        "function": {
            "name": "health_check",
            "description": "Check server health",
            "parameters": {"type": "object", "properties": {}},
        },
    }
    response = await acompletion(
        model="openai/" + os.environ["PROXY_MODEL"],
        api_base=os.environ["OPENAI_BASE_URL"],
        api_key=os.environ["OPENAI_API_KEY"],
        messages=[{"role": "user", "content": "Call health_check now."}],
        tools=[tool],
        tool_choice={"type": "function", "function": {"name": "health_check"}},
        max_tokens=128,
        timeout=45,
    )
    calls = response.choices[0].message.tool_calls
    if not calls or calls[0].function.name != "health_check":
        raise RuntimeError("Proxy did not return the requested tool call")
    print("Proxy model:", os.environ["PROXY_MODEL"])
    print("Function calling OK:", calls[0].function.name)


if __name__ == "__main__":
    asyncio.run(main())
