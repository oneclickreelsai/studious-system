"""
Production-Grade AI-Enabled Facebook Page Poster
=================================================
Complete automation system with error handling, logging, and analytics.
"""

import os
import sys
import signal
import requests
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from functools import wraps
from openai import OpenAI
from dotenv import load_dotenv
import schedule

# ==================== CONFIGURATION ====================

# Load from project root config.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config.env'))

# Environment variables (mapped to your existing config.env names)
PAGE_ID = os.getenv("FB_PAGE_ID")
PAGE_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
POST_SCHEDULE = os.getenv("POST_SCHEDULE", "09:00")
ENABLE_MODERATION = os.getenv("ENABLE_MODERATION", "true").lower() == "true"

# Validate configuration
if not all([PAGE_ID, PAGE_ACCESS_TOKEN, PERPLEXITY_API_KEY]):
    raise ValueError("[ERROR] Missing required environment variables. Check your config.env file.")

# ==================== LOGGING SETUP ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'logs', 'facebook_poster.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== PERPLEXITY CLIENT ====================

client = OpenAI(
    base_url="https://api.perplexity.ai",
    api_key=PERPLEXITY_API_KEY,
    timeout=30.0
)

# ==================== UTILITY FUNCTIONS ====================

def rate_limit(seconds: int = 5):
    """Decorator to rate-limit function calls."""
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < seconds:
                time.sleep(seconds - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

def retry_with_backoff(max_retries: int = 3, base_delay: int = 2):
    """Decorator for exponential backoff retry logic."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"[ERROR] All {max_retries} attempts failed: {e}")
                        raise
                    delay = base_delay ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

# ==================== TOKEN VALIDATION ====================

def validate_facebook_token() -> bool:
    """Check if Facebook token is valid and has required permissions."""
    try:
        url = "https://graph.facebook.com/v20.0/me"
        params = {"access_token": PAGE_ACCESS_TOKEN}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            logger.info("[OK] Facebook token is valid")
            
            # Check token expiration
            debug_url = "https://graph.facebook.com/v20.0/debug_token"
            debug_params = {
                "input_token": PAGE_ACCESS_TOKEN,
                "access_token": PAGE_ACCESS_TOKEN
            }
            debug_response = requests.get(debug_url, params=debug_params, timeout=10)
            
            if debug_response.status_code == 200:
                data = debug_response.json().get("data", {})
                expires_at = data.get("expires_at", 0)
                
                if expires_at == 0:
                    logger.info("[OK] Token never expires")
                else:
                    expiry_date = datetime.fromtimestamp(expires_at)
                    days_left = (expiry_date - datetime.now()).days
                    logger.info(f"Token expires on {expiry_date.strftime('%Y-%m-%d')} ({days_left} days left)")
                    
                    if days_left < 7:
                        logger.warning(f"Token expires soon! Renew within {days_left} days.")
            
            return True
        else:
            logger.error(f"[ERROR] Invalid token: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"[ERROR] Token validation error: {e}")
        return False

# ==================== CONTENT GENERATION ====================

@retry_with_backoff(max_retries=3)
def generate_ai_post(topic: str) -> str:
    """Generate engaging post using Perplexity Sonar model."""
    try:
        logger.info(f"🤖 Generating content for: {topic}")
        
        response = client.chat.completions.create(
            model=PERPLEXITY_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional social media manager for a trading/quantitative finance page "
                        "targeting Indian retail traders and algo developers. "
                        "Create engaging, informative Facebook posts (150-200 words). "
                        "Requirements:\n"
                        "- Conversational tone with strategic emoji use (2-4 max)\n"
                        "- Include 1-2 specific facts/stats with sources when available\n"
                        "- End with engaging CTA (question or call-to-action)\n"
                        "- Reference Indian markets (NSE/BSE) and platforms (Angel One, Zerodha)\n"
                        "- Avoid overhyped language or financial advice\n"
                        "- Add relevant hashtags (3-5 max) at the end"
                    )
                },
                {"role": "user", "content": topic}
            ],
            temperature=0.7,
            max_tokens=600
        )
        
        content = response.choices[0].message.content.strip()
        logger.info(f"✅ Generated {len(content)} characters")
        return content
        
    except Exception as e:
        logger.error(f"❌ Content generation failed: {e}")
        return f"[Generation Error: {str(e)}]"

def moderate_content(content: str) -> tuple[bool, str]:
    """Basic content moderation to avoid policy violations."""
    if not ENABLE_MODERATION:
        return True, "Moderation disabled"
    
    # Forbidden terms (customize based on your needs)
    forbidden_terms = [
        "guaranteed returns", "risk-free", "get rich quick",
        "buy now", "pump", "dump", "insider tip"
    ]
    
    content_lower = content.lower()
    
    for term in forbidden_terms:
        if term in content_lower:
            logger.warning(f"⚠️ Content flagged: contains '{term}'")
            return False, f"Contains forbidden term: {term}"
    
    # Check length
    if len(content) < 50:
        return False, "Content too short"
    
    if len(content) > 2000:
        return False, "Content too long (FB limit: 63,206 chars, but keep it reasonable)"
    
    logger.info("✅ Content passed moderation")
    return True, "Approved"

# ==================== FACEBOOK POSTING ====================

@rate_limit(seconds=5)
@retry_with_backoff(max_retries=3)
def post_to_facebook(message: str, image_url: Optional[str] = None) -> Optional[Dict]:
    """Post message to Facebook Page with error handling."""
    try:
        # Moderate content first
        is_safe, reason = moderate_content(message)
        if not is_safe:
            logger.error(f"❌ Post blocked by moderation: {reason}")
            return None
        
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
        payload = {
            "message": message,
            "access_token": PAGE_ACCESS_TOKEN
        }
        
        if image_url:
            payload["link"] = image_url
        
        response = requests.post(url, data=payload, timeout=15)
        response.raise_for_status()
        
        post_data = response.json()
        post_id = post_data.get('id')
        
        logger.info(f"✅ Post published successfully: {post_id}")
        logger.info(f"🔗 View at: https://facebook.com/{post_id}")
        
        return post_data
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error posting to Facebook: {e}")
        raise

# ==================== ANALYTICS ====================

def get_post_insights(post_id: str) -> Optional[Dict]:
    """Fetch engagement metrics for a post."""
    try:
        url = f"https://graph.facebook.com/v20.0/{post_id}/insights"
        params = {
            "metric": "post_impressions,post_engaged_users,post_clicks",
            "access_token": PAGE_ACCESS_TOKEN
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"📊 Insights for {post_id}: {data}")
            return data
        else:
            logger.warning(f"⚠️ Could not fetch insights: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error fetching insights: {e}")
        return None

def get_page_stats() -> Optional[Dict]:
    """Get overall page statistics."""
    try:
        url = f"https://graph.facebook.com/v20.0/{PAGE_ID}"
        params = {
            "fields": "name,fan_count,followers_count,talking_about_count",
            "access_token": PAGE_ACCESS_TOKEN
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            logger.info(f"📈 Page Stats: {stats.get('name')} - "
                       f"{stats.get('fan_count', 0)} likes, "
                       f"{stats.get('followers_count', 0)} followers")
            return stats
        else:
            logger.warning(f"⚠️ Could not fetch page stats: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error fetching page stats: {e}")
        return None

# ==================== TOPIC MANAGEMENT ====================

class TopicManager:
    """Manages post topics with rotation and tracking."""
    
    def __init__(self):
        self.topics = [
            "latest NSE options trading strategies for {month}",
            "Angel One API updates and new features for algo traders",
            "machine learning models for predicting options Greeks",
            "Nifty 50 volatility analysis and trading opportunities",
            "Python libraries for algorithmic trading in Indian markets",
            "risk management strategies for options traders",
            "backtesting frameworks for quantitative strategies",
            "market microstructure and order flow analysis",
            "statistical arbitrage opportunities in NSE stocks",
            "automated trading system architecture best practices"
        ]
        self.used_topics = []
    
    def get_next_topic(self) -> str:
        """Get next topic with smart rotation."""
        # Reset if all topics used
        if len(self.used_topics) >= len(self.topics):
            self.used_topics = []
            logger.info("🔄 Resetting topic rotation")
        
        # Get unused topics
        available = [t for t in self.topics if t not in self.used_topics]
        
        # Select random topic
        topic = random.choice(available)
        self.used_topics.append(topic)
        
        # Format with current date
        topic = topic.format(
            month=datetime.now().strftime('%B %Y'),
            date=datetime.now().strftime('%Y-%m-%d')
        )
        
        return topic

topic_manager = TopicManager()

# ==================== SCHEDULED JOBS ====================

def daily_post_job():
    """Main scheduled job: Generate and post daily content."""
    try:
        logger.info("=" * 50)
        logger.info(f"🚀 Starting scheduled post at {datetime.now()}")
        
        # Get page stats
        get_page_stats()
        
        # Generate content
        topic = topic_manager.get_next_topic()
        logger.info(f"📝 Topic: {topic}")
        
        ai_content = generate_ai_post(topic)
        
        if "[Generation Error" in ai_content:
            logger.error("❌ Skipping post due to generation error")
            return
        
        logger.info(f"✨ Preview: {ai_content[:150]}...")
        
        # Post to Facebook
        result = post_to_facebook(ai_content)
        
        if result:
            post_id = result.get('id')
            logger.info(f"✅ Daily post completed: {post_id}")
            
            # Wait a bit before fetching insights
            time.sleep(10)
            get_post_insights(post_id)
        
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Daily post job failed: {e}")

# ==================== SIGNAL HANDLING ====================

def signal_handler(sig, frame):
    """Graceful shutdown handler."""
    logger.info("\n🛑 Shutdown signal received. Cleaning up...")
    logger.info("📊 Final page stats:")
    get_page_stats()
    logger.info("👋 Goodbye!")
    sys.exit(0)

# ==================== MAIN EXECUTION ====================

def test_generation_only():
    """Test AI content generation without posting."""
    logger.info("=" * 50)
    logger.info("🧪 TEST MODE - Content Generation Only")
    logger.info("=" * 50)
    
    test_topic = "Python automation tips for Angel One API trading"
    logger.info(f"📝 Topic: {test_topic}")
    
    content = generate_ai_post(test_topic)
    
    logger.info("=" * 50)
    logger.info("[GENERATED CONTENT]")
    logger.info("=" * 50)
    
    # Write to file to avoid Windows console encoding issues
    output_file = os.path.join(os.path.dirname(__file__), '..', 'logs', 'test_post_output.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[Content saved to: {output_file}]")
    
    logger.info("=" * 50)
    
    is_safe, reason = moderate_content(content)
    logger.info(f"🛡️ Moderation: {reason}")
    
    return content

def main():
    """Main application entry point."""
    logger.info("=" * 50)
    logger.info("🚀 Facebook AI Poster - Production Mode")
    logger.info("=" * 50)
    logger.info(f"📄 Target Page: {PAGE_ID}")
    logger.info(f"⏰ Scheduled Time: {POST_SCHEDULE}")
    logger.info(f"🛡️ Moderation: {'Enabled' if ENABLE_MODERATION else 'Disabled'}")
    logger.info("=" * 50)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Validate token
    if not validate_facebook_token():
        logger.error("❌ Token validation failed. Exiting.")
        sys.exit(1)
    
    # Get initial page stats
    get_page_stats()
    
    # Test run (optional - comment out for production)
    user_input = input("\n🧪 Run test post now? (y/n): ").lower()
    if user_input == 'y':
        logger.info("\n🧪 Running test post...")
        test_topic = "Python automation tips for Angel One API trading"
        test_content = generate_ai_post(test_topic)
        post_to_facebook(test_content)
    
    # Schedule daily posts
    schedule.every().day.at(POST_SCHEDULE).do(daily_post_job)
    
    logger.info(f"\n⏰ Scheduler active. Next post at {POST_SCHEDULE}")
    logger.info("📊 Press Ctrl+C to stop\n")
    
    # Run scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # Check for --test flag
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_generation_only()
    else:
        try:
            main()
        except KeyboardInterrupt:
            signal_handler(None, None)
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            sys.exit(1)
