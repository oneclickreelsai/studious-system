import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load config
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / "config.env", override=True)

PAGE_ID = os.getenv("FB_PAGE_ID")
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

print(f"Checking Page ID: {PAGE_ID}")

url = f"https://graph.facebook.com/v20.0/{PAGE_ID}"
params = {"access_token": ACCESS_TOKEN, "fields": "name,followers_count,link,username"}

try:
    res = requests.get(url, params=params)
    print(f"Status: {res.status_code}")
    print(res.text)
except Exception as e:
    print(f"Error: {e}")
