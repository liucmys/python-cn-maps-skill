# Install python-cn-maps skill to agent-specific directories.
param(
    [ValidateSet("cursor", "claude", "github", "agents", "gemini", "codex", "opencode", "all-project")]
    [string]$Target = "cursor",
    [ValidateSet("project", "global")]
    [string]$Scope = "project",
    [string]$ProjectRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$SkillName = "python-cn-maps"
$RepoRoot = Split-Path -Parent $PSScriptRoot

$relPaths = @{
    cursor   = ".cursor/skills/$SkillName"
    claude   = ".claude/skills/$SkillName"
    github   = ".github/skills/$SkillName"
    agents   = ".agents/skills/$SkillName"
    gemini   = ".gemini/skills/$SkillName"
    codex    = ".codex/skills/$SkillName"
    opencode = "skills/$SkillName"
}

$exclude = @(".git", ".venv", "__pycache__", "artifacts")

function Get-DestRoot([string]$rel) {
    if ($Scope -eq "global") {
        $home = $env:USERPROFILE
        if ($rel -match "^\.cursor") { return Join-Path $home ".cursor/skills/$SkillName" }
        if ($rel -match "^\.claude") { return Join-Path $home ".claude/skills/$SkillName" }
        if ($rel -match "^\.codex")  { return Join-Path $home ".codex/skills/$SkillName" }
        if ($rel -match "^\.gemini") { return Join-Path $home ".gemini/skills/$SkillName" }
        if ($rel -match "^\.agents") { return Join-Path $home ".agents/skills/$SkillName" }
        throw "Global scope not defined for path: $rel"
    }
    return Join-Path $ProjectRoot ($rel -replace "/", "\")
}

function Install-To([string]$dest) {
    if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Get-ChildItem -Path $RepoRoot -Force | Where-Object {
        $_.Name -notin $exclude -and $_.Name -ne "artifacts"
    } | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $dest -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path (Join-Path $dest "artifacts") | Out-Null
    if (-not (Test-Path (Join-Path $dest "artifacts/.gitkeep"))) {
        New-Item -ItemType File -Path (Join-Path $dest "artifacts/.gitkeep") -Force | Out-Null
    }
    Write-Host "Installed -> $dest"
}

$targets = if ($Target -eq "all-project") { @("cursor", "claude", "github", "agents", "gemini", "codex", "opencode") } else { @($Target) }

foreach ($t in $targets) {
    $rel = $relPaths[$t]
    if (-not $rel) { throw "Unknown target: $t" }
    Install-To (Get-DestRoot $rel)
}

Write-Host "Done. Target=$Target Scope=$Scope"
