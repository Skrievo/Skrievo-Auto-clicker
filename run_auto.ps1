#!/usr/bin/env pwsh
<#
Simple PowerShell launcher for `auto.py`.
Usage: .\run_auto.ps1 -- --noninteractive --title "Mein Spiel" --mouse --mouse-button left
The `--` separates PowerShell args from the script args so all following args are passed to Python.
#>
param([Parameter(ValueFromRemainingArguments=$true)] $remaining)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python nicht gefunden. Bitte Python installieren und in PATH setzen."
    exit 1
}

# Build argument list
$pyArgs = @()
if ($remaining) { $pyArgs += $remaining }

& python "$scriptDir\auto.py" @pyArgs
