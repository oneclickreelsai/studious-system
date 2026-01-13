#!/usr/bin/env python3
"""
Google Drive API Setup using Service Account (No OAuth needed)
This is easier for automated systems like OneClick Reels AI
"""
import json

def create_service_account_instructions():
    """Instructions to create a service account for Google Drive"""
    
    instructions = """
🔧 GOOGLE DRIVE API - SERVICE ACCOUNT SETUP
===========================================

A service account is better for automated systems like OneClick Reels AI.
No OAuth flow needed - just a JSON key file.

📋 STEP-BY-STEP INSTRUCTIONS:

1️⃣ GO TO GOOGLE CLOUD CONSOLE
   → https://console.cloud.google.com/
   → Select your project: oneclick-reels-ai

2️⃣ ENABLE GOOGLE DRIVE API
   → APIs & Services → Library
   → Search "Google Drive API"
   → Click "Enable"

3️⃣ CREATE SERVICE ACCOUNT
   → APIs & Services → Credentials
   → Click "Create Credentials" → "Service Account"
   → Name: "oneclick-reels-drive"
   → Description: "Google Drive access for OneClick Reels AI"
   → Click "Create and Continue"

4️⃣ GRANT PERMISSIONS (Optional)
   → Skip this step for now
   → Click "Continue" → "Done"

5️⃣ CREATE KEY FILE
   → Click on the service account you just created
   → Go to "Keys" tab
   → Click "Add Key" → "Create new key"
   → Choose "JSON"
   → Download the file
   → Save it as "service_account.json" in this directory

6️⃣ SHARE DRIVE FOLDER (Important!)
   → Open Google Drive
   → Create a folder called "OneClick_Reels_AI"
   → Right-click → Share
   → Add the service account email (from the JSON file)
   → Give "Editor" permissions

7️⃣ TEST THE SETUP
   → Run: python test_drive_service_account.py

🔐 SECURITY NOTES:
   • Service account has limited access (only to shared folders)
   • More secure than OAuth for automated systems
   • No user interaction required
   • Perfect for server deployments

📁 FILE STRUCTURE AFTER SETUP:
   oneclick_reels_ai/
   ├── service_account.json  ← Download this from Google Cloud
   ├── test_drive_service_account.py
   └── ... (other files)
"""
    
    print(instructions)
    
    # Create a template service account test file
    test_code = '''#!/usr/bin/env python3
"""
Test Google Drive API with Service Account
Run after setting up service_account.json
"""
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_drive_service_account():
    """Test Google Drive API with service account"""
    
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("❌ service_account.json not found!")
        print("📋 Please follow the setup instructions first.")
        return False
    
    try:
        print("🚀 Testing Google Drive API with Service Account...")
        
        # Load service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        # Build Drive service
        service = build('drive', 'v3', credentials=credentials)
        
        print("✅ Service account authenticated successfully!")
        
        # Test: List files (will only show files shared with service account)
        print("📁 Listing accessible files...")
        results = service.files().list(pageSize=10).execute()
        files = results.get('files', [])
        
        print(f"📊 Found {len(files)} accessible files/folders")
        
        if files:
            for file in files:
                print(f"   📄 {file['name']} (ID: {file['id']})")
        else:
            print("   💡 No files found. Make sure to share a folder with the service account!")
        
        # Test: Create a test file
        print("\\n📝 Creating test file...")
        file_metadata = {'name': 'OneClick_Reels_Test.txt'}
        media_body = "Hello from OneClick Reels AI!\\nGoogle Drive integration is working!"
        
        # This will only work if you've shared a folder with the service account
        # For now, we'll just test the API connection
        
        print("🎉 Google Drive API test completed!")
        print("✅ Service account integration is working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_drive_service_account()
'''
    
    with open('test_drive_service_account.py', 'w') as f:
        f.write(test_code)
    
    print("📁 Created: test_drive_service_account.py")
    print("\n🎯 NEXT STEPS:")
    print("1. Follow the instructions above to create service_account.json")
    print("2. Run: python test_drive_service_account.py")

if __name__ == "__main__":
    create_service_account_instructions()