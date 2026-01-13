import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
    Cloud,
    Upload,
    RefreshCw,
    FolderOpen,
    File,
    Video,
    Music,
    Image,
    ExternalLink,
    CheckCircle,
    AlertCircle,
    Clock,
    HardDrive,
    Loader2,
    Play
} from "lucide-react";

const API_URL = "http://localhost:8002";

interface SyncStats {
    total_files: number;
    total_size_mb: number;
    last_sync: string;
    status: string;
}

interface DriveFile {
    name: string;
    path: string;
    type: string;
    size: number;
    created: number;
    created_str: string;
    drive_id?: string;
    web_link?: string;
    synced?: boolean;
}

export function GoogleDrivePage() {
    const [isSyncing, setIsSyncing] = useState(false);
    const [syncProgress, setSyncProgress] = useState(0);
    const [syncStatus, setSyncStatus] = useState<string>("idle");
    const [syncStats, setSyncStats] = useState<SyncStats | null>(null);
    const [localFiles, setLocalFiles] = useState<DriveFile[]>([]);
    const [syncLog, setSyncLog] = useState<Record<string, any>>({});
    const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
    const [autoSync, setAutoSync] = useState(false);

    // Fetch local assets
    useEffect(() => {
        fetchLocalAssets();
        fetchSyncLog();
    }, []);

    const fetchLocalAssets = async () => {
        try {
            const res = await fetch(`${API_URL}/api/assets`);
            const data = await res.json();
            if (data.success) {
                setLocalFiles(data.assets || []);
            }
        } catch (error) {
            console.error("Failed to fetch assets:", error);
        }
    };

    const fetchSyncLog = async () => {
        try {
            const res = await fetch(`${API_URL}/api/drive/sync-log`);
            const data = await res.json();
            if (data.success) {
                setSyncLog(data.log || {});
                setSyncStats(data.stats || null);
            }
        } catch (error) {
            console.error("Failed to fetch sync log:", error);
        }
    };

    const startSync = async () => {
        setIsSyncing(true);
        setSyncStatus("syncing");
        setSyncProgress(0);

        try {
            const res = await fetch(`${API_URL}/api/drive/sync`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    files: selectedFiles.size > 0 ? Array.from(selectedFiles) : null
                })
            });

            const data = await res.json();

            if (data.success) {
                setSyncStatus("completed");
                setSyncProgress(100);
                fetchSyncLog();
                fetchLocalAssets();
            } else {
                setSyncStatus("error");
            }
        } catch (error) {
            console.error("Sync failed:", error);
            setSyncStatus("error");
        } finally {
            setIsSyncing(false);
        }
    };

    const getFileIcon = (type: string) => {
        switch (type) {
            case "video": return <Video className="w-5 h-5 text-purple-400" />;
            case "audio": return <Music className="w-5 h-5 text-green-400" />;
            case "image": return <Image className="w-5 h-5 text-blue-400" />;
            default: return <File className="w-5 h-5 text-neutral-400" />;
        }
    };

    const formatSize = (bytes: number) => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    };

    const isFileSynced = (filePath: string) => {
        return syncLog[`output/${filePath.split('/').pop()}`] !== undefined;
    };

    const getFileLink = (filePath: string) => {
        const key = `output/${filePath.split('/').pop()}`;
        return syncLog[key]?.web_link || null;
    };

    const toggleFileSelection = (path: string) => {
        const newSelection = new Set(selectedFiles);
        if (newSelection.has(path)) {
            newSelection.delete(path);
        } else {
            newSelection.add(path);
        }
        setSelectedFiles(newSelection);
    };

    const selectAll = () => {
        if (selectedFiles.size === localFiles.length) {
            setSelectedFiles(new Set());
        } else {
            setSelectedFiles(new Set(localFiles.map(f => f.path)));
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                        <Cloud className="w-8 h-8 text-cyan-400" />
                        Google Drive Sync
                    </h1>
                    <p className="text-neutral-400 mt-1">
                        Backup and sync your generated content to Google Drive
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={fetchLocalAssets}
                        className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-neutral-400 hover:text-white transition-colors"
                    >
                        <RefreshCw className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 rounded-2xl p-5"
                >
                    <div className="flex items-center gap-3">
                        <div className="p-3 rounded-xl bg-cyan-500/20">
                            <FolderOpen className="w-6 h-6 text-cyan-400" />
                        </div>
                        <div>
                            <p className="text-sm text-neutral-400">Local Files</p>
                            <p className="text-2xl font-bold text-white">{localFiles.length}</p>
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-2xl p-5"
                >
                    <div className="flex items-center gap-3">
                        <div className="p-3 rounded-xl bg-green-500/20">
                            <CheckCircle className="w-6 h-6 text-green-400" />
                        </div>
                        <div>
                            <p className="text-sm text-neutral-400">Synced Files</p>
                            <p className="text-2xl font-bold text-white">{Object.keys(syncLog).length}</p>
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-2xl p-5"
                >
                    <div className="flex items-center gap-3">
                        <div className="p-3 rounded-xl bg-purple-500/20">
                            <HardDrive className="w-6 h-6 text-purple-400" />
                        </div>
                        <div>
                            <p className="text-sm text-neutral-400">Total Size</p>
                            <p className="text-2xl font-bold text-white">
                                {formatSize(localFiles.reduce((acc, f) => acc + f.size, 0))}
                            </p>
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-gradient-to-br from-orange-500/10 to-amber-500/10 border border-orange-500/20 rounded-2xl p-5"
                >
                    <div className="flex items-center gap-3">
                        <div className="p-3 rounded-xl bg-orange-500/20">
                            <Clock className="w-6 h-6 text-orange-400" />
                        </div>
                        <div>
                            <p className="text-sm text-neutral-400">Last Sync</p>
                            <p className="text-lg font-bold text-white">
                                {syncStats?.last_sync || "Never"}
                            </p>
                        </div>
                    </div>
                </motion.div>
            </div>

            {/* Sync Controls */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="bg-[#12121a] border border-white/5 rounded-2xl p-6"
            >
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                        <Upload className="w-5 h-5 text-cyan-400" />
                        Sync Controls
                    </h2>
                    <div className="flex items-center gap-4">
                        <label className="flex items-center gap-2 text-sm text-neutral-400">
                            <input
                                type="checkbox"
                                checked={autoSync}
                                onChange={(e) => setAutoSync(e.target.checked)}
                                className="rounded bg-white/10 border-white/20 text-cyan-500 focus:ring-cyan-500"
                            />
                            Auto-sync new files
                        </label>
                    </div>
                </div>

                {/* Progress Bar */}
                {isSyncing && (
                    <div className="mb-4">
                        <div className="flex items-center justify-between text-sm mb-2">
                            <span className="text-neutral-400">Syncing to Google Drive...</span>
                            <span className="text-cyan-400">{syncProgress}%</span>
                        </div>
                        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                            <motion.div
                                className="h-full bg-gradient-to-r from-cyan-500 to-blue-500"
                                initial={{ width: 0 }}
                                animate={{ width: `${syncProgress}%` }}
                                transition={{ duration: 0.3 }}
                            />
                        </div>
                    </div>
                )}

                {/* Sync Status */}
                {syncStatus === "completed" && (
                    <div className="mb-4 p-3 bg-green-500/10 border border-green-500/20 rounded-xl flex items-center gap-2 text-green-400">
                        <CheckCircle className="w-5 h-5" />
                        Sync completed successfully!
                    </div>
                )}

                {syncStatus === "error" && (
                    <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-2 text-red-400">
                        <AlertCircle className="w-5 h-5" />
                        Sync failed. Please check your connection and try again.
                    </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center gap-3">
                    <button
                        onClick={startSync}
                        disabled={isSyncing}
                        className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white font-medium rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isSyncing ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Syncing...
                            </>
                        ) : (
                            <>
                                <Cloud className="w-5 h-5" />
                                {selectedFiles.size > 0 ? `Sync ${selectedFiles.size} Files` : "Sync All Files"}
                            </>
                        )}
                    </button>

                    <button
                        onClick={selectAll}
                        className="px-4 py-3 bg-white/5 hover:bg-white/10 text-neutral-300 font-medium rounded-xl transition-colors"
                    >
                        {selectedFiles.size === localFiles.length ? "Deselect All" : "Select All"}
                    </button>

                    <a
                        href="https://drive.google.com/drive/folders/1a0O1XVdD7K3amytz7rX8zIyKuOeK0qDs"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-4 py-3 bg-white/5 hover:bg-white/10 text-neutral-300 font-medium rounded-xl transition-colors"
                    >
                        <ExternalLink className="w-5 h-5" />
                        Open Google Drive
                    </a>
                </div>
            </motion.div>

            {/* Files List */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="bg-[#12121a] border border-white/5 rounded-2xl overflow-hidden"
            >
                <div className="p-4 border-b border-white/5">
                    <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                        <FolderOpen className="w-5 h-5 text-cyan-400" />
                        Output Files
                    </h2>
                </div>

                <div className="divide-y divide-white/5 max-h-[500px] overflow-y-auto">
                    {localFiles.length === 0 ? (
                        <div className="p-8 text-center text-neutral-500">
                            <FolderOpen className="w-12 h-12 mx-auto mb-3 opacity-50" />
                            <p>No files in output folder</p>
                        </div>
                    ) : (
                        localFiles.map((file, index) => {
                            const synced = isFileSynced(file.path);
                            const driveLink = getFileLink(file.path);
                            const isSelected = selectedFiles.has(file.path);

                            return (
                                <motion.div
                                    key={file.path}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.02 }}
                                    className={`flex items-center gap-4 p-4 hover:bg-white/5 transition-colors ${isSelected ? 'bg-cyan-500/10' : ''}`}
                                >
                                    <input
                                        type="checkbox"
                                        checked={isSelected}
                                        onChange={() => toggleFileSelection(file.path)}
                                        className="rounded bg-white/10 border-white/20 text-cyan-500 focus:ring-cyan-500"
                                    />

                                    <div className="p-2 rounded-lg bg-white/5">
                                        {getFileIcon(file.type)}
                                    </div>

                                    <div className="flex-1 min-w-0">
                                        <p className="text-white font-medium truncate">{file.name}</p>
                                        <p className="text-sm text-neutral-500">
                                            {formatSize(file.size)} • {file.created_str}
                                        </p>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        {synced ? (
                                            <span className="flex items-center gap-1 px-2 py-1 bg-green-500/10 text-green-400 text-xs rounded-lg">
                                                <CheckCircle className="w-3 h-3" />
                                                Synced
                                            </span>
                                        ) : (
                                            <span className="flex items-center gap-1 px-2 py-1 bg-orange-500/10 text-orange-400 text-xs rounded-lg">
                                                <Clock className="w-3 h-3" />
                                                Pending
                                            </span>
                                        )}

                                        {driveLink && (
                                            <a
                                                href={driveLink}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-neutral-400 hover:text-white transition-colors"
                                            >
                                                <ExternalLink className="w-4 h-4" />
                                            </a>
                                        )}

                                        {file.type === "video" && (
                                            <button className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-neutral-400 hover:text-white transition-colors">
                                                <Play className="w-4 h-4" />
                                            </button>
                                        )}
                                    </div>
                                </motion.div>
                            );
                        })
                    )}
                </div>
            </motion.div>
        </div>
    );
}