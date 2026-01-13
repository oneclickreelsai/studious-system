import { useState, useRef } from "react";
import { Upload, Loader2, CheckCircle, AlertCircle, Youtube, Facebook, FileVideo, Sparkles, Send } from "lucide-react";

import { API_URL } from '../config/api';

interface UploadResult {
  success: boolean;
  youtube_id?: string;
  youtube_url?: string;
  facebook_id?: string;
  facebook_url?: string;
  error?: string;
}

export function VideoUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [niche, setNiche] = useState("tech");
  const [uploadYoutube, setUploadYoutube] = useState(true);
  const [uploadFacebook, setUploadFacebook] = useState(false);
  const [privacy, setPrivacy] = useState("public");
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const niches = [
    { value: "tech", label: "Technology" },
    { value: "trading", label: "Trading & Finance" },
    { value: "motivation", label: "Motivation" },
    { value: "entertainment", label: "Entertainment" },
    { value: "education", label: "Education" },
    { value: "gaming", label: "Gaming" },
  ];

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      // Auto-generate title from filename
      if (!title) {
        const name = selectedFile.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");
        setTitle(name);
      }
    }
  };

  const handleGenerateMetadata = async () => {
    if (!title) return;
    
    setGenerating(true);
    try {
      const res = await fetch(`${API_URL}/api/generate-metadata`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, niche })
      });
      
      if (res.ok) {
        const data = await res.json();
        if (data.description) setDescription(data.description);
        if (data.title) setTitle(data.title);
      }
    } catch (e) {
      console.error("Failed to generate metadata:", e);
    } finally {
      setGenerating(false);
    }
  };

  const handleUpload = async () => {
    if (!file || !title) return;
    
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("title", title);
      formData.append("description", description);
      formData.append("niche", niche);
      formData.append("privacy", privacy);
      formData.append("upload_youtube", uploadYoutube.toString());
      formData.append("upload_facebook", uploadFacebook.toString());

      const res = await fetch(`${API_URL}/api/upload-and-publish`, {
        method: "POST",
        body: formData
      });

      const data = await res.json();
      
      if (!res.ok) throw new Error(data.detail || JSON.stringify(data) || "Upload failed");
      
      setResult(data);
    } catch (e: unknown) {
      const errorMsg = e instanceof Error ? e.message : "Upload failed";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setTitle("");
    setDescription("");
    setResult(null);
    setError("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-green-600 to-emerald-500 mb-6 shadow-lg shadow-green-500/30">
          <Upload className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-3">Upload & Publish</h2>
        <p className="text-neutral-400">Upload your video to YouTube and Facebook with AI-generated metadata</p>
      </div>

      {!result ? (
        <div className="space-y-6">
          {/* File Upload */}
          <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6">
            <label className="block text-sm text-neutral-400 mb-3">Video File</label>
            
            {!file ? (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-white/10 rounded-xl p-12 text-center cursor-pointer hover:border-green-500/50 hover:bg-green-500/5 transition-all"
              >
                <FileVideo className="w-12 h-12 text-neutral-600 mx-auto mb-4" />
                <p className="text-neutral-400 mb-2">Click to select video file</p>
                <p className="text-xs text-neutral-600">MP4, MOV, AVI (max 2GB)</p>
              </div>
            ) : (
              <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                <FileVideo className="w-10 h-10 text-green-400" />
                <div className="flex-1 min-w-0">
                  <p className="text-white font-medium truncate">{file.name}</p>
                  <p className="text-sm text-neutral-500">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                </div>
                <button onClick={resetForm} className="text-neutral-400 hover:text-red-400">
                  Remove
                </button>
              </div>
            )}
            
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* Metadata */}
          <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-neutral-400">Video Details</label>
              <button
                onClick={handleGenerateMetadata}
                disabled={generating || !title}
                className="flex items-center gap-2 px-3 py-1.5 text-xs bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 disabled:opacity-50"
              >
                {generating ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                AI Generate
              </button>
            </div>

            <div>
              <label className="block text-xs text-neutral-500 mb-1">Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter video title..."
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-neutral-600 focus:outline-none focus:border-green-500"
              />
            </div>

            <div>
              <label className="block text-xs text-neutral-500 mb-1">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter video description..."
                rows={4}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-neutral-600 focus:outline-none focus:border-green-500 resize-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-neutral-500 mb-1">Niche</label>
                <select
                  value={niche}
                  onChange={(e) => setNiche(e.target.value)}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-green-500"
                >
                  {niches.map((n) => (
                    <option key={n.value} value={n.value} className="bg-[#12121a]">{n.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-neutral-500 mb-1">Privacy</label>
                <select
                  value={privacy}
                  onChange={(e) => setPrivacy(e.target.value)}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-green-500"
                >
                  <option value="public" className="bg-[#12121a]">Public</option>
                  <option value="unlisted" className="bg-[#12121a]">Unlisted</option>
                  <option value="private" className="bg-[#12121a]">Private</option>
                </select>
              </div>
            </div>
          </div>

          {/* Platform Selection */}
          <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6">
            <label className="block text-sm text-neutral-400 mb-4">Upload To</label>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => setUploadYoutube(!uploadYoutube)}
                className={`p-4 rounded-xl border flex items-center gap-3 transition-all ${
                  uploadYoutube
                    ? "bg-red-500/20 border-red-500 text-red-400"
                    : "bg-white/5 border-white/10 text-neutral-400 hover:border-white/20"
                }`}
              >
                <Youtube className="w-6 h-6" />
                <div className="text-left">
                  <p className="font-medium">YouTube</p>
                  <p className="text-xs opacity-70">Shorts / Video</p>
                </div>
                {uploadYoutube && <CheckCircle className="w-5 h-5 ml-auto" />}
              </button>

              <button
                onClick={() => setUploadFacebook(!uploadFacebook)}
                className={`p-4 rounded-xl border flex items-center gap-3 transition-all ${
                  uploadFacebook
                    ? "bg-blue-500/20 border-blue-500 text-blue-400"
                    : "bg-white/5 border-white/10 text-neutral-400 hover:border-white/20"
                }`}
              >
                <Facebook className="w-6 h-6" />
                <div className="text-left">
                  <p className="font-medium">Facebook</p>
                  <p className="text-xs opacity-70">Reels / Video</p>
                </div>
                {uploadFacebook && <CheckCircle className="w-5 h-5 ml-auto" />}
              </button>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-red-300">{error}</p>
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={loading || !file || !title || (!uploadYoutube && !uploadFacebook)}
            className="w-full py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Upload & Publish
              </>
            )}
          </button>
        </div>
      ) : (
        /* Success Result */
        <div className="bg-gradient-to-br from-green-900/20 to-emerald-900/20 border border-green-500/20 rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Upload Complete!</h3>
              <p className="text-green-400 text-sm">Your video has been published</p>
            </div>
          </div>

          <div className="space-y-4 mb-6">
            {result.youtube_id && (
              <div className="flex items-center gap-3 p-4 bg-black/20 rounded-xl">
                <Youtube className="w-6 h-6 text-red-400" />
                <div className="flex-1">
                  <p className="text-white font-medium">YouTube</p>
                  <p className="text-sm text-neutral-400">Video ID: {result.youtube_id}</p>
                </div>
                <a
                  href={result.youtube_url || `https://youtube.com/watch?v=${result.youtube_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 text-sm"
                >
                  View
                </a>
              </div>
            )}

            {result.facebook_id && (
              <div className="flex items-center gap-3 p-4 bg-black/20 rounded-xl">
                <Facebook className="w-6 h-6 text-blue-400" />
                <div className="flex-1">
                  <p className="text-white font-medium">Facebook</p>
                  <p className="text-sm text-neutral-400">Post ID: {result.facebook_id}</p>
                </div>
                <a
                  href={result.facebook_url || `https://facebook.com/${result.facebook_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30 text-sm"
                >
                  View
                </a>
              </div>
            )}
          </div>

          <button
            onClick={resetForm}
            className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
          >
            Upload Another
          </button>
        </div>
      )}
    </div>
  );
}

