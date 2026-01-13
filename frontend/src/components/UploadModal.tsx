
import { useState } from 'react';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';

interface UploadModalProps {
    onClose: () => void;
    onSubmit: (file: File, title: string, niche: string, uploadYoutube: boolean) => void;
}

export function UploadModal({ onClose, onSubmit }: UploadModalProps) {
    const [file, setFile] = useState<File | null>(null);
    const [title, setTitle] = useState("");
    const [niche, setNiche] = useState("motivation");
    const [uploadYoutube, setUploadYoutube] = useState(false);

    const niches = ["motivation", "finance", "facts", "fitness", "quotes", "tech", "lifestyle"];

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleSubmit = () => {
        if (!file) {
            alert("Please select a video file");
            return;
        }
        if (!title.trim()) {
            alert("Please enter a title");
            return;
        }
        onSubmit(file, title, niche, uploadYoutube);
    };

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6"
            onClick={onClose}
        >
            <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
                className="bg-neutral-900 border border-white/10 rounded-3xl p-8 max-w-2xl w-full"
            >
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-green-500 bg-clip-text text-transparent">
                        Upload Existing Video
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/5 rounded-full transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="space-y-4">
                    {/* File Upload */}
                    <div>
                        <label className="block text-sm font-medium text-neutral-300 mb-2">
                            Video File *
                        </label>
                        <div className="relative">
                            <input
                                type="file"
                                accept="video/*"
                                onChange={handleFileChange}
                                className="w-full bg-neutral-800/50 border border-white/10 rounded-xl p-4 text-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-emerald-500/10 file:text-emerald-400 hover:file:bg-emerald-500/20 transition-all"
                            />
                        </div>
                        {file && (
                            <p className="mt-2 text-sm text-emerald-400">
                                ✓ Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                            </p>
                        )}
                    </div>

                    {/* Title */}
                    <div>
                        <label className="block text-sm font-medium text-neutral-300 mb-2">
                            Video Title *
                        </label>
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="Enter video title..."
                            className="w-full bg-neutral-800/50 border border-white/10 rounded-xl p-4 text-white placeholder-neutral-500 focus:border-emerald-500/50 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-all"
                        />
                    </div>

                    {/* Niche Selection */}
                    <div>
                        <label className="block text-sm font-medium text-neutral-300 mb-2">
                            Niche Category
                        </label>
                        <select
                            value={niche}
                            onChange={(e) => setNiche(e.target.value)}
                            className="w-full bg-neutral-800/50 border border-white/10 rounded-xl p-4 text-white focus:border-emerald-500/50 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-all"
                        >
                            {niches.map((n) => (
                                <option key={n} value={n}>
                                    {n.charAt(0).toUpperCase() + n.slice(1)}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Upload to YouTube */}
                    <div className="flex items-center gap-3">
                        <input
                            type="checkbox"
                            id="upload-youtube"
                            checked={uploadYoutube}
                            onChange={(e) => setUploadYoutube(e.target.checked)}
                            className="w-5 h-5 rounded bg-neutral-800 border-white/10 text-emerald-500 focus:ring-emerald-500/20"
                        />
                        <label htmlFor="upload-youtube" className="text-neutral-300">
                            Upload to YouTube Shorts
                        </label>
                    </div>

                    <button
                        onClick={handleSubmit}
                        className="w-full mt-6 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 text-white font-semibold py-4 rounded-xl transition-all hover:shadow-lg hover:shadow-emerald-500/25"
                    >
                        Upload Video
                    </button>
                </div>
            </motion.div>
        </motion.div>
    );
}
