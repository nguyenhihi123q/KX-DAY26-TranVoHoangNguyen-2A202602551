"""Check WeatherAPI credentials without displaying the key or request URLs."""
import asyncio
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


async def main():
    load_dotenv(Path(__file__).resolve().parents[1] / "mcp-server" / ".env")
    key = os.getenv("WEATHERAPI_KEY")
    if not key:
        raise SystemExit("FAIL: WEATHERAPI_KEY is not configured")
    async with httpx.AsyncClient(timeout=30) as client:
        for endpoint, city, extra in [
            ("current.json", "Hanoi", {}),
            ("forecast.json", "Tokyo", {"days": 3}),
        ]:
            try:
                response = await client.get(
                    "https://api.weatherapi.com/v1/" + endpoint,
                    params={"key": key, "q": city, "aqi": "no", **extra},
                )
            except httpx.RequestError:
                raise SystemExit("FAIL: WeatherAPI network request failed") from None
            if response.status_code != 200:
                raise SystemExit(f"FAIL: WeatherAPI HTTP {response.status_code}")
            data = response.json()
            location = data["location"]
            print(f"PASS: {endpoint}, HTTP 200, {location['name']}, {location['country']}")
            if endpoint == "current.json":
                current = data["current"]
                print(f"Temperature: {current['temp_c']} C; updated: {current['last_updated']}")
            else:
                days = data["forecast"]["forecastday"]
                if len(days) != 3:
                    raise SystemExit(f"FAIL: Expected 3 forecast days, received {len(days)}")
                print("Forecast dates:", ", ".join(day["date"] for day in days))
    print("WeatherAPI credentials and current/forecast access: OK")


if __name__ == "__main__":
    asyncio.run(main())
