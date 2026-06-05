# Run smoke tests via uv from the skill directory.
$ErrorActionPreference = "Stop"
$SkillRoot = Split-Path -Parent $PSScriptRoot
Set-Location $SkillRoot
$env:MPLBACKEND = "Agg"

Write-Host "==> uv sync"
uv sync

Write-Host "==> check_deps"
uv run python scripts/check_deps.py

Write-Host "==> smoke_e1_cnmaps"
uv run python scripts/smoke_e1_cnmaps.py

Write-Host "==> smoke_e3_frykit"
uv run python scripts/smoke_e3_frykit.py

Write-Host "Smoke tests passed."
