$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $taskUv = Join-Path $PSScriptRoot '../../.tools/bin/uv.exe'
    if (Test-Path -LiteralPath $taskUv) {
        & $taskUv run --locked --cache-dir '../../.uv-cache' adk web
    } else {
        uv run --locked adk web
    }
    if ($LASTEXITCODE -ne 0) { throw 'ADK exited with an error.' }
} finally {
    Pop-Location
}
