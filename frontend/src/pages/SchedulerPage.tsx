import { useState, useEffect } from "react";
import { Calendar, Clock, Plus, Trash2, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

const API_URL = "http://localhost:8002";

interface ScheduledPost {
  id: string;
  title: string;
  platform: "youtube" | "facebook" | "both";
  scheduled_time: string;
  status: "pending" | "processing" | "completed" | "failed";
  content_type: "video" | "post";
  niche: string;
  topic: string;
}

export function SchedulerPage() {
  const [posts, setPosts] = useState<ScheduledPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    platform: "youtube" as "youtube" | "facebook" | "both",
    scheduled_time: "",
    content_type: "video" as "video" | "post",
    niche: "tech",
    topic: ""
  });

  useEffect(() => {
    fetchScheduledPosts();
  }, []);

  const fetchScheduledPosts = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/scheduler/posts`);
      if (res.ok) {
        const data = await res.json();
        setPosts(data.posts || []);
      }
    } catch (e) {
      console.error("Failed to fetch scheduled posts:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_URL}/api/scheduler/posts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        setShowForm(false);
        setFormData({ title: "", platform: "youtube", scheduled_time: "", content_type: "video", niche: "tech", topic: "" });
        fetchScheduledPosts();
      }
    } catch (e) {
      console.error("Failed to schedule post:", e);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await fetch(`${API_URL}/api/scheduler/posts/${id}`, { method: "DELETE" });
      fetchScheduledPosts();
    } catch (e) {
      console.error("Failed to delete:", e);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed": return <CheckCircle className="w-4 h-4 text-green-400" />;
      case "failed": return <AlertCircle className="w-4 h-4 text-red-400" />;
      case "processing": return <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />;
      default: return <Clock className="w-4 h-4 text-yellow-400" />;
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Smart Scheduler</h1>
          <p className="text-neutral-400">Schedule your content for optimal engagement</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl font-semibold text-white flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Schedule New
        </button>
      </div>

      {showForm && (
        <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6 mb-8">
          <h3 className="text-lg font-semibold text-white mb-4">Schedule Content</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-neutral-400 mb-2">Title</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white"
                placeholder="Content title"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-neutral-400 mb-2">Platform</label>
              <select
                value={formData.platform}
                onChange={(e) => setFormData({ ...formData, platform: e.target.value as "youtube" | "facebook" | "both" })}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white"
              >
                <option value="youtube">YouTube</option>
                <option value="facebook">Facebook</option>
                <option value="both">Both</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-neutral-400 mb-2">Schedule Time</label>
              <input
                type="datetime-local"
                value={formData.scheduled_time}
                onChange={(e) => setFormData({ ...formData, scheduled_time: e.target.value })}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-neutral-400 mb-2">Topic</label>
              <input
                type="text"
                value={formData.topic}
                onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white"
                placeholder="Content topic"
              />
            </div>
            <div className="md:col-span-2 flex justify-end gap-3">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-neutral-400 hover:text-white">
                Cancel
              </button>
              <button type="submit" className="px-6 py-2 bg-blue-600 hover:bg-blue-500 rounded-xl font-semibold text-white">
                Schedule
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-[#12121a] border border-white/10 rounded-2xl overflow-hidden">
        <div className="p-4 border-b border-white/10 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-purple-400" />
          <span className="font-semibold text-white">Scheduled Posts</span>
          <span className="ml-auto text-sm text-neutral-500">{posts.length} items</span>
        </div>

        {loading ? (
          <div className="p-12 text-center">
            <Loader2 className="w-8 h-8 text-neutral-500 animate-spin mx-auto" />
          </div>
        ) : posts.length === 0 ? (
          <div className="p-12 text-center text-neutral-500">
            No scheduled posts yet. Click "Schedule New" to get started.
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {posts.map((post) => (
              <div key={post.id} className="p-4 flex items-center gap-4 hover:bg-white/5 transition-colors">
                {getStatusIcon(post.status)}
                <div className="flex-1 min-w-0">
                  <p className="text-white font-medium truncate">{post.title}</p>
                  <p className="text-sm text-neutral-500">
                    {post.platform} • {new Date(post.scheduled_time).toLocaleString()}
                  </p>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  post.status === "completed" ? "bg-green-500/20 text-green-400" :
                  post.status === "failed" ? "bg-red-500/20 text-red-400" :
                  post.status === "processing" ? "bg-blue-500/20 text-blue-400" :
                  "bg-yellow-500/20 text-yellow-400"
                }`}>
                  {post.status}
                </span>
                <button
                  onClick={() => handleDelete(post.id)}
                  className="p-2 text-neutral-500 hover:text-red-400 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
