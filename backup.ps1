# 🏆 World-Class Backup Launcher (PowerShell)
# Interactive menu or use command-line args

param(
    [switch]$Full,
    [switch]$Schedule,
    [switch]$Cleanup,
    [string]$Verify
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackupScript = Join-Path $ScriptDir "scripts\backup_world_class.py"

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "  ╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║       🏆 WORLD-CLASS BACKUP SYSTEM v2.0           ║" -ForegroundColor Cyan
    Write-Host "  ╠═══════════════════════════════════════════════════╣" -ForegroundColor Cyan
    Write-Host "  ║                                                   ║" -ForegroundColor Cyan
    Write-Host "  ║   [1]  📦 Quick Backup (Incremental)              ║" -ForegroundColor White
    Write-Host "  ║   [2]  📦 Full Backup (All Files)                 ║" -ForegroundColor White
    Write-Host "  ║   [3]  ⏰ Start Scheduled Backups (30 min)        ║" -ForegroundColor White
    Write-Host "  ║   [4]  🧹 Cleanup Old Backups                     ║" -ForegroundColor White
    Write-Host "  ║   [5]  🔍 Verify a ZIP File                       ║" -ForegroundColor White
    Write-Host "  ║   [6]  📂 Open Backup Folder                      ║" -ForegroundColor White
    Write-Host "  ║   [0]  ❌ Exit                                    ║" -ForegroundColor White
    Write-Host "  ║                                                   ║" -ForegroundColor Cyan
    Write-Host "  ╚═══════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

# If command-line args provided, use them directly
if ($Verify) {
    python $BackupScript --verify $Verify
    exit
} elseif ($Cleanup) {
    python $BackupScript --cleanup
    exit
} elseif ($Schedule) {
    python $BackupScript
    exit
} elseif ($Full) {
    python $BackupScript --once --full
    exit
} elseif ($PSBoundParameters.Count -gt 0) {
    python $BackupScript --once
    exit
}

# Interactive menu
do {
    Show-Menu
    $choice = Read-Host "  Select option [0-6]"
    
    switch ($choice) {
        "1" {
            Write-Host "`n  🚀 Running incremental backup..." -ForegroundColor Green
            python $BackupScript --once
            Write-Host "`n  Press any key to continue..."
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "2" {
            Write-Host "`n  🚀 Running FULL backup (all files)..." -ForegroundColor Yellow
            python $BackupScript --once --full
            Write-Host "`n  Press any key to continue..."
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "3" {
            Write-Host "`n  ⏰ Starting scheduled backups (every 30 min)..." -ForegroundColor Cyan
            Write-Host "  Press Ctrl+C to stop`n" -ForegroundColor DarkGray
            python $BackupScript
        }
        "4" {
            Write-Host "`n  🧹 Cleaning up old backups..." -ForegroundColor Magenta
            python $BackupScript --cleanup
            Write-Host "`n  Press any key to continue..."
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "5" {
            $zipPath = Read-Host "`n  Enter ZIP file path to verify"
            if ($zipPath -and (Test-Path $zipPath)) {
                python $BackupScript --verify $zipPath
            } else {
                Write-Host "  ❌ File not found: $zipPath" -ForegroundColor Red
            }
            Write-Host "`n  Press any key to continue..."
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "6" {
            $backupDir = "D:\oneclick_reels_ai\backups"
            if (Test-Path $backupDir) {
                explorer.exe $backupDir
            } else {
                Write-Host "  ❌ Backup folder not found" -ForegroundColor Red
            }
        }
        "0" {
            Write-Host "`n  👋 Goodbye!`n" -ForegroundColor Cyan
        }
        default {
            Write-Host "`n  ⚠️ Invalid option. Try again." -ForegroundColor Yellow
            Start-Sleep -Seconds 1
        }
    }
} while ($choice -ne "0")
