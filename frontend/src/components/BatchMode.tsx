
import { useState } from "react";
import { Layers, Loader2, Play } from "lucide-react";
import { motion } from "framer-motion";

export function BatchMode() {
    const [count, setCount] = useState(3);
    const [niche, setNiche] = useState("viral");
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState<string | null>(null);

    const startBatch = async () => {
        setLoading(true);
        setStatus("Initiating...");
        try {
            const res = await fetch("http://localhost:8002/api/batch-generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ count, niche, upload_youtube: true }),
            });
            const data = await res.json();
            setStatus(data.message);

            // Reset after delay
            setTimeout(() => {
                setLoading(false);
                setStatus(null);
            }, 5000);
        } catch (e) {
            setStatus("Failed to start batch.");
            setLoading(false);
        }
    };

    return (
        <div className="bg-gradient-to-br from-indigo-900/40 to-blue-900/40 border border-indigo-500/20 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-indigo-500/20 rounded-lg">
                    <Layers className="w-5 h-5 text-indigo-400" />
                </div>
                <div>
                    <h3 className="text-lg font-bold text-white">Batch Generator</h3>
                    <p className="text-xs text-indigo-300">Run multiple automated pipelines</p>
                </div>
            </div>

            <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="text-xs text-neutral-400 mb-1 block">Quantity</label>
                        <select
                            value={count}
                            onChange={(e) => setCount(Number(e.target.value))}
                            className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                        >
                            {[1, 3, 5, 10].map(n => <option key={n} value={n}>{n} Videos</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="text-xs text-neutral-400 mb-1 block">Category</label>
                        <select
                            value={niche}
                            onChange={(e) => setNiche(e.target.value)}
                            className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                        >
                            <option value="viral">Viral Mix</option>
                            <option value="funny">Comedy</option>
                            <option value="music">Music</option>
                            <option value="nature">Nature</option>
                            <option value="artistic">Artistic</option>
                        </select>
                    </div>
                </div>

                <button
                    onClick={startBatch}
                    disabled={loading}
                    className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
                    {loading ? "Processing in Background..." : "Start Batch"}
                </button>

                {status && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-xs text-center text-indigo-300 bg-indigo-500/10 py-2 rounded-lg"
                    >
                        {status}
                    </motion.div>
                )}
            </div>
        </div>
    );
}
