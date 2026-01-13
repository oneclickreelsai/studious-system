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
print("INSTAGRAM INTEGRATION CHECK")
print("="*50)

if not PAGE_ID or not ACCESS_TOKEN:
    print("[X] Missing Credentials")
    exit(1)

# 1. Check Permissions
print("\n[*] Checking Token Permissions...")
try:
    perm_res = requests.get(
        "https://graph.facebook.com/v20.0/me/permissions",
        params={"access_token": ACCESS_TOKEN}
    )
    perms = perm_res.json().get('data', [])
    granted = [p['permission'] for p in perms if p['status'] == 'granted']
    
    required = ['instagram_basic', 'instagram_content_publish']
    missing = [p for p in required if p not in granted]
    
    if missing:
        print(f"[!] MISSING PERMISSIONS for Instagram: {', '.join(missing)}")
        print("    You need to regenerate the token with these scopes selected.")
    else:
        print("[OK] All Instagram permissions granted!")
        
except Exception as e:
    print(f"[X] Failed to check permissions: {e}")

# 2. Check Linked Account
print("\n[*] Checking for Linked Instagram Account...")
try:
    link_res = requests.get(
        f"https://graph.facebook.com/v20.0/{PAGE_ID}",
        params={
            "fields": "instagram_business_account",
            "access_token": ACCESS_TOKEN
        }
    )
    data = link_res.json()
    
    if 'instagram_business_account' in data:
        ig_id = data['instagram_business_account']['id']
        print(f"[OK] Found Linked Instagram Account!")
        print(f"    IG Business ID: {ig_id}")
        print("\n[ACTION] I will add this ID to your config.")
    else:
        print("[X] No Instagram Account linked to this Facebook Page.")
        print("    Please go to Facebook Page Settings -> Linked Accounts -> Instagram and connect it.")
        
except Exception as e:
    print(f"[X] Link check failed: {e}")
