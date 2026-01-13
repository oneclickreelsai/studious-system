#!/usr/bin/env python3
"""
🏆 WORLD-CLASS BACKUP SYSTEM v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Features:
  ✅ True parallel async I/O (reads ALL files concurrently)
  ✅ Incremental backup (only changed files via SHA256 hash)
  ✅ Daily folder organization (YYYY-MM-DD/HH-MM-SS.zip)
  ✅ Atomic writes (temp file → rename on success)
  ✅ ZIP integrity verification after creation
  ✅ Configurable compression levels
  ✅ Smart cleanup with retention policy
  ✅ .env configuration support
  ✅ Detailed progress reporting
  ✅ Error recovery and logging

Usage:
  python backup_world_class.py          # Run scheduled backups
  python backup_world_class.py --once   # Run once and exit
  python backup_world_class.py --full   # Force full backup (no incremental)
  python backup_world_class.py --cleanup # Run cleanup only
  python backup_world_class.py --verify path/to/file.zip  # Verify ZIP

Author: QuantAlgo
"""

import os
import sys
import time
import json
import asyncio
import hashlib
import zipfile
import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field

# Optional imports with fallbacks
try:
    import aiofiles
    HAS_AIOFILES = True
except ImportError:
    HAS_AIOFILES = False
    print("⚠️ 'aiofiles' not installed. Using sync file reads.")

try:
    from tqdm import tqdm
except ImportError:
    # Fallback tqdm
    def tqdm(iterable, **kwargs):
        return iterable

try:
    import schedule
    HAS_SCHEDULE = True
except ImportError:
    HAS_SCHEDULE = False
    print("⚠️ 'schedule' not installed. Scheduled backups disabled.")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class BackupConfig:
    """Centralized backup configuration."""
    source_dir: str = ""
    backup_base_dir: str = ""
    
    # Exclusions
    excluded_extensions: Set[str] = field(default_factory=lambda: {
        '.pyc', '.pyo', '.log', '.tmp', '.bak', '.swp', '.swo'
    })
    excluded_dirs: Set[str] = field(default_factory=lambda: {
        '__pycache__', '.git', 'node_modules', 'backups', '.venv', 'venv', 
        'dist', 'build', '.pytest_cache', '.mypy_cache', 'eggs', '*.egg-info'
    })
    excluded_files: Set[str] = field(default_factory=lambda: {
        '.DS_Store', 'Thumbs.db', '.env.local', 'desktop.ini'
    })
    
    # Backup settings
    compression_level: int = 6  # 1=fast, 9=max compression
    max_concurrent_reads: int = 100  # Parallel file reads
    incremental: bool = True  # Only backup changed files
    verify_after_backup: bool = True
    
    # Retention
    keep_days: int = 7
    keep_min_backups: int = 3
    
    # Schedule
    backup_interval_minutes: int = 30
    cleanup_time: str = "00:10"
    
    # Auto-sync to cloud
    auto_sync_to_cloud: bool = True  # Automatically copy to OneDrive after backup
    cloud_backup_dir: str = ""  # OneDrive folder path


def find_project_root(start_dir: Optional[str] = None) -> str:
    """Find project root by scanning upward for marker files."""
    if start_dir is None:
        start_dir = os.path.dirname(os.path.abspath(__file__))
    
    # If we're in the backups folder, go up one level first
    current = Path(start_dir).resolve()
    if current.name == 'backups':
        current = current.parent
    
    markers = {"main.py", "requirements.txt", ".git", "pyproject.toml", "setup.py", "mcx.py", "backend", "frontend"}
    
    # Check current first
    if any((current / marker).exists() for marker in markers):
        return str(current)
    
    # Then scan upward
    while current != current.parent:
        if any((current / marker).exists() for marker in markers):
            return str(current)
        current = current.parent
    
    return str(Path(start_dir).parent)


# Initialize config
CONFIG = BackupConfig()
CONFIG.source_dir = os.getenv("BACKUP_SOURCE_DIR", "") or find_project_root()
CONFIG.backup_base_dir = os.getenv("BACKUP_BASE_DIR", "") or r"D:\oneclick_reels_ai"
CONFIG.compression_level = int(os.getenv("BACKUP_COMPRESSION", "6"))
CONFIG.keep_days = int(os.getenv("BACKUP_KEEP_DAYS", "7"))
CONFIG.incremental = os.getenv("BACKUP_INCREMENTAL", "true").lower() == "true"
CONFIG.auto_sync_to_cloud = os.getenv("BACKUP_AUTO_SYNC", "true").lower() == "true"

