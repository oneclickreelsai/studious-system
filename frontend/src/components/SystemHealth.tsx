import { useState, useEffect } from "react";
import { Activity, CheckCircle, XCircle, AlertCircle } from "lucide-react";

import { API_URL } from '../config/api';

export function SystemHealth() {
    const [status, setStatus] = useState<"loading" | "healthy" | "degraded" | "offline">("loading");

    useEffect(() => {
        checkHealth();
        const interval = setInterval(checkHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    const checkHealth = async () => {
        try {
            const res = await fetch(`${API_URL}/health`, {
                method: "GET",
                signal: AbortSignal.timeout(5000)
            });
            if (res.ok) {
                const data = await res.json();
                setStatus(data.status === "healthy" ? "healthy" : "degraded");
            } else {
                setStatus("degraded");
            }
        } catch {
            setStatus("offline");
        }
    };

    const statusConfig = {
        loading: { icon: Activity, color: "text-neutral-400", bg: "bg-neutral-500/10", label: "Checking..." },
        healthy: { icon: CheckCircle, color: "text-green-400", bg: "bg-green-500/10", label: "All Systems Go" },
        degraded: { icon: AlertCircle, color: "text-yellow-400", bg: "bg-yellow-500/10", label: "Degraded" },
        offline: { icon: XCircle, color: "text-red-400", bg: "bg-red-500/10", label: "Offline" }
    };

    const config = statusConfig[status];
    const Icon = config.icon;

    return (
        <button
            onClick={checkHealth}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${config.bg} ${config.color} text-xs font-medium transition-all hover:opacity-80`}
        >
            <Icon className={`w-3.5 h-3.5 ${status === "loading" ? "animate-spin" : ""}`} />
            <span className="hidden sm:inline">{config.label}</span>
        </button>
    );
}

