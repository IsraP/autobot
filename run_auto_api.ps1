# run-api.ps1
# PowerShell script to run your FastAPI app with Uvicorn

Write-Host '🔧 Starting Auto-API with Uvicorn...' -ForegroundColor Cyan

# Ensure virtualenv is activated if not already
if (-not $env:VIRTUAL_ENV) {
    Write-Host '⚠️  Virtual environment not detected. Trying to activate .venv...' -ForegroundColor Yellow
    $venvPath = Join-Path $PSScriptRoot '.venv\Scripts\Activate.ps1'
    if (Test-Path $venvPath) {
        & $venvPath
        Write-Host '✅ Virtual environment activated.' -ForegroundColor Green
    } else {
        Write-Host '❌ Could not find .venv. Please activate manually.' -ForegroundColor Red
    }
}

# Run Uvicorn pointing to application.api:app
python -m uvicorn application.api:app --host 127.0.0.1 --port 8000
