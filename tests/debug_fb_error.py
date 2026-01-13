import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load config
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / "config.env", override=True)

PAGE_ID = os.getenv("FB_PAGE_ID")
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

print("="*50)
print("DEBUGGING FACEBOOK ERROR")
print("="*50)
print(f"Page ID: {PAGE_ID}")

# Exchange User Token for Page Token
print("\n[*] Exchanging User Token for Page Token...")
token_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}?fields=access_token&access_token={ACCESS_TOKEN}"
token_res = requests.get(token_url)
if token_res.status_code == 200 and "access_token" in token_res.json():
    PAGE_TOKEN = token_res.json()["access_token"]
    print("✅ Got Page Token!")
else:
    PAGE_TOKEN = ACCESS_TOKEN
    print(f"⚠️ Could not get Page Token, using User Token: {token_res.text}")

# Attempt Initialize Upload
url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/video_reels"
alt_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/videos"

payload = {
    "upload_phase": "start",
    "access_token": PAGE_TOKEN  # Use Page Token!
}

print(f"\n[*] Sending POST to: {url}")
try:
    res = requests.post(url, data=payload)
    print(f"Status Code: {res.status_code}")
    print(res.text)
    
    if res.status_code == 400 or res.status_code == 404:
        print(f"\n[*] Retrying with ALT URL: {alt_url}")
        res2 = requests.post(alt_url, data=payload)
        print(f"ALT Status Code: {res2.status_code}")
        print(res2.text)

    print("---------------------")
    
    if res.status_code == 400:
        print("\n[ANALYSIS]")
        if "(#368)" in res.text:
            print("❌ SPAM BLOCK CONFIRMED. Facebook has temporarily blocked you from posting.")
            print("   You must wait (usually 24h).")
        elif "Permissions" in res.text:
            print("❌ PERMISSION ERROR. Token doesn't have 'publish_video'.")
        else:
            print("❌ UNKNOWN ERROR. See above.")

except Exception as e:
    print(f"Code Error: {e}")
