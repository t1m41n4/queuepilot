param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,
    [switch]$ConfirmRestore
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $BackupFile)) {
    throw "Backup file not found: $BackupFile"
}
if (-not $ConfirmRestore) {
    throw "Restore is destructive. Re-run with -ConfirmRestore."
}
$dbUser = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "queuepilot" }
$dbName = if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { "queuepilot" }

Get-Content -Raw -LiteralPath $BackupFile | docker compose exec -T db psql -U $dbUser -d $dbName
if ($LASTEXITCODE -ne 0) {
    throw "Database restore failed"
}
Write-Host "Database restore completed from $BackupFile"
