import { useState, useRef } from 'react';
import { Upload, Video, Send, Loader2, CheckCircle, XCircle, FileVideo } from 'lucide-react';

const API_URL = "http://localhost:8002";

export function FacebookReelUpload() {
    const [file, setFile] = useState<File | null>(null);
    const [caption, setCaption] = useState('');
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<{ success: boolean; message: string; postId?: string } | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            setResult(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setResult(null);

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('caption', caption);

            const res = await fetch(`${API_URL}/api/upload-facebook-reel`, {
                method: 'POST',
                body: formData,
            });

            const data = await res.json();

            if (res.ok && data.success) {
                setResult({
                    success: true,
                    message: 'Reel uploaded successfully!',
                    postId: data.video_id,
                });
                setFile(null);
                setCaption('');
                if (fileInputRef.current) fileInputRef.current.value = '';
            } else {
                setResult({
                    success: false,
                    message: data.error || 'Upload failed',
                });
            }
        } catch (err) {
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
                    <Video className="w-8 h-8 text-blue-400" />
                    Facebook Reel Upload
                </h1>
                <p className="text-neutral-400 mt-2">Upload video reels directly to your Facebook Page</p>
            </div>

            {/* Upload Card */}
            <div className="bg-[#13131c] border border-white/5 rounded-2xl p-6 space-y-6">
                {/* File Input */}
                <div
                    onClick={() => fileInputRef.current?.click()}
                    className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition ${file
                            ? 'border-green-500/50 bg-green-500/5'
                            : 'border-white/10 hover:border-purple-500/50 hover:bg-purple-500/5'
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
                            <p className="text-sm text-neutral-500 mt-1">MP4, MOV, or WebM up to 1GB</p>
                        </>
                    )}
                </div>

                {/* Caption Input */}
                <div>
                    <label className="block text-sm font-medium text-neutral-400 mb-2">
                        Caption (optional)
                    </label>
                    <textarea
                        value={caption}
                        onChange={(e) => setCaption(e.target.value)}
                        placeholder="Write a caption for your reel..."
                        className="w-full bg-[#1a1a2e] border border-white/10 rounded-lg p-3 text-white placeholder-neutral-500 focus:outline-none focus:border-purple-500/50 resize-none"
                        rows={3}
                    />
                </div>

                {/* Upload Button */}
                <button
                    onClick={handleUpload}
                    disabled={!file || uploading}
                    className={`w-full py-3 rounded-xl font-medium flex items-center justify-center gap-2 transition ${!file || uploading
                            ? 'bg-neutral-700 text-neutral-400 cursor-not-allowed'
                            : 'bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:opacity-90'
                        }`}
                >
                    {uploading ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Uploading to Facebook...
                        </>
                    ) : (
                        <>
                            <Send className="w-5 h-5" />
                            Upload Reel
                        </>
                    )}
                </button>

                {/* Result */}
                {result && (
                    <div
                        className={`p-4 rounded-lg flex items-start gap-3 ${result.success
                                ? 'bg-green-500/10 border border-green-500/20'
                                : 'bg-red-500/10 border border-red-500/20'
                            }`}
                    >
                        {result.success ? (
                            <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                        ) : (
                            <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                        )}
                        <div>
                            <p className={result.success ? 'text-green-400' : 'text-red-400'}>
                                {result.message}
                            </p>
                            {result.postId && (
                                <p className="text-sm text-neutral-400 mt-1">
                                    Post ID: <code className="bg-black/30 px-1 rounded">{result.postId}</code>
                                </p>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
