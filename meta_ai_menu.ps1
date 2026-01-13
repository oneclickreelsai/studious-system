# Meta AI to YouTube - Automated Pipeline
# Interactive Menu for OneClick Reels AI

$Host.UI.RawUI.WindowTitle = "Meta AI to YouTube Pipeline"

function Show-Banner {
    Clear-Host
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║                                                          ║" -ForegroundColor Cyan
    Write-Host "  ║   META AI TO YOUTUBE - AUTOMATED PIPELINE                ║" -ForegroundColor Cyan
    Write-Host "  ║   OneClick Reels AI                                      ║" -ForegroundColor Cyan
    Write-Host "  ║                                                          ║" -ForegroundColor Cyan
    Write-Host "  ╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Menu {
    Write-Host "  ┌──────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
    Write-Host "  │                    MAIN MENU                             │" -ForegroundColor Yellow
    Write-Host "  ├──────────────────────────────────────────────────────────┤" -ForegroundColor Yellow
    Write-Host "  │                                                          │" -ForegroundColor Yellow
    Write-Host "  │   [1] Auto Generate & Upload (Random Prompt)             │" -ForegroundColor White
    Write-Host "  │   [2] Custom Prompt - Generate & Upload                  │" -ForegroundColor White
    Write-Host "  │   [3] Custom Prompt - Generate Only (No Upload)          │" -ForegroundColor White
    Write-Host "  │   [4] Batch Mode - Generate Multiple Videos              │" -ForegroundColor White
    Write-Host "  │                                                          │" -ForegroundColor Yellow
    Write-Host "  │   [5] Download from Meta AI URL                          │" -ForegroundColor White
    Write-Host "  │   [6] Re-Engineer & Upload to YouTube from URL           │" -ForegroundColor Magenta
    Write-Host "  │   [7] Add Music to Mute Video                            │" -ForegroundColor Green
    Write-Host "  │                                                          │" -ForegroundColor Yellow
    Write-Host "  │   [8] Login to Meta AI (Setup Session)                   │" -ForegroundColor Gray
    Write-Host "  │   [9] View Daily Content Plan                            │" -ForegroundColor Gray
    Write-Host "  │   [S] Start Backend Server                               │" -ForegroundColor Gray
    Write-Host "  │                                                          │" -ForegroundColor Yellow
    Write-Host "  │   [0] Exit                                               │" -ForegroundColor Red
    Write-Host "  │                                                          │" -ForegroundColor Yellow
    Write-Host "  └──────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
    Write-Host ""
}

function Run-AutoPipeline {
    Write-Host "`n  [*] Starting Auto Pipeline with Random Prompt..." -ForegroundColor Green
    Write-Host "  [*] This will generate a trending video and upload to YouTube" -ForegroundColor Gray
    Write-Host ""
    python cli/auto_pipeline.py
    Write-Host ""
    Read-Host "  Press Enter to continue"
}

function Run-CustomPrompt {
    param([bool]$Upload = $true)
    
    Write-Host ""
    $prompt = Read-Host "  Enter your video prompt"
    
    if ([string]::IsNullOrWhiteSpace($prompt)) {
        Write-Host "  [!] No prompt entered" -ForegroundColor Yellow
        return
    }
    
    Write-Host ""
    if ($Upload) {
        Write-Host "  [*] Generating video and uploading..." -ForegroundColor Green
        python cli/auto_pipeline.py --prompt "$prompt"
    } else {
        Write-Host "  [*] Generating video (no upload)..." -ForegroundColor Green
        python cli/auto_pipeline.py --prompt "$prompt" --no-upload
    }
    Write-Host ""
    Read-Host "  Press Enter to continue"
}

function Run-BatchMode {
    Write-Host ""
    $count = Read-Host "  How many videos to generate? (1-10)"
    
    if (-not ($count -match '^\d+$') -or [int]$count -lt 1 -or [int]$count -gt 10) {
        Write-Host "  [!] Invalid number. Please enter 1-10" -ForegroundColor Yellow
        return
    }
    
    Write-Host ""
    $uploadChoice = Read-Host "  Upload to YouTube? (y/n)"
    
    Write-Host ""
    Write-Host "  [*] Starting batch mode for $count videos..." -ForegroundColor Green
    
    if ($uploadChoice -eq 'y' -or $uploadChoice -eq 'Y') {
        python cli/auto_pipeline.py --batch $count
    } else {
        python cli/auto_pipeline.py --batch $count --no-upload
    }
    Write-Host ""
    Read-Host "  Press Enter to continue"
}

function Run-DownloadURL {
    Write-Host ""
    $url = Read-Host "  Enter Meta AI post URL"
    
    if ([string]::IsNullOrWhiteSpace($url)) {
        Write-Host "  [!] No URL entered" -ForegroundColor Yellow
        return
    }
    
    Write-Host ""
    Write-Host "  [*] Downloading from Meta AI..." -ForegroundColor Green
    python cli/meta_pipeline.py "$url"
    Write-Host ""
    Read-Host "  Press Enter to continue"
}

