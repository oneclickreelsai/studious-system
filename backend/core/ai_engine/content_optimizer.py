"""
AI-powered content optimization for viral potential
Uses Perplexity as PRIMARY, OpenAI as FALLBACK
"""
import os
import logging
import requests
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from backend.utils.error_handler import retry_with_backoff, handle_api_error
from backend.utils.rate_limiter import rate_limit
from backend.utils.cache_manager import cached
from backend.config.settings import settings

load_dotenv("config.env")
logger = logging.getLogger(__name__)

# Perplexity (PRIMARY)
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")

# OpenAI (FALLBACK)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_ai_client():
    """Get AI client - Perplexity first, OpenAI fallback."""
    if PERPLEXITY_API_KEY:
        return OpenAI(
            base_url="https://api.perplexity.ai",
            api_key=PERPLEXITY_API_KEY,
            timeout=30.0
        ), PERPLEXITY_MODEL, "perplexity"
    elif OPENAI_API_KEY:
        return OpenAI(api_key=OPENAI_API_KEY, timeout=30.0), "gpt-4o-mini", "openai"
    return None, None, None


client, model, provider = get_ai_client()

class ContentOptimizer:
    """Optimize content for maximum viral potential."""
    
    def __init__(self):
        self.viral_patterns = {
            "motivation": {
                "hooks": ["Stop scrolling if", "This changed my life", "Nobody talks about", "The truth about"],
                "emotions": ["urgency", "curiosity", "inspiration", "fear_of_missing_out"],
                "keywords": ["success", "mindset", "discipline", "growth", "habits"]
            },
            "finance": {
                "hooks": ["Rich people know", "Banks don't want", "Money secret", "Financial mistake"],
                "emotions": ["greed", "fear", "security", "aspiration"],
                "keywords": ["wealth", "investment", "passive income", "financial freedom"]
            },
            "facts": {
                "hooks": ["Did you know", "Scientists discovered", "This will blow your mind", "Fact that"],
                "emotions": ["curiosity", "surprise", "amazement", "knowledge"],
                "keywords": ["research", "study", "discovery", "science", "psychology"]
            }
        }
    
    @retry_with_backoff(max_retries=3)
    @handle_api_error
    @rate_limit("openai")
    @cached("content_optimization", ttl=7200)  # 2 hours cache
    def analyze_viral_potential(self, script: str, niche: str) -> Dict[str, Any]:
        """Analyze script for viral potential and suggest improvements."""
        
        analysis_prompt = f"""
        Analyze this {niche} script for viral potential on social media platforms like TikTok, Instagram Reels, and YouTube Shorts.

        Script: "{script}"

        Provide analysis in this JSON format:
        {{
            "viral_score": 0-100,
            "hook_strength": 0-10,
            "emotional_impact": 0-10,
            "retention_factors": ["factor1", "factor2"],
            "improvement_suggestions": ["suggestion1", "suggestion2"],
            "optimal_length": "seconds",
            "target_demographics": ["demo1", "demo2"],
            "trending_elements": ["element1", "element2"],
            "call_to_action_strength": 0-10
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a viral content expert who analyzes short-form video scripts. Return only valid JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                timeout=30
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content.strip())
            logger.info(f"Viral analysis completed for {niche} script using {provider}")
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse viral analysis JSON: {e}")
            return self._get_fallback_analysis(script, niche)
        except Exception as e:
            logger.error(f"Viral analysis failed: {e}")
            raise
    
    def _get_fallback_analysis(self, script: str, niche: str) -> Dict[str, Any]:
        """Provide fallback analysis when AI fails."""
        patterns = self.viral_patterns.get(niche, self.viral_patterns["motivation"])
        
        # Simple heuristic analysis
        hook_strength = 8 if any(hook.lower() in script.lower() for hook in patterns["hooks"]) else 5
        keyword_count = sum(1 for keyword in patterns["keywords"] if keyword.lower() in script.lower())
        
        return {
            "viral_score": min(85, 40 + (hook_strength * 3) + (keyword_count * 5)),
            "hook_strength": hook_strength,
            "emotional_impact": 7,
            "retention_factors": ["strong_hook", "clear_message"],
            "improvement_suggestions": ["Add more emotional triggers", "Include trending keywords"],
            "optimal_length": "30-45",
            "target_demographics": ["18-34", "entrepreneurs"],
            "trending_elements": patterns["keywords"][:2],
            "call_to_action_strength": 6
        }
    
    @retry_with_backoff(max_retries=3)
    @handle_api_error
    @rate_limit("openai")
    def optimize_script(self, script: str, niche: str, target_score: int = 85) -> Dict[str, Any]:
        """Optimize script to improve viral potential."""
        
        # First analyze current script
        analysis = self.analyze_viral_potential(script, niche)
        
        if analysis["viral_score"] >= target_score:
            logger.info(f"Script already optimized (score: {analysis['viral_score']})")
            return {"optimized_script": script, "analysis": analysis, "improved": False}
        
        # Generate optimized version
        optimization_prompt = f"""
        Optimize this {niche} script to increase viral potential. Current viral score: {analysis['viral_score']}/100

        Original script: "{script}"

        Improvement areas:
        {', '.join(analysis.get('improvement_suggestions', []))}

        Create an optimized version that:
        1. Strengthens the hook (current: {analysis['hook_strength']}/10)
        2. Increases emotional impact (current: {analysis['emotional_impact']}/10)
        3. Adds trending elements: {', '.join(analysis.get('trending_elements', []))}
        4. Maintains the core message
        5. Stays under 40 seconds when spoken

        Return only the optimized script, no explanations.
        """
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a viral content optimizer. Create engaging, scroll-stopping scripts."},
                    {"role": "user", "content": optimization_prompt}
                ],
                temperature=0.7,
                timeout=30
            )
            
            optimized_script = response.choices[0].message.content.strip()
            
            # Analyze optimized version
            new_analysis = self.analyze_viral_potential(optimized_script, niche)
            
            logger.info(f"Script optimized: {analysis['viral_score']} → {new_analysis['viral_score']}")
            
            return {
                "optimized_script": optimized_script,
                "original_analysis": analysis,
                "optimized_analysis": new_analysis,
                "improved": new_analysis["viral_score"] > analysis["viral_score"],
                "improvement": new_analysis["viral_score"] - analysis["viral_score"]
            }
            
        except Exception as e:
            logger.error(f"Script optimization failed: {e}")
            return {"optimized_script": script, "analysis": analysis, "improved": False, "error": str(e)}
    
    def get_trending_topics(self, niche: str, count: int = 10) -> List[str]:
        """Get trending topics for a niche (mock implementation - could integrate with real trend APIs)."""
        trending_topics = {
            "motivation": [
                "morning routine", "discipline", "mindset shift", "productivity hacks",
                "success habits", "mental strength", "goal setting", "time management",
                "self improvement", "confidence building"
            ],
            "finance": [
                "passive income", "investing tips", "money mindset", "financial freedom",
                "side hustles", "crypto basics", "budgeting", "wealth building",
                "retirement planning", "debt elimination"
            ],
            "facts": [
                "psychology facts", "brain science", "human behavior", "productivity secrets",
                "memory tricks", "decision making", "cognitive biases", "social psychology",
                "neuroscience", "behavioral economics"
            ]
        }
        
        return trending_topics.get(niche, trending_topics["motivation"])[:count]
    
    def suggest_optimal_posting_times(self, niche: str, timezone: str = "UTC") -> Dict[str, List[str]]:
        """Suggest optimal posting times based on niche and audience."""
        # Based on social media research and niche-specific audience behavior
        posting_times = {
            "motivation": {
                "weekdays": ["06:00-08:00", "12:00-13:00", "18:00-20:00"],
                "weekends": ["08:00-10:00", "14:00-16:00", "19:00-21:00"],
                "best_days": ["Monday", "Tuesday", "Thursday"]
            },
            "finance": {
                "weekdays": ["07:00-09:00", "12:00-14:00", "17:00-19:00"],
                "weekends": ["09:00-11:00", "15:00-17:00"],
                "best_days": ["Tuesday", "Wednesday", "Thursday"]
            },
            "facts": {
                "weekdays": ["11:00-13:00", "15:00-17:00", "20:00-22:00"],
                "weekends": ["10:00-12:00", "16:00-18:00", "20:00-22:00"],
                "best_days": ["Wednesday", "Thursday", "Friday"]
            }
        }
        
        return posting_times.get(niche, posting_times["motivation"])
    
    def generate_hashtag_strategy(self, script: str, niche: str, platform: str = "instagram") -> Dict[str, List[str]]:
        """Generate strategic hashtags for maximum reach."""
        
        base_hashtags = {
            "motivation": {
                "high_volume": ["#motivation", "#success", "#mindset", "#inspiration", "#goals"],
                "medium_volume": ["#discipline", "#productivity", "#selfimprovement", "#hustle", "#growth"],
                "niche_specific": ["#morningroutine", "#successmindset", "#entrepreneurlife", "#personaldevelopment"],
                "trending": ["#motivationmonday", "#successstory", "#mindsetshift", "#levelup"]
            },
            "finance": {
                "high_volume": ["#money", "#finance", "#investing", "#wealth", "#business"],
                "medium_volume": ["#financialfreedom", "#passiveincome", "#entrepreneur", "#investing101"],
                "niche_specific": ["#moneytips", "#wealthbuilding", "#financialplanning", "#sidehustle"],
                "trending": ["#financetips", "#moneygoals", "#investingtips", "#wealthmindset"]
            },
            "facts": {
                "high_volume": ["#facts", "#psychology", "#science", "#knowledge", "#learning"],
                "medium_volume": ["#psychologyfacts", "#brainfacts", "#interesting", "#educational"],
                "niche_specific": ["#humanbehavior", "#cognitivescience", "#neuroscience", "#mindtricks"],
                "trending": ["#didyouknow", "#amazingfacts", "#mindblown", "#sciencefacts"]
            }
        }
        
        hashtags = base_hashtags.get(niche, base_hashtags["motivation"])
        
        # Platform-specific adjustments
        if platform == "tiktok":
            hashtags["platform_specific"] = ["#fyp", "#viral", "#trending", "#foryou"]
        elif platform == "youtube":
            hashtags["platform_specific"] = ["#shorts", "#viral", "#trending"]
        else:  # Instagram
            hashtags["platform_specific"] = ["#reels", "#viral", "#explore", "#trending"]
        
        return hashtags

# Global content optimizer instance
content_optimizer = ContentOptimizer()