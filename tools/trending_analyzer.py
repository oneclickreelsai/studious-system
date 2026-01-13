"""
YouTube Trending Content Analyzer (Legal Research Tool)
Analyzes trending videos to extract topic ideas and insights
WITHOUT downloading copyrighted content

Integrates with ai_engine.trend_analyzer for comprehensive trend analysis
"""
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from video_engine.youtube_downloader_ytdlp import get_video_info
from dotenv import load_dotenv
from rich import print
from rich.table import Table
from rich.console import Console

load_dotenv("config.env")
console = Console()
logger = logging.getLogger(__name__)


def analyze_video(video_url: str):
    """
    Analyze a single video for insights (metadata only)
    
    Args:
        video_url: YouTube video/shorts URL
    
    Returns:
        dict: Analysis results
    """
    try:
        info = get_video_info(video_url)
        
        # Extract insights
        engagement_rate = 0
        if info.get('views', 0) > 0:
            engagement_rate = (info.get('likes', 0) / info['views']) * 100
        
        return {
            "title": info.get("title"),
            "channel": info.get("channel"),
            "views": info.get("views", 0),
            "likes": info.get("likes", 0),
            "duration": info.get("duration", 0),
            "engagement_rate": round(engagement_rate, 2),
            "upload_date": info.get("upload_date"),
            "description": info.get("description", "")[:100]
        }
    except Exception as e:
        print(f"❌ Error analyzing {video_url}: {e}")
        return None


def analyze_trending_topics(video_urls: list, niche: str = "General"):
    """
    Analyze multiple trending videos and extract insights
    
    Args:
        video_urls: List of YouTube URLs to analyze
        niche: Topic category (e.g., "Comedy", "Motivation", "Finance")
    
    Returns:
        dict: Aggregated insights and recommendations
    """
    print(f"\n[cyan]🔍 Analyzing {len(video_urls)} trending videos in '{niche}' niche...[/cyan]\n")
    
    results = []
    total_views = 0
    total_engagement = 0
    
    for url in video_urls:
        analysis = analyze_video(url)
        if analysis:
            results.append(analysis)
            total_views += analysis["views"]
            total_engagement += analysis["engagement_rate"]
    
    if not results:
        print("[red]❌ No videos analyzed successfully[/red]")
        return None
    
    # Create results table
    table = Table(title=f"📊 {niche} Niche Analysis", show_lines=True)
    table.add_column("Title", style="cyan", width=40)
    table.add_column("Channel", style="green")
    table.add_column("Views", style="yellow", justify="right")
    table.add_column("Engagement %", style="magenta", justify="right")
    table.add_column("Duration", style="blue", justify="right")
    
    for result in results:
        views_formatted = f"{result['views']:,}" if result['views'] else "N/A"
        duration_formatted = f"{result['duration']}s" if result['duration'] else "N/A"
        
        table.add_row(
            result['title'][:40] + "..." if len(result['title']) > 40 else result['title'],
            result['channel'],
            views_formatted,
            f"{result['engagement_rate']:.2f}%",
            duration_formatted
        )
    
    console.print(table)
    
    # Calculate insights
    avg_views = total_views // len(results)
    avg_engagement = total_engagement / len(results)
    
    insights = {
        "niche": niche,
        "videos_analyzed": len(results),
        "avg_views": avg_views,
        "avg_engagement": round(avg_engagement, 2),
        "top_video": max(results, key=lambda x: x['views']),
        "recommendations": []
    }
    
    # Generate recommendations
    print("\n[bold green]💡 Content Strategy Recommendations:[/bold green]")
    
    if avg_engagement > 5:
        print("✅ High engagement niche - Great opportunity!")
        insights["recommendations"].append("High engagement potential")
    elif avg_engagement > 2:
        print("⚠️ Moderate engagement - Focus on quality")
        insights["recommendations"].append("Focus on quality over quantity")
    else:
        print("⚠️ Low engagement - Consider different angles")
        insights["recommendations"].append("Try unique angles or different subtopics")
    
    # Duration insights
    avg_duration = sum(r['duration'] for r in results if r['duration']) / len([r for r in results if r['duration']])
    print(f"\n📏 Optimal duration: ~{int(avg_duration)}s")
    insights["optimal_duration"] = int(avg_duration)
    
    return insights


def suggest_content_ideas(analyzed_data: dict):
    """
    Generate original content ideas based on trending analysis
    
    Args:
        analyzed_data: Results from analyze_trending_topics()
    """
    print("\n[bold magenta]🎯 Original Content Ideas (Based on Trends):[/bold magenta]")
    
    niche = analyzed_data["niche"]
    
    ideas = {
        "Comedy": [
            f"Create {int(analyzed_data['optimal_duration'])}s comedy shorts about daily life",
            "Use Indian humor style with Hindi/Hinglish mix",
            "Focus on relatable situations (work, family, relationships)"
        ],
        "Motivation": [
            f"Make {int(analyzed_data['optimal_duration'])}s motivational clips",
            "Use powerful quotes with dynamic visuals",
            "Focus on discipline and consistency themes"
        ],
        "Finance": [
            f"Create {int(analyzed_data['optimal_duration'])}s money tips",
            "Explain investing concepts simply",
            "Share practical wealth-building strategies"
        ],
        "General": [
            f"Create {int(analyzed_data['optimal_duration'])}s engaging shorts",
            "Focus on high-quality visuals and clear messaging",
            "Test different content angles"
        ]
    }
    
    for idea in ideas.get(niche, ideas["General"]):
        print(f"  💡 {idea}")