function Run-ReEngineerUpload {
    Write-Host ""
    Write-Host "  ┌──────────────────────────────────────────────────────────┐" -ForegroundColor Magenta
    Write-Host "  │   RE-ENGINEER & UPLOAD TO YOUTUBE                        │" -ForegroundColor Magenta
    Write-Host "  │   Download -> Analyze -> Generate Metadata -> Upload     │" -ForegroundColor Magenta
    Write-Host "  └──────────────────────────────────────────────────────────┘" -ForegroundColor Magenta
    Write-Host ""
    
    $url = Read-Host "  Enter Meta AI post URL"
    
    if ([string]::IsNullOrWhiteSpace($url)) {
        Write-Host "  [!] No URL entered" -ForegroundColor Yellow
        return
    }
    
    Write-Host ""
    Write-Host "  Upload options:" -ForegroundColor Cyan
    Write-Host "    [1] Upload to YouTube"
    Write-Host "    [2] Just analyze (no upload)"
    Write-Host ""
    $uploadOption = Read-Host "  Select upload option"
    
    Write-Host ""
    Write-Host "  [*] Processing Meta AI video..." -ForegroundColor Green
    Write-Host "  [*] Step 1: Downloading video" -ForegroundColor Gray
    Write-Host "  [*] Step 2: Analyzing content" -ForegroundColor Gray
    Write-Host "  [*] Step 3: Generating AI metadata" -ForegroundColor Gray
    Write-Host "  [*] Step 4: Uploading to YouTube" -ForegroundColor Gray
    Write-Host ""
    
    switch ($uploadOption) {
        "1" { python cli/reengineer_upload.py "$url" --youtube }
        "2" { python cli/reengineer_upload.py "$url" --no-upload }
        default { python cli/reengineer_upload.py "$url" --youtube }
    }
    
    Write-Host ""
    Read-Host "  Press Enter to continue"
}

function Run-Login {
    Write-Host ""
    Write-Host "  [*] Opening browser for Meta AI login..." -ForegroundColor Green
    Write-Host "  [*] Please login with your Facebook account" -ForegroundColor Gray
    Write-Host ""
    python cli/auto_pipeline.py --login
    Write-Host ""
    Read-Host "  Press Enter to continue"
}

function Run-AddMusic {
    Write-Host ""
    Write-Host "  ┌──────────────────────────────────────────────────────────┐" -ForegroundColor Green
    Write-Host "  │   ADD MUSIC TO VIDEO                                     │" -ForegroundColor Green
    Write-Host "  └──────────────────────────────────────────────────────────┘" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Options:" -ForegroundColor Cyan
    Write-Host "    [1] From Meta AI Create Page URL (uses Meta AI music)"
    Write-Host "    [2] From Local Video File (uses Pixabay music)"
    Write-Host ""
    $option = Read-Host "  Select option"
    
    if ($option -eq "1") {
        Write-Host ""
        $url = Read-Host "  Enter Meta AI create page URL"
        
        if ([string]::IsNullOrWhiteSpace($url)) {
            Write-Host "  [!] No URL entered" -ForegroundColor Yellow
            return
        }
        
        Write-Host ""
        Write-Host "  [*] Downloading video with music from Meta AI..." -ForegroundColor Green
        python -c "
from backend.core.video_engine.meta_ai_generator import run_add_music_to_create_url
result = run_add_music_to_create_url('$url', headless=False)
if result and result.get('success'):
    print(f'[OK] Downloaded: {result[\"file_path\"]}')
    print(f'[OK] Music: {\"Yes\" if result.get(\"music_added\") else \"No\"}')
else:
    print('[X] Download failed')
"
    }
    elseif ($option -eq "2") {
        Write-Host ""
        $videoPath = Read-Host "  Enter video file path"
        
        if ([string]::IsNullOrWhiteSpace($videoPath)) {
            Write-Host "  [!] No path entered" -ForegroundColor Yellow
            return
        }
        
        if (-not (Test-Path $videoPath)) {
            Write-Host "  [!] File not found: $videoPath" -ForegroundColor Red
            return
        }
        
        Write-Host ""
        $prompt = Read-Host "  Enter video description/prompt (optional, helps mood detection)"
        
        Write-Host ""
        Write-Host "  [*] Analyzing video and adding Pixabay music..." -ForegroundColor Green
        
        if ([string]::IsNullOrWhiteSpace($prompt)) {
            python -m backend.core.video_engine.audio_enhancer "$videoPath"
        } else {
            python -m backend.core.video_engine.audio_enhancer "$videoPath" --prompt "$prompt"
        }
    }
    else {
        Write-Host "  [!] Invalid option" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Read-Host "  Press Enter to continue"
}

function Show-ContentPlan {
    Write-Host ""
    Write-Host "  [*] Generating daily content plan..." -ForegroundColor Green
    Write-Host ""
    python backend/core/ai_engine/content_curator.py
    Write-Host ""
    Read-Host "  Press Enter to continue"
}

function Start-Backend {
    Write-Host ""
    Write-Host "  [*] Starting backend server on port 8002..." -ForegroundColor Green
    Write-Host "  [*] Press Ctrl+C to stop" -ForegroundColor Gray
    Write-Host ""
    python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8002 --reload
}

# Main Loop
while ($true) {
    Show-Banner
    Show-Menu
    
    $choice = Read-Host "  Select option"
    
    switch ($choice) {
        "1" { Run-AutoPipeline }
        "2" { Run-CustomPrompt -Upload $true }
        "3" { Run-CustomPrompt -Upload $false }
        "4" { Run-BatchMode }
        "5" { Run-DownloadURL }
        "6" { Run-ReEngineerUpload }
        "7" { Run-AddMusic }
        "8" { Run-Login }
        "9" { Show-ContentPlan }
        "S" { Start-Backend }
        "s" { Start-Backend }
        "0" { 
            Write-Host "`n  Goodbye!" -ForegroundColor Cyan
            exit 
        }
        default {
            Write-Host "`n  [!] Invalid option" -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
}
