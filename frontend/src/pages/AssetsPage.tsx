import { useState, useEffect } from "react";
import { FolderOpen, FileVideo, FileImage, FileAudio, Download, Trash2, Search, Play, ExternalLink, Loader2, RefreshCw } from "lucide-react";

const API_URL = "http://localhost:8002";

interface Asset {
    name: string;
    path: string;
    type: "video" | "image" | "audio" | "unknown";
    size: number;
    created: number;
    created_str: string;
}

export function AssetsPage() {
    const [assets, setAssets] = useState<Asset[]>([]);
    const [loading, setLoading] = useState(false);
    const [filter, setFilter] = useState("all");
    const [search, setSearch] = useState("");
    const [deleting, setDeleting] = useState<string | null>(null);

    const fetchAssets = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/assets`);
            const data = await res.json();
            if (data.success) {
                setAssets(data.assets);
            }
        } catch (e) {
            console.error("Failed to fetch assets", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAssets();
    }, []);

    const handleDelete = async (filename: string) => {
        if (!window.confirm(`Are you sure you want to delete ${filename}?`)) return;

        setDeleting(filename);
        try {
            const res = await fetch(`${API_URL}/api/assets/${filename}`, {
                method: "DELETE"
            });

            if (res.ok) {
                setAssets(prev => prev.filter(a => a.name !== filename));
            }
        } catch (e) {
            console.error("Failed to delete asset", e);
        } finally {
            setDeleting(null);
        }
    };

    const formatSize = (bytes: number) => {
        if (bytes === 0) return "0 B";
        const k = 1024;
        const sizes = ["B", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    };

    const filteredAssets = assets.filter(asset => {
        const matchesType = filter === "all" || asset.type === filter;
        const matchesSearch = asset.name.toLowerCase().includes(search.toLowerCase());
        return matchesType && matchesSearch;
    });

    return (
        <div className="max-w-6xl mx-auto p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                        <FolderOpen className="w-8 h-8 text-yellow-400" />
                        Asset Manager
                    </h2>
                    <p className="text-neutral-400">View and manage your generated content</p>
                </div>
                <button
                    onClick={fetchAssets}
                    disabled={loading}
                    className="p-3 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 transition-colors disabled:opacity-50"
                >
                    <RefreshCw className={`w-5 h-5 text-white ${loading ? "animate-spin" : ""}`} />
                </button>
            </div>

            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 mb-8">
                <div className="relative flex-1">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-500" />
                    <input
                        type="text"
                        placeholder="Search files..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 bg-[#12121a] border border-white/10 rounded-xl text-white focus:outline-none focus:border-yellow-500"
                    />
                </div>
                <div className="flex gap-2 bg-[#12121a] p-1 rounded-xl border border-white/10">
                    {["all", "video", "image", "audio"].map(type => (
                        <button
                            key={type}
                            onClick={() => setFilter(type)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-all ${filter === type
                                ? "bg-yellow-500 text-black shadow-lg shadow-yellow-500/20"
                                : "text-neutral-400 hover:text-white hover:bg-white/5"
                                }`}
                        >
                            {type}
                        </button>
                    ))}
                </div>
            </div>

            {/* Assets Grid */}
            {loading && assets.length === 0 ? (
                <div className="text-center py-20">
                    <Loader2 className="w-10 h-10 text-yellow-500 animate-spin mx-auto mb-4" />
                    <p className="text-neutral-400">Loading assets...</p>
                </div>
            ) : filteredAssets.length === 0 ? (
                <div className="text-center py-20 bg-[#12121a] border border-white/10 rounded-2xl">
                    <FolderOpen className="w-12 h-12 text-neutral-600 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">No files found</h3>
                    <p className="text-neutral-400">Generated videos and assets will appear here.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredAssets.map(asset => (
                        <div key={asset.name} className="group bg-[#12121a] border border-white/5 hover:border-yellow-500/30 rounded-2xl overflow-hidden transition-all hover:shadow-xl hover:shadow-black/50">
                            {/* Preview Area */}
                            <div className="aspect-video bg-black/40 relative flex items-center justify-center overflow-hidden">
                                {asset.type === "video" ? (
                                    <div className="relative w-full h-full">
                                        <video src={`${API_URL}${asset.path}`} className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
                                        <div className="absolute inset-0 flex items-center justify-center">
                                            <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                                                <Play className="w-5 h-5 text-white fill-current ml-1" />
                                            </div>
                                        </div>
                                    </div>
                                ) : asset.type === "image" ? (
                                    <img src={`${API_URL}${asset.path}`} alt={asset.name} className="w-full h-full object-cover opacity-80 group-hover:opacity-100" />
                                ) : (
                                    <FileAudio className="w-16 h-16 text-neutral-600 group-hover:text-yellow-500 transition-colors" />
                                )}

                                <div className="absolute top-3 right-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <a
                                        href={`${API_URL}${asset.path}`}
                                        download
                                        target="_blank"
                                        className="p-2 bg-black/60 backdrop-blur-md rounded-lg text-white hover:bg-yellow-500 hover:text-black transition-colors"
                                    >
                                        <Download className="w-4 h-4" />
                                    </a>
                                    <a
                                        href={`${API_URL}${asset.path}`}
                                        target="_blank"
                                        className="p-2 bg-black/60 backdrop-blur-md rounded-lg text-white hover:bg-blue-500 hover:text-white transition-colors"
                                    >
                                        <ExternalLink className="w-4 h-4" />
                                    </a>
                                </div>
                            </div>

                            {/* Info Area */}
                            <div className="p-5">
                                <div className="flex items-start justify-between gap-3 mb-2">
                                    <div className="flex items-center gap-2 min-w-0">
                                        {asset.type === "video" ? <FileVideo className="w-4 h-4 text-blue-400 shrink-0" /> :
                                            asset.type === "image" ? <FileImage className="w-4 h-4 text-green-400 shrink-0" /> :
                                                <FileAudio className="w-4 h-4 text-purple-400 shrink-0" />}
                                        <h4 className="font-semibold text-white truncate text-sm" title={asset.name}>{asset.name}</h4>
                                    </div>
                                    <div className="text-xs font-mono text-neutral-500 shrink-0">{formatSize(asset.size)}</div>
                                </div>

                                <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/5">
                                    <span className="text-xs text-neutral-500">{asset.created_str}</span>
                                    <button
                                        onClick={() => handleDelete(asset.name)}
                                        disabled={deleting === asset.name}
                                        className="text-neutral-500 hover:text-red-400 transition-colors disabled:opacity-50"
                                    >
                                        {deleting === asset.name ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
