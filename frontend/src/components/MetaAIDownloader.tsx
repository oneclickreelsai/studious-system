import { useState } from "react";
import { Bot, Download, CheckCircle, AlertCircle, Loader2, Play, Film, Image, FileText, Youtube, Sparkles, Facebook, Instagram } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface DownloadResult {
    success: boolean;
    type: "video" | "animation" | "frames" | "metadata";
    file_path?: string;
    filename?: string;
    file_size?: number;
    frame_count?: number;
    frames_dir?: string;
    output_folder?: string;
    message?: string;
    error?: string;
    prompt?: string;
    prompt_file?: string;
    audio?: { type: string; path: string; size: number };
}

interface UploadResult {
    success: boolean;
    youtube?: { success: boolean; video_id?: string; video_url?: string; title?: string; error?: string };
    facebook?: { success: boolean; post_id?: string; error?: string };
    instagram?: { success: boolean; media_id?: string; error?: string };
    error?: string;
}

export function MetaAIDownloader() {
    const [url, setUrl] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<DownloadResult | null>(null);
    const [error, setError] = useState("");

    // Upload options
    const [uploadYoutube, setUploadYoutube] = useState(true);
    const [uploadFacebook, setUploadFacebook] = useState(true);
    const [uploadInstagram, setUploadInstagram] = useState(false);

    // Upload state
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState("");
    const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);

    const handleDownload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!url.trim()) return;

        setLoading(true);
        setError("");
        setResult(null);

        try {
            const res = await fetch("http://localhost:8000/api/download-meta-video", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url }),
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Failed to download");
            }

            const data = await res.json();
            setResult(data);
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : "Download failed");
        } finally {
            setLoading(false);
        }
    };

    const handleReEngineerAndUpload = async () => {
        if (!url.trim()) return;
        if (!uploadYoutube && !uploadFacebook && !uploadInstagram) {
            setError("Please select at least one platform to upload");
            return;
        }

        setUploading(true);
        setUploadProgress("Starting pipeline...");
        setUploadResult(null);

        try {
            setUploadProgress("Downloading video from Meta AI...");

            const res = await fetch("http://localhost:8000/api/meta-to-social", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    url,
                    analyze_content: true,
                    upload_youtube: uploadYoutube,
                    upload_facebook: uploadFacebook,
                    upload_instagram: uploadInstagram
                }),
            });

            setUploadProgress("Analyzing content & uploading...");

            const data = await res.json();

            if (res.ok && data.success) {
                setUploadResult(data);
                setUploadProgress("Upload complete!");
            } else {
                setUploadResult({
                    success: false,
                    error: data.error || "Upload failed"
                });
            }
        } catch (e: unknown) {
            setUploadResult({
                success: false,
                error: e instanceof Error ? e.message : "Pipeline failed"
            });
        } finally {
            setUploading(false);
        }
    };

    const getTypeIcon = () => {
        if (!result) return <Play className="w-12 h-12 text-white/80" />;
        switch (result.type) {
            case "video": return <Film className="w-12 h-12 text-emerald-400" />;
            case "animation": return <Film className="w-12 h-12 text-purple-400" />;
            case "frames": return <Image className="w-12 h-12 text-blue-400" />;
            case "metadata": return <FileText className="w-12 h-12 text-yellow-400" />;
            default: return <Play className="w-12 h-12 text-white/80" />;
        }
    };

    const getTypeLabel = () => {
        if (!result) return "";
        switch (result.type) {
            case "video": return "Video Downloaded";
            case "animation": return "Animation Created";
            case "frames": return "Frames Captured";
            case "metadata": return "Metadata Extracted";
            default: return "Download Complete";
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-6">
            <div className="text-center mb-10">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-cyan-500 mb-6 shadow-lg shadow-blue-500/30">
                    <Bot className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-white mb-3">Meta AI Video Downloader</h2>
                <p className="text-neutral-400 max-w-lg mx-auto">
                    Download videos and AI-generated animations from Meta AI posts.
                </p>
            </div>

            <div className="bg-[#1a1a24] border border-white/5 rounded-2xl p-2 md:p-3 shadow-xl mb-8">
                <form onSubmit={handleDownload} className="relative flex items-center">
                    <input
                        type="text"
                        placeholder="https://www.meta.ai/@username/post/..."
                        className="w-full bg-[#0f0f16] text-white px-6 py-4 rounded-xl border border-white/5 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 placeholder-neutral-600 transition-all font-mono text-sm"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                    />
                    <button
                        type="submit"
                        disabled={loading || !url}
                        className="absolute right-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                        {loading ? "Processing..." : "Download"}
                    </button>
                </form>
            </div>

            {/* Re-Engineer & Upload Section */}
            <div className="bg-[#1a1a24] border border-white/5 rounded-2xl p-6 mb-8">
                <div className="flex items-center gap-3 mb-4">
                    <Sparkles className="w-6 h-6 text-orange-400" />
                    <div>
                        <p className="text-white font-medium">Re-Engineer & Upload to Social Media</p>
                        <p className="text-neutral-500 text-xs">Download, analyze, generate metadata, and upload in one click</p>
                    </div>
                </div>

                {/* Platform Selection */}
                <div className="flex flex-wrap gap-4 mb-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={uploadYoutube}
                            onChange={(e) => setUploadYoutube(e.target.checked)}
                            className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-red-500 focus:ring-red-500"
                        />
                        <Youtube className="w-5 h-5 text-red-500" />
                        <span className="text-white text-sm">YouTube</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={uploadFacebook}
                            onChange={(e) => setUploadFacebook(e.target.checked)}
                            className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500"
                        />
                        <Facebook className="w-5 h-5 text-blue-500" />
                        <span className="text-white text-sm">Facebook</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={uploadInstagram}
                            onChange={(e) => setUploadInstagram(e.target.checked)}
                            className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-pink-500 focus:ring-pink-500"
                        />
                        <Instagram className="w-5 h-5 text-pink-500" />
                        <span className="text-white text-sm">Instagram</span>
                    </label>
                </div>

                <button
                    onClick={handleReEngineerAndUpload}
                    disabled={uploading || !url || (!uploadYoutube && !uploadFacebook && !uploadInstagram)}
                    className="w-full px-6 py-3 bg-gradient-to-r from-red-600 via-blue-600 to-pink-600 hover:from-red-500 hover:via-blue-500 hover:to-pink-500 text-white font-semibold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                    {uploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                    {uploading ? uploadProgress : "Re-Engineer & Upload Now"}
                </button>

                {/* Upload Results */}
                {uploadResult && (
                    <div className="mt-4 space-y-2">
                        {uploadResult.youtube && (
                            <div className={`p-3 rounded-lg ${uploadResult.youtube.success ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
                                <div className="flex items-center gap-2">
                                    <Youtube className="w-4 h-4 text-red-500" />
                                    {uploadResult.youtube.success ? (
                                        <div>
                                            <span className="text-green-400 text-sm">YouTube: Uploaded!</span>
                                            {uploadResult.youtube.video_url && (
                                                <a href={uploadResult.youtube.video_url} target="_blank" rel="noopener noreferrer" className="text-blue-400 text-xs hover:underline ml-2">
                                                    View
                                                </a>
                                            )}
                                        </div>
                                    ) : (
                                        <span className="text-red-400 text-sm">YouTube: {uploadResult.youtube.error}</span>
                                    )}
                                </div>
                            </div>
                        )}
                        {uploadResult.facebook && (
                            <div className={`p-3 rounded-lg ${uploadResult.facebook.success ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
                                <div className="flex items-center gap-2">
                                    <Facebook className="w-4 h-4 text-blue-500" />
                                    {uploadResult.facebook.success ? (
                                        <span className="text-green-400 text-sm">Facebook: Posted!</span>
                                    ) : (
                                        <span className="text-red-400 text-sm">Facebook: {uploadResult.facebook.error}</span>
                                    )}
                                </div>
                            </div>
                        )}
                        {uploadResult.instagram && (
                            <div className={`p-3 rounded-lg ${uploadResult.instagram.success ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
                                <div className="flex items-center gap-2">
                                    <Instagram className="w-4 h-4 text-pink-500" />
                                    {uploadResult.instagram.success ? (
                                        <span className="text-green-400 text-sm">Instagram: Posted!</span>
                                    ) : (
                                        <span className="text-red-400 text-sm">Instagram: {uploadResult.instagram.error}</span>
                                    )}
                                </div>
                            </div>
                        )}
                        {uploadResult.error && !uploadResult.youtube && !uploadResult.facebook && !uploadResult.instagram && (
                            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                                <div className="flex items-center gap-2">
                                    <AlertCircle className="w-4 h-4 text-red-400" />
                                    <span className="text-red-400 text-sm">{uploadResult.error}</span>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {loading && (
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-6 mb-8">
                    <div className="flex items-center gap-4">
                        <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
                        <div>
                            <p className="text-blue-300 font-medium">Extracting content...</p>
                            <p className="text-blue-400/70 text-sm">This may take 10-20 seconds for animations</p>
                        </div>
                    </div>
                </div>
            )}

            <AnimatePresence mode="wait">
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-red-200 mb-8"
                    >
                        <div className="flex items-center gap-3 mb-2">
                            <AlertCircle className="w-5 h-5 text-red-400" />
                            <span className="font-semibold">Error</span>
                        </div>
                        <p className="text-sm opacity-80">{error}</p>
                    </motion.div>
                )}

                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-gradient-to-br from-emerald-900/20 to-teal-900/20 border border-emerald-500/20 rounded-2xl overflow-hidden mb-8"
                    >
                        <div className="p-8 flex flex-col md:flex-row items-center gap-8">
                            <div className="w-full md:w-64 aspect-video bg-black/40 rounded-xl flex items-center justify-center border border-white/5 relative overflow-hidden">
                                <div className="absolute inset-0 bg-gradient-to-tr from-emerald-500/20 to-transparent opacity-50"></div>
                                {getTypeIcon()}
                            </div>

                            <div className="flex-1 text-center md:text-left">
                                <div className="flex items-center gap-3 justify-center md:justify-start mb-2">
                                    <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
                                        <CheckCircle className="w-5 h-5 text-emerald-400" />
                                    </div>
                                    <h3 className="text-xl font-bold text-white">{getTypeLabel()}</h3>
                                </div>

                                <div className="space-y-2 mb-6">
                                    {result.message && (
                                        <p className="text-emerald-400 text-sm">{result.message}</p>
                                    )}
                                    {result.filename && (
                                        <p className="text-neutral-400 text-sm font-mono truncate max-w-md">{result.filename}</p>
                                    )}
                                    {result.file_size && (
                                        <p className="text-neutral-500 text-xs">Size: {(result.file_size / 1024 / 1024).toFixed(2)} MB</p>
                                    )}
                                    {result.prompt && (
                                        <div className="mt-3 p-3 bg-black/30 rounded-lg border border-white/5">
                                            <p className="text-yellow-400 text-xs flex items-center gap-1 mb-1">
                                                <FileText className="w-3 h-3" /> Prompt Extracted:
                                            </p>
                                            <p className="text-neutral-300 text-xs line-clamp-3">{result.prompt}</p>
                                        </div>
                                    )}
                                </div>

                                <span className="text-xs text-neutral-500">
                                    Saved to: {result.output_folder || "output/meta_ai_downloads/"}
                                </span>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Instructions */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                    { icon: Bot, title: "Find Content", desc: "Go to Meta AI and find a video or animation you like." },
                    { icon: Download, title: "Paste URL", desc: "Copy the post URL from your browser and paste it here." },
                    { icon: Film, title: "Auto Upload", desc: "Select platforms and upload to YouTube, Facebook & Instagram." }
                ].map((item, i) => (
                    <div key={i} className="p-6 rounded-2xl bg-[#0f0f16] border border-white/5 text-center">
                        <item.icon className="w-8 h-8 text-neutral-600 mx-auto mb-4" />
                        <h4 className="text-white font-semibold mb-2">{item.title}</h4>
                        <p className="text-sm text-neutral-500">{item.desc}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
