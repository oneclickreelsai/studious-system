import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  Play,
  Trash2,
  Sparkles,
  CheckCircle,
  AlertCircle,
  Loader2,
  FolderOpen,
  Youtube,
  Facebook,
  Instagram,
  FileVideo,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { API_URL } from "../config/api";

interface VideoItem {
  id: string;
  file: File;
  preview: string;
  title: string;
  description: string;
  tags: string;
  status: "pending" | "uploading" | "success" | "error";
  progress: number;
  error?: string;
  expanded: boolean;
}

const NICHES = [
  "Technology",
  "Motivation",
  "Finance",
  "Entertainment",
  "Education",
  "Lifestyle",
  "Gaming",
  "Music",
  "Comedy",
  "Facts",
];

export function BatchUploadPage() {
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [globalNiche, setGlobalNiche] = useState("Technology");
  const [globalPrivacy, setGlobalPrivacy] = useState("public");
  const [uploadYoutube, setUploadYoutube] = useState(true);
  const [uploadFacebook, setUploadFacebook] = useState(false);
  const [uploadInstagram, setUploadInstagram] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [currentUploadIndex, setCurrentUploadIndex] = useState(-1);

  // Handle file selection
  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    addFiles(files);
  }, []);

  // Handle drag and drop
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files).filter((f) =>
      f.type.startsWith("video/")
    );
    addFiles(files);
  }, []);

  const addFiles = (files: File[]) => {
    const newVideos: VideoItem[] = files.map((file) => ({
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      file,
      preview: URL.createObjectURL(file),
      title: file.name.replace(/\.[^/.]+$/, "").replace(/[_-]/g, " "),
      description: "",
      tags: "",
      status: "pending",
      progress: 0,
      expanded: false,
    }));
    setVideos((prev) => [...prev, ...newVideos]);
  };

  // Remove video from list
  const removeVideo = (id: string) => {
    setVideos((prev) => {
      const video = prev.find((v) => v.id === id);
      if (video) URL.revokeObjectURL(video.preview);
      return prev.filter((v) => v.id !== id);
    });
  };

  // Update video details
  const updateVideo = (id: string, updates: Partial<VideoItem>) => {
    setVideos((prev) =>
      prev.map((v) => (v.id === id ? { ...v, ...updates } : v))
    );
  };

  // Toggle video expansion
  const toggleExpand = (id: string) => {
    setVideos((prev) =>
      prev.map((v) => (v.id === id ? { ...v, expanded: !v.expanded } : v))
    );
  };

  // AI Generate metadata for all videos
  const generateAllMetadata = async () => {
    setGenerating(true);
    
    for (const video of videos) {
      if (video.status === "pending") {
        try {
          const res = await fetch(`${API_URL}/api/generate-metadata`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              title: video.title,
              niche: globalNiche.toLowerCase(),
            }),
          });
          
          if (res.ok) {
            const data = await res.json();
            updateVideo(video.id, {
              title: data.title || video.title,
              description: data.description || "",
              tags: (data.hashtags || []).join(", "),
            });
          }
        } catch (err) {
          console.error("Metadata generation failed:", err);
        }
      }
    }
    
    setGenerating(false);
  };

  // Upload single video
  const uploadSingleVideo = async (video: VideoItem): Promise<boolean> => {
    updateVideo(video.id, { status: "uploading", progress: 10 });

    try {
      const formData = new FormData();
      formData.append("file", video.file);
      formData.append("title", video.title);
      formData.append("description", video.description);
      formData.append("niche", globalNiche.toLowerCase());
      formData.append("privacy", globalPrivacy);
      formData.append("upload_youtube", uploadYoutube.toString());
      formData.append("upload_facebook", uploadFacebook.toString());

      updateVideo(video.id, { progress: 30 });

      const res = await fetch(`${API_URL}/api/upload-and-publish`, {
        method: "POST",
        body: formData,
      });

      updateVideo(video.id, { progress: 80 });

      if (res.ok) {
        await res.json();
        updateVideo(video.id, {
          status: "success",
          progress: 100,
        });
        return true;
      } else {
        const error = await res.text();
        updateVideo(video.id, {
          status: "error",
          error: error || "Upload failed",
        });
        return false;
      }
    } catch (err) {
      updateVideo(video.id, {
        status: "error",
        error: err instanceof Error ? err.message : "Upload failed",
      });
      return false;
    }
  };

  // Upload all videos
  const uploadAll = async () => {
    setIsUploading(true);
    const pendingVideos = videos.filter((v) => v.status === "pending");

    for (let i = 0; i < pendingVideos.length; i++) {
      setCurrentUploadIndex(i);
      await uploadSingleVideo(pendingVideos[i]);
      // Small delay between uploads
      await new Promise((r) => setTimeout(r, 1000));
    }

    setIsUploading(false);
    setCurrentUploadIndex(-1);
  };

  // Clear all videos
  const clearAll = () => {
    videos.forEach((v) => URL.revokeObjectURL(v.preview));
    setVideos([]);
  };

  const pendingCount = videos.filter((v) => v.status === "pending").length;
  const successCount = videos.filter((v) => v.status === "success").length;
  const errorCount = videos.filter((v) => v.status === "error").length;

  return (
    <div className="min-h-screen p-6 lg:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-600 mb-4">
            <FolderOpen className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">Batch Upload</h1>
          <p className="text-neutral-400 mt-2">
            Upload multiple videos at once with AI-generated metadata
          </p>
        </div>

        {/* Drop Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          className="border-2 border-dashed border-neutral-700 hover:border-purple-500 rounded-2xl p-8 text-center transition-colors bg-neutral-900/50"
        >
          <input
            type="file"
            multiple
            accept="video/*"
            onChange={handleFileSelect}
            className="hidden"
            id="batch-file-input"
          />
          <label
            htmlFor="batch-file-input"
            className="cursor-pointer flex flex-col items-center"
          >
            <Upload className="w-12 h-12 text-neutral-500 mb-4" />
            <p className="text-white font-medium mb-2">
              Drop videos here or click to select
            </p>
            <p className="text-neutral-500 text-sm">
              MP4, MOV, AVI (max 256MB each)
            </p>
          </label>
        </div>

        {/* Global Settings */}
        {videos.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-neutral-900/80 border border-neutral-800 rounded-2xl p-6"
          >
            <h3 className="text-lg font-semibold text-white mb-4">
              Global Settings
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Niche */}
              <div>
                <label className="block text-sm text-neutral-400 mb-2">
                  Niche
                </label>
                <select
                  value={globalNiche}
                  onChange={(e) => setGlobalNiche(e.target.value)}
                  className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-4 py-2.5 text-white"
                >
                  {NICHES.map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
              </div>

              {/* Privacy */}
              <div>
                <label className="block text-sm text-neutral-400 mb-2">
                  Privacy
                </label>
                <select
                  value={globalPrivacy}
                  onChange={(e) => setGlobalPrivacy(e.target.value)}
                  className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-4 py-2.5 text-white"
                >
                  <option value="public">Public</option>
                  <option value="unlisted">Unlisted</option>
                  <option value="private">Private</option>
                </select>
              </div>

              {/* Platforms */}
              <div>
                <label className="block text-sm text-neutral-400 mb-2">
                  Platforms
                </label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setUploadYoutube(!uploadYoutube)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors ${
                      uploadYoutube
                        ? "bg-red-500/20 border-red-500 text-red-400"
                        : "bg-neutral-800 border-neutral-700 text-neutral-400"
                    }`}
                  >
                    <Youtube className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setUploadFacebook(!uploadFacebook)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors ${
                      uploadFacebook
                        ? "bg-blue-500/20 border-blue-500 text-blue-400"
                        : "bg-neutral-800 border-neutral-700 text-neutral-400"
                    }`}
                  >
                    <Facebook className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setUploadInstagram(!uploadInstagram)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors ${
                      uploadInstagram
                        ? "bg-pink-500/20 border-pink-500 text-pink-400"
                        : "bg-neutral-800 border-neutral-700 text-neutral-400"
                    }`}
                  >
                    <Instagram className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Auto Generate */}
              <div>
                <label className="block text-sm text-neutral-400 mb-2">
                  AI Metadata
                </label>
                <button
                  onClick={generateAllMetadata}
                  disabled={generating || videos.length === 0}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 text-white rounded-lg font-medium disabled:opacity-50 transition-all"
                >
                  {generating ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Sparkles className="w-4 h-4" />
                  )}
                  Generate All
                </button>
              </div>
            </div>
          </motion.div>
        )}


        {/* Video List */}
        {videos.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">
                Videos ({videos.length})
              </h3>
              <div className="flex items-center gap-4 text-sm">
                {successCount > 0 && (
                  <span className="text-green-400">
                    ✓ {successCount} uploaded
                  </span>
                )}
                {errorCount > 0 && (
                  <span className="text-red-400">✗ {errorCount} failed</span>
                )}
                <button
                  onClick={clearAll}
                  className="text-neutral-400 hover:text-red-400 transition-colors"
                >
                  Clear All
                </button>
              </div>
            </div>

            <AnimatePresence>
              {videos.map((video) => (
                <motion.div
                  key={video.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  className={`bg-neutral-900/80 border rounded-xl overflow-hidden transition-colors ${
                    video.status === "success"
                      ? "border-green-500/50"
                      : video.status === "error"
                      ? "border-red-500/50"
                      : video.status === "uploading"
                      ? "border-purple-500/50"
                      : "border-neutral-800"
                  }`}
                >
                  {/* Video Header */}
                  <div className="flex items-center gap-4 p-4">
                    {/* Thumbnail */}
                    <div className="relative w-24 h-16 bg-neutral-800 rounded-lg overflow-hidden flex-shrink-0">
                      <video
                        src={video.preview}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 flex items-center justify-center bg-black/30">
                        <FileVideo className="w-6 h-6 text-white/70" />
                      </div>
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <input
                        type="text"
                        value={video.title}
                        onChange={(e) =>
                          updateVideo(video.id, { title: e.target.value })
                        }
                        className="w-full bg-transparent text-white font-medium border-b border-transparent hover:border-neutral-700 focus:border-purple-500 outline-none pb-1 truncate"
                        placeholder="Video title..."
                      />
                      <p className="text-neutral-500 text-sm mt-1">
                        {(video.file.size / 1024 / 1024).toFixed(1)} MB
                      </p>
                    </div>

                    {/* Status */}
                    <div className="flex items-center gap-3">
                      {video.status === "uploading" && (
                        <div className="flex items-center gap-2">
                          <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
                          <span className="text-purple-400 text-sm">
                            {video.progress}%
                          </span>
                        </div>
                      )}
                      {video.status === "success" && (
                        <CheckCircle className="w-5 h-5 text-green-400" />
                      )}
                      {video.status === "error" && (
                        <AlertCircle className="w-5 h-5 text-red-400" />
                      )}

                      {/* Expand/Collapse */}
                      <button
                        onClick={() => toggleExpand(video.id)}
                        className="p-2 text-neutral-400 hover:text-white transition-colors"
                      >
                        {video.expanded ? (
                          <ChevronUp className="w-5 h-5" />
                        ) : (
                          <ChevronDown className="w-5 h-5" />
                        )}
                      </button>

                      {/* Remove */}
                      <button
                        onClick={() => removeVideo(video.id)}
                        className="p-2 text-neutral-400 hover:text-red-400 transition-colors"
                        disabled={video.status === "uploading"}
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  {video.status === "uploading" && (
                    <div className="h-1 bg-neutral-800">
                      <div
                        className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-300"
                        style={{ width: `${video.progress}%` }}
                      />
                    </div>
                  )}

                  {/* Expanded Details */}
                  <AnimatePresence>
                    {video.expanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="border-t border-neutral-800 overflow-hidden"
                      >
                        <div className="p-4 space-y-4">
                          {/* Description */}
                          <div>
                            <label className="block text-sm text-neutral-400 mb-2">
                              Description
                            </label>
                            <textarea
                              value={video.description}
                              onChange={(e) =>
                                updateVideo(video.id, {
                                  description: e.target.value,
                                })
                              }
                              rows={3}
                              className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-4 py-3 text-white resize-none focus:border-purple-500 outline-none"
                              placeholder="Video description..."
                            />
                          </div>

                          {/* Tags */}
                          <div>
                            <label className="block text-sm text-neutral-400 mb-2">
                              Tags (comma separated)
                            </label>
                            <input
                              type="text"
                              value={video.tags}
                              onChange={(e) =>
                                updateVideo(video.id, { tags: e.target.value })
                              }
                              className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-4 py-3 text-white focus:border-purple-500 outline-none"
                              placeholder="#motivation, #success, #viral"
                            />
                          </div>

                          {/* Error Message */}
                          {video.error && (
                            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                              {video.error}
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}

        {/* Upload Button */}
        {videos.length > 0 && pendingCount > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-center"
          >
            <button
              onClick={uploadAll}
              disabled={isUploading || pendingCount === 0}
              className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 text-white rounded-xl font-semibold text-lg disabled:opacity-50 transition-all shadow-lg shadow-purple-500/25"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin" />
                  Uploading {currentUploadIndex + 1}/{pendingCount}...
                </>
              ) : (
                <>
                  <Play className="w-6 h-6" />
                  Upload All ({pendingCount} videos)
                </>
              )}
            </button>
          </motion.div>
        )}

        {/* Empty State */}
        {videos.length === 0 && (
          <div className="text-center py-12 text-neutral-500">
            <FileVideo className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p>No videos selected</p>
            <p className="text-sm mt-1">
              Drop videos above or click to select files
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