if __name__ == "__main__":
    # Example: Analyze trending comedy shorts
    comedy_urls = [
        "https://www.youtube.com/shorts/EXAMPLE1",
        "https://www.youtube.com/shorts/EXAMPLE2",
        # Add actual trending video URLs
    ]
    
    print("[yellow]⚠️ Replace EXAMPLE URLs with actual trending video URLs to analyze[/yellow]")
    print("[green]This tool only reads metadata - it doesn't download copyrighted content[/green]")
    
    print("\n[cyan]💡 TIP: Use ai_engine.trend_analyzer for AI-powered trend discovery:[/cyan]")
    print("  from ai_engine.trend_analyzer import trend_analyzer")
    print("  trends = trend_analyzer.get_trending_topics('motivation', limit=10)")
    print("  opportunities = trend_analyzer.find_content_opportunities('motivation')")



def get_comprehensive_trend_analysis(niche: str, video_urls: List[str] = None) -> Dict[str, Any]:
    """
    Combine YouTube video analysis with AI trend analysis for comprehensive insights.
    
    Args:
        niche: Content niche (motivation, finance, facts, comedy)
        video_urls: Optional list of YouTube URLs to analyze
    
    Returns:
        dict: Combined analysis with competitor insights and trend opportunities
    """
    try:
        from ai_engine.trend_analyzer import trend_analyzer
        
        results = {
            "niche": niche,
            "competitor_analysis": None,
            "trending_topics": [],
            "content_opportunities": [],
            "recommendations": []
        }
        
        # 1. Analyze competitor videos if URLs provided
        if video_urls:
            print(f"\n[cyan]📊 Analyzing {len(video_urls)} competitor videos...[/cyan]")
            results["competitor_analysis"] = analyze_trending_topics(video_urls, niche)
        
        # 2. Get AI-powered trending topics
        print(f"\n[cyan]🔍 Discovering trending topics for '{niche}'...[/cyan]")
        results["trending_topics"] = trend_analyzer.get_trending_topics(niche, limit=10)
        
        # 3. Find content opportunities
        print(f"\n[cyan]💡 Finding content opportunities...[/cyan]")
        results["content_opportunities"] = trend_analyzer.find_content_opportunities(niche, days_ahead=7)
        
        # 4. Generate combined recommendations
        recommendations = []
        
        # From competitor analysis
        if results["competitor_analysis"]:
            comp = results["competitor_analysis"]
            recommendations.append(f"Target video duration: ~{comp.get('optimal_duration', 30)}s")
            recommendations.append(f"Aim for {comp.get('avg_engagement', 3):.1f}%+ engagement rate")
        
        # From trending topics
        if results["trending_topics"]:
            top_topics = [t["topic"] for t in results["trending_topics"][:3]]
            recommendations.append(f"Hot topics to cover: {', '.join(top_topics)}")
        
        # From content opportunities
        if results["content_opportunities"]:
            top_opportunity = results["content_opportunities"][0]
            recommendations.append(f"Best opportunity: {top_opportunity['topic']} (score: {top_opportunity['opportunity_score']})")
        
        results["recommendations"] = recommendations
        
        # Display summary
        print("\n[bold green]📈 Comprehensive Analysis Summary:[/bold green]")
        for rec in recommendations:
            print(f"  ✅ {rec}")
        
        return results
        
    except ImportError:
        print("[yellow]⚠️ ai_engine.trend_analyzer not available. Using basic analysis only.[/yellow]")
        if video_urls:
            return {"competitor_analysis": analyze_trending_topics(video_urls, niche)}
        return {"error": "No video URLs provided and AI trend analyzer not available"}
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        return {"error": str(e)}


class YouTubeTrendingAnalyzer:
    """
    Class-based analyzer for integration with other modules.
    """
    
    def __init__(self):
        self.analyzed_videos = []
        self.insights_cache = {}
    
    def analyze_single_video(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Analyze a single YouTube video."""
        result = analyze_video(video_url)
        if result:
            self.analyzed_videos.append(result)
        return result
    
    def analyze_batch(self, video_urls: List[str], niche: str = "General") -> Dict[str, Any]:
        """Analyze multiple videos and generate insights."""
        return analyze_trending_topics(video_urls, niche)
    
    def get_content_ideas(self, niche: str) -> List[str]:
        """Get content ideas based on analyzed data."""
        if niche not in self.insights_cache:
            return [
                f"Create engaging {niche} content",
                "Focus on trending topics in your niche",
                "Analyze competitor videos for inspiration"
            ]
        
        analyzed_data = self.insights_cache[niche]
        ideas = []
        
        if analyzed_data.get("optimal_duration"):
            ideas.append(f"Create {analyzed_data['optimal_duration']}s videos")
        
        if analyzed_data.get("avg_engagement", 0) > 5:
            ideas.append("High engagement niche - focus on quality hooks")
        
        return ideas
    
    def export_analysis(self, format: str = "json") -> str:
        """Export analysis results."""
        import json
        
        export_data = {
            "analyzed_videos": self.analyzed_videos,
            "insights": self.insights_cache,
            "total_videos_analyzed": len(self.analyzed_videos)
        }
        
        if format == "json":
            return json.dumps(export_data, indent=2, default=str)
        else:
            return str(export_data)


# Global instance for easy access
youtube_analyzer = YouTubeTrendingAnalyzer()