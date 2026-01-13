
import { useState, useEffect } from "react";
import { Calendar, RefreshCw, Hash, Copy, Check } from "lucide-react";
import { motion } from "framer-motion";

interface PlanItem {
    slot: number;
    category: string;
    prompt: string;
    hashtags: string[];
    best_time: string;
}

export function ContentPlanPage() {
    const [days, setDays] = useState(3);
    const [loading, setLoading] = useState(true);
    const [plan, setPlan] = useState<PlanItem[]>([]);
    const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

    const fetchPlan = async () => {
        setLoading(true);
        try {
            const res = await fetch(`http://localhost:8002/api/content-plan?days=${days}`);
            const data = await res.json();
            if (data.success) {
                setPlan(data.plan);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPlan();
    }, [days]);

    const copyToClipboard = (text: string, index: number) => {
        navigator.clipboard.writeText(text);
        setCopiedIndex(index);
        setTimeout(() => setCopiedIndex(null), 2000);
    };

    return (
        <div className="max-w-6xl mx-auto p-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2">Daily Content Planner</h2>
                    <p className="text-neutral-400">AI-curated viral content ideas tailored for your audience.</p>
                </div>

                <div className="flex items-center gap-4 bg-[#1a1a24] p-2 rounded-xl border border-white/5">
                    <select
                        value={days}
                        onChange={(e) => setDays(Number(e.target.value))}
                        className="bg-[#0f0f16] text-white px-4 py-2 rounded-lg border border-white/5 focus:outline-none focus:border-blue-500 text-sm"
                    >
                        <option value={3}>3 Ideas</option>
                        <option value={5}>5 Ideas</option>
                        <option value={7}>7 Ideas</option>
                    </select>
                    <button
                        onClick={fetchPlan}
                        disabled={loading}
                        className="p-2hover:bg-white/5 rounded-lg text-neutral-400 hover:text-white transition-colors"
                        title="Refresh Plan"
                    >
                        <RefreshCw className={`w-5 h-5 ${loading ? "animate-spin" : ""}`} />
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6">
                {loading ? (
                    <div className="py-20 text-center">
                        <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" />
                        <p className="text-neutral-500">Curating viral trends...</p>
                    </div>
                ) : (
                    plan.map((item, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="bg-[#1a1a24] border border-white/5 rounded-2xl p-6 shadow-xl hover:border-blue-500/20 transition-all group"
                        >
                            <div className="flex flex-col md:flex-row gap-6">
                                {/* Status/Time Column */}
                                <div className="md:w-48 shrink-0 flex flex-col justify-between">
                                    <div>
                                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-xs font-semibold mb-3">
                                            <Calendar className="w-3 h-3" />
                                            Slot {item.slot}
                                        </div>
                                        <h4 className="text-lg font-bold text-white capitalize mb-1">{item.category}</h4>
                                        <p className="text-neutral-500 text-sm">Post at {item.best_time}</p>
                                    </div>
                                </div>

                                {/* Content Column */}
                                <div className="flex-1 space-y-4">
                                    <div className="bg-[#0f0f16] rounded-xl p-4 border border-white/5 group-hover:border-blue-500/10 transition-colors">
                                        <p className="text-neutral-300 leading-relaxed font-medium">"{item.prompt}"</p>
                                        <div className="mt-3 flex justify-end">
                                            <button
                                                onClick={() => copyToClipboard(item.prompt, i)}
                                                className="text-xs flex items-center gap-1.5 text-neutral-500 hover:text-white transition-colors"
                                            >
                                                {copiedIndex === i ? (
                                                    <><Check className="w-3 h-3 text-emerald-400" /> Copied</>
                                                ) : (
                                                    <><Copy className="w-3 h-3" /> Copy Prompt</>
                                                )}
                                            </button>
                                        </div>
                                    </div>

                                    <div className="flex flex-wrap gap-2">
                                        {item.hashtags.map((tag, t) => (
                                            <span key={t} className="text-xs text-blue-400/80 bg-blue-500/5 px-2 py-1 rounded-md border border-blue-500/10 flex items-center gap-1">
                                                <Hash className="w-2.5 h-2.5" />
                                                {tag.replace('#', '')}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))
                )}
            </div>
        </div>
    );
}

