"""Weather Agent using MCP and optional 9router proxy."""
import logging
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams
from google.genai import types

load_dotenv(Path(__file__).resolve().parents[1] / '.env')
logger = logging.getLogger(__name__)
proxy_url = os.getenv('OPENAI_BASE_URL')
if proxy_url:
    from google.adk.models.lite_llm import LiteLlm
    if not os.getenv('OPENAI_API_KEY') or not os.getenv('PROXY_MODEL'):
        raise ValueError('Configure OPENAI_API_KEY and PROXY_MODEL for the proxy')
    agent_model = LiteLlm(model='openai/' + os.environ['PROXY_MODEL'],
                         api_base=proxy_url, api_key=os.environ['OPENAI_API_KEY'],
                         timeout=30, num_retries=0)
else:
    agent_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')

MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'http://localhost:8085/mcp')
weather_tools = McpToolset(connection_params=StreamableHTTPConnectionParams(
    url=MCP_SERVER_URL, timeout=30.0))


async def check_mcp_before_run(callback_context):
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async def discover():
        async with streamablehttp_client(MCP_SERVER_URL) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                names = {tool.name for tool in (await session.list_tools()).tools}
                if not {'get_current_weather', 'get_forecast', 'health_check'}.issubset(names):
                    raise ValueError('Weather tools missing')
    try:
        await asyncio.wait_for(discover(), timeout=8)
    except Exception:
        return types.Content(role='model', parts=[types.Part(
            text='Không thể kết nối hoặc khám phá công cụ MCP. Hãy kiểm tra MCP server và MCP_SERVER_URL; chưa có dữ liệu thời tiết mới.')])
    return None


def validate_tool_args(tool, args, tool_context):
    allowed = {
        'get_current_weather': {'city'},
        'get_forecast': {'city', 'days'},
        'health_check': {'reason'},
    }.get(tool.name)
    if allowed is not None:
        unexpected = set(args) - allowed
        if unexpected:
            return {'error': 'Unsupported tool arguments: ' + ', '.join(sorted(unexpected)),
                    'instruction': 'Retry using only the declared tool parameters. Do not invent weather.'}
    return None


def tool_error(tool, args, tool_context, error):
    return {'error': 'Weather tool failed. Check MCP server and API configuration.',
            'instruction': 'Explain that fresh weather data is unavailable. Do not invent values.'}


def model_error(callback_context, llm_request, error):
    # Do not expose exception text, credentials, or switch to another provider.
    return LlmResponse(content=types.Content(role='model', parts=[types.Part(
        text='Không thể hoàn tất yêu cầu tới dịch vụ model hoặc MCP. Hãy kiểm tra MCP server, 9router, API key và model; chưa có câu trả lời thời tiết mới.')]))


root_agent = Agent(
    name='weather_agent', model=agent_model, tools=[weather_tools],
    instruction=(
        'Ban la tro ly thoi tiet, tra loi bang tieng Viet co dau. '
        'Chi dung so lieu tu tool thanh cong; khi tool bao loi thi thong bao loi, khong bia du lieu. '
        'Dung dung schema tool, khong them tham so ngoai schema. '
        'Du bao chi ho tro 1-3 ngay. Neu yeu cau nhieu hon 3, noi ro gioi han va chi tra du lieu 3 ngay. '
        'Neu days <= 0, giai thich dau vao khong hop le va hoi so ngay trong 1-3. '
        'health_check chi xac nhan MCP phan hoi; khong xac nhan WeatherAPI, API key hay do on dinh lau dai. '
        'Giữ dung ngay, don vi va thoi diem cap nhat. Chenh lech do am phan tram la diem phan tram. '
        'Khi nguoi dung yeu cau du lieu moi hoac so sanh, goi lai tool cho tung thanh pho.'
    ),
    before_tool_callback=validate_tool_args,
    before_agent_callback=check_mcp_before_run,
    on_tool_error_callback=tool_error,
    on_model_error_callback=model_error,
)
logger.info('Agent and MCP toolset configured; connectivity is verified when tools are discovered/called.')
