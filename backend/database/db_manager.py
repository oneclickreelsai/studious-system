"""
SQLite Database Manager for OneClick Reels AI
Stores account info, video history, analytics, and settings
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

DB_PATH = Path(__file__).parent / "oneclick_reels.db"

class DatabaseManager:
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Accounts table - Store social media accounts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                account_name TEXT NOT NULL,
                account_url TEXT,
                studio_url TEXT,
                credentials TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Videos table - Store generated video history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                niche TEXT,
                topic TEXT,
                script TEXT,
                file_path TEXT,
                thumbnail_path TEXT,
                duration_seconds INTEGER,
                file_size_mb REAL,
                generation_mode TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Uploads table - Track uploads to platforms
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER,
                account_id INTEGER,
                platform TEXT NOT NULL,
                platform_video_id TEXT,
                platform_url TEXT,
                caption TEXT,
                hashtags TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_synced_at TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(id),
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)
        
        # Links table - Store important links and resources
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                is_favorite BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Settings table - Store app settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analytics table - Store daily metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                videos_generated INTEGER DEFAULT 0,
                videos_uploaded INTEGER DEFAULT 0,
                total_views INTEGER DEFAULT 0,
                total_likes INTEGER DEFAULT 0,
                total_comments INTEGER DEFAULT 0,
                api_calls INTEGER DEFAULT 0,
                errors INTEGER DEFAULT 0,
                UNIQUE(date)
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ===== Account Management =====
    def add_account(self, platform: str, account_name: str, account_url: str = None, 
                    studio_url: str = None, credentials: Dict = None) -> int:
        """Add a new social media account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        creds_json = json.dumps(credentials) if credentials else None
        
        cursor.execute("""
            INSERT INTO accounts (platform, account_name, account_url, studio_url, credentials)
            VALUES (?, ?, ?, ?, ?)
        """, (platform, account_name, account_url, studio_url, creds_json))
        
        account_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return account_id
    
    def get_accounts(self, platform: str = None, active_only: bool = True) -> List[Dict]:
        """Get all accounts or filter by platform"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM accounts WHERE 1=1"
        params = []
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        if active_only:
            query += " AND is_active = 1"
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        accounts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return accounts
    
    def update_account(self, account_id: int, **kwargs):
        """Update account details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if 'credentials' in kwargs and isinstance(kwargs['credentials'], dict):
            kwargs['credentials'] = json.dumps(kwargs['credentials'])
        
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"
        
        cursor.execute(f"""
            UPDATE accounts SET {set_clause}
            WHERE id = ?
        """, list(kwargs.values()) + [account_id])
        
        conn.commit()
        conn.close()
    
    # ===== Video Management =====
    def add_video(self, title: str, niche: str = None, topic: str = None, 
                  script: str = None, file_path: str = None, 
                  generation_mode: str = "one-click", **kwargs) -> int:
        """Add a new video record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO videos (title, niche, topic, script, file_path, generation_mode,
                              thumbnail_path, duration_seconds, file_size_mb)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, niche, topic, script, file_path, generation_mode,
              kwargs.get('thumbnail_path'), kwargs.get('duration_seconds'), 
              kwargs.get('file_size_mb')))
        
        video_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return video_id
    
    def get_videos(self, limit: int = 50, niche: str = None) -> List[Dict]:
        """Get video history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM videos WHERE 1=1"
        params = []
        
        if niche:
            query += " AND niche = ?"
            params.append(niche)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        videos = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return videos
    
    def get_video_by_id(self, video_id: int) -> Optional[Dict]:
        """Get video by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [col[0] for col in cursor.description]
            video = dict(zip(columns, row))
        else:
            video = None
        
        conn.close()
        return video
    
    # ===== Upload Management =====
    def add_upload(self, video_id: int, platform: str, platform_video_id: str = None,
                   platform_url: str = None, caption: str = None, 
                   hashtags: str = None, account_id: int = None) -> int:
        """Record a video upload"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO uploads (video_id, account_id, platform, platform_video_id, 
                               platform_url, caption, hashtags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (video_id, account_id, platform, platform_video_id, 
              platform_url, caption, hashtags))
        
        upload_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return upload_id
    
    def update_upload_stats(self, upload_id: int, views: int = None, 
                           likes: int = None, comments: int = None, shares: int = None):
        """Update upload statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if views is not None:
            updates.append("views = ?")
            params.append(views)
        if likes is not None:
            updates.append("likes = ?")
            params.append(likes)
        if comments is not None:
            updates.append("comments = ?")
            params.append(comments)
        if shares is not None:
            updates.append("shares = ?")
            params.append(shares)
        
        updates.append("last_synced_at = CURRENT_TIMESTAMP")
        params.append(upload_id)
        
        cursor.execute(f"""
            UPDATE uploads SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        
        conn.commit()
        conn.close()
    
    def get_uploads(self, video_id: int = None, platform: str = None, limit: int = 50) -> List[Dict]:
        """Get upload history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM uploads WHERE 1=1"
        params = []
        
        if video_id:
            query += " AND video_id = ?"
            params.append(video_id)
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        query += " ORDER BY uploaded_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        uploads = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return uploads
    
    # ===== Links Management =====
    def add_link(self, category: str, title: str, url: str, 
                 description: str = None, icon: str = None) -> int:
        """Add a new link"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO links (category, title, url, description, icon)
            VALUES (?, ?, ?, ?, ?)
        """, (category, title, url, description, icon))
        
        link_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return link_id
    
    def get_links(self, category: str = None, favorites_only: bool = False) -> List[Dict]:
        """Get saved links"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM links WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if favorites_only:
            query += " AND is_favorite = 1"
        
        query += " ORDER BY is_favorite DESC, created_at DESC"
        
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        links = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return links
    
    def toggle_favorite(self, link_id: int):
        """Toggle favorite status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE links SET is_favorite = NOT is_favorite
            WHERE id = ?
        """, (link_id,))
        
        conn.commit()
        conn.close()
    
    # ===== Settings Management =====
    def set_setting(self, key: str, value: Any):
        """Set a setting value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        value_str = json.dumps(value) if not isinstance(value, str) else value
        
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value_str))
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            try:
                return json.loads(row[0])
            except:
                return row[0]
        return default
    
    # ===== Analytics =====
    def update_analytics(self, date: str = None, **kwargs):
        """Update analytics for a date"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current values
        cursor.execute("SELECT * FROM analytics WHERE date = ?", (date,))
        row = cursor.fetchone()
        
        if row:
            # Update existing
            updates = []
            params = []
            for key, value in kwargs.items():
                updates.append(f"{key} = {key} + ?")
                params.append(value)
            
            params.append(date)
            cursor.execute(f"""
                UPDATE analytics SET {', '.join(updates)}
                WHERE date = ?
            """, params)
        else:
            # Insert new
            cursor.execute(f"""
                INSERT INTO analytics (date, {', '.join(kwargs.keys())})
                VALUES (?, {', '.join(['?'] * len(kwargs))})
            """, [date] + list(kwargs.values()))
        
        conn.commit()
        conn.close()
    
    def get_analytics(self, days: int = 30) -> List[Dict]:
        """Get analytics for last N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM analytics
            ORDER BY date DESC
            LIMIT ?
        """, (days,))
        
        columns = [col[0] for col in cursor.description]
        analytics = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return analytics
    
    def get_total_stats(self) -> Dict:
        """Get total statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_videos,
                SUM(file_size_mb) as total_size_mb
            FROM videos
        """)
        video_stats = cursor.fetchone()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_uploads,
                SUM(views) as total_views,
                SUM(likes) as total_likes,
                SUM(comments) as total_comments
            FROM uploads
        """)
        upload_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_videos": video_stats[0] or 0,
            "total_size_mb": video_stats[1] or 0,
            "total_uploads": upload_stats[0] or 0,
            "total_views": upload_stats[1] or 0,
            "total_likes": upload_stats[2] or 0,
            "total_comments": upload_stats[3] or 0
        }

# Global instance
db = DatabaseManager()
