<#
PowerShell script to set up and launch the Autobot CLI in headful mode.
Place this file in your project root (where `autobot_cli.py` lives) and run:

    .\run_autobot.ps1
#>

Param(
    # Defaults to the directory containing this script
    [string]$ProjectDir = "$PSScriptRoot",
    [string]$VenvPath = "C:\Users\Israel\Documents\Code\IP\autobot\.venv"
)

# Stop on errors
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "📁 Project directory: $ProjectDir"

# 1. Create (or reuse) virtual environment at .venv
$venvPath = Join-Path $ProjectDir '.venv'
if (!(Test-Path $venvPath)) {
    Write-Host "🐍 Creating virtual environment at $venvPath..."
    python -m venv $venvPath
} else {
    Write-Host "✅ Virtual environment already exists at $venvPath"
}

# 2. Activate the virtual environment
Write-Host "🔌 Activating virtual environment..."
& "$venvPath\Scripts\Activate.ps1"

# 5. Launch the Autobot CLI in headful mode
Write-Host '🚀 Launching Autobot CLI (headful)...'
# you can even skip the variable and call python directly:
$scriptPath = Join-Path $ProjectDir 'autobot_cli.py'
& python $scriptPath '--headful'

