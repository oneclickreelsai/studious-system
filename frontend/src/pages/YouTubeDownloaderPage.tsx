import { useState } from "react";
import { Download, Loader2, CheckCircle, AlertCircle, Play, Clock, Eye, ThumbsUp, User, Folder } from "lucide-react";

import { API_URL } from '../config/api';

interface VideoInfo {
  title: string;
  duration: number;
  views: number;
  likes: number;
  channel: string;
  thumbnail: string;
  upload_date: string;
}

interface DownloadResult {
  success: boolean;
  title: string;
  file_path: string;
  duration: number;
  channel: string;
  output_folder: string;
}

export function YouTubeDownloaderPage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [downloadResult, setDownloadResult] = useState<DownloadResult | null>(null);
  const [error, setError] = useState("");

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const formatViews = (views: number) => {
    if (views >= 1000000) return `${(views / 1000000).toFixed(1)}M`;
    if (views >= 1000) return `${(views / 1000).toFixed(1)}K`;
    return views?.toString() || "0";
  };

  const handleFetchInfo = async () => {
    if (!url.trim()) return;
    
    setLoading(true);
    setError("");
    setVideoInfo(null);
    setDownloadResult(null);

    try {
      const res = await fetch(`${API_URL}/api/youtube-info`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });

      const data = await res.json();
      
      if (!res.ok) throw new Error(data.detail || "Failed to fetch video info");
      
      setVideoInfo(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to fetch video info");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!url.trim()) return;
    
    setDownloading(true);
    setError("");

    try {
      const res = await fetch(`${API_URL}/api/youtube-download`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });

      const data = await res.json();
      
      if (!res.ok) throw new Error(data.detail || "Download failed");
      
      setDownloadResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Download failed");
    } finally {
      setDownloading(false);
    }
  };

  const resetForm = () => {
    setUrl("");
    setVideoInfo(null);
    setDownloadResult(null);
    setError("");
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-red-600 to-red-500 mb-6 shadow-lg shadow-red-500/30">
          <Download className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-3">YouTube Downloader</h2>
        <p className="text-neutral-400">Download YouTube videos for offline use</p>
      </div>

      {/* URL Input */}
      <div className="bg-[#1a1a24] border border-white/5 rounded-2xl p-2 md:p-3 shadow-xl mb-8">
        <div className="relative flex items-center gap-2">
          <input
            type="text"
            placeholder="https://www.youtube.com/watch?v=..."
            className="flex-1 bg-[#0f0f16] text-white px-6 py-4 rounded-xl border border-white/5 focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 placeholder-neutral-600 transition-all font-mono text-sm"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleFetchInfo()}
          />
          <button
            onClick={handleFetchInfo}
            disabled={loading || !url.trim()}
            className="px-6 py-4 bg-red-600 hover:bg-red-500 text-white font-semibold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
            {loading ? "Loading..." : "Fetch"}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-8 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <p className="text-red-300">{error}</p>
        </div>
      )}

      {/* Video Info */}
      {videoInfo && !downloadResult && (
        <div className="bg-[#12121a] border border-white/10 rounded-2xl overflow-hidden mb-8">
          <div className="flex flex-col md:flex-row">
            {/* Thumbnail */}
            <div className="md:w-80 aspect-video bg-black/50 relative flex-shrink-0">
              {videoInfo.thumbnail ? (
                <img 
                  src={videoInfo.thumbnail} 
                  alt={videoInfo.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Play className="w-12 h-12 text-neutral-600" />
                </div>
              )}
              <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 rounded text-xs text-white font-mono">
                {formatDuration(videoInfo.duration)}
              </div>
            </div>

            {/* Info */}
            <div className="p-6 flex-1">
              <h3 className="text-xl font-bold text-white mb-3 line-clamp-2">{videoInfo.title}</h3>
              
              <div className="flex items-center gap-2 text-neutral-400 mb-4">
                <User className="w-4 h-4" />
                <span>{videoInfo.channel}</span>
              </div>

              <div className="flex flex-wrap gap-4 text-sm text-neutral-400 mb-6">
                <div className="flex items-center gap-1.5">
                  <Eye className="w-4 h-4" />
                  <span>{formatViews(videoInfo.views)} views</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <ThumbsUp className="w-4 h-4" />
                  <span>{formatViews(videoInfo.likes)} likes</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Clock className="w-4 h-4" />
                  <span>{formatDuration(videoInfo.duration)}</span>
                </div>
              </div>

              <button
                onClick={handleDownload}
                disabled={downloading}
                className="w-full md:w-auto px-8 py-3 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 text-white font-semibold rounded-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {downloading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Downloading...
                  </>
                ) : (
                  <>
                    <Download className="w-5 h-5" />
                    Download Video
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Download Result */}
      {downloadResult && (
        <div className="bg-gradient-to-br from-green-900/20 to-emerald-900/20 border border-green-500/20 rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Download Complete!</h3>
              <p className="text-green-400 text-sm">Video saved successfully</p>
            </div>
          </div>

          <div className="space-y-3 mb-6">
            <div className="flex items-start gap-3 p-3 bg-black/20 rounded-lg">
              <Play className="w-5 h-5 text-neutral-400 mt-0.5" />
              <div>
                <p className="text-xs text-neutral-500 mb-1">Title</p>
                <p className="text-white font-medium">{downloadResult.title}</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-3 bg-black/20 rounded-lg">
              <Folder className="w-5 h-5 text-neutral-400 mt-0.5" />
              <div>
                <p className="text-xs text-neutral-500 mb-1">Saved to</p>
                <p className="text-white font-mono text-sm break-all">{downloadResult.file_path}</p>
              </div>
            </div>
          </div>

          <button
            onClick={resetForm}
            className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
          >
            Download Another
          </button>
        </div>
      )}

      {/* Instructions */}
      {!videoInfo && !downloadResult && !error && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          {[
            { icon: Play, title: "Paste URL", desc: "Copy any YouTube video or Shorts URL" },
            { icon: Eye, title: "Preview", desc: "See video details before downloading" },
            { icon: Download, title: "Download", desc: "Save to your local output folder" }
          ].map((item, i) => (
            <div key={i} className="p-6 rounded-2xl bg-[#0f0f16] border border-white/5 text-center">
              <item.icon className="w-8 h-8 text-neutral-600 mx-auto mb-4" />
              <h4 className="text-white font-semibold mb-2">{item.title}</h4>
              <p className="text-sm text-neutral-500">{item.desc}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

