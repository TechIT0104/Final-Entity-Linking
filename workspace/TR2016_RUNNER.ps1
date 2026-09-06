#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Execute TR2016 benchmark evaluation on remote servers
    
.DESCRIPTION
    Runs mReFinED TR2016 evaluation (4 languages: de, es, fr, it)
    on servers 172.20.70.80 and 172.20.70.170
    
.PARAMETER Password
    SSH password for kmpooja@172.20.70.80 (only needed once)
    
.EXAMPLE
    .\TR2016_RUNNER.ps1 -Password "kmpooja123"
#>

param(
    [Parameter(Mandatory=$true)]
    [SecureString]$Password
)

# Convert SecureString to plain text for sshpass
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password)
$plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

$servers = @(
    @{
        Host = '172.20.70.80'
        Script = 'remote_cmd_tr2016_server80.sh'
        Languages = 'DE + ES'
    },
    @{
        Host = '172.20.70.170'
        Script = 'remote_cmd_tr2016_server170.sh'
        Languages = 'FR + IT'
    }
)

$startTime = Get-Date
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "TR2016 Evaluation Launcher - mReFinED" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Green

foreach ($server in $servers) {
    $serverName = $server.Host
    $scriptPath = "/DATA/kmpooja/mrefined_option1/$($server.Script)"
    $languages = $server.Languages
    
    Write-Host "Server: $serverName ($languages)" -ForegroundColor Yellow
    Write-Host "Script: $scriptPath" -ForegroundColor Gray
    Write-Host "Status: Launching..." -ForegroundColor Cyan
    
    try {
        # Use sshpass (if available) to avoid repeated password prompts
        if (Get-Command sshpass -ErrorAction SilentlyContinue) {
            sshpass -p $plainPassword ssh kmpooja@$serverName "bash $scriptPath 2>&1 | tee /tmp/tr2016_run_$(date +%s).log"
        } else {
            # Fallback: standard SSH (will prompt for password)
            Write-Host "⚠️  sshpass not found. Standard SSH will prompt for password." -ForegroundColor Yellow
            ssh kmpooja@$serverName "bash $scriptPath"
        }
        
        Write-Host "✓ Completed successfully!`n" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Error: $($_.Exception.Message)`n" -ForegroundColor Red
    }
}

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "========================================" -ForegroundColor Green
Write-Host "TR2016 Evaluation Complete" -ForegroundColor Cyan
Write-Host "Total Time: $($duration.TotalMinutes) minutes" -ForegroundColor Gray
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Check logs at /DATA/kmpooja/mrefined_option1/logs/tr2016_*.log"
Write-Host "2. Expected results:"
Write-Host "   - German (de):     28.2% recall"
Write-Host "   - Spanish (es):    34.4% recall"
Write-Host "   - French (fr):     25.3% recall"
Write-Host "   - Italian (it):    25.8% recall"
Write-Host "   - Macro-avg:       28.4% recall`n"
