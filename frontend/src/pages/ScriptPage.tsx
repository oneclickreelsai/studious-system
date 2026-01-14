import { useState, useEffect } from "react";
import { Copy, Video, Volume2, Loader2, Mic, Music, AlertCircle, Share2, Facebook, Instagram, Send } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Voice {
    id: string;
    name: string;
    gender: string;
}

export function ScriptPage() {
    const [script, setScript] = useState("");
    const [theme, setTheme] = useState("");
    const [musicPrompt, setMusicPrompt] = useState("");

    // TTS State
    const [voices, setVoices] = useState<Voice[]>([]);
    const [selectedVoice, setSelectedVoice] = useState("af_heart");
    const [previewLoading, setPreviewLoading] = useState(false);
    const [previewAudio, setPreviewAudio] = useState<string | null>(null);

    // Generation State
    const [generating, setGenerating] = useState(false);
    const [resultVideo, setResultVideo] = useState<string | null>(null);
    const [resultPath, setResultPath] = useState<string | null>(null); // For backend path
    const [error, setError] = useState<string | null>(null);
    const [successMsg, setSuccessMsg] = useState<string | null>(null);

    // Social Upload State
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [caption, setCaption] = useState("");

    useEffect(() => {
        fetch("http://localhost:8000/api/tts/voices")
            .then(res => res.json())
            .then(data => {
                if (data.voices) setVoices(data.voices);
            })
            .catch(err => console.error("Failed to load voices:", err));
    }, []);

    const handlePreviewVoice = async () => {
        if (!selectedVoice) return;
        setPreviewLoading(true);
        setPreviewAudio(null);

        try {
            const res = await fetch("http://localhost:8000/api/tts/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: "Hello! This is a preview of my voice.",
                    voice: selectedVoice,
                    speed: 1.0
                })
            });
            const data = await res.json();
            if (data.success) {
                setPreviewAudio(`http://localhost:8000${data.url}`);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setPreviewLoading(false);
        }
    };

    const handleGenerateVideo = async () => {
        if (!script) {
            setError("Please enter a script.");
            return;
        }
        if (!theme) {
            setError("Please enter a visual theme.");
            return;
        }

        setGenerating(true);
        setError(null);
        setSuccessMsg(null);
        setResultVideo(null);
        setResultPath(null);

        try {
            const res = await fetch("http://localhost:8000/api/video/generate-from-script", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    script: script,
                    voice_id: selectedVoice,
                    theme: theme,
                    music_prompt: musicPrompt || null
                })
            });

            const data = await res.json();
            if (data.success) {
                setResultVideo(`http://localhost:8000${data.video_url}`);
                setResultPath(data.video_path);
                setCaption(`${script.substring(0, 100)}... #AI #Reels`);
            } else {
                setError(data.detail || "Generation failed.");
            }
        } catch (e) {
            console.error(e);
            setError("Network error. Please try again.");
        } finally {
            setGenerating(false);
        }
    };

    const handleUploadToSocials = async () => {
        if (!resultPath) return;
        setUploading(true);
        setError(null);
        setSuccessMsg(null);

        try {
            const res = await fetch("http://localhost:8000/api/social/upload", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    video_path: resultPath,
                    caption: caption,
                    platforms: ["instagram", "facebook"]
                })
            });

            const data = await res.json();
            if (data.success) {
                setSuccessMsg("Posted successfully! Check your Meta Business Suite.");
                setShowUploadModal(false);
            } else {
                setError("Upload failed: " + (data.error || "Unknown error"));
            }
        } catch (e) {
            setError("Network error during upload.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="max-w-6xl mx-auto pb-20 relative">
            <div className="text-center mb-10">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-600 to-blue-500 mb-6 shadow-lg shadow-cyan-500/20">
                    <Copy className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-white mb-3">Script Studio</h2>
                <p className="text-neutral-400">Turn your text scripts into engaging videos with AI Voiceovers</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Script Input */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6 shadow-xl">
                        <label className="block text-sm font-medium text-neutral-400 mb-3 ml-1">Your Script</label>
                        <textarea
                            value={script}
                            onChange={(e) => setScript(e.target.value)}
                            placeholder="Paste your video script here... (Keep it short for faster generation)"
                            className="w-full h-64 bg-white/5 border border-white/10 rounded-xl p-4 text-white placeholder-neutral-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all resize-none font-sans text-lg leading-relaxed"
                        />
                    </div>

                    <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6 shadow-xl">
                        <label className="block text-sm font-medium text-neutral-400 mb-3 ml-1">Visual Theme</label>
                        <input
                            value={theme}
                            onChange={(e) => setTheme(e.target.value)}
                            placeholder="e.g., Cyberpunk City, serene nature, minimalist office..."
                            className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white placeholder-neutral-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
                        />
                    </div>

                    {/* Result Video */}
                    <AnimatePresence>
                        {resultVideo && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="bg-[#12121a] border border-cyan-500/30 rounded-2xl p-6 shadow-xl shadow-cyan-500/10"
                            >
                                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                    <Video className="w-5 h-5 text-cyan-400" />
                                    Generated Video
                                </h3>
                                <div className="aspect-[9/16] max-w-sm mx-auto bg-black rounded-lg overflow-hidden border border-white/10">
                                    <video src={resultVideo} controls className="w-full h-full object-cover" />
                                </div>
                                <div className="mt-6 flex justify-center gap-4">
                                    <a
                                        href={resultVideo}
                                        download
                                        className="px-6 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-white text-sm font-medium transition-all"
                                    >
                                        Download mp4
                                    </a>
                                    <button
                                        onClick={() => setShowUploadModal(true)}
                                        className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-xl text-white text-sm font-bold shadow-lg shadow-purple-500/20 flex items-center gap-2 transition-all"
                                    >
                                        <Share2 className="w-4 h-4" />
                                        Upload to Socials
                                    </button>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Sidebar: Voice & Settings */}
                <div className="space-y-6">
                    <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6 shadow-xl h-fit">
                        <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
                            <Mic className="w-5 h-5 text-cyan-400" />
                            Voice Settings
                        </h3>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs font-medium text-neutral-500 mb-2 uppercase tracking-wide">Select Voice</label>
                                <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto pr-2 custom-scrollbar">
                                    {voices.map((voice) => (
                                        <button
                                            key={voice.id}
                                            onClick={() => { setSelectedVoice(voice.id); setPreviewAudio(null); }}
                                            className={`flex items-center justify-between p-3 rounded-xl border text-left transition-all ${selectedVoice === voice.id
                                                    ? "bg-cyan-500/10 border-cyan-500/50 text-white"
                                                    : "bg-white/5 border-white/5 text-neutral-400 hover:border-white/10 hover:bg-white/10"
                                                }`}
                                        >
                                            <span className="font-medium text-sm">{voice.name}</span>
                                            <span className="text-[10px] bg-black/30 px-2 py-0.5 rounded text-neutral-500">{voice.gender}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Preview Section */}
                            <div className="pt-4 border-t border-white/5">
                                <button
                                    onClick={handlePreviewVoice}
                                    disabled={previewLoading}
                                    className="w-full py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm font-medium text-cyan-300 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                                >
                                    {previewLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Volume2 className="w-4 h-4" />}
                                    {previewLoading ? "Generating..." : "Preview Voice"}
                                </button>

                                {previewAudio && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 5 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="mt-3 bg-black/40 rounded-lg p-2 border border-cyan-500/20"
                                    >
                                        <audio controls src={previewAudio} className="w-full h-8" />
                                    </motion.div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Music Settings */}
                    <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6 shadow-xl h-fit">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Music className="w-5 h-5 text-purple-400" />
                            Background Music
                        </h3>
                        <input
                            value={musicPrompt}
                            onChange={(e) => setMusicPrompt(e.target.value)}
                            placeholder="e.g., generic upbeat, sad piano..."
                            className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white placeholder-neutral-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all text-sm"
                        />
                        <p className="text-xs text-neutral-500 mt-2">Leave empty for no music.</p>
                    </div>

                    {/* Status Messages */}
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                            <p className="text-sm text-red-200">{error}</p>
                        </div>
                    )}

                    {successMsg && (
                        <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4 flex items-start gap-3">
                            <div className="w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center shrink-0 mt-0.5">
                                <span className="text-green-400 text-xs">✓</span>
                            </div>
                            <p className="text-sm text-green-200">{successMsg}</p>
                        </div>
                    )}

                    <button
                        onClick={handleGenerateVideo}
                        disabled={generating}
                        className="w-full py-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-xl font-bold text-white text-lg shadow-lg shadow-cyan-500/25 transition-all hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2 disabled:opacity-50 disabled:scale-100"
                    >
                        {generating ? <Loader2 className="w-6 h-6 animate-spin" /> : <Video className="w-6 h-6" />}
                        {generating ? "Generating..." : "Generate Video"}
                    </button>
                </div>
            </div>

            {/* Social Upload Modal */}
            <AnimatePresence>
                {showUploadModal && (
                    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="bg-[#1a1a24] border border-white/10 rounded-2xl p-6 w-full max-w-md shadow-2xl"
                        >
                            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                                <Share2 className="w-5 h-5 text-purple-400" />
                                Post to Socials
                            </h3>

                            <div className="space-y-4 mb-6">
                                <div>
                                    <label className="block text-sm font-medium text-neutral-400 mb-2">Caption</label>
                                    <textarea
                                        value={caption}
                                        onChange={(e) => setCaption(e.target.value)}
                                        className="w-full h-32 bg-black/40 border border-white/10 rounded-xl p-3 text-white placeholder-neutral-500 text-sm focus:outline-none focus:border-purple-500 transition-all"
                                    />
                                </div>
                                <div className="flex gap-4">
                                    <div className="flex items-center gap-2 text-neutral-400 text-sm">
                                        <Facebook className="w-4 h-4 text-blue-500" /> Facebook
                                    </div>
                                    <div className="flex items-center gap-2 text-neutral-400 text-sm">
                                        <Instagram className="w-4 h-4 text-pink-500" /> Instagram
                                    </div>
                                </div>
                                <div className="text-xs text-neutral-500 italic bg-white/5 p-3 rounded-lg border border-white/5">
                                    ⚠️ This will open a browser window to automate the upload via Meta Business Suite. Please ensure you are logged in.
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={() => setShowUploadModal(false)}
                                    disabled={uploading}
                                    className="flex-1 py-3 bg-white/5 hover:bg-white/10 rounded-xl font-medium text-white transition-all"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleUploadToSocials}
                                    disabled={uploading}
                                    className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-xl font-bold text-white shadow-lg shadow-purple-500/20 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                                >
                                    {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                                    {uploading ? "Posting..." : "Publish Now"}
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}

