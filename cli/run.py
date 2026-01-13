"""
OneClick Reels AI - CLI Runner
Run with: python -m cli.run
"""
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv("config.env")

# Initialize logging
from backend.config.logging_config import setup_logging
setup_logging()

import logging
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from backend.config.settings import settings
from backend.utils.health_checker import health_checker
from backend.utils.cache_manager import cache_manager

logger = logging.getLogger(__name__)
console = Console()

def show_banner():
    console.print(Panel.fit(
        "[bold cyan]🎬 OneClick Reels AI[/bold cyan]\n"
        "[dim]Automated Short-Form Video Generator[/dim]",
        border_style="cyan"
    ))

def show_menu():
    table = Table(show_header=False, box=None)
    table.add_column("Option", style="bold yellow")
    table.add_column("Description")
    
    table.add_row("1", "🚀 One-Click Mode (Full Auto)")
    table.add_row("2", "🎯 Select Niche Manually")
    table.add_row("3", "📝 Generate Script Only")
    table.add_row("4", "🎬 Create Video Only")
    table.add_row("5", "📤 Upload Existing Video")
    table.add_row("6", "⚙️  Check Configuration")
    table.add_row("7", "📁 List Available Assets")
    table.add_row("8", "🏥 Health Check")
    table.add_row("9", "🧹 Clear Cache")
    table.add_row("0", "❌ Exit")
    
    console.print(table)
    console.print()

def check_configuration():
    """Check configuration status."""
    console.print("\n[bold green]🔧 Configuration Status[/bold green]\n")
    
    config_status = settings.get_all_settings()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Status")
    
    table.add_row("OpenAI API", "✅ Configured" if config_status["has_openai_key"] else "❌ Missing")
    table.add_row("YouTube API", "✅ Configured" if config_status["has_youtube_credentials"] else "❌ Missing")
    table.add_row("Facebook API", "✅ Configured" if config_status["has_facebook_credentials"] else "❌ Missing")
    table.add_row("Pexels API", "✅ Configured" if config_status["has_pexels_key"] else "❌ Missing")
    table.add_row("Pixabay API", "✅ Configured" if config_status["has_pixabay_key"] else "❌ Missing")
    table.add_row("Caching", "✅ Enabled" if config_status["enable_caching"] else "⚪ Disabled")
    
    console.print(table)

def run_health_check():
    """Run health check."""
    console.print("\n[bold green]🏥 Running Health Check...[/bold green]\n")
    
    with console.status("[bold green]Checking services..."):
        health_status = health_checker.health_check_with_cache()
    
    status_color = "green" if health_status["overall_status"] == "healthy" else "yellow" if health_status["overall_status"] == "degraded" else "red"
    console.print(f"[bold {status_color}]Overall: {health_status['overall_status'].upper()}[/bold {status_color}]")
    console.print(f"Healthy: {health_status['healthy_services']}/{health_status['total_services']}")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Service", style="cyan")
    table.add_column("Status")
    
    for service_name, service_data in health_status["services"].items():
        status = service_data["status"]
        icon = "✅" if status == "healthy" else "❌"
        table.add_row(service_name.title(), f"{icon} {status.title()}")
    
    console.print(table)

def clear_cache():
    """Clear cache."""
    console.print("\n[bold yellow]🧹 Cache Management[/bold yellow]\n")
    
    stats = cache_manager.get_cache_stats()
    console.print(f"Total entries: {stats['total_entries']}")
    console.print(f"Total size: {stats['total_size_mb']} MB")
    
    if stats['total_entries'] > 0 and Confirm.ask("Clear expired entries?"):
        cleared = cache_manager.clear_expired()
        console.print(f"[green]✅ Cleared {cleared} entries[/green]")

def one_click_mode():
    """Full automated mode."""
    from backend.core.ai_engine.niche_selector import select_niche
    from backend.core.ai_engine.script_generator import generate_script
    from backend.core.ai_engine.caption_hashtags import generate_caption
    from backend.core.video_engine.voiceover import generate_voiceover
    from backend.core.video_engine.pexels_downloader import get_video_for_keyword
    from backend.core.video_engine.advanced_video_builder import advanced_video_builder
    from backend.core.post_engine.youtube import upload_youtube_short
    from backend.core.post_engine.facebook import upload_facebook_reel
    
    console.print("\n[bold green]🚀 ONE-CLICK MODE[/bold green]\n")
    
    try:
        # 1. Select niche
        console.print("[cyan]🎯 Selecting niche...[/cyan]")
        niche_data = select_niche()
        niche, topic = niche_data["niche"], niche_data["topic"]
        console.print(f"Selected: {niche} - {topic}")
        
        # 2. Generate script
        console.print("[cyan]✍️ Generating script...[/cyan]")
        script = generate_script(niche, topic)
        console.print(f"Script: {len(script)} chars")
        
        # 3. Generate voiceover
        console.print("[cyan]🎤 Generating voiceover...[/cyan]")
        voiceover = generate_voiceover(script, niche=niche)
        
        # 4. Get background video
        console.print("[cyan]🎥 Getting background video...[/cyan]")
        video_path = get_video_for_keyword(topic)
        
        # 5. Build video
        console.print("[cyan]🎬 Building video...[/cyan]")
        output_path = f"output/reel_{int(__import__('time').time())}.mp4"
        final_video = advanced_video_builder.build_video_gpu_accelerated(
            background_video=video_path,
            voiceover_audio=voiceover,
            script=script,
            niche=niche,
            output_path=output_path,
            quality="high"
        )
        
        console.print(f"[green]✅ Video created: {final_video}[/green]")
        
        # 6. Upload
        meta = None
        if Confirm.ask("Upload to YouTube?"):
            meta = generate_caption(niche, topic)
            video_id = upload_youtube_short(final_video, meta["title"], meta["description"])
            console.print(f"[green]✅ Uploaded to YouTube: https://youtube.com/shorts/{video_id}[/green]")

        if Confirm.ask("Upload to Facebook?"):
            if not meta:
                meta = generate_caption(niche, topic)
            
            # Use title + description for Facebook caption
            fb_caption = f"{meta['title']}\n\n{meta['description']}"
            fb_id = upload_facebook_reel(final_video, fb_caption)
            console.print(f"[green]✅ Uploaded to Facebook. ID: {fb_id}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        logger.error(f"One-click mode error: {e}", exc_info=True)

def main():
    """Main CLI loop."""
    try:
        settings.create_directories()
        show_banner()
        
        while True:
            show_menu()
            choice = Prompt.ask("Choose option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
            
            try:
                if choice == "0":
                    console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                elif choice == "1":
                    one_click_mode()
                elif choice == "6":
                    check_configuration()
                elif choice == "8":
                    run_health_check()
                elif choice == "9":
                    clear_cache()
                else:
                    console.print(f"[yellow]⚠️ Option {choice} not implemented yet[/yellow]")
                
                console.print("\n" + "="*50 + "\n")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Cancelled[/yellow]")
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")
                logger.error(f"Menu error: {e}", exc_info=True)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")

if __name__ == "__main__":
    main()
