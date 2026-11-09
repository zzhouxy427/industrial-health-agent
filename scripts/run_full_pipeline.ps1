[CmdletBinding()]
param(
    [switch]$SkipTests,
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot

if (-not $Python) {
    $Python = Join-Path $projectRoot ".venv\Scripts\python.exe"
}

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Python executable not found: $Python. Create .venv and install requirements first."
}

$requiredFiles = @(
    "data\raw\train_FD001.txt",
    "data\raw\test_FD001.txt",
    "data\raw\RUL_FD001.txt"
)
foreach ($relativePath in $requiredFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $projectRoot $relativePath))) {
        throw "Required dataset file is missing: $relativePath"
    }
}

function Invoke-ProjectPython {
    param([string[]]$Arguments)

    Write-Host "> $Python $($Arguments -join ' ')" -ForegroundColor Cyan
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE"
    }
}

Push-Location $projectRoot
try {
    Invoke-ProjectPython @("src\prepare_data.py")
    Invoke-ProjectPython @("src\save_predictions.py")
    Invoke-ProjectPython @("src\evaluate_official_test.py")
    Invoke-ProjectPython @("src\evaluate_prediction_intervals.py")
    Invoke-ProjectPython @("src\evaluate_alert_timing.py")
    Invoke-ProjectPython @("src\monitor_data_drift.py")
    Invoke-ProjectPython @("src\build_risk_queue.py")
    Invoke-ProjectPython @("src\generate_review_summary.py")

    if (-not $SkipTests) {
        Invoke-ProjectPython @("-m", "pytest", "-q")
    }

    Write-Host "Pipeline completed. Inspect the artifacts directory for generated outputs." -ForegroundColor Green
}
finally {
    Pop-Location
}
