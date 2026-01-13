"""
Initialize database with default data
"""
from backend.database.db_manager import db

def init_database():
    """Initialize database with default accounts and links"""
    
    # Add YouTube account
    accounts = db.get_accounts(platform="youtube")
    if not accounts:
        print("Adding YouTube account...")
        db.add_account(
            platform="youtube",
            account_name="oneclick_reels",
            account_url="https://www.youtube.com/@oneclick_reels",
            studio_url="https://studio.youtube.com/channel/UCzefTJDoZeWzix8az4rsUYg"
        )
        print("✓ YouTube account added")
    
    # Add default links
    print("\nAdding default links...")
    
    # YouTube links
    db.add_link(
        category="youtube",
        title="YouTube Channel",
        url="https://www.youtube.com/@oneclick_reels",
        description="Main YouTube channel for OneClick Reels",
        icon="Youtube"
    )
    
    db.add_link(
        category="youtube",
        title="YouTube Studio",
        url="https://studio.youtube.com/channel/UCzefTJDoZeWzix8az4rsUYg",
        description="YouTube Studio dashboard for analytics and management",
        icon="LayoutDashboard"
    )
    
    # Useful resources
    db.add_link(
        category="resources",
        title="Pexels",
        url="https://www.pexels.com/",
        description="Free stock videos and images",
        icon="Image"
    )
    
    db.add_link(
        category="resources",
        title="OpenAI Platform",
        url="https://platform.openai.com/",
        description="OpenAI API dashboard",
        icon="Brain"
    )
    
    db.add_link(
        category="tools",
        title="YouTube Shorts Trends",
        url="https://trends.google.com/trends/explore?q=youtube%20shorts&geo=US",
        description="Track trending topics for YouTube Shorts",
        icon="TrendingUp"
    )
    
    print("✓ Links added")
    
    # Set default settings
    print("\nSetting default preferences...")
    db.set_setting("default_niche", "motivation")
    db.set_setting("auto_upload_youtube", False)
    db.set_setting("default_voice", "en-US-AriaNeural")
    print("✓ Settings configured")
    
    print("Database initialized successfully!")
    print("\nDatabase location:", db.db_path)

if __name__ == "__main__":
    init_database()
