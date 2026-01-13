import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load config
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / "config.env", override=True)

ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
PAGE_ID = os.getenv("FB_PAGE_ID")

print("="*50)
print("FACEBOOK IDENTITY CHECK")
print("="*50)

if not ACCESS_TOKEN:
    print("[X] No Token")
    exit()

# Check ME
url = "https://graph.facebook.com/v20.0/me"
params = {"access_token": ACCESS_TOKEN}

try:
    res = requests.get(url, params=params)
    data = res.json()
    print(f"Token Owner: {data.get('name')}")
    print(f"Owner ID: {data.get('id')}")
    
    # Check if Owner ID matches Page ID
    if str(data.get('id')) == str(PAGE_ID):
        print("MATCH! The Token belongs directly to the Page ID.")
    else:
        print(f"MISMATCH. Token Owner ID ({data.get('id')}) != Config Page ID ({PAGE_ID})")
        
    print(f"\nRaw Response: {data}")
    
except Exception as e:
    print(f"Error: {e}")
