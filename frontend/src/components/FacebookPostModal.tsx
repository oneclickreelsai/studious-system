import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, Facebook, Users, Heart, MessageCircle, Share2, Loader2, RefreshCw, Copy, Check, ExternalLink, Image as ImageIcon, X } from 'lucide-react';
import { API_URL } from '../config/api';

interface PageStats {
    success: boolean;
    name?: string;
    likes?: number;
    followers?: number;
    talking_about?: number;
    error?: string;
}

interface RecentPost {
    id: string;
    message: string;
    created_time: string;
    reactions: number;
    comments: number;
    shares: number;
}

const NICHE_OPTIONS = [
    { value: "trading", label: "Trading & Finance" },
    { value: "tech", label: "Technology" },
    { value: "motivation", label: "Motivation" },
    { value: "finance", label: "Personal Finance" },
    { value: "general", label: "General" },
];

export function FacebookPostModal() {
    const [topic, setTopic] = useState("");
    const [niche, setNiche] = useState("trading");
    const [generatedContent, setGeneratedContent] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);
    const [isPosting, setIsPosting] = useState(false);
    const [pageStats, setPageStats] = useState<PageStats | null>(null);
    const [recentPosts, setRecentPosts] = useState<RecentPost[]>([]);
    const [topicSuggestions, setTopicSuggestions] = useState<string[]>([]);
    const [postResult, setPostResult] = useState<{ success: boolean; url?: string; error?: string } | null>(null);
    const [copied, setCopied] = useState(false);
    const [loadingStats, setLoadingStats] = useState(false);
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [fetchedImage, setFetchedImage] = useState<{ url: string; credit: string; local_path: string } | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);

    // Fetch stats on mount
    useEffect(() => {
        fetchStats();
    }, []);

    // Update suggestions when niche changes
    useEffect(() => {
        if (pageStats && (pageStats as any).topics) {
            setTopicSuggestions((pageStats as any).topics[niche] || []);
        }
    }, [niche, pageStats]);

    const fetchStats = async () => {
        setLoadingStats(true);
        try {
            const res = await fetch(`${API_URL}/api/facebook-stats`);
            const data = await res.json();
            setPageStats(data.page);
            setRecentPosts(data.recent_posts || []);
            if (data.topics) {
                setTopicSuggestions(data.topics[niche] || []);
            }
        } catch (e) {
            console.error("Failed to fetch stats:", e);
        } finally {
            setLoadingStats(false);
        }
    };

    const handleGenerate = async () => {
        if (!topic.trim()) return;

        setIsGenerating(true);
        setGeneratedContent("");
        setPostResult(null);

        try {
            const res = await fetch(`${API_URL}/api/facebook-preview`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic, niche }),
            });

            const data = await res.json();

            if (data.success) {
                setGeneratedContent(data.content);
                if (data.image) {
                    setFetchedImage(data.image);
                    setImagePreview(data.image.url); // Use the URL provided by backend
                }
            } else {
                setGeneratedContent(`Error: ${data.detail || "Failed to generate"}`);
            }
        } catch (e: any) {
            setGeneratedContent(`Error: ${e.message}`);
        } finally {
            setIsGenerating(false);
        }
    };

    const handlePost = async () => {
        if (!generatedContent) return;

        setIsPosting(true);
        setPostResult(null);

        try {
            const formData = new FormData();
            formData.append("topic", topic);
            formData.append("niche", niche);
            formData.append("post_now", "true");
            formData.append("content", generatedContent);
            if (selectedImage) {
                formData.append("image", selectedImage);
            } else if (fetchedImage) {
                formData.append("image_path", fetchedImage.local_path);
            }

            const res = await fetch(`${API_URL}/api/facebook-post`, {
                method: "POST",
                body: formData, // Browser sets Content-Type to multipart/form-data automatically
            });

            const data = await res.json();

            if (data.success && data.posted) {
                setPostResult({ success: true, url: data.post_url });
                fetchStats(); // Refresh stats
            } else {
                setPostResult({ success: false, error: data.error || "Failed to post" });
            }
        } catch (e: any) {
            setPostResult({ success: false, error: e.message });
        } finally {
            setIsPosting(false);
        }
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(generatedContent);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const formatTimeAgo = (dateStr: string) => {
        try {
            const date = new Date(dateStr);
            const now = new Date();
            const diffMs = now.getTime() - date.getTime();
            const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
            const diffDays = Math.floor(diffHours / 24);

            if (diffDays > 0) return `${diffDays}d ago`;
            if (diffHours > 0) return `${diffHours}h ago`;
            return "Just now";
        } catch {
            return dateStr;
        }
    };

    return (
        <div className="max-w-6xl mx-auto space-y-8">
            {/* Header Section */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2">Facebook Post Generator</h2>
                    <div className="flex items-center gap-2 text-neutral-400">
                        <Facebook className="w-4 h-4 text-blue-400" />
                        <span>Create AI-powered content for your audience</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Panel - Generator */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6">
                        {/* Niche Selection */}
                        <div className="mb-6">
                            <label className="block text-sm font-medium text-neutral-300 mb-2">Content Niche</label>
                            <select
                                value={niche}
                                onChange={(e) => setNiche(e.target.value)}
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-blue-500/50"
                            >
                                {NICHE_OPTIONS.map((opt) => (
                                    <option key={opt.value} value={opt.value} className="bg-[#12121a]">
                                        {opt.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Image Selection */}
                        <div className="mb-6">
                            <label className="block text-sm font-medium text-neutral-300 mb-2">Image (Optional)</label>
                            {imagePreview ? (
                                <div className="relative rounded-xl overflow-hidden border border-white/10 group">
                                    <img src={imagePreview} alt="Selected" className="w-full h-48 object-cover" />
                                    <button
                                        onClick={() => {
                                            setSelectedImage(null);
                                            setFetchedImage(null);
                                            setImagePreview(null);
                                        }}
                                        className="absolute top-2 right-2 p-1 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors"
                                    >
                                        <X className="w-4 h-4" />
                                    </button>
                                    {fetchedImage && !selectedImage && (
                                        <div className="absolute bottom-2 left-2 px-2 py-1 bg-black/60 rounded text-[10px] text-white/80">
                                            Photo by {fetchedImage.credit} on Pexels
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-white/10 rounded-xl hover:border-white/20 hover:bg-white/5 cursor-pointer transition-all group">
                                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                        <ImageIcon className="w-8 h-8 text-neutral-500 group-hover:text-neutral-400 mb-2" />
                                        <p className="text-sm text-neutral-500 group-hover:text-neutral-400">Click to upload image</p>
                                    </div>
                                    <input
                                        type="file"
                                        className="hidden"
                                        accept="image/*"
                                        onChange={(e) => {
                                            if (e.target.files && e.target.files[0]) {
                                                setSelectedImage(e.target.files[0]);
                                                setImagePreview(URL.createObjectURL(e.target.files[0]));
                                            }
                                        }}
                                    />
                                </label>
                            )}
                        </div>

                        {/* Topic Input */}
                        <div className="mb-6">
                            <label className="block text-sm font-medium text-neutral-300 mb-2">Topic</label>
                            <input
                                type="text"
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                placeholder="Enter a topic for your post..."
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-neutral-500 focus:outline-none focus:border-blue-500/50"
                            />
                        </div>

                        {/* Topic Suggestions */}
                        {topicSuggestions.length > 0 && (
                            <div className="mb-6">
                                <label className="block text-xs font-medium text-neutral-400 mb-2">Suggestions</label>
                                <div className="flex flex-wrap gap-2">
                                    {topicSuggestions.slice(0, 5).map((suggestion, i) => (
                                        <button
                                            key={i}
                                            onClick={() => setTopic(suggestion)}
                                            className="px-3 py-1.5 text-xs bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-neutral-300 transition-colors"
                                        >
                                            {suggestion}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Generate Button */}
                        <button
                            onClick={handleGenerate}
                            disabled={isGenerating || !topic.trim()}
                            className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-500/20"
                        >
                            {isGenerating ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-5 h-5" />
                                    Generate Post
                                </>
                            )}
                        </button>
                    </div>

                    {/* Generated Content Preview */}
                    <AnimatePresence>
                        {generatedContent && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="bg-[#1a1a24] border border-white/10 rounded-2xl p-6"
                            >
                                <div className="flex items-center justify-between mb-4">
                                    <label className="text-sm font-medium text-neutral-300">Preview</label>
                                    <button
                                        onClick={handleCopy}
                                        className="flex items-center gap-1.5 text-xs text-neutral-400 hover:text-white transition-colors bg-white/5 px-3 py-1.5 rounded-lg border border-white/5 hover:border-white/10"
                                    >
                                        {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
                                        {copied ? "Copied" : "Copy Text"}
                                    </button>
                                </div>
                                <div className="p-4 bg-black/20 rounded-xl text-sm text-neutral-200 whitespace-pre-wrap max-h-96 overflow-y-auto mb-6 font-normal leading-relaxed">
                                    {generatedContent}
                                </div>

                                {/* Post Button */}
                                <button
                                    onClick={handlePost}
                                    disabled={isPosting}
                                    className="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all"
                                >
                                    {isPosting ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                            Posting...
                                        </>
                                    ) : (
                                        <>
                                            <Send className="w-5 h-5" />
                                            Post to Facebook
                                        </>
                                    )}
                                </button>

                                {/* Post Result */}
                                {postResult && (
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className={`mt-4 p-4 rounded-xl ${postResult.success ? "bg-green-500/10 border border-green-500/20" : "bg-red-500/10 border border-red-500/20"}`}
                                    >
                                        {postResult.success ? (
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-2 text-green-400">
                                                    <Check className="w-4 h-4" />
                                                    <span className="font-medium">Published successfully!</span>
                                                </div>
                                                {postResult.url && (
                                                    <a
                                                        href={postResult.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="flex items-center gap-1 text-sm text-blue-400 hover:text-blue-300 underline underline-offset-4"
                                                    >
                                                        View Post <ExternalLink className="w-3.5 h-3.5" />
                                                    </a>
                                                )}
                                            </div>
                                        ) : (
                                            <div className="flex items-center gap-2 text-red-400">
                                                <span className="font-bold">Error:</span>
                                                <span>{postResult.error}</span>
                                            </div>
                                        )}
                                    </motion.div>
                                )}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Right Panel - Stats */}
                <div className="space-y-6">
                    <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="font-semibold text-white">Page Performance</h3>
                            <button
                                onClick={fetchStats}
                                disabled={loadingStats}
                                className="p-2 hover:bg-white/5 rounded-lg transition-colors text-neutral-400 hover:text-white"
                            >
                                <RefreshCw className={`w-4 h-4 ${loadingStats ? "animate-spin" : ""}`} />
                            </button>
                        </div>

                        {pageStats?.success ? (
                            <div className="space-y-4">
                                <div className="p-4 bg-gradient-to-br from-blue-900/20 to-transparent border border-blue-500/20 rounded-xl">
                                    <div className="text-sm text-blue-300 mb-1">Page Name</div>
                                    <div className="text-lg font-bold text-white truncate">{pageStats.name}</div>
                                </div>
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="p-4 bg-white/5 border border-white/5 rounded-xl text-center hover:bg-white/[0.07] transition-colors">
                                        <Users className="w-5 h-5 text-blue-400 mx-auto mb-2" />
                                        <div className="text-xl font-bold text-white">{pageStats.followers?.toLocaleString()}</div>
                                        <div className="text-xs text-neutral-400 font-medium tracking-wide">FOLLOWERS</div>
                                    </div>
                                    <div className="p-4 bg-white/5 border border-white/5 rounded-xl text-center hover:bg-white/[0.07] transition-colors">
                                        <Heart className="w-5 h-5 text-pink-400 mx-auto mb-2" />
                                        <div className="text-xl font-bold text-white">{pageStats.likes?.toLocaleString()}</div>
                                        <div className="text-xs text-neutral-400 font-medium tracking-wide">LIKES</div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="p-4 bg-yellow-500/5 border border-yellow-500/10 rounded-xl">
                                <p className="text-sm text-yellow-200/80">
                                    {pageStats ? pageStats.error : "Unable to load stats. Ensure your backend is running and Facebook token is valid."}
                                </p>
                            </div>
                        )}
                    </div>

                    <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6">
                        <h3 className="font-semibold text-white mb-4">Recent Activity</h3>
                        {recentPosts.length > 0 ? (
                            <div className="space-y-4">
                                {recentPosts.map((post) => (
                                    <div key={post.id} className="p-4 bg-white/5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                                        <div className="flex items-start justify-between mb-2">
                                            <span className="text-[10px] font-mono text-neutral-500 bg-black/30 px-2 py-1 rounded">{formatTimeAgo(post.created_time)}</span>
                                        </div>
                                        <p className="text-sm text-neutral-300 line-clamp-2 mb-3 leading-relaxed">{post.message}</p>
                                        <div className="flex items-center gap-4 text-xs text-neutral-400 border-t border-white/5 pt-3">
                                            <span className="flex items-center gap-1.5 hover:text-pink-400 transition-colors">
                                                <Heart className="w-3.5 h-3.5" /> {post.reactions}
                                            </span>
                                            <span className="flex items-center gap-1.5 hover:text-blue-400 transition-colors">
                                                <MessageCircle className="w-3.5 h-3.5" /> {post.comments}
                                            </span>
                                            <span className="flex items-center gap-1.5 hover:text-green-400 transition-colors">
                                                <Share2 className="w-3.5 h-3.5" /> {post.shares}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-neutral-500 bg-white/[0.02] rounded-xl border border-dashed border-white/5">
                                No recent posts found
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

