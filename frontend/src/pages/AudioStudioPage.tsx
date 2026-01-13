
import { useState } from "react";
import { Music, Wand2, Upload, CheckCircle, AlertCircle, Loader2, Music4, Search, Download } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface EnhanceResult {
    success: boolean;
    output_video?: string;
    music_track?: {
        name: string;
        url: string;
        duration: number;
        mood: string;
    };
    mood?: {
        mood: string;
        energy: string;
    };
    error?: string;
}

export function AudioStudioPage() {
    const [videoPath, setVideoPath] = useState("");
    const [prompt, setPrompt] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<EnhanceResult | null>(null);
    const [error, setError] = useState("");

    // Music Search State
    const [searchQuery, setSearchQuery] = useState("");
    const [searching, setSearching] = useState(false);
    const [searchResults, setSearchResults] = useState<any[]>([]);
    const [downloadingId, setDownloadingId] = useState<string | null>(null);

    const handleSearch = async () => {
        if (!searchQuery.trim()) return;
        setSearching(true);
        try {
            const res = await fetch(`http://localhost:8002/api/audio/search?q=${encodeURIComponent(searchQuery)}`);
            const data = await res.json();
            if (data.success) setSearchResults(data.results);
        } catch (e) {
            console.error(e);
        } finally {
            setSearching(false);
        }
    };

    const handleDownload = async (id: string) => {
        setDownloadingId(id);
        try {
            const res = await fetch("http://localhost:8002/api/audio/download", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ video_id: id })
            });
            const data = await res.json();
            if (data.success) {
                alert(`Downloaded to: ${data.track.path}`);
            }
        } catch (e) {
            console.error(e);
            alert("Download failed");
        } finally {
            setDownloadingId(null);
        }
    };

    const handleEnhance = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!videoPath.trim()) return;

        setLoading(true);
        setError("");
        setResult(null);

        try {
            const res = await fetch("http://localhost:8002/api/add-music", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    video_path: videoPath.replace(/"/g, ""), // Remove quotes if user copied path
                    prompt: prompt
                }),
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Failed to add music");
            }

            const data = await res.json();
            setResult(data);
        } catch (e: any) {
            setError(e.message || "Enhancement failed");
        } finally {
            setLoading(false);
        }
    };

    // AI Generation State
    const [activeTab, setActiveTab] = useState<'search' | 'ai'>('search');
    const [aiPrompt, setAiPrompt] = useState("");
    const [aiDuration, setAiDuration] = useState(15);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generatedAudio, setGeneratedAudio] = useState<{ url: string, filename: string } | null>(null);

    const handleGenerateAudio = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!aiPrompt.trim()) return;

        setIsGenerating(true);
        setGeneratedAudio(null);
        try {
            const res = await fetch("http://localhost:8002/api/audio/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: aiPrompt, duration: aiDuration })
            });
            const data = await res.json();
            if (data.success) {
                setGeneratedAudio(data);
            } else {
                alert("Generation failed");
            }
        } catch (e) {
            console.error(e);
            alert("Generation failed");
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="max-w-5xl mx-auto p-6">
            <div className="mb-10 text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-600 to-fuchsia-600 mb-6 shadow-lg shadow-violet-500/30">
                    <Music className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-white mb-3">AI Audio Studio</h2>
                <p className="text-neutral-400 max-w-xl mx-auto">
                    Automatically add mood-matched, royalty-free music to your mute videos.
                    We analyze the video context and prompt to find the perfect track.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
                {/* Input Form */}
                <div className="bg-[#1a1a24] border border-white/5 rounded-2xl p-6 shadow-xl h-fit">
                    <h3 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
                        <Upload className="w-5 h-5 text-violet-400" />
                        Input Video
                    </h3>

                    <form onSubmit={handleEnhance} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-neutral-400">Video File Path</label>
                            <input
                                type="text"
                                placeholder="D:\videos\my_video.mp4"
                                className="w-full bg-[#0f0f16] text-white px-4 py-3 rounded-xl border border-white/5 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 placeholder-neutral-600 transition-all font-mono text-sm"
                                value={videoPath}
                                onChange={(e) => setVideoPath(e.target.value)}
                            />
                            <p className="text-xs text-neutral-600">Paste the absolute path to your local video file.</p>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-neutral-400">Context Prompt (Optional)</label>
                            <textarea
                                rows={3}
                                placeholder="A cinematic drone shot of a misty forest at sunrise..."
                                className="w-full bg-[#0f0f16] text-white px-4 py-3 rounded-xl border border-white/5 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 placeholder-neutral-600 transition-all resize-none"
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                            />
                            <p className="text-xs text-neutral-600">Helps AI determine the correct mood (Happy, Kinetic, Dark, etc.)</p>
                        </div>

                        <button
                            type="submit"
                            disabled={loading || !videoPath}
                            className="w-full py-4 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white font-bold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 shadow-lg shadow-violet-900/20"
                        >
                            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Wand2 className="w-5 h-5" />}
                            {loading ? "Analyzing Mood & Mixing..." : "Enhance Audio"}
                        </button>
                    </form>
                </div>

                {/* Results / instructions */}
                <div className="space-y-6">
                    <AnimatePresence mode="wait">
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 text-red-200"
                            >
                                <div className="flex items-center gap-3 mb-2">
                                    <AlertCircle className="w-5 h-5 text-red-400" />
                                    <span className="font-semibold">Processing Failed</span>
                                </div>
                                <p className="text-sm opacity-80">{error}</p>
                            </motion.div>
                        )}

                        {loading && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="bg-[#1a1a24] border border-white/5 rounded-2xl p-8 flex flex-col items-center justify-center text-center h-full min-h-[300px]"
                            >
                                <div className="w-16 h-16 mb-6 relative">
                                    <div className="absolute inset-0 rounded-full border-4 border-white/10"></div>
                                    <div className="absolute inset-0 rounded-full border-4 border-t-violet-500 border-r-fuchsia-500 animate-spin"></div>
                                </div>
                                <h4 className="text-xl font-semibold text-white mb-2">Finding the Perfect Track</h4>
                                <p className="text-neutral-400 max-w-xs">We are analyzing your video mood and searching Pixabay's library...</p>
                            </motion.div>
                        )}

                        {!loading && !result && !error && (
                            <div className="bg-[#1a1a24] border border-white/5 rounded-2xl p-8 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
                                <Music4 className="w-16 h-16 text-neutral-700 mb-6" />
                                <h4 className="text-lg font-medium text-neutral-300 mb-2">Ready to Enhance</h4>
                                <p className="text-neutral-500 max-w-xs text-sm">
                                    Your processed video will appear here with details about the added track and mood analysis.
                                </p>
                            </div>
                        )}

                        {result && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="bg-gradient-to-br from-violet-900/20 to-fuchsia-900/20 border border-violet-500/20 rounded-2xl overflow-hidden shadow-2xl"
                            >
                                <div className="p-6 border-b border-white/5 bg-black/20">
                                    <div className="flex items-center gap-3">
                                        <CheckCircle className="w-6 h-6 text-emerald-400" />
                                        <h3 className="text-lg font-bold text-white">Audio Added Successfully</h3>
                                    </div>
                                </div>

                                <div className="p-6 space-y-6">
                                    {/* Mood Analysis */}
                                    {result.mood && (
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="bg-black/30 rounded-xl p-4 border border-white/5">
                                                <p className="text-neutral-500 text-xs uppercase tracking-wider mb-1">Detected Mood</p>
                                                <p className="text-white font-medium capitalize">{result.mood?.mood}</p>
                                            </div>
                                            <div className="bg-black/30 rounded-xl p-4 border border-white/5">
                                                <p className="text-neutral-500 text-xs uppercase tracking-wider mb-1">Energy Level</p>
                                                <p className="text-white font-medium capitalize">{result.mood?.energy}</p>
                                            </div>
                                        </div>
                                    )}

                                    {/* Track Info */}
                                    {result.music_track && (
                                        <div className="bg-violet-500/10 rounded-xl p-4 border border-violet-500/20 flex items-start gap-4">
                                            <div className="w-10 h-10 rounded-full bg-violet-500/20 flex items-center justify-center shrink-0">
                                                <Music className="w-5 h-5 text-violet-400" />
                                            </div>
                                            <div>
                                                <p className="text-white font-semibold">{result.music_track?.name}</p>
                                                <p className="text-violet-300 text-xs mt-0.5">Royalty-Free • Pixabay License</p>
                                            </div>
                                        </div>
                                    )}

                                    {/* Output */}
                                    <div className="pt-4 border-t border-white/5">
                                        <p className="text-sm text-neutral-400 mb-2">Saved to:</p>
                                        <div className="bg-black/50 rounded-lg p-3 font-mono text-xs text-neutral-300 break-all">
                                            {result.output_video}
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>

            {/* Audio Tools Section */}
            <div className="mt-16 border-t border-white/5 pt-12">
                <div className="text-center mb-10">
                    <h2 className="text-2xl font-bold text-white mb-2">Audio Library</h2>
                    <p className="text-neutral-400">Search for tracks or generate new unique music with AI</p>

                    {/* Tabs */}
                    <div className="flex justify-center gap-4 mt-6">
                        <button
                            onClick={() => setActiveTab('search')}
                            className={`px-6 py-2 rounded-full font-medium transition-all ${activeTab === 'search'
                                ? 'bg-white text-black'
                                : 'bg-white/5 text-neutral-400 hover:bg-white/10'
                                }`}
                        >
                            <Search className="w-4 h-4 inline mr-2" />
                            Search YouTube
                        </button>
                        <button
                            onClick={() => setActiveTab('ai')}
                            className={`px-6 py-2 rounded-full font-medium transition-all ${activeTab === 'ai'
                                ? 'bg-gradient-to-r from-cyan-400 to-blue-500 text-black'
                                : 'bg-white/5 text-neutral-400 hover:bg-white/10'
                                }`}
                        >
                            <Wand2 className="w-4 h-4 inline mr-2" />
                            AI Generator
                        </button>
                    </div>
                </div>

                {activeTab === 'search' ? (
                    <>
                        {/* Search UI */}
                        <div className="max-w-2xl mx-auto mb-10">
                            <form onSubmit={(e) => { e.preventDefault(); handleSearch(); }} className="relative flex items-center">
                                <input
                                    type="text"
                                    placeholder="Search for song, artist, or mood..."
                                    className="w-full bg-[#1a1a24] text-white pl-6 pr-14 py-4 rounded-full border border-white/10 focus:outline-none focus:border-violet-500 shadow-xl transition-all"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                />
                                <button
                                    type="submit"
                                    disabled={searching || !searchQuery.trim()}
                                    className="absolute right-2 p-2 bg-violet-600 rounded-full text-white hover:bg-violet-500 transition-colors disabled:opacity-50"
                                >
                                    {searching ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                                </button>
                            </form>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {searchResults.map((track) => (
                                <div key={track.id} className="bg-[#1a1a24] border border-white/5 rounded-xl overflow-hidden group hover:border-violet-500/50 transition-all">
                                    <div className="aspect-video bg-black relative group-hover:block">
                                        <iframe
                                            src={`https://www.youtube.com/embed/${track.id}`}
                                            title={track.title}
                                            className="w-full h-full"
                                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                            allowFullScreen
                                        />
                                    </div>

                                    <div className="p-4">
                                        <h4 className="font-semibold text-white line-clamp-1 mb-1" title={track.title}>{track.title}</h4>
                                        <div className="flex items-center justify-between text-xs text-neutral-400 mb-4">
                                            <span>{track.uploader}</span>
                                            <span>{track.duration_str}</span>
                                        </div>

                                        <button
                                            onClick={() => handleDownload(track.id)}
                                            disabled={downloadingId === track.id}
                                            className="w-full py-2 bg-white/5 hover:bg-violet-600 hover:text-white border border-white/10 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                                        >
                                            {downloadingId === track.id ? (
                                                <><Loader2 className="w-4 h-4 animate-spin" /> Downloading...</>
                                            ) : (
                                                <><Download className="w-4 h-4" /> Download to Assets</>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </>
                ) : (
                    /* AI Generation UI */
                    <div className="max-w-3xl mx-auto bg-[#1a1a24] border border-white/10 rounded-2xl p-8 relative overflow-hidden">
                        {/* Background mesh effect */}
                        <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 blur-[100px] rounded-full pointer-events-none"></div>
                        <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/10 blur-[100px] rounded-full pointer-events-none"></div>

                        <div className="relative z-10">
                            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                                <Wand2 className="w-5 h-5 text-cyan-400" />
                                Generate Unique Music
                            </h3>

                            <form onSubmit={handleGenerateAudio} className="space-y-6">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-neutral-300">Prompt Consideration</label>
                                    <textarea
                                        rows={3}
                                        value={aiPrompt}
                                        onChange={(e) => setAiPrompt(e.target.value)}
                                        placeholder="e.g. 'Upbeat lo-fi study beat with jazzy piano' or 'Dark cinematic drone with heavy bass'"
                                        className="w-full bg-black/30 text-white px-4 py-3 rounded-xl border border-white/10 focus:outline-none focus:border-cyan-500 transition-all resize-none placeholder-neutral-600"
                                    />
                                </div>

                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <label className="text-sm font-medium text-neutral-300">Duration</label>
                                        <span className="text-sm text-cyan-400 font-mono">{aiDuration}s</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="5"
                                        max="60"
                                        step="1"
                                        value={aiDuration}
                                        onChange={(e) => setAiDuration(parseInt(e.target.value))}
                                        className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                                    />
                                </div>

                                <button
                                    type="submit"
                                    disabled={isGenerating || !aiPrompt.trim()}
                                    className="w-full py-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 shadow-lg shadow-cyan-900/20"
                                >
                                    {isGenerating ? (
                                        <><Loader2 className="w-5 h-5 animate-spin" /> Generating Music (this takes time)...</>
                                    ) : (
                                        <><Wand2 className="w-5 h-5" /> Generate Track</>
                                    )}
                                </button>
                            </form>

                            {generatedAudio && (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="mt-8 bg-black/30 border border-cyan-500/30 rounded-xl p-4"
                                >
                                    <h4 className="text-cyan-400 font-semibold mb-2 flex items-center gap-2">
                                        <CheckCircle className="w-4 h-4" /> Generation Complete
                                    </h4>
                                    <div className="flex flex-col gap-3">
                                        <audio controls src={`http://localhost:8002${generatedAudio?.url}`} className="w-full" />
                                        <div className="flex gap-3">
                                            <a
                                                href={`http://localhost:8002${generatedAudio?.url}`}
                                                download
                                                className="flex-1 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm text-center text-white transition-colors"
                                            >
                                                Download .WAV
                                            </a>
                                            <button
                                                onClick={() => setVideoPath(prev => prev || "Use this file manually for now")}
                                                className="flex-1 py-2 bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-200 rounded-lg text-sm transition-colors"
                                            >
                                                Use in Project
                                            </button>
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
