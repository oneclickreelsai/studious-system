"""
YouTube OAuth2 Authentication Setup

This script helps you get a new refresh token for YouTube API.
Run this when you see "Token has been expired or revoked" error.

Usage:
    python scripts/youtube_auth.py
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv("config.env")

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json

# YouTube API scopes
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

def get_credentials():
    """Get or refresh YouTube credentials."""
    
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
    
    if not client_id or not client_secret:
        print("[X] Missing YOUTUBE_CLIENT_ID or YOUTUBE_CLIENT_SECRET in config.env")
        return None
    
    print("\n" + "=" * 60)
    print("YOUTUBE OAUTH2 AUTHENTICATION")
    print("=" * 60)
    print(f"\nClient ID: {client_id[:20]}...")
    print(f"Client Secret: {client_secret[:10]}...")
    print(f"Refresh Token: {'Set' if refresh_token else 'Not set'}")
    
    # Try to use existing refresh token first
    if refresh_token:
        print("\n[*] Testing existing refresh token...")
        try:
            creds = Credentials(
                None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
            )
            creds.refresh(Request())
            print("[OK] Existing token is valid!")
            print(f"    Access Token: {creds.token[:30]}...")
            return creds
        except Exception as e:
            print(f"[X] Token refresh failed: {e}")
            print("[*] Need to re-authenticate...")
    
    # Create OAuth flow for new authentication
    print("\n[*] Starting OAuth2 flow...")
    print("[*] A browser window will open for authentication.")
    print("[*] Please sign in with your YouTube account.\n")
    
    # Create client config from env vars
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/", "urn:ietf:wg:oauth:2.0:oob"]
        }
    }
    
    try:
        # Try local server first, fallback to manual OOB flow
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        
        try:
            creds = flow.run_local_server(port=8080, prompt='consent', access_type='offline')
        except Exception as e:
            print(f"[!] Local server failed: {e}")
            print("[*] Using manual authorization flow...\n")
            
            # Manual flow - user copies URL and pastes code
            flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            
            print("=" * 60)
            print("MANUAL AUTHORIZATION")
            print("=" * 60)
            print("\n1. Open this URL in your browser:\n")
            print(auth_url)
            print("\n2. Sign in and authorize the app")
            print("3. Copy the authorization code and paste it below\n")
            
            code = input("Enter authorization code: ").strip()
            flow.fetch_token(code=code)
            creds = flow.credentials
        
        print("\n[OK] Authentication successful!")
        print(f"\n{'=' * 60}")
        print("NEW REFRESH TOKEN (copy this to config.env):")
        print("=" * 60)
        print(f"\nYOUTUBE_REFRESH_TOKEN={creds.refresh_token}")
        print(f"\n{'=' * 60}")
        
        # Ask to update config.env
        update = input("\nUpdate config.env automatically? (y/n): ").strip().lower()
        if update == 'y':
            update_config_env(creds.refresh_token)
        
        return creds
        
    except Exception as e:
        print(f"\n[X] OAuth flow failed: {e}")
        return None


def update_config_env(new_refresh_token):
    """Update the refresh token in config.env"""
    try:
        config_path = PROJECT_ROOT / "config.env"
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Replace the refresh token line
        import re
        pattern = r'YOUTUBE_REFRESH_TOKEN=.*'
        replacement = f'YOUTUBE_REFRESH_TOKEN={new_refresh_token}'
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
        else:
            new_content = content + f"\nYOUTUBE_REFRESH_TOKEN={new_refresh_token}\n"
        
        with open(config_path, 'w') as f:
            f.write(new_content)
        
        print("[OK] config.env updated successfully!")
        print("[*] Please restart the pipeline to use the new token.")
        
    except Exception as e:
        print(f"[X] Failed to update config.env: {e}")
        print("[*] Please update manually.")


def test_upload_capability():
    """Test if we can upload to YouTube."""
    from googleapiclient.discovery import build
    
    creds = get_credentials()
    if not creds:
        return False
    
    try:
        youtube = build("youtube", "v3", credentials=creds)
        
        # Test by getting channel info
        request = youtube.channels().list(part="snippet", mine=True)
        response = request.execute()
        
        if response.get("items"):
            channel = response["items"][0]["snippet"]
            print(f"\n[OK] Connected to channel: {channel['title']}")
            return True
        else:
            print("[X] No channel found for this account")
            return False
            
    except Exception as e:
        print(f"[X] API test failed: {e}")
        return False


if __name__ == "__main__":
    print("\nYouTube OAuth2 Setup")
    print("=" * 40)
    
    # Check for required packages
    try:
        import google_auth_oauthlib
    except ImportError:
        print("[X] Missing package: google-auth-oauthlib")
        print("[*] Install with: pip install google-auth-oauthlib")
        sys.exit(1)
    
    creds = get_credentials()
    
    if creds:
        print("\n[*] Testing YouTube API access...")
        test_upload_capability()
    
    print("\nDone!")
