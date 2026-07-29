param(
    [string]$OutputDirectory = "backups"
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outputPath = Join-Path $OutputDirectory "queuepilot-$timestamp.sql"
$dbUser = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "queuepilot" }
$dbName = if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { "queuepilot" }

$dump = docker compose exec -T db pg_dump -U $dbUser -d $dbName --clean --if-exists
if ($LASTEXITCODE -ne 0) {
    throw "Database backup failed"
}
$dump | Set-Content -Path $outputPath -Encoding utf8
Write-Host "Database backup written to $outputPath"
