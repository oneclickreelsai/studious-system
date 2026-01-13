"""
Application monitoring and metrics
"""
import time
import psutil
import logging
from typing import Dict, Any, List
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and track application metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics = defaultdict(deque)
        self.counters = defaultdict(int)
        self.timers = {}
        
    def increment_counter(self, metric_name: str, value: int = 1):
        """Increment a counter metric."""
        self.counters[metric_name] += value
        
    def record_timing(self, metric_name: str, duration: float):
        """Record a timing metric."""
        if len(self.metrics[metric_name]) >= self.max_history:
            self.metrics[metric_name].popleft()
        
        self.metrics[metric_name].append({
            "timestamp": time.time(),
            "value": duration
        })
    
    def start_timer(self, timer_name: str):
        """Start a timer."""
        self.timers[timer_name] = time.time()
    
    def end_timer(self, timer_name: str) -> float:
        """End a timer and record the duration."""
        if timer_name not in self.timers:
            return 0.0
        
        duration = time.time() - self.timers[timer_name]
        del self.timers[timer_name]
        
        self.record_timing(timer_name, duration)
        return duration
    
    def get_counter(self, metric_name: str) -> int:
        """Get current counter value."""
        return self.counters[metric_name]
    
    def get_timing_stats(self, metric_name: str, hours: int = 1) -> Dict[str, float]:
        """Get timing statistics for the last N hours."""
        cutoff_time = time.time() - (hours * 3600)
        recent_timings = [
            m["value"] for m in self.metrics[metric_name] 
            if m["timestamp"] > cutoff_time
        ]
        
        if not recent_timings:
            return {"count": 0, "avg": 0, "min": 0, "max": 0}
        
        return {
            "count": len(recent_timings),
            "avg": sum(recent_timings) / len(recent_timings),
            "min": min(recent_timings),
            "max": max(recent_timings)
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics summary."""
        return {
            "counters": dict(self.counters),
            "timing_stats": {
                name: self.get_timing_stats(name) 
                for name in self.metrics.keys()
            },
            "system": self.get_system_metrics()
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}

class PerformanceMonitor:
    """Monitor application performance and health."""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.alerts = []
        self.thresholds = {
            "video_generation_time": 300,  # 5 minutes
            "api_response_time": 30,  # 30 seconds
            "error_rate": 0.1,  # 10%
            "memory_usage": 80,  # 80%
            "cpu_usage": 90  # 90%
        }
    
    def record_video_generation(self, duration: float, success: bool, niche: str = None):
        """Record video generation metrics."""
        self.metrics.record_timing("video_generation_time", duration)
        
        if success:
            self.metrics.increment_counter("videos_generated_success")
        else:
            self.metrics.increment_counter("videos_generated_failed")
        
        if niche:
            self.metrics.increment_counter(f"videos_by_niche_{niche}")
        
        # Check for performance alerts
        if duration > self.thresholds["video_generation_time"]:
            self.add_alert("slow_video_generation", f"Video generation took {duration:.1f}s")
    
    def record_api_call(self, service: str, duration: float, success: bool):
        """Record API call metrics."""
        self.metrics.record_timing(f"api_{service}_time", duration)
        
        if success:
            self.metrics.increment_counter(f"api_{service}_success")
        else:
            self.metrics.increment_counter(f"api_{service}_failed")
        
        # Check for API performance alerts
        if duration > self.thresholds["api_response_time"]:
            self.add_alert("slow_api_response", f"{service} API took {duration:.1f}s")
    
    def record_upload(self, platform: str, success: bool, duration: float = None):
        """Record upload metrics."""
        if success:
            self.metrics.increment_counter(f"uploads_{platform}_success")
        else:
            self.metrics.increment_counter(f"uploads_{platform}_failed")
        
        if duration:
            self.metrics.record_timing(f"upload_{platform}_time", duration)
    
    def add_alert(self, alert_type: str, message: str):
        """Add a performance alert."""
        alert = {
            "timestamp": time.time(),
            "type": alert_type,
            "message": message
        }
        self.alerts.append(alert)
        
        # Keep only recent alerts (last 24 hours)
        cutoff_time = time.time() - 86400
        self.alerts = [a for a in self.alerts if a["timestamp"] > cutoff_time]
        
        logger.warning(f"Performance alert: {alert_type} - {message}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        metrics = self.metrics.get_all_metrics()
        
        # Calculate error rates
        error_rates = {}
        for service in ["openai", "youtube", "pexels", "pixabay", "facebook"]:
            success = metrics["counters"].get(f"api_{service}_success", 0)
            failed = metrics["counters"].get(f"api_{service}_failed", 0)
            total = success + failed
            
            if total > 0:
                error_rates[service] = failed / total
        
        # Recent alerts
        recent_alerts = [
            a for a in self.alerts 
            if a["timestamp"] > time.time() - 3600  # Last hour
        ]
        
        return {
            "metrics": metrics,
            "error_rates": error_rates,
            "recent_alerts": recent_alerts,
            "alert_count_24h": len(self.alerts),
            "health_score": self.calculate_health_score(metrics, error_rates)
        }
    
    def calculate_health_score(self, metrics: Dict, error_rates: Dict) -> float:
        """Calculate overall health score (0-100)."""
        score = 100.0
        
        # Deduct for high error rates
        avg_error_rate = sum(error_rates.values()) / len(error_rates) if error_rates else 0
        if avg_error_rate > self.thresholds["error_rate"]:
            score -= (avg_error_rate - self.thresholds["error_rate"]) * 100
        
        # Deduct for high resource usage
        system_metrics = metrics.get("system", {})
        if system_metrics.get("memory_percent", 0) > self.thresholds["memory_usage"]:
            score -= 10
        
        if system_metrics.get("cpu_percent", 0) > self.thresholds["cpu_usage"]:
            score -= 10
        
        # Deduct for recent alerts
        recent_alert_count = len([
            a for a in self.alerts 
            if a["timestamp"] > time.time() - 3600
        ])
        score -= min(recent_alert_count * 5, 20)  # Max 20 points deduction
        
        return max(0.0, min(100.0, score))

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def timed_operation(operation_name: str):
    """Decorator to time operations and record metrics."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                logger.error(f"Operation {operation_name} failed: {e}")
                raise
            finally:
                duration = time.time() - start_time
                performance_monitor.metrics.record_timing(operation_name, duration)
                
                if operation_name.startswith("api_"):
                    service = operation_name.replace("api_", "")
                    performance_monitor.record_api_call(service, duration, success)
        
        return wrapper
    return decorator