<#
PowerShell script to set up and launch the Autobot CLI in headful mode.
Place this file in your project root (where `autobot_cli.py` lives) and run:

    .\run_autobot.ps1
#>

Param(
    # Defaults to the directory containing this script
    [string]$ProjectDir = "$PSScriptRoot"
)

# ─── Declare before strict mode ─────────────────────────────────────────────────
$venvPath = Join-Path $ProjectDir '.venv'

# ─── Now turn on strict mode ─────────────────────────────────────────────────────
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "📁 Project directory: $ProjectDir"
Write-Host "🐍 Virtual environment path: $venvPath"

# 1. Create (or reuse) virtual environment at .venv
if (!(Test-Path $venvPath)) {
    Write-Host "🐍 Creating virtual environment at $venvPath..."
    python -m venv $venvPath
} else {
    Write-Host "✅ Virtual environment already exists at $venvPath"
}

# 2. Activate the virtual environment
Write-Host "🔌 Activating virtual environment..."
& "$venvPath\Scripts\Activate.ps1"

# 3. Install requirements if needed
$reqFile = Join-Path $ProjectDir 'requirements.txt'
if (Test-Path $reqFile) {
    Write-Host "📦 Installing/upgrading Python dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r $reqFile
} else {
    Write-Warning "⚠️ requirements.txt not found at $reqFile – skipping dependency installation."
}

# 4. Launch the Autobot CLI in headful mode
Write-Host '🚀 Launching Autobot CLI (headful)...'
$scriptPath = Join-Path $ProjectDir 'autobot_cli.py'
& python $scriptPath '--headful'
