"""
AI-powered trend analysis and content suggestions
"""
import os
import logging
import time
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from openai import OpenAI
from backend.utils.error_handler import retry_with_backoff, handle_api_error
from backend.utils.rate_limiter import rate_limit
from backend.utils.cache_manager import cached
from backend.config.settings import settings

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.openai_api_key)

class TrendAnalyzer:
    """Analyze trends and suggest viral content opportunities."""
    
    def __init__(self):
        self.trend_sources = {
            "google_trends": "https://trends.google.com/trends/api/dailytrends",
            "youtube_trending": "https://www.googleapis.com/youtube/v3/videos",
            "reddit_trending": "https://www.reddit.com/r/all/hot.json"
        }
        
        # Trend categories mapping
        self.category_mapping = {
            "motivation": ["self-improvement", "productivity", "success", "mindset", "goals"],
            "finance": ["investing", "money", "business", "cryptocurrency", "economy"],
            "facts": ["science", "psychology", "technology", "research", "education"]
        }
    
    @cached("trending_topics", ttl=3600)  # Cache for 1 hour
    def get_trending_topics(self, niche: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending topics for a specific niche."""
        
        trending_topics = []
        
        # Get trends from multiple sources
        try:
            # Reddit trends (most accessible)
            reddit_trends = self._get_reddit_trends(niche, limit // 2)
            trending_topics.extend(reddit_trends)
            
            # Google Trends simulation (would need real API)
            google_trends = self._simulate_google_trends(niche, limit // 2)
            trending_topics.extend(google_trends)
            
        except Exception as e:
            logger.error(f"Error fetching trends: {e}")
            # Fallback to curated trending topics
            trending_topics = self._get_fallback_trends(niche, limit)
        
        # Sort by trend score and return top results
        trending_topics.sort(key=lambda x: x.get("trend_score", 0), reverse=True)
        return trending_topics[:limit]
    
    def _get_reddit_trends(self, niche: str, limit: int) -> List[Dict[str, Any]]:
        """Get trending topics from Reddit."""
        try:
            # Map niche to relevant subreddits
            subreddit_mapping = {
                "motivation": ["GetMotivated", "productivity", "selfimprovement", "decidingtobebetter"],
                "finance": ["personalfinance", "investing", "financialindependence", "stocks"],
                "facts": ["todayilearned", "science", "psychology", "interestingasfuck"]
            }
            
            subreddits = subreddit_mapping.get(niche, subreddit_mapping["motivation"])
            trending_topics = []
            
            for subreddit in subreddits[:2]:  # Limit API calls
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                    headers = {"User-Agent": "OneClickReels/1.0"}
                    
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        
                        for post in data["data"]["children"][:5]:
                            post_data = post["data"]
                            
                            # Calculate trend score based on engagement
                            trend_score = (
                                post_data.get("score", 0) * 0.4 +
                                post_data.get("num_comments", 0) * 0.3 +
                                (1000 - (time.time() - post_data.get("created_utc", 0)) / 3600) * 0.3
                            )
                            
                            trending_topics.append({
                                "title": post_data.get("title", ""),
                                "topic": self._extract_topic_from_title(post_data.get("title", "")),
                                "source": f"r/{subreddit}",
                                "trend_score": max(0, trend_score),
                                "engagement": post_data.get("score", 0),
                                "url": f"https://reddit.com{post_data.get('permalink', '')}",
                                "created": datetime.fromtimestamp(post_data.get("created_utc", 0))
                            })
                            
                except Exception as e:
                    logger.warning(f"Failed to fetch from r/{subreddit}: {e}")
                    continue
            
            return trending_topics
            
        except Exception as e:
            logger.error(f"Reddit trends fetch failed: {e}")
            return []
    
    def _simulate_google_trends(self, niche: str, limit: int) -> List[Dict[str, Any]]:
        """Simulate Google Trends data (replace with real API when available)."""
        
        # Simulated trending topics based on current patterns
        simulated_trends = {
            "motivation": [
                {"topic": "morning routine 2024", "trend_score": 85, "growth": "+150%"},
                {"topic": "productivity hacks", "trend_score": 78, "growth": "+120%"},
                {"topic": "discipline mindset", "trend_score": 72, "growth": "+95%"},
                {"topic": "success habits", "trend_score": 68, "growth": "+80%"},
                {"topic": "goal setting method", "trend_score": 65, "growth": "+75%"}
            ],
            "finance": [
                {"topic": "passive income 2024", "trend_score": 92, "growth": "+200%"},
                {"topic": "investing for beginners", "trend_score": 88, "growth": "+180%"},
                {"topic": "side hustle ideas", "trend_score": 82, "growth": "+160%"},
                {"topic": "financial freedom", "trend_score": 76, "growth": "+140%"},
                {"topic": "money mindset", "trend_score": 70, "growth": "+110%"}
            ],
            "facts": [
                {"topic": "psychology facts 2024", "trend_score": 89, "growth": "+170%"},
                {"topic": "brain science", "trend_score": 84, "growth": "+155%"},
                {"topic": "human behavior", "trend_score": 79, "growth": "+130%"},
                {"topic": "productivity secrets", "trend_score": 74, "growth": "+115%"},
                {"topic": "memory techniques", "trend_score": 69, "growth": "+100%"}
            ]
        }
        
        trends = simulated_trends.get(niche, simulated_trends["motivation"])
        
        # Add metadata
        for trend in trends:
            trend.update({
                "source": "Google Trends",
                "created": datetime.now(),
                "title": f"Trending: {trend['topic']}",
                "url": f"https://trends.google.com/trends/explore?q={trend['topic'].replace(' ', '+')}"
            })
        
        return trends[:limit]
    
    def _get_fallback_trends(self, niche: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback trending topics when APIs fail."""
        
        fallback_trends = {
            "motivation": [
                "morning routine", "discipline", "productivity", "success mindset", "goal setting",
                "time management", "self improvement", "mental strength", "habits", "focus"
            ],
            "finance": [
                "passive income", "investing", "money mindset", "financial freedom", "side hustle",
                "wealth building", "budgeting", "retirement", "crypto", "stocks"
            ],
            "facts": [
                "psychology facts", "brain science", "human behavior", "productivity secrets",
                "memory tricks", "cognitive bias", "neuroscience", "social psychology"
            ]
        }
        
        topics = fallback_trends.get(niche, fallback_trends["motivation"])
        
        return [
            {
                "topic": topic,
                "title": f"Evergreen: {topic}",
                "source": "Curated",
                "trend_score": 50,
                "created": datetime.now(),
                "url": ""
            }
            for topic in topics[:limit]
        ]
    
    def _extract_topic_from_title(self, title: str) -> str:
        """Extract main topic from a title using simple NLP."""
        # Remove common words and extract key terms
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = [word.lower().strip(".,!?") for word in title.split() if word.lower() not in stop_words]
        
        # Return first few meaningful words
        return " ".join(words[:3])
    
    @retry_with_backoff(max_retries=3)
    @handle_api_error
    @rate_limit("openai")
    @cached("trend_analysis", ttl=1800)  # 30 minutes cache
    def analyze_trend_potential(self, topic: str, niche: str) -> Dict[str, Any]:
        """Analyze the viral potential of a trending topic."""
        
        analysis_prompt = f"""
        Analyze the viral potential of this topic for {niche} content on social media platforms:
        
        Topic: "{topic}"
        Niche: {niche}
        
        Provide analysis in JSON format:
        {{
            "viral_potential": 0-100,
            "audience_interest": 0-10,
            "content_saturation": 0-10,
            "trending_keywords": ["keyword1", "keyword2", "keyword3"],
            "content_angles": ["angle1", "angle2", "angle3"],
            "target_demographics": ["demo1", "demo2"],
            "optimal_platforms": ["platform1", "platform2"],
            "content_suggestions": ["suggestion1", "suggestion2"],
            "hashtag_recommendations": ["#hashtag1", "#hashtag2"],
            "timing_recommendation": "best time to post about this topic"
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a viral content trend analyst. Return only valid JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                timeout=30
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content.strip())
            
            # Add metadata
            analysis["analyzed_at"] = datetime.now().isoformat()
            analysis["topic"] = topic
            analysis["niche"] = niche
            
            logger.info(f"Trend analysis completed for '{topic}' in {niche}")
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse trend analysis JSON: {e}")
            return self._get_fallback_analysis(topic, niche)
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            raise
    
    def _get_fallback_analysis(self, topic: str, niche: str) -> Dict[str, Any]:
        """Provide fallback analysis when AI fails."""
        return {
            "viral_potential": 65,
            "audience_interest": 7,
            "content_saturation": 5,
            "trending_keywords": [topic.split()[0], niche, "trending"],
            "content_angles": ["educational", "motivational", "behind-the-scenes"],
            "target_demographics": ["18-34", "professionals"],
            "optimal_platforms": ["instagram", "tiktok", "youtube"],
            "content_suggestions": [f"Create {niche} content about {topic}"],
            "hashtag_recommendations": [f"#{niche}", f"#{topic.replace(' ', '')}", "#viral"],
            "timing_recommendation": "Post during peak hours (6-9 PM)",
            "analyzed_at": datetime.now().isoformat(),
            "topic": topic,
            "niche": niche
        }
    
    @cached("content_opportunities", ttl=7200)  # 2 hours cache
    def find_content_opportunities(self, niche: str, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Find upcoming content opportunities based on trends and events."""
        
        opportunities = []
        
        # Get trending topics
        trending_topics = self.get_trending_topics(niche, 10)
        
        # Analyze each trend for content opportunities
        for trend in trending_topics[:5]:  # Limit API calls
            try:
                analysis = self.analyze_trend_potential(trend["topic"], niche)
                
                if analysis["viral_potential"] > 60:  # Only high-potential trends
                    opportunity = {
                        "topic": trend["topic"],
                        "opportunity_score": analysis["viral_potential"],
                        "content_angles": analysis["content_angles"],
                        "suggested_scripts": self._generate_script_ideas(trend["topic"], niche),
                        "optimal_timing": analysis["timing_recommendation"],
                        "hashtags": analysis["hashtag_recommendations"],
                        "competition_level": analysis["content_saturation"],
                        "trend_source": trend["source"],
                        "expires_at": datetime.now() + timedelta(days=days_ahead)
                    }
                    opportunities.append(opportunity)
                    
            except Exception as e:
                logger.warning(f"Failed to analyze trend '{trend['topic']}': {e}")
                continue
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        logger.info(f"Found {len(opportunities)} content opportunities for {niche}")
        return opportunities
    
    def _generate_script_ideas(self, topic: str, niche: str) -> List[str]:
        """Generate quick script ideas for a trending topic."""
        
        script_templates = {
            "motivation": [
                f"The truth about {topic} that nobody talks about",
                f"How {topic} changed my life in 30 days",
                f"3 {topic} mistakes that keep you stuck"
            ],
            "finance": [
                f"The {topic} strategy rich people use",
                f"How I made money with {topic}",
                f"{topic} mistakes that cost you thousands"
            ],
            "facts": [
                f"Mind-blowing facts about {topic}",
                f"The science behind {topic}",
                f"What you didn't know about {topic}"
            ]
        }
        
        templates = script_templates.get(niche, script_templates["motivation"])
        return templates
    
    def get_competitor_analysis(self, niche: str, topic: str) -> Dict[str, Any]:
        """Analyze competitor content for a specific topic."""
        
        # This would integrate with social media APIs in production
        # For now, return simulated competitor analysis
        
        return {
            "topic": topic,
            "niche": niche,
            "top_performers": [
                {
                    "creator": "MotivationDaily",
                    "views": 2500000,
                    "engagement_rate": 8.5,
                    "content_style": "Bold text, fast cuts"
                },
                {
                    "creator": "SuccessMindset",
                    "views": 1800000,
                    "engagement_rate": 7.2,
                    "content_style": "Storytelling, personal examples"
                }
            ],
            "content_gaps": [
                "Lack of actionable steps",
                "Missing personal stories",
                "No call-to-action"
            ],
            "opportunity_score": 75,
            "recommended_approach": "Focus on actionable advice with personal examples",
            "analyzed_at": datetime.now().isoformat()
        }

# Global trend analyzer instance
trend_analyzer = TrendAnalyzer()