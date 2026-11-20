# PowerShell wrapper for Hermes Agent Antigravity / 9Router Patcher
# Windows PowerShell & PowerShell Core compatible

param(
    [switch]$Check,
    [switch]$Rollback,
    [switch]$NoRestart,
    [switch]$NoVerify,
    [string]$HermesDir,
    [string]$RouterDb,
    [switch]$Help
)

if ($Help) {
    Write-Host "Usage: .\patch.ps1 [-Check] [-Rollback] [-NoRestart] [-NoVerify] [-HermesDir <path>] [-RouterDb <path>]"
    exit 0
}

# Locate Python executable
$Python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Python) {
    $Python = (Get-Command python3 -ErrorAction SilentlyContinue).Source
}
if (-not $Python) {
    Write-Error "Python is required but was not found in PATH. Please install Python 3 or add it to PATH."
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PatchPy = Join-Path $ScriptDir "patch.py"

$ArgsList = @()
if ($Check) { $ArgsList += "--check" }
if ($Rollback) { $ArgsList += "--rollback" }
if ($NoRestart) { $ArgsList += "--no-restart" }
if ($NoVerify) { $ArgsList += "--no-verify" }
if ($HermesDir) { $ArgsList += @("--hermes-dir", $HermesDir) }
if ($RouterDb) { $ArgsList += @("--router-db", $RouterDb) }

& $Python $PatchPy @ArgsList
exit $LASTEXITCODE
