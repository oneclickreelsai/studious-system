import { useState, useRef } from "react";
import { Upload, Loader2, CheckCircle, AlertCircle, Film, FileVideo, ExternalLink } from "lucide-react";

const API_URL = "http://localhost:8002";

interface UploadResult {
  success: boolean;
  video_id: string;
  url: string;
  title: string;
}

export function YouTubeUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [tags, setTags] = useState("");
  const [privacy, setPrivacy] = useState<"public" | "unlisted" | "private">("public");
  const [category, setCategory] = useState("22"); // People & Blogs
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const categories = [
    { id: "1", name: "Film & Animation" },
    { id: "2", name: "Autos & Vehicles" },
    { id: "10", name: "Music" },
    { id: "15", name: "Pets & Animals" },
    { id: "17", name: "Sports" },
    { id: "20", name: "Gaming" },
    { id: "22", name: "People & Blogs" },
    { id: "23", name: "Comedy" },
    { id: "24", name: "Entertainment" },
    { id: "25", name: "News & Politics" },
    { id: "26", name: "Howto & Style" },
    { id: "27", name: "Education" },
    { id: "28", name: "Science & Technology" },
  ];

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      // Auto-fill title from filename
      if (!title) {
        const nameWithoutExt = selectedFile.name.replace(/\.[^/.]+$/, "");
        setTitle(nameWithoutExt);
      }
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith("video/")) {
      setFile(droppedFile);
      if (!title) {
        const nameWithoutExt = droppedFile.name.replace(/\.[^/.]+$/, "");
        setTitle(nameWithoutExt);
      }
    }
  };

  const handleUpload = async () => {
    if (!file || !title.trim()) return;

    setUploading(true);
    setError("");
    setResult(null);
    setProgress(0);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    formData.append("description", description);
    formData.append("tags", tags);
    formData.append("privacy", privacy);
    formData.append("category", category);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 500);

      const res = await fetch(`${API_URL}/api/youtube-upload`, {
        method: "POST",
        body: formData
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
      }

      const data = await res.json();
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setTitle("");
    setDescription("");
    setTags("");
    setResult(null);
    setError("");
    setProgress(0);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-red-600 to-orange-500 mb-6 shadow-lg shadow-red-500/30">
          <Upload className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-3">YouTube Upload</h2>
        <p className="text-neutral-400">Upload your videos directly to YouTube</p>
      </div>

      {!result ? (
        <div className="space-y-6">
          {/* File Upload */}
          <div
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className={`bg-[#12121a] border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
              file ? "border-red-500/50 bg-red-500/5" : "border-white/10 hover:border-white/20"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            {file ? (
              <div className="space-y-3">
                <FileVideo className="w-12 h-12 text-red-400 mx-auto" />
                <p className="text-white font-medium">{file.name}</p>
                <p className="text-sm text-neutral-400">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
                <button
                  onClick={(e) => { e.stopPropagation(); setFile(null); }}
                  className="text-sm text-red-400 hover:text-red-300"
                >
                  Remove
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <Film className="w-12 h-12 text-neutral-600 mx-auto" />
                <p className="text-neutral-400">
                  Drag and drop your video here, or <span className="text-red-400">browse</span>
                </p>
                <p className="text-xs text-neutral-500">MP4, MOV, AVI up to 256GB</p>
              </div>
            )}
          </div>

          {/* Video Details */}
          <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6 space-y-5">
            <h3 className="text-lg font-semibold text-white">Video Details</h3>

            <div>
              <label className="block text-sm text-neutral-400 mb-2">Title *</label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter video title..."
                maxLength={100}
                className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white placeholder-neutral-500 focus:outline-none focus:border-red-500"
              />
              <p className="text-xs text-neutral-500 mt-1">{title.length}/100</p>
            </div>

            <div>
              <label className="block text-sm text-neutral-400 mb-2">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Tell viewers about your video..."
                rows={4}
                maxLength={5000}
                className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white placeholder-neutral-500 focus:outline-none focus:border-red-500 resize-none"
              />
              <p className="text-xs text-neutral-500 mt-1">{description.length}/5000</p>
            </div>

            <div>
              <label className="block text-sm text-neutral-400 mb-2">Tags</label>
              <input
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="tag1, tag2, tag3..."
                className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white placeholder-neutral-500 focus:outline-none focus:border-red-500"
              />
              <p className="text-xs text-neutral-500 mt-1">Separate tags with commas</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-neutral-400 mb-2">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white focus:outline-none focus:border-red-500"
                >
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id} className="bg-[#12121a]">
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-neutral-400 mb-2">Privacy</label>
                <div className="flex gap-2">
                  {(["public", "unlisted", "private"] as const).map((p) => (
                    <button
                      key={p}
                      onClick={() => setPrivacy(p)}
                      className={`flex-1 py-3 rounded-xl text-sm font-medium capitalize transition-colors ${
                        privacy === p
                          ? "bg-red-500/20 text-red-400 border border-red-500/50"
                          : "bg-white/5 text-neutral-400 border border-white/10 hover:border-white/20"
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-300 flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              {error}
            </div>
          )}

          {/* Upload Progress */}
          {uploading && (
            <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-3">
                <span className="text-white font-medium">Uploading...</span>
                <span className="text-neutral-400">{progress}%</span>
              </div>
              <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-red-500 to-orange-500 transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={uploading || !file || !title.trim()}
            className="w-full py-4 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-2xl font-bold text-white text-lg flex items-center justify-center gap-3"
          >
            {uploading ? (
              <><Loader2 className="w-6 h-6 animate-spin" /> Uploading...</>
            ) : (
              <><Upload className="w-6 h-6" /> Upload to YouTube</>
            )}
          </button>
        </div>
      ) : (
        <div className="bg-gradient-to-br from-green-900/20 to-emerald-900/20 border border-green-500/20 rounded-2xl p-8 text-center">
          <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-white mb-2">Upload Successful!</h3>
          <p className="text-neutral-400 mb-6">Your video is now on YouTube</p>

          <div className="bg-black/20 rounded-xl p-4 mb-6">
            <p className="text-white font-medium mb-2">{result.title}</p>
            <a
              href={result.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-red-400 hover:text-red-300 flex items-center justify-center gap-2"
            >
              {result.url}
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>

          <div className="flex gap-4 justify-center">
            <a
              href={result.url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 bg-red-600 hover:bg-red-500 rounded-xl font-semibold text-white flex items-center gap-2"
            >
              <ExternalLink className="w-4 h-4" /> View on YouTube
            </a>
            <button
              onClick={resetForm}
              className="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-xl font-semibold text-white"
            >
              Upload Another
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
