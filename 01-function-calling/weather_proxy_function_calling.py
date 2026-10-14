"""Manual Function Calling through 9router; no MCP or ADK involved."""
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from weather_function_calling import SYSTEM_INSTRUCTION, get_weather


def run(prompt):
    load_dotenv(Path(__file__).resolve().parents[1] / "04-lab/mcp-client/.env")
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION + " Dùng tên thành phố tiếng Việt có dấu khi gọi tool. Đây là dữ liệu mock để học."},
        {"role": "user", "content": prompt},
    ]
    tools = [{"type": "function", "function": {
        "name": "get_weather", "description": "Lấy thời tiết mock của một thành phố",
        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
    }}]
    call_count = 0
    cities = set()
    with httpx.Client(timeout=60) as client:
        for turn in range(8):
            response = client.post(
                os.environ["OPENAI_BASE_URL"].rstrip("/") + "/chat/completions",
                headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]},
                json={"model": os.environ["PROXY_MODEL"], "messages": messages,
                      "tools": tools, "stream": False,
                      "tool_choice": "required" if turn == 0 else "auto"},
            )
            if response.status_code != 200:
                raise RuntimeError(f"Proxy HTTP {response.status_code}")
            message = response.json()["choices"][0]["message"]
            calls = message.get("tool_calls")
            if not calls:
                if not {"Hà Nội", "Đà Nẵng"}.issubset(cities):
                    raise RuntimeError("Demo did not call both requested cities")
                print("Function calls executed:", call_count)
                return message.get("content", "")
            messages.append({k: v for k, v in message.items() if k in ("role", "content", "tool_calls")})
            for call in calls:
                function = call["function"]
                if function["name"] != "get_weather":
                    raise RuntimeError("Unexpected tool name")
                args = json.loads(function["arguments"])
                city = args.get("city")
                if not isinstance(city, str):
                    raise RuntimeError("Missing city argument")
                print("[model yêu cầu] get_weather:", city)
                result = get_weather(city=city)
                print("[app thực thi]", result)
                cities.add(city)
                call_count += 1
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    raise RuntimeError("Function calling exceeded 8 turns")


if __name__ == "__main__":
    print("Provider: 9router; data: MOCK; transport: OpenAI-compatible HTTP")
    question = "Thời tiết Hà Nội và Đà Nẵng hôm nay thế nào?"
    print("User:", question)
    print("Trả lời:", run(question))
