"""
Facebook AI Poster - Monitoring Dashboard
Real-time status monitoring and analytics viewer.

Usage:
    python monitor.py
    python monitor.py --watch  # Auto-refresh every 30 seconds
"""

import os
import sys
import time
import argparse
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config.env'))

# Use your existing variable names
PAGE_ID = os.getenv("FB_PAGE_ID")
PAGE_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')

def print_header():
    """Print dashboard header."""
    print("=" * 80)
    print("  FACEBOOK AI POSTER - MONITORING DASHBOARD")
    print("=" * 80)
    print(f"  Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

def get_page_info():
    """Fetch page information."""
    try:
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}"
        params = {
            "fields": "name,fan_count,followers_count,talking_about_count,link,category",
            "access_token": PAGE_ACCESS_TOKEN
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def get_recent_posts(limit=5):
    """Fetch recent posts."""
    try:
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/posts"
        params = {
            "fields": "id,message,created_time,reactions.summary(true),comments.summary(true),shares",
            "limit": limit,
            "access_token": PAGE_ACCESS_TOKEN
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            return []
    except Exception as e:
        return []

def get_post_insights(post_id):
    """Fetch post insights."""
    try:
        url = f"https://graph.facebook.com/v20.0/{post_id}/insights"
        params = {
            "metric": "post_impressions,post_engaged_users,post_clicks",
            "access_token": PAGE_ACCESS_TOKEN
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json().get('data', [])
            insights = {}
            for metric in data:
                insights[metric['name']] = metric['values'][0]['value']
            return insights
        else:
            return {}
    except Exception:
        return {}

def check_log_file():
    """Check log file status."""
    log_file = os.path.join(os.path.dirname(__file__), '..', 'logs', 'facebook_poster.log')
    
    if not os.path.exists(log_file):
        return {
            'exists': False,
            'size': 0,
            'last_modified': None,
            'recent_errors': 0
        }
    
    stat = os.stat(log_file)
    size_mb = stat.st_size / (1024 * 1024)
    last_modified = datetime.fromtimestamp(stat.st_mtime)
    
    # Count recent errors
    recent_errors = 0
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f.readlines()[-100:]:  # Last 100 lines
                if 'ERROR' in line:
                    recent_errors += 1
    except:
        pass
    
    return {
        'exists': True,
        'size': size_mb,
        'last_modified': last_modified,
        'recent_errors': recent_errors
    }

def format_time_ago(dt):
    """Format datetime as 'X hours ago'."""
    if not dt:
        return "Unknown"
    
    try:
        # Parse ISO format from Facebook
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)
        
        diff = datetime.now() - dt
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds >= 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds >= 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return f"{diff.seconds}s ago"
    except:
        return str(dt)

def display_dashboard(watch_mode=False):
    """Display the monitoring dashboard."""
    clear_screen()
    print_header()
    
    # Page Information
    print("[PAGE INFORMATION]")
    print("-" * 80)
    page_info = get_page_info()
    
    if page_info:
        print(f"Name:           {page_info.get('name', 'N/A')}")
        print(f"Category:       {page_info.get('category', 'N/A')}")
        print(f"Page Likes:     {page_info.get('fan_count', 0):,}")
        print(f"Followers:      {page_info.get('followers_count', 0):,}")
        print(f"Talking About:  {page_info.get('talking_about_count', 0):,}")
        print(f"URL:            {page_info.get('link', 'N/A')}")
    else:
        print("[!] Could not fetch page information")
    
    print()
    print()
    
    # Log File Status
    print("[LOG FILE STATUS]")
    print("-" * 80)
    log_info = check_log_file()
    
    if log_info['exists']:
        print(f"Status:         [OK] Active")
        print(f"Size:           {log_info['size']:.2f} MB")
        print(f"Last Modified:  {format_time_ago(log_info['last_modified'])}")
        print(f"Recent Errors:  {'[!] ' + str(log_info['recent_errors']) if log_info['recent_errors'] > 0 else '[OK] 0'}")
    else:
        print("Status:         [!] Log file not found")
    
    print()
    print()
    
    # Recent Posts
    print("[RECENT POSTS (Last 5)]")
    print("-" * 80)
    posts = get_recent_posts(limit=5)
    
    if posts:
        for i, post in enumerate(posts, 1):
            post_id = post.get('id')
            message = post.get('message', 'No message')[:60] + '...' if post.get('message') else '[No text]'
            created = post.get('created_time')
            
            reactions = post.get('reactions', {}).get('summary', {}).get('total_count', 0)
            comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
            shares = post.get('shares', {}).get('count', 0)
            
            print(f"\n{i}. Posted {format_time_ago(created)}")
            print(f"   {message}")
            print(f"   Reactions: {reactions}  |  Comments: {comments}  |  Shares: {shares}")
            
            # Try to get insights
            insights = get_post_insights(post_id)
            if insights:
                impressions = insights.get('post_impressions', 0)
                engaged = insights.get('post_engaged_users', 0)
                clicks = insights.get('post_clicks', 0)
                print(f"   Impressions: {impressions:,}  |  Engaged: {engaged}  |  Clicks: {clicks}")
    else:
        print("[!] No recent posts found")
    
    print()
    print()
    
    # System Status
    print("[SYSTEM STATUS]")
    print("-" * 80)
    
    # Check if script is running (basic check)
    script_running = False
    try:
        import psutil
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'facebook_poster.py' in ' '.join(cmdline):
                    script_running = True
                    break
            except:
                pass
        print(f"Poster Script:  {'[OK] Running' if script_running else '[!] Not Running'}")
    except ImportError:
        print("Poster Script:  [?] psutil not installed, cannot check")
    
    # Token expiration check
    try:
        debug_url = "https://graph.facebook.com/v20.0/debug_token"
        debug_params = {
            "input_token": PAGE_ACCESS_TOKEN,
            "access_token": PAGE_ACCESS_TOKEN
        }
        debug_response = requests.get(debug_url, params=debug_params, timeout=10)
        
        if debug_response.status_code == 200:
            data = debug_response.json().get('data', {})
            expires_at = data.get('expires_at', 0)
            
            if expires_at == 0:
                print("Token:          [OK] Never expires")
            else:
                expiry_date = datetime.fromtimestamp(expires_at)
                days_left = (expiry_date - datetime.now()).days
                
                if days_left < 7:
                    print(f"Token:          [!] Expires in {days_left} days!")
                else:
                    print(f"Token:          [OK] Valid ({days_left} days left)")
        else:
            print("Token:          [X] Invalid or expired")
    except:
        print("Token:          [?] Could not validate")
    
    print()
    print("=" * 80)
    
    if watch_mode:
        print("\n[Auto-refreshing every 30 seconds... Press Ctrl+C to exit]")
    else:
        print("\nRun with --watch to auto-refresh")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Facebook AI Poster Monitoring Dashboard')
    parser.add_argument('--watch', action='store_true', help='Auto-refresh every 30 seconds')
    args = parser.parse_args()
    
    try:
        if args.watch:
            while True:
                display_dashboard(watch_mode=True)
                time.sleep(30)
        else:
            display_dashboard(watch_mode=False)
    except KeyboardInterrupt:
        print("\n\nDashboard closed")
        sys.exit(0)

if __name__ == "__main__":
    main()
