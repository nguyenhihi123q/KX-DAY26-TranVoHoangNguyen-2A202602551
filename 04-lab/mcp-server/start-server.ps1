$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path -LiteralPath '.env')) {
        throw 'Create .env from .env.example and configure WEATHERAPI_KEY first.'
    }
    $taskUv = Join-Path $PSScriptRoot '../../.tools/bin/uv.exe'
    # Force Streamable HTTP even when launched without an interactive stdin.
    $env:PORT = '8085'
    if (Test-Path -LiteralPath $taskUv) {
        & $taskUv run --locked --env-file .env --cache-dir '../../.uv-cache' python weather.py
    } else {
        uv run --locked --env-file .env python weather.py
    }
    if ($LASTEXITCODE -ne 0) { throw 'MCP server exited with an error.' }
} finally {
    Pop-Location
}
