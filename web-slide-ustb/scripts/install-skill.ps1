param([string]$SkillsRoot)
$ErrorActionPreference = 'Stop'
$packageRoot = Split-Path -Parent $PSScriptRoot
$skillSource = Join-Path $packageRoot 'SKILL.md'
if (-not (Test-Path -LiteralPath $skillSource)) { $skillSource = Join-Path $packageRoot 'skill.md' }
foreach ($required in @($skillSource, (Join-Path $packageRoot 'template.html'), (Join-Path $packageRoot 'assets'))) {
    if (-not (Test-Path -LiteralPath $required)) { throw "Package is incomplete: $required" }
}
if (-not $SkillsRoot) {
    $codexDirectory = [Environment]::GetEnvironmentVariable('CODEX_HOME')
    if (-not $codexDirectory) { $codexDirectory = Join-Path $env:USERPROFILE '.codex' }
    $SkillsRoot = Join-Path $codexDirectory 'skills'
}
$SkillsRoot = [IO.Path]::GetFullPath($SkillsRoot)
$destination = Join-Path $SkillsRoot 'beike-ppt-template'
if (Test-Path -LiteralPath $destination) { throw "Already installed; no files overwritten. Back up or rename this directory first: $destination" }
New-Item -ItemType Directory -Path $destination -Force | Out-Null
Get-ChildItem -LiteralPath $packageRoot -File | Where-Object { $_.Extension -in @('.md','.html','.pdf','.cmd') } | ForEach-Object {
    if ($_.Name -ieq 'skill.md') { Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $destination 'SKILL.md') }
    else { Copy-Item -LiteralPath $_.FullName -Destination $destination }
}
foreach ($folder in @('assets','scripts','references')) { if (-not (Test-Path -LiteralPath (Join-Path $packageRoot $folder))) { continue }; Copy-Item -LiteralPath (Join-Path $packageRoot $folder) -Destination $destination -Recurse }
Write-Output "Installed: $destination"
Write-Output 'Use $beike-ppt-template in your next Codex turn. Python and Chrome/Edge are needed only for PDF export.'
