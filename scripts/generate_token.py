
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from rich import print

# Scopes required for uploading
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_refresh_token():
    print("[bold cyan]🔐 Generating New YouTube Refresh Token[/bold cyan]")
    
    # Load config directly or ask user
    client_id = os.getenv("YOUTUBE_CLIENT_ID") or "979521830362-3gsndbk7qet18q41pbdnem3mnnbg902o.apps.googleusercontent.com"
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET") or "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"
    
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
            }
        },
        SCOPES
    )

    print("\n[yellow]1. I will launch a browser window (or give you a link).[/yellow]")
    print("[yellow]2. Login with your PERSONAL account.[/yellow]")
    print("[yellow]3. If you see 'Google hasn't verified this app', click 'Advanced' -> 'Go to oneclick_reels_ai (unsafe)'.[/yellow]")
    print("[yellow]4. Allow the permissions.[/yellow]")
    
    try:
        creds = flow.run_local_server(port=0)
    except OSError:
        print("\n[red]Could not launch local server. Trying console mode...[/red]")
        creds = flow.run_console()
        
    print("\n[green]✅ Authorization Successful![/green]")
    print(f"\n[bold]Configuration for config.env:[/bold]")
    print(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")
    
    # Auto-update if possible
    # (Simplified for now, just print it)

if __name__ == "__main__":
    get_refresh_token()
