import { useState, useEffect } from "react";
import { Activity, Server, CheckCircle, XCircle, AlertTriangle, RefreshCw, Cpu, Youtube, Facebook, Image as ImageIcon } from "lucide-react";

interface HealthStatus {
    service: string;
    status: "healthy" | "unhealthy";
    details: string;
    error?: string;
    response_time?: number;
}

interface HealthResponse {
    overall_status: "healthy" | "degraded" | "unhealthy";
    healthy_services: number;
    total_services: number;
    timestamp: number;
    from_cache: boolean;
    services: Record<string, HealthStatus>;
}

const API_URL = "http://localhost:8002";

export function HealthPage() {
    const [data, setData] = useState<HealthResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const fetchHealth = async () => {
        setLoading(true);
        setError("");
        try {
            const res = await fetch(`${API_URL}/api/health`);
            if (!res.ok) throw new Error("Failed to fetch health status");
            const json = await res.json();
            setData(json);
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHealth();
    }, []);

    const getServiceIcon = (name: string) => {
        switch (name) {
            case "openai": return <Cpu className="w-5 h-5 text-green-400" />;
            case "youtube": return <Youtube className="w-5 h-5 text-red-400" />;
            case "facebook": return <Facebook className="w-5 h-5 text-blue-400" />;
            case "pexels":
            case "pixabay": return <ImageIcon className="w-5 h-5 text-purple-400" />;
            default: return <Server className="w-5 h-5 text-neutral-400" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "healthy": return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
            case "unhealthy": return "text-red-400 bg-red-500/10 border-red-500/20";
            default: return "text-yellow-400 bg-yellow-500/10 border-yellow-500/20";
        }
    };

    return (
        <div className="max-w-6xl mx-auto p-6">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                        <Activity className="w-8 h-8 text-emerald-400" />
                        System Health
                    </h2>
                    <p className="text-neutral-400">Monitor external API connections and services</p>
                </div>
                <button
                    onClick={fetchHealth}
                    disabled={loading}
                    className="p-3 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 transition-colors disabled:opacity-50"
                >
                    <RefreshCw className={`w-5 h-5 text-white ${loading ? "animate-spin" : ""}`} />
                </button>
            </div>

            {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-300 mb-6 flex items-center gap-3">
                    <XCircle className="w-5 h-5" />
                    {error}
                </div>
            )}

            {data && (
                <div className="space-y-8">
                    {/* Overall Status Banner */}
                    <div className={`p-6 rounded-2xl border ${data.overall_status === "healthy" ? "bg-emerald-500/10 border-emerald-500/20" :
                            data.overall_status === "degraded" ? "bg-yellow-500/10 border-yellow-500/20" :
                                "bg-red-500/10 border-red-500/20"
                        }`}>
                        <div className="flex items-center gap-4">
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center ${data.overall_status === "healthy" ? "bg-emerald-500/20 text-emerald-400" :
                                    data.overall_status === "degraded" ? "bg-yellow-500/20 text-yellow-400" :
                                        "bg-red-500/20 text-red-400"
                                }`}>
                                {data.overall_status === "healthy" ? <CheckCircle className="w-6 h-6" /> : <AlertTriangle className="w-6 h-6" />}
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-white capitalize">{data.overall_status} System</h3>
                                <p className="text-neutral-400">
                                    {data.healthy_services}/{data.total_services} services operational
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Services Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {Object.entries(data.services).map(([key, service]) => (
                            <div key={key} className={`p-5 rounded-xl border transition-all ${getStatusColor(service.status)}`}>
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-black/20">
                                            {getServiceIcon(key)}
                                        </div>
                                        <h4 className="font-semibold capitalize">{key}</h4>
                                    </div>
                                    <div className={`px-2 py-0.5 rounded-full text-xs font-bold border ${service.status === "healthy" ? "bg-emerald-500/20 border-emerald-500/30 text-emerald-400" : "bg-red-500/20 border-red-500/30 text-red-400"
                                        }`}>
                                        {service.status.toUpperCase()}
                                    </div>
                                </div>

                                <p className="text-sm opacity-80 mb-2">{service.details}</p>
                                {service.error && (
                                    <p className="text-xs font-mono bg-black/20 p-2 rounded text-red-300 break-all">
                                        {service.error}
                                    </p>
                                )}
                                <div className="text-xs opacity-50 mt-2 flex items-center gap-1">
                                    Last check: {new Date(data.timestamp * 1000).toLocaleTimeString()}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