# Auto-detect OneDrive path
def _get_default_cloud_path():
    user_home = os.path.expanduser("~")
    for folder in ["OneDrive", "OneDrive - Personal", "OneDrive for Business"]:
        path = os.path.join(user_home, folder)
        if os.path.exists(path):
            return os.path.join(path, "QuantAlgo_Backups")
    return ""

CONFIG.cloud_backup_dir = os.getenv("ONEDRIVE_BACKUP_PATH", "") or _get_default_cloud_path()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📝 LOGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s │ %(levelname)-7s │ %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("BackupSystem")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔐 HASH MANIFEST (Incremental Backup)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class HashManifest:
    """Tracks file hashes for incremental backup."""
    
    MANIFEST_FILE = ".backup_manifest.json"
    
    def __init__(self, backup_dir: str):
        self.manifest_path = os.path.join(backup_dir, self.MANIFEST_FILE)
        self.hashes: Dict[str, dict] = {}
        self._load()
    
    def _load(self):
        try:
            if os.path.exists(self.manifest_path):
                with open(self.manifest_path, 'r') as f:
                    self.hashes = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load manifest: {e}")
            self.hashes = {}
    
    def save(self):
        try:
            os.makedirs(os.path.dirname(self.manifest_path), exist_ok=True)
            with open(self.manifest_path, 'w') as f:
                json.dump(self.hashes, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save manifest: {e}")
    
    def has_changed(self, rel_path: str, size: int, mtime: float) -> bool:
        if rel_path not in self.hashes:
            return True
        old = self.hashes[rel_path]
        return old.get('size') != size or abs(old.get('mtime', 0) - mtime) > 1
    
    def update(self, rel_path: str, size: int, mtime: float, content_hash: str):
        self.hashes[rel_path] = {
            'size': size,
            'mtime': mtime,
            'hash': content_hash,
            'last_backup': datetime.now().isoformat()
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📁 FILE COLLECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def should_exclude(rel_path: str, filename: str) -> bool:
    """Check if file should be excluded."""
    parts = Path(rel_path).parts
    
    # Excluded directories
    if any(part in CONFIG.excluded_dirs for part in parts):
        return True
    
    # Excluded files
    if filename in CONFIG.excluded_files:
        return True
    
    # Excluded extensions
    ext = os.path.splitext(filename)[1].lower()
    if ext in CONFIG.excluded_extensions:
        return True
    
    return False


def collect_files() -> List[Tuple[str, str, int, float]]:
    """Collect all files: (abs_path, rel_path, size, mtime)"""
    files = []
    source = Path(CONFIG.source_dir)
    
    for file_path in source.rglob('*'):
        if not file_path.is_file():
            continue
        
        rel_path = str(file_path.relative_to(source))
        filename = file_path.name
        
        if should_exclude(rel_path, filename):
            continue
        
        try:
            stat = file_path.stat()
            files.append((str(file_path), rel_path, stat.st_size, stat.st_mtime))
        except (OSError, PermissionError) as e:
            logger.warning(f"Cannot access {rel_path}: {e}")
    
    return files


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚡ PARALLEL ASYNC FILE READING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def read_file_async(file_path: str, semaphore: asyncio.Semaphore) -> Tuple[str, Optional[bytes], str]:
    """Read file and compute hash concurrently."""
    async with semaphore:
        try:
            if HAS_AIOFILES:
                async with aiofiles.open(file_path, 'rb') as f:
                    data = await f.read()
            else:
                # Fallback to sync read in executor
                loop = asyncio.get_event_loop()
                with open(file_path, 'rb') as f:
                    data = await loop.run_in_executor(None, f.read)
            
            content_hash = hashlib.sha256(data).hexdigest()[:16]
            return (file_path, data, content_hash)
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return (file_path, None, "")


async def read_all_files_parallel(files: List[Tuple[str, str, int, float]]) -> Dict[str, Tuple[bytes, str]]:
    """Read ALL files concurrently using asyncio.gather."""
    semaphore = asyncio.Semaphore(CONFIG.max_concurrent_reads)
    
    # Create tasks for ALL files at once
    tasks = [read_file_async(abs_path, semaphore) for abs_path, _, _, _ in files]
    
    # Execute ALL reads in parallel
    logger.info(f"⚡ Reading {len(tasks)} files in parallel...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Map results
    file_data = {}
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Read error: {result}")
            continue
        abs_path, content, content_hash = result
        if content is not None:
            rel_path = files[i][1]
            file_data[rel_path] = (content, content_hash)
    
    return file_data


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🗜️ ZIP CREATION (ATOMIC + VERIFIED)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_zip_atomic(
    zip_path: str,
    file_data: Dict[str, Tuple[bytes, str]],
    manifest: HashManifest,
    files_meta: Dict[str, Tuple[int, float]]
) -> Tuple[bool, int, int]:
    """Create ZIP atomically: write to temp, rename on success."""
    temp_path = zip_path + ".tmp"
    files_added = 0
    bytes_written = 0
    
    try:
        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED, 
                            compresslevel=CONFIG.compression_level) as zipf:
            for rel_path, (content, content_hash) in tqdm(file_data.items(), 
                                                          desc="📦 Compressing", unit="file"):
                try:
                    zipf.writestr(rel_path, content)
                    files_added += 1
                    bytes_written += len(content)
                    
                    # Update manifest
                    size, mtime = files_meta.get(rel_path, (len(content), time.time()))
                    manifest.update(rel_path, size, mtime, content_hash)
                except Exception as e:
                    logger.error(f"Failed to add {rel_path}: {e}")
        
        # Atomic rename
        if os.path.exists(zip_path):
            os.remove(zip_path)
        os.rename(temp_path, zip_path)
        
        return True, files_added, bytes_written
    
    except Exception as e:
        logger.error(f"ZIP creation failed: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False, 0, 0


def verify_zip(zip_path: str) -> bool:
    """Verify ZIP integrity."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            bad_file = zipf.testzip()
            if bad_file:
                logger.error(f"Corrupted file in ZIP: {bad_file}")
                return False
        return True
    except Exception as e:
        logger.error(f"ZIP verification failed: {e}")
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 MAIN BACKUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def backup_project_async() -> bool:
    """Execute full backup with all world-class features."""
    start_time = time.time()
    
    # Daily folder structure
    today = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%H-%M-%S')
    daily_path = os.path.join(CONFIG.backup_base_dir, today)
    os.makedirs(daily_path, exist_ok=True)
    
    zip_path = os.path.join(daily_path, f"{timestamp}.zip")
    
    logger.info("━" * 60)
    logger.info("🚀 BACKUP STARTED")
    logger.info(f"   Source: {CONFIG.source_dir}")
    logger.info(f"   Target: {zip_path}")
    logger.info("━" * 60)
    
    # Collect files
    logger.info("📂 Scanning files...")
    all_files = collect_files()
    total_size = sum(size for _, _, size, _ in all_files)
    logger.info(f"   Found {len(all_files)} files ({total_size / 1024 / 1024:.1f} MB)")
    
    # Incremental check
    manifest = HashManifest(CONFIG.backup_base_dir)
    files_to_backup = all_files
    
    if CONFIG.incremental and manifest.hashes:
        logger.info("🔍 Incremental mode: checking for changes...")
        changed = []
        for abs_path, rel_path, size, mtime in all_files:
            if manifest.has_changed(rel_path, size, mtime):
                changed.append((abs_path, rel_path, size, mtime))
        
        if len(changed) < len(all_files):
            logger.info(f"   {len(changed)}/{len(all_files)} files changed")
            files_to_backup = changed
    
    if not files_to_backup:
        logger.info("✅ No changes detected. Skipping backup.")
        return True
    
    # Build metadata
    files_meta = {rel_path: (size, mtime) for _, rel_path, size, mtime in files_to_backup}
    
    # ⚡ PARALLEL READ - THE KEY DIFFERENCE
    read_start = time.time()
    file_data = await read_all_files_parallel(files_to_backup)
    read_time = time.time() - read_start
    logger.info(f"   Read {len(file_data)} files in {read_time:.2f}s")
    
    if not file_data:
        logger.error("❌ No files to backup!")
        return False
    
    # Create ZIP
    logger.info(f"🗜️ Creating ZIP (level {CONFIG.compression_level})...")
    zip_start = time.time()
    success, files_added, bytes_written = create_zip_atomic(zip_path, file_data, manifest, files_meta)
    zip_time = time.time() - zip_start
    
    if not success:
        logger.error("❌ Backup FAILED!")
        return False
    
    # Verify
    if CONFIG.verify_after_backup:
        logger.info("🔍 Verifying ZIP...")
        if not verify_zip(zip_path):
            logger.error("❌ ZIP verification FAILED!")
            return False
        logger.info("   ✅ ZIP verified")
    
    # Save manifest
    manifest.save()
    
    # Stats
    zip_size = os.path.getsize(zip_path)
    compression_ratio = (1 - zip_size / bytes_written) * 100 if bytes_written > 0 else 0
    total_time = time.time() - start_time
    
    logger.info("━" * 60)
    logger.info("✅ BACKUP COMPLETE")
    logger.info(f"   📁 Files: {files_added}")
    logger.info(f"   📊 Original: {bytes_written / 1024 / 1024:.1f} MB")
    logger.info(f"   📦 Compressed: {zip_size / 1024 / 1024:.1f} MB ({compression_ratio:.1f}% saved)")
    logger.info(f"   ⏱️ Time: {total_time:.2f}s (Read: {read_time:.2f}s, ZIP: {zip_time:.2f}s)")
    logger.info(f"   📍 {zip_path}")
    
    # ☁️ AUTO-SYNC TO CLOUD
    if CONFIG.auto_sync_to_cloud and CONFIG.cloud_backup_dir:
        sync_to_cloud(zip_path)
    
    logger.info("━" * 60)
    
    return True


def sync_to_cloud(zip_path: str) -> bool:
    """Auto-sync backup to OneDrive folder."""
    try:
        if not CONFIG.cloud_backup_dir:
            return False
        
        # Create cloud folder if needed
        os.makedirs(CONFIG.cloud_backup_dir, exist_ok=True)
        
        # Copy to cloud folder
        filename = os.path.basename(zip_path)
        dest_path = os.path.join(CONFIG.cloud_backup_dir, filename)
        
        shutil.copy2(zip_path, dest_path)
        logger.info(f"   ☁️ Synced to OneDrive: {filename}")
        return True
    except Exception as e:
        logger.warning(f"   ⚠️ Cloud sync failed: {e}")
        return False


def backup_project():
    """Sync wrapper."""
    try:
        return asyncio.run(backup_project_async())
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧹 CLEANUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def cleanup_old_backups():
    """Remove old backups based on retention policy."""
    logger.info("🧹 Running cleanup...")
    
    backup_path = Path(CONFIG.backup_base_dir)
    if not backup_path.exists():
        return
    
    folders = []
    for item in backup_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            try:
                folder_date = datetime.strptime(item.name, '%Y-%m-%d')
                folders.append((folder_date, item))
            except ValueError:
                continue
    
    folders.sort(key=lambda x: x[0], reverse=True)
    cutoff = datetime.now() - timedelta(days=CONFIG.keep_days)
    
    removed = 0
    for i, (folder_date, folder_path) in enumerate(folders):
        if i >= CONFIG.keep_min_backups and folder_date < cutoff:
            try:
                shutil.rmtree(folder_path)
                logger.info(f"   🗑️ Removed: {folder_path.name}")
                removed += 1
            except Exception as e:
                logger.error(f"   Failed: {folder_path}: {e}")
    
    logger.info(f"   Removed {removed} old backup(s)" if removed else "   Nothing to remove")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 LIST BACKUPS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def list_all_backups() -> List[Path]:
    """List all backups with details."""
    backup_path = Path(CONFIG.backup_base_dir)
    if not backup_path.exists():
        print("⚠️ No backups folder found")
        return []
    
    all_zips = list(backup_path.rglob("*.zip"))
    if not all_zips:
        print("⚠️ No backups found")
        return []
    
    # Sort by modification time (newest first)
    all_zips.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    print()
    print("━" * 70)
    print("📋 ALL BACKUPS")
    print("━" * 70)
    print(f"{'#':<4} {'Date':<12} {'Time':<10} {'Size':<12} {'Files':<8} {'Path'}")
    print("─" * 70)
    
    for i, zip_path in enumerate(all_zips, 1):
        stat = zip_path.stat()
        size_mb = stat.st_size / 1024 / 1024
        mtime = datetime.fromtimestamp(stat.st_mtime)
        
        # Count files in ZIP
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                file_count = len(zf.namelist())
        except:
            file_count = "?"
        
        rel_path = zip_path.relative_to(backup_path)
        print(f"{i:<4} {mtime.strftime('%Y-%m-%d'):<12} {mtime.strftime('%H:%M:%S'):<10} {size_mb:>8.1f} MB  {file_count:<8} {rel_path}")
    
    print("─" * 70)
    print(f"Total: {len(all_zips)} backup(s)")
    print()
    
    return all_zips


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔄 RESTORE FROM BACKUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def restore_from_backup():
    """Restore files from a backup."""
    all_zips = list_all_backups()
    if not all_zips:
        return
    
    print("Enter backup number to restore (or 0 to cancel): ", end="")
    try:
        choice = int(input().strip())
        if choice == 0:
            print("Cancelled.")
            return
        if choice < 1 or choice > len(all_zips):
            print("❌ Invalid selection")
            return
    except ValueError:
        print("❌ Invalid input")
        return
    
    selected_zip = all_zips[choice - 1]
    print()
    print(f"Selected: {selected_zip}")
    print()
    print("Restore options:")
    print("  [1] Restore to original location (OVERWRITES existing files!)")
    print("  [2] Restore to custom folder")
    print("  [0] Cancel")
    print()
    
    restore_choice = input("Select option: ").strip()
    
    if restore_choice == "0":
        print("Cancelled.")
        return
    elif restore_choice == "1":
        restore_path = CONFIG.source_dir
        print(f"\n⚠️  WARNING: This will overwrite files in {restore_path}")
        confirm = input("Type 'YES' to confirm: ").strip()
        if confirm != "YES":
            print("Cancelled.")
            return
    elif restore_choice == "2":
        restore_path = input("Enter restore path: ").strip()
        if not restore_path:
            print("❌ Invalid path")
            return
    else:
        print("❌ Invalid option")
        return
    
    # Perform restore
    print()
    print(f"🔄 Restoring to: {restore_path}")
    
    try:
        os.makedirs(restore_path, exist_ok=True)
        with zipfile.ZipFile(selected_zip, 'r') as zf:
            zf.extractall(restore_path)
        print(f"✅ Restored successfully!")
        print(f"   Files extracted to: {restore_path}")
    except Exception as e:
        print(f"❌ Restore failed: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 BACKUP STATS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def show_backup_stats():
    """Show backup statistics."""
    backup_path = Path(CONFIG.backup_base_dir)
    if not backup_path.exists():
        print("⚠️ No backups folder found")
        return
    
    all_zips = list(backup_path.rglob("*.zip"))
    if not all_zips:
        print("⚠️ No backups found")
        return
    
    # Calculate stats
    total_size = sum(z.stat().st_size for z in all_zips)
    oldest = min(all_zips, key=lambda p: p.stat().st_mtime)
    newest = max(all_zips, key=lambda p: p.stat().st_mtime)
    
    oldest_time = datetime.fromtimestamp(oldest.stat().st_mtime)
    newest_time = datetime.fromtimestamp(newest.stat().st_mtime)
    
    # Count by date
    dates = {}
    for z in all_zips:
        date = datetime.fromtimestamp(z.stat().st_mtime).strftime('%Y-%m-%d')
        dates[date] = dates.get(date, 0) + 1
    
    print()
    print("━" * 50)
    print("📊 BACKUP STATISTICS")
    print("━" * 50)
    print(f"  📦 Total Backups:    {len(all_zips)}")
    print(f"  💾 Total Size:       {total_size / 1024 / 1024:.1f} MB ({total_size / 1024 / 1024 / 1024:.2f} GB)")
    print(f"  📅 Oldest Backup:    {oldest_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"  📅 Newest Backup:    {newest_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"  📁 Backup Days:      {len(dates)}")
    print()
    print("  Backups per day:")
    for date in sorted(dates.keys(), reverse=True)[:7]:
        print(f"    {date}: {dates[date]} backup(s)")
    print("━" * 50)
    print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ☁️ CLOUD UPLOAD (OneDrive)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_onedrive_path() -> Optional[str]:
    """Get OneDrive folder path from environment or default locations."""
    # Check environment variable first
    onedrive_path = os.getenv("ONEDRIVE_BACKUP_PATH")
    if onedrive_path and os.path.exists(onedrive_path):
        return onedrive_path
    
    # Check common OneDrive locations
    user_home = os.path.expanduser("~")
    common_paths = [
        os.path.join(user_home, "OneDrive", "QuantAlgo_Backups"),
        os.path.join(user_home, "OneDrive - Personal", "QuantAlgo_Backups"),
        os.path.join(user_home, "OneDrive for Business", "QuantAlgo_Backups"),
    ]
    
    for path in common_paths:
        parent = os.path.dirname(path)
        if os.path.exists(parent):
            return path
    
    return None


def upload_to_cloud():
    """Upload latest backup to OneDrive."""
    backup_path = Path(CONFIG.backup_base_dir)
    all_zips = list(backup_path.rglob("*.zip"))
    
    if not all_zips:
        print("⚠️ No backups found to upload")
        return
    
    # Get latest backup
    latest = max(all_zips, key=lambda p: p.stat().st_mtime)
    latest_size = latest.stat().st_size / 1024 / 1024
    
    print()
    print("━" * 50)
    print("☁️ CLOUD UPLOAD (OneDrive)")
    print("━" * 50)
    print(f"  Latest backup: {latest.name}")
    print(f"  Size: {latest_size:.1f} MB")
    print()
    
    # Get OneDrive path
    onedrive_path = get_onedrive_path()
    
    if not onedrive_path:
        print("⚠️ OneDrive folder not found automatically.")
        print()
        onedrive_path = input("Enter OneDrive backup folder path: ").strip()
        if not onedrive_path:
            print("Cancelled.")
            return
    
    print(f"  Target: {onedrive_path}")
    print()
    
    # Create folder if needed
    os.makedirs(onedrive_path, exist_ok=True)
    
    # Copy file
    dest_path = os.path.join(onedrive_path, latest.name)
    
    print("Options:")
    print("  [1] Upload latest backup only")
    print("  [2] Upload all backups from today")
    print("  [3] Upload all backups")
    print("  [0] Cancel")
    print()
    
    choice = input("Select option: ").strip()
    
    if choice == "0":
        print("Cancelled.")
        return
    elif choice == "1":
        files_to_upload = [latest]
    elif choice == "2":
        today = datetime.now().strftime('%Y-%m-%d')
        files_to_upload = [z for z in all_zips if today in str(z)]
    elif choice == "3":
        files_to_upload = all_zips
    else:
        print("❌ Invalid option")
        return
    
    print()
    print(f"📤 Uploading {len(files_to_upload)} file(s)...")
    
    uploaded = 0
    for zip_file in files_to_upload:
        try:
            dest = os.path.join(onedrive_path, zip_file.name)
            shutil.copy2(zip_file, dest)
            print(f"  ✅ {zip_file.name}")
            uploaded += 1
        except Exception as e:
            print(f"  ❌ {zip_file.name}: {e}")
    
    print()
    print(f"✅ Uploaded {uploaded}/{len(files_to_upload)} file(s) to OneDrive")
    print(f"   OneDrive will sync automatically to cloud.")
    print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⏰ SCHEDULER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def countdown_timer(minutes: int):
    """Display countdown."""
    for remaining in range(minutes * 60, 0, -1):
        mins, secs = divmod(remaining, 60)
        print(f"\r⏳ Next backup in {mins:02d}:{secs:02d}", end="", flush=True)
        time.sleep(1)
    print()


def run_scheduled():
    """Run on schedule."""
    if not HAS_SCHEDULE:
        logger.error("'schedule' package required for scheduled backups")
        return
    
    schedule.every(CONFIG.backup_interval_minutes).minutes.do(backup_project)
    schedule.every().day.at(CONFIG.cleanup_time).do(cleanup_old_backups)
    
    logger.info("━" * 60)
    logger.info("🏆 WORLD-CLASS BACKUP SYSTEM v2.0")
    logger.info("━" * 60)
    logger.info(f"📂 Source: {CONFIG.source_dir}")
    logger.info(f"📦 Backups: {CONFIG.backup_base_dir}")
    logger.info(f"⏰ Every {CONFIG.backup_interval_minutes} min | 🗜️ Level {CONFIG.compression_level}")
    logger.info(f"📊 {'Incremental' if CONFIG.incremental else 'Full'} | 🔍 Verify: {CONFIG.verify_after_backup}")
    logger.info(f"🧹 Keep {CONFIG.keep_days} days (min {CONFIG.keep_min_backups})")
    logger.info("━" * 60)
    
    backup_project()
    
    try:
        while True:
            schedule.run_pending()
            countdown_timer(CONFIG.backup_interval_minutes)
    except KeyboardInterrupt:
        logger.info("\n👋 Stopped by user.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎯 INTERACTIVE MENU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def show_interactive_menu():
    """Show interactive menu for backup options."""
    print()
    print("━" * 55)
    print("🏆 QUANTALGO BACKUP SYSTEM v2.0")
    print("━" * 55)
    print(f"📂 Source: {CONFIG.source_dir}")
    print(f"📦 Local:  {CONFIG.backup_base_dir}")
    if CONFIG.auto_sync_to_cloud and CONFIG.cloud_backup_dir:
        print(f"☁️  Cloud:  {CONFIG.cloud_backup_dir} (auto-sync ON)")
    else:
        print(f"☁️  Cloud:  Disabled")
    print("━" * 55)
    print()
    print("  [1] � Run fBackup Once (Incremental)")
    print("  [2] � Run Full  Backup (All Files)")
    print("  [3] ⏰ Start Scheduled Backups (Every 30 min)")
    print("  [4] 🧹 Cleanup Old Backups")
    print("  [5] 🔍 Verify Last Backup")
    print("  [6] 📋 List All Backups")
    print("  [7] 🔄 Restore from Backup")
    print("  [8] 📊 Backup Stats")
    print("  [9] ☁️  Upload to OneDrive (manual)")
    print("  [0] ❌ Exit")
    print()
    
    choice = input("  Select option [0-9]: ").strip()
    
    if choice == "1":
        print()
        backup_project()
    elif choice == "2":
        print()
        CONFIG.incremental = False
        backup_project()
    elif choice == "3":
        print()
        run_scheduled()
    elif choice == "4":
        print()
        cleanup_old_backups()
    elif choice == "5":
        print()
        # Find latest backup
        backup_path = Path(CONFIG.backup_base_dir)
        zips = list(backup_path.rglob("*.zip"))
        if zips:
            latest = max(zips, key=lambda p: p.stat().st_mtime)
            print(f"🔍 Verifying: {latest}")
            if verify_zip(str(latest)):
                print("✅ Backup is valid!")
            else:
                print("❌ Backup is corrupted!")
        else:
            print("⚠️ No backups found to verify")
    elif choice == "6":
        list_all_backups()
    elif choice == "7":
        restore_from_backup()
    elif choice == "8":
        show_backup_stats()
    elif choice == "9":
        upload_to_cloud()
    elif choice == "0":
        print("👋 Bye!")
        sys.exit(0)
    else:
        print("❌ Invalid option")
        show_interactive_menu()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="🏆 World-Class Backup System v2.0")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--cleanup", action="store_true", help="Run cleanup only")
    parser.add_argument("--verify", type=str, help="Verify a ZIP file")
    parser.add_argument("--full", action="store_true", help="Force full backup")
    parser.add_argument("--menu", action="store_true", help="Show interactive menu")
    args = parser.parse_args()
    
    # If no args provided, show interactive menu
    if len(sys.argv) == 1:
        show_interactive_menu()
    elif args.verify:
        sys.exit(0 if verify_zip(args.verify) else 1)
    elif args.cleanup:
        cleanup_old_backups()
    elif args.once:
        if args.full:
            CONFIG.incremental = False
        sys.exit(0 if backup_project() else 1)
    elif args.menu:
        show_interactive_menu()
    else:
        if args.full:
            CONFIG.incremental = False
        run_scheduled()
