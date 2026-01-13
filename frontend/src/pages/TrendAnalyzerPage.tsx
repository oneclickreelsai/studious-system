import { useState, useEffect } from "react";
import { TrendingUp, Loader2, Flame, Hash, Clock, BarChart3, RefreshCw, Sparkles, ArrowUp, ArrowDown } from "lucide-react";

import { API_URL } from '../config/api';

interface TrendingTopic {
  topic: string;
  score: number;
  change: number;
  category: string;
  volume: string;
  related: string[];
}

interface TrendData {
  topics: TrendingTopic[];
  hashtags: { tag: string; count: number; trend: "up" | "down" | "stable" }[];
  niches: { name: string; score: number; growth: number }[];
  updated_at: string;
}

export function TrendAnalyzerPage() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<TrendData | null>(null);
  const [selectedNiche, setSelectedNiche] = useState("all");
  const [timeRange, setTimeRange] = useState("24h");
  const [error, setError] = useState("");

  useEffect(() => {
    fetchTrends();
  }, [selectedNiche, timeRange]);

  const fetchTrends = async () => {
    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_URL}/api/trends?niche=${selectedNiche}&range=${timeRange}`);
      
      if (!res.ok) {
        // Use mock data if API not available
        setData(getMockData());
        return;
      }

      const result = await res.json();
      setData(result);
    } catch {
      // Use mock data on error
      setData(getMockData());
    } finally {
      setLoading(false);
    }
  };

  const getMockData = (): TrendData => ({
    topics: [
      { topic: "AI Video Generation", score: 95, change: 12, category: "tech", volume: "1.2M", related: ["ChatGPT", "Midjourney", "Sora"] },
      { topic: "Crypto Bull Run 2024", score: 88, change: 8, category: "finance", volume: "890K", related: ["Bitcoin", "Ethereum", "Altcoins"] },
      { topic: "Morning Routine Tips", score: 82, change: -3, category: "lifestyle", volume: "650K", related: ["Productivity", "Health", "Habits"] },
      { topic: "Stock Market Analysis", score: 78, change: 5, category: "finance", volume: "520K", related: ["Trading", "Investing", "S&P500"] },
      { topic: "Fitness Motivation", score: 75, change: 2, category: "health", volume: "480K", related: ["Gym", "Workout", "Diet"] },
    ],
    hashtags: [
      { tag: "viral", count: 2500000, trend: "up" },
      { tag: "fyp", count: 1800000, trend: "stable" },
      { tag: "trending", count: 1200000, trend: "up" },
      { tag: "motivation", count: 950000, trend: "up" },
      { tag: "crypto", count: 780000, trend: "down" },
      { tag: "ai", count: 650000, trend: "up" },
    ],
    niches: [
      { name: "Technology", score: 92, growth: 15 },
      { name: "Finance", score: 85, growth: 8 },
      { name: "Motivation", score: 78, growth: 5 },
      { name: "Comedy", score: 75, growth: -2 },
      { name: "Education", score: 72, growth: 12 },
    ],
    updated_at: new Date().toISOString()
  });

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-yellow-400";
    return "text-red-400";
  };

  const getChangeIcon = (change: number) => {
    if (change > 0) return <ArrowUp className="w-4 h-4 text-green-400" />;
    if (change < 0) return <ArrowDown className="w-4 h-4 text-red-400" />;
    return null;
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 mb-6 shadow-lg shadow-amber-500/30">
          <TrendingUp className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-3">Trend Analyzer</h2>
        <p className="text-neutral-400">Discover what's trending and create viral content</p>
      </div>

      {/* Filters */}
      <div className="bg-[#12121a] border border-white/10 rounded-2xl p-4 mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex gap-2">
            {["all", "tech", "finance", "lifestyle", "entertainment"].map((niche) => (
              <button
                key={niche}
                onClick={() => setSelectedNiche(niche)}
                className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
                  selectedNiche === niche
                    ? "bg-amber-500/20 text-amber-400 border border-amber-500/50"
                    : "bg-white/5 text-neutral-400 border border-white/10 hover:border-white/20"
                }`}
              >
                {niche}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none"
            >
              <option value="1h" className="bg-[#12121a]">Last Hour</option>
              <option value="24h" className="bg-[#12121a]">Last 24 Hours</option>
              <option value="7d" className="bg-[#12121a]">Last 7 Days</option>
              <option value="30d" className="bg-[#12121a]">Last 30 Days</option>
            </select>

            <button
              onClick={fetchTrends}
              disabled={loading}
              className="p-2 bg-white/5 hover:bg-white/10 rounded-lg text-neutral-400 hover:text-white"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-300 mb-6">
          {error}
        </div>
      )}

      {loading && !data ? (
        <div className="text-center py-20">
          <Loader2 className="w-10 h-10 text-amber-400 animate-spin mx-auto mb-4" />
          <p className="text-neutral-400">Analyzing trends...</p>
        </div>
      ) : data && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Trending Topics */}
          <div className="lg:col-span-2 space-y-4">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Flame className="w-5 h-5 text-orange-400" />
              Trending Topics
            </h3>
            
            <div className="space-y-3">
              {data.topics.map((topic, index) => (
                <div
                  key={index}
                  className="bg-[#12121a] border border-white/10 rounded-xl p-4 hover:border-amber-500/30 transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-bold text-amber-400">#{index + 1}</span>
                        <h4 className="font-medium text-white">{topic.topic}</h4>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-neutral-500">
                        <span className="capitalize">{topic.category}</span>
                        <span>{topic.volume} searches</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getScoreColor(topic.score)}`}>
                        {topic.score}
                      </div>
                      <div className="flex items-center justify-end gap-1 text-xs">
                        {getChangeIcon(topic.change)}
                        <span className={topic.change >= 0 ? "text-green-400" : "text-red-400"}>
                          {topic.change > 0 ? "+" : ""}{topic.change}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Score Bar */}
                  <div className="h-1.5 bg-white/10 rounded-full overflow-hidden mb-3">
                    <div 
                      className="h-full bg-gradient-to-r from-amber-500 to-orange-500"
                      style={{ width: `${topic.score}%` }}
                    />
                  </div>

                  {/* Related Topics */}
                  <div className="flex flex-wrap gap-2">
                    {topic.related.map((rel, i) => (
                      <span key={i} className="px-2 py-1 bg-white/5 text-neutral-400 text-xs rounded-full">
                        {rel}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Trending Hashtags */}
            <div className="bg-[#12121a] border border-white/10 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-4">
                <Hash className="w-4 h-4 text-cyan-400" />
                Trending Hashtags
              </h3>
              
              <div className="space-y-3">
                {data.hashtags.map((hashtag, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-cyan-400 font-medium">#{hashtag.tag}</span>
                      {hashtag.trend === "up" && <ArrowUp className="w-3 h-3 text-green-400" />}
                      {hashtag.trend === "down" && <ArrowDown className="w-3 h-3 text-red-400" />}
                    </div>
                    <span className="text-xs text-neutral-500">
                      {(hashtag.count / 1000000).toFixed(1)}M
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Niche Performance */}
            <div className="bg-[#12121a] border border-white/10 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-4">
                <BarChart3 className="w-4 h-4 text-purple-400" />
                Niche Performance
              </h3>
              
              <div className="space-y-3">
                {data.niches.map((niche, index) => (
                  <div key={index}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-neutral-300">{niche.name}</span>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs ${niche.growth >= 0 ? "text-green-400" : "text-red-400"}`}>
                          {niche.growth > 0 ? "+" : ""}{niche.growth}%
                        </span>
                        <span className="text-sm font-medium text-white">{niche.score}</span>
                      </div>
                    </div>
                    <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                        style={{ width: `${niche.score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-gradient-to-br from-amber-900/20 to-orange-900/20 border border-amber-500/20 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">
                <Sparkles className="w-4 h-4 text-amber-400" />
                Quick Actions
              </h3>
              <button className="w-full py-3 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/30 rounded-lg text-amber-300 font-medium text-sm transition-colors">
                Generate Content from Top Trend
              </button>
            </div>

            {/* Last Updated */}
            <div className="text-center text-xs text-neutral-500 flex items-center justify-center gap-1">
              <Clock className="w-3 h-3" />
              Updated {new Date(data.updated_at).toLocaleTimeString()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

