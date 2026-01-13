import os
import requests
from dotenv import load_dotenv

# Load config
load_dotenv("d:/oneclick_reels_ai/config.env")

PAGE_ID = os.getenv("FB_PAGE_ID")
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

print(f"DEBUG: Loaded PAGE_ID: {PAGE_ID}")
print(f"DEBUG: Access Token starts with: {ACCESS_TOKEN[:10] if ACCESS_TOKEN else 'None'}...")

def check_token():
    if not ACCESS_TOKEN:
        print("❌ Error: FB_ACCESS_TOKEN is missing in config.env")
        return

    # 1. Debug Token
    url = f"https://graph.facebook.com/debug_token?input_token={ACCESS_TOKEN}&access_token={ACCESS_TOKEN}"
    res = requests.get(url)
    data = res.json()
    
    if "error" in data:
        print(f"❌ Token Validtion Failed: {data['error']['message']}")
        return

    token_data = data.get("data", {})
    print("\n[Token Info]")
    print(f"Valid: {token_data.get('is_valid')}")
    print(f"Type: {token_data.get('type')}")
    print(f"Scopes: {', '.join(token_data.get('scopes', []))}")
    print(f"Expires At: {token_data.get('expires_at')}")

    # 2. Check Page Access
    if not PAGE_ID:
        print("❌ Error: FB_PAGE_ID is missing in config.env")
        return

    print(f"\n[Checking Page ID: {PAGE_ID}]")
    page_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}?fields=id,name,access_token&access_token={ACCESS_TOKEN}"
    page_res = requests.get(page_url)
    
    page_token = ACCESS_TOKEN  # Default to user token
    if page_res.status_code == 200:
        page_info = page_res.json()
        print(f"✅ Page Found: {page_info.get('name')} (ID: {page_info.get('id')})")
        if "access_token" in page_info:
            page_token = page_info["access_token"]
            print("✅ Token has page access (Page Access Token retrieved)")
        else:
             print("⚠️ Token might be a User Token (not a Page Token), but has some access.")
    else:
        print(f"❌ Failed to access page: {page_res.text}")
        
    # 3. Test /video_reels endpoint access (dry run) - USE PAGE TOKEN
    print("\n[Testing /video_reels endpoint capability]")
    test_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/video_reels"
    # Use the PAGE TOKEN, not the user token
    test_res = requests.get(test_url, params={"access_token": page_token})
    print(f"Endpoint Check Response: {test_res.status_code} - {test_res.text}")

if __name__ == "__main__":
    check_token()
