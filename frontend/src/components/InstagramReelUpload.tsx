import { useState, useRef } from 'react';
import { Upload, Loader2, CheckCircle, XCircle, FileVideo, Instagram, AlertTriangle, ExternalLink } from 'lucide-react';

import { API_URL } from '../config/api';

export function InstagramReelUpload() {
    const [file, setFile] = useState<File | null>(null);
    const [videoUrl, setVideoUrl] = useState('');
    const [caption, setCaption] = useState('');
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<{ success: boolean; message: string; suggestion?: string } | null>(null);
    const [uploadMode, setUploadMode] = useState<'file' | 'url'>('url');
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            setResult(null);
        }
    };

    const handleUpload = async () => {
        setUploading(true);
        setResult(null);

        try {
            if (uploadMode === 'url') {
                // Upload via URL
                const res = await fetch(`${API_URL}/api/upload-instagram-reel-url`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ video_url: videoUrl, caption }),
                });

                const data = await res.json();

                if (res.ok && data.success) {
                    setResult({
                        success: true,
                        message: 'Reel uploaded successfully!',
                    });
                    setVideoUrl('');
                    setCaption('');
                } else {
                    setResult({
                        success: false,
                        message: data.error || 'Upload failed',
                        suggestion: data.suggestion,
                    });
                }
            } else {
                // Upload via file
                if (!file) return;

                const formData = new FormData();
                formData.append('file', file);
                formData.append('caption', caption);

                const res = await fetch(`${API_URL}/api/upload-instagram-reel`, {
                    method: 'POST',
                    body: formData,
                });

                const data = await res.json();

                if (res.ok && data.success) {
                    setResult({
                        success: true,
                        message: 'Reel uploaded successfully!',
                    });
                    setFile(null);
                    setCaption('');
                    if (fileInputRef.current) fileInputRef.current.value = '';
                } else {
                    setResult({
                        success: false,
                        message: data.error || 'Upload failed',
                        suggestion: data.suggestion,
                    });
                }
            }
        } catch {
            setResult({
                success: false,
                message: 'Failed to connect to server',
            });
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            {/* Header */}
            <div className="text-center">
                <h1 className="text-3xl font-bold text-white flex items-center justify-center gap-3">
                    <Instagram className="w-8 h-8 text-pink-400" />
                    Instagram Reel Upload
                </h1>
                <p className="text-neutral-400 mt-2">Upload video reels to your Instagram Business account</p>
            </div>

            {/* Info Banner */}
            <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                <div>
                    <p className="text-amber-300 font-medium">Requirements</p>
                    <ul className="text-amber-400/80 text-sm mt-1 space-y-1">
                        <li>• Instagram Business or Creator account</li>
                        <li>• Account must be linked to your Facebook Page</li>
                        <li>• Video must be hosted at a public URL (Instagram API limitation)</li>
                    </ul>
                </div>
            </div>

            {/* Upload Mode Toggle */}
            <div className="flex bg-[#1a1a2e] rounded-xl p-1">
                <button
                    onClick={() => setUploadMode('url')}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition ${uploadMode === 'url'
                            ? 'bg-pink-500 text-white'
                            : 'text-neutral-400 hover:text-white'
                        }`}
                >
                    Video URL
                </button>
                <button
                    onClick={() => setUploadMode('file')}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition ${uploadMode === 'file'
                            ? 'bg-pink-500 text-white'
                            : 'text-neutral-400 hover:text-white'
                        }`}
                >
                    Local File (Beta)
                </button>
            </div>

            {/* Upload Card */}
            <div className="bg-[#13131c] border border-white/5 rounded-2xl p-6 space-y-6">
                {uploadMode === 'url' ? (
                    <div>
                        <label className="block text-sm font-medium text-neutral-400 mb-2">
                            Video URL
                        </label>
                        <input
                            type="url"
                            value={videoUrl}
                            onChange={(e) => setVideoUrl(e.target.value)}
                            placeholder="https://example.com/video.mp4"
                            className="w-full bg-[#1a1a2e] border border-white/10 rounded-lg p-3 text-white placeholder-neutral-500 focus:outline-none focus:border-pink-500/50"
                        />
                        <p className="text-xs text-neutral-500 mt-2">
                            Video must be publicly accessible. Supports direct links to MP4 files.
                        </p>
                    </div>
                ) : (
                    <div
                        onClick={() => fileInputRef.current?.click()}
                        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition ${file
                                ? 'border-green-500/50 bg-green-500/5'
                                : 'border-white/10 hover:border-pink-500/50 hover:bg-pink-500/5'
                            }`}
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="video/*"
                            onChange={handleFileChange}
                            className="hidden"
                        />
                        {file ? (
                            <div className="flex items-center justify-center gap-3">
                                <FileVideo className="w-8 h-8 text-green-400" />
                                <div className="text-left">
                                    <p className="text-white font-medium">{file.name}</p>
                                    <p className="text-sm text-neutral-500">
                                        {(file.size / 1024 / 1024).toFixed(2)} MB
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <>
                                <Upload className="w-12 h-12 text-neutral-500 mx-auto mb-3" />
                                <p className="text-white font-medium">Click to select a video</p>
                                <p className="text-sm text-neutral-500 mt-1">MP4, MOV, or WebM</p>
                            </>
                        )}
                    </div>
                )}

                {/* Caption Input */}
                <div>
                    <label className="block text-sm font-medium text-neutral-400 mb-2">
                        Caption
                    </label>
                    <textarea
                        value={caption}
                        onChange={(e) => setCaption(e.target.value)}
                        placeholder="Write a caption for your reel... #hashtags #work"
                        className="w-full bg-[#1a1a2e] border border-white/10 rounded-lg p-3 text-white placeholder-neutral-500 focus:outline-none focus:border-pink-500/50 resize-none"
                        rows={3}
                    />
                </div>

                {/* Upload Button */}
                <button
                    onClick={handleUpload}
                    disabled={(uploadMode === 'url' ? !videoUrl : !file) || uploading}
                    className={`w-full py-3 rounded-xl font-medium flex items-center justify-center gap-2 transition ${(uploadMode === 'url' ? !videoUrl : !file) || uploading
                            ? 'bg-neutral-700 text-neutral-400 cursor-not-allowed'
                            : 'bg-gradient-to-r from-pink-500 to-purple-500 text-white hover:opacity-90'
                        }`}
                >
                    {uploading ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Uploading to Instagram...
                        </>
                    ) : (
                        <>
                            <Instagram className="w-5 h-5" />
                            Upload Reel
                        </>
                    )}
                </button>

                {/* Result */}
                {result && (
                    <div
                        className={`p-4 rounded-lg ${result.success
                                ? 'bg-green-500/10 border border-green-500/20'
                                : 'bg-red-500/10 border border-red-500/20'
                            }`}
                    >
                        <div className="flex items-start gap-3">
                            {result.success ? (
                                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                            ) : (
                                <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                            )}
                            <div>
                                <p className={result.success ? 'text-green-400' : 'text-red-400'}>
                                    {result.message}
                                </p>
                                {result.suggestion && (
                                    <p className="text-sm text-neutral-400 mt-2">{result.suggestion}</p>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Help Links */}
            <div className="flex items-center justify-center gap-4 text-sm">
                <a
                    href="https://help.instagram.com/502981923235522"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-neutral-500 hover:text-pink-400 flex items-center gap-1 transition"
                >
                    <ExternalLink className="w-4 h-4" />
                    Link Instagram to Facebook
                </a>
                <a
                    href="https://help.instagram.com/138925576505882"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-neutral-500 hover:text-pink-400 flex items-center gap-1 transition"
                >
                    <ExternalLink className="w-4 h-4" />
                    Switch to Business Account
                </a>
            </div>
        </div>
    );
}

