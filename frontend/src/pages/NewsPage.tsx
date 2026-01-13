import { useState } from "react";
import { Newspaper, Loader2, Cpu, DollarSign, Globe, Trophy, Play, Copy, Check, Flame, CheckCircle } from "lucide-react";

import { API_URL } from '../config/api';

// Backend response format
interface NewsResponse {
  title: string;
  script: string;
  hashtags: string;
  visual_keywords: string;
}

interface GeneratedContent {
  script: string;
  title: string;
  caption: string;
  hashtags: string[];
}

export function NewsPage() {
  const [category, setCategory] = useState("Technology"); // Changed default ID to match backend expectation
  const [loading, setLoading] = useState(false);

  // Single news item from backend
  const [news, setNews] = useState<NewsResponse | null>(null);

  const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  // New state for video creation
  const [creatingVideo, setCreatingVideo] = useState(false);
  const [videoPath, setVideoPath] = useState<string | null>(null);

  const handleCreateVideo = async () => {
    if (!generatedContent || !news) return;

    setCreatingVideo(true);
    setError("");

    try {
      const res = await fetch(`${API_URL}/api/generate-from-script`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          script: generatedContent.script,
          niche: "News",
          topic: generatedContent.title,
          visual_keywords: news.visual_keywords
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Video creation failed");
      }

      const data = await res.json();
      if (data.success) {
        setVideoPath(data.video_path);
      }
    } catch (e: any) {
      setError(e.message || "Failed to create video");
    } finally {
      setCreatingVideo(false);
    }
  };

  const categories = [
    { id: "Technology", label: "Tech & AI", icon: <Cpu className="w-5 h-5" />, color: "blue" },
    { id: "Finance", label: "Crypto & Finance", icon: <DollarSign className="w-5 h-5" />, color: "yellow" },
    { id: "World", label: "Global News", icon: <Globe className="w-5 h-5" />, color: "purple" },
    { id: "Sports", label: "Sports", icon: <Trophy className="w-5 h-5" />, color: "orange" },
  ];

  const fetchNews = async () => {
    setLoading(true);
    setError("");
    setNews(null);
    setGeneratedContent(null);

    try {
      const res = await fetch(`${API_URL}/api/news-generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to fetch news");
      }

      const data = await res.json();

      // Backend returns { success: true, news: { ... } }
      if (data.success && data.news) {
        setNews(data.news);
        // Auto-populate generated content since backend already does the scripting
        setGeneratedContent({
          title: data.news.title,
          script: data.news.script,
          caption: `${data.news.title}\n\n${data.news.hashtags}`,
          hashtags: data.news.hashtags.split(' ')
        });
      } else {
        throw new Error("Invalid response format");
      }

    } catch (e: any) {
      setError(e.message || "Failed to fetch news");
    } finally {
      setLoading(false);
    }
  };

  const copyScript = () => {
    if (generatedContent) {
      navigator.clipboard.writeText(generatedContent.script);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-orange-600 to-red-500 mb-6 shadow-lg shadow-orange-500/30">
          <Newspaper className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-3">News Generator</h2>
        <p className="text-neutral-400">Turn trending news into viral video content</p>
      </div>

      {/* Category Selection */}
      <div className="bg-[#12121a] border border-white/10 rounded-2xl p-8 mb-8">
        <h3 className="text-sm font-medium text-neutral-400 mb-4">Select Category</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setCategory(cat.id)}
              className={`p-6 rounded-xl border flex flex-col items-center gap-3 transition-all ${category === cat.id
                ? `bg-${cat.color}-500/20 border-${cat.color}-500 text-${cat.color}-400`
                : "bg-white/5 border-white/10 text-neutral-400 hover:border-white/20 hover:bg-white/10"
                }`}
            >
              {cat.icon}
              <span className="font-medium">{cat.label}</span>
            </button>
          ))}
        </div>

        <button
          onClick={fetchNews}
          disabled={loading}
          className="w-full mt-8 py-4 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 disabled:opacity-50 rounded-xl font-bold text-lg text-white flex items-center justify-center gap-2 shadow-lg shadow-orange-900/20 transition-all hover:scale-[1.01]"
        >
          {loading ? (
            <><Loader2 className="w-6 h-6 animate-spin" /> Analyzing Trends...</>
          ) : (
            <><Newspaper className="w-6 h-6" /> Generate News Reel</>
          )}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-300 mb-6 flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-red-500"></div>
          {error}
        </div>
      )}

      {/* Generated Content Result */}
      {generatedContent && (
        <div className="space-y-6">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Flame className="w-5 h-5 text-orange-500" />
            Viral Content Generated
          </h3>

          <div className="bg-[#12121a] border border-white/10 rounded-2xl overflow-hidden">
            {/* Header / Title */}
            <div className="p-6 border-b border-white/10 bg-white/5">
              <h2 className="text-2xl font-bold text-white leading-tight">{generatedContent.title}</h2>
              <div className="flex flex-wrap gap-2 mt-3">
                {generatedContent.hashtags.map((tag, i) => (
                  <span key={i} className="px-3 py-1 bg-orange-500/10 text-orange-400 text-xs rounded-full border border-orange-500/20">
                    {tag.startsWith('#') ? tag : `#${tag}`}
                  </span>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-white/10">
              {/* Script Section */}
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <label className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">Video Script</label>
                  <button
                    onClick={copyScript}
                    className="flex items-center gap-1.5 text-xs font-medium text-neutral-400 hover:text-white transition-colors bg-white/5 px-2 py-1 rounded-lg hover:bg-white/10"
                  >
                    {copied ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
                    {copied ? "Copied" : "Copy Script"}
                  </button>
                </div>
                <div className="bg-black/30 p-4 rounded-xl border border-white/5 h-64 overflow-y-auto custom-scrollbar">
                  <p className="text-neutral-300 text-lg leading-relaxed whitespace-pre-wrap font-medium">
                    {generatedContent.script}
                  </p>
                </div>
              </div>

              {/* Meta / Visuals Section */}
              <div className="p-6 flex flex-col h-full">
                <div className="mb-6">
                  <label className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3 block">Visual Keywords</label>
                  <div className="bg-blue-500/5 p-4 rounded-xl border border-blue-500/10">
                    <p className="text-blue-300 text-sm">
                      {news?.visual_keywords}
                    </p>
                  </div>
                </div>

                <div className="mt-auto">
                  {videoPath ? (
                    <div className="space-y-3">
                      <div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-xl flex items-center justify-between">
                        <span className="text-emerald-400 font-medium flex items-center gap-2">
                          <CheckCircle className="w-5 h-5" /> Video Created!
                        </span>
                        <a
                          href={`${API_URL}${videoPath}`}
                          target="_blank"
                          className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600/10 text-black hover:text-white font-bold rounded-lg transition-all"
                        >
                          View Video
                        </a>
                      </div>
                      <video src={`${API_URL}${videoPath}`} controls className="w-full rounded-xl border border-white/10" />
                    </div>
                  ) : (
                    <button
                      onClick={handleCreateVideo}
                      disabled={creatingVideo}
                      className="w-full py-4 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 rounded-xl font-bold text-lg text-white flex items-center justify-center gap-2 disabled:opacity-50 transition-all shadow-lg shadow-orange-900/20"
                    >
                      {creatingVideo ? (
                        <><Loader2 className="w-6 h-6 animate-spin" /> Creating Video... (This takes ~1-2 mins)</>
                      ) : (
                        <><Play className="w-6 h-6 fill-current" /> Create Viral Video</>
                      )}
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

