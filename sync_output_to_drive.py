#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sync Output Folder to Google Drive
Automatically uploads all files from output/ folder to Google Drive
"""
import os
import sys
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import datetime
import hashlib

# Configuration
SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = 'drive_oauth_token.json'
OUTPUT_DIR = 'output'
DRIVE_FOLDER_NAME = 'OneClick_Reels_AI'
SYNC_LOG_FILE = 'sync_log.json'

def load_credentials():
    """Load existing OAuth credentials"""
    if not os.path.exists(TOKEN_FILE):
        safe_print("[ERROR] OAuth token not found. Run test_drive_oauth_fixed.py first!")
        return None
    
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            safe_print("[*] Refreshing expired token...")
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        else:
            safe_print("[ERROR] Invalid credentials. Re-run OAuth setup.")
            return None
    
    return creds

def get_file_hash(file_path):
    """Get MD5 hash of file for change detection"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def load_sync_log():
    """Load sync log to track uploaded files"""
    if os.path.exists(SYNC_LOG_FILE):
        with open(SYNC_LOG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_sync_log(sync_log):
    """Save sync log"""
    with open(SYNC_LOG_FILE, 'w') as f:
        json.dump(sync_log, f, indent=2)

def find_or_create_folder(service, folder_name, parent_id=None):
    """Find or create a folder in Google Drive"""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    results = service.files().list(q=query).execute()
    folders = results.get('files', [])
    
    if folders:
        return folders[0]['id']
    
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        folder_metadata['parents'] = [parent_id]
    
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    safe_print(f"[+] Created folder: {folder_name}")
    return folder.get('id')

def get_mime_type(file_path):
    """Get MIME type based on file extension"""
    ext = Path(file_path).suffix.lower()
    mime_types = {
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.txt': 'text/plain',
        '.json': 'application/json'
    }
    return mime_types.get(ext, 'application/octet-stream')

def safe_print(text):
    """Print text safely, handling Unicode characters on Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace non-ASCII characters with ?
        print(text.encode('ascii', 'replace').decode('ascii'))

def upload_file(service, local_path, drive_folder_id, sync_log):
    """Upload a single file to Google Drive"""
    file_path = Path(local_path)
    file_name = file_path.name
    
    file_hash = get_file_hash(local_path)
    sync_key = str(file_path)
    
    if sync_key in sync_log:
        if sync_log[sync_key].get('hash') == file_hash:
            safe_print(f"[SKIP] {file_name} (already synced)")
            return sync_log[sync_key]['drive_id']
    
    try:
        stats = file_path.stat()
        file_size_mb = round(stats.st_size / (1024 * 1024), 2)
        
        safe_print(f"[UPLOAD] {file_name} ({file_size_mb} MB)...")
        
        file_metadata = {
            'name': file_name,
            'parents': [drive_folder_id]
        }
        
        mime_type = get_mime_type(local_path)
        media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
        
        request = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,webViewLink,size'
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                safe_print(f"   Progress: {progress}%")
        
        sync_log[sync_key] = {
            'drive_id': response['id'],
            'drive_name': response['name'],
            'hash': file_hash,
            'size': response.get('size', '0'),
            'uploaded_at': datetime.datetime.now().isoformat(),
            'web_link': response.get('webViewLink', '')
        }
        
        safe_print(f"   [OK] Uploaded: {response['name']}")
        safe_print(f"   Link: {response.get('webViewLink', 'N/A')}")
        
        return response['id']
        
    except HttpError as e:
        safe_print(f"   [ERROR] Upload failed: {e}")
        return None
    except Exception as e:
        safe_print(f"   [ERROR] {e}")
        return None

def sync_directory(service, local_dir, drive_folder_id, sync_log, folder_name=""):
    """Recursively sync a directory"""
    local_path = Path(local_dir)
    
    if not local_path.exists():
        safe_print(f"[ERROR] Directory not found: {local_dir}")
        return
    
    safe_print(f"\n[FOLDER] Syncing: {folder_name or local_path.name}")
    safe_print("-" * 50)
    
    items = list(local_path.iterdir())
    files = [item for item in items if item.is_file()]
    dirs = [item for item in items if item.is_dir()]
    
    for file_path in files:
        upload_file(service, str(file_path), drive_folder_id, sync_log)
    
    for dir_path in dirs:
        subdir_name = dir_path.name
        sub_drive_folder_id = find_or_create_folder(service, subdir_name, drive_folder_id)
        sync_directory(service, str(dir_path), sub_drive_folder_id, sync_log, subdir_name)

def main():
    """Main sync function"""
    safe_print("=" * 50)
    safe_print("OneClick Reels AI - Output Folder Sync")
    safe_print("=" * 50)
    
    creds = load_credentials()
    if not creds:
        return
    
    service = build('drive', 'v3', credentials=creds)
    safe_print("[OK] Connected to Google Drive")
    
    sync_log = load_sync_log()
    
    main_folder_id = find_or_create_folder(service, DRIVE_FOLDER_NAME)
    safe_print(f"[*] Using Drive folder: {DRIVE_FOLDER_NAME}")
    
    output_folder_id = find_or_create_folder(service, "Generated_Content", main_folder_id)
    
    start_time = datetime.datetime.now()
    
    try:
        sync_directory(service, OUTPUT_DIR, output_folder_id, sync_log, "output")
        
        save_sync_log(sync_log)
        
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        
        safe_print("\n" + "=" * 50)
        safe_print("[SUCCESS] Sync completed!")
        safe_print(f"Duration: {duration.total_seconds():.1f} seconds")
        safe_print(f"Total files tracked: {len(sync_log)}")
        safe_print(f"Drive folder: https://drive.google.com/drive/folders/{main_folder_id}")
        safe_print("=" * 50)
        
    except Exception as e:
        safe_print(f"\n[ERROR] Sync failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()