import { useState, useEffect } from 'react';
import { BarChart3, Youtube, ExternalLink, Server, Cpu, HardDrive, RefreshCw } from 'lucide-react';

const API_URL = "http://localhost:8002";

export function AdminDashboard() {
    const [activeTab, setActiveTab] = useState("overview");
    const [systemStatus, setSystemStatus] = useState<any>(null);
    const [healthStatus, setHealthStatus] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchSystemStatus();
    }, []);

    const fetchSystemStatus = async () => {
        setLoading(true);
        try {
            const [healthRes, systemRes] = await Promise.all([
                fetch(`${API_URL}/health`).then(r => r.json()).catch(() => null),
                fetch(`${API_URL}/system/status`).then(r => r.json()).catch(() => null)
            ]);
            setHealthStatus(healthRes);
            setSystemStatus(systemRes);
        } catch (e) {
            console.error("Failed to fetch status:", e);
        } finally {
            setLoading(false);
        }
    };

    const tabs = [
        { id: "overview", label: "Overview", icon: <BarChart3 className="w-4 h-4" /> },
        { id: "system", label: "System", icon: <Server className="w-4 h-4" /> },
        { id: "youtube", label: "YouTube", icon: <Youtube className="w-4 h-4" /> },
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-2">
                        Admin Dashboard
                    </h2>
                    <p className="text-neutral-400">System status and configuration.</p>
                </div>
                <button 
                    onClick={fetchSystemStatus}
                    disabled={loading}
                    className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 rounded-xl text-neutral-300 transition-colors"
                >
                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    Refresh
                </button>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 overflow-x-auto border-b border-white/10 pb-1 mb-6">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-4 py-3 flex items-center gap-2 text-sm font-medium border-b-2 transition-all whitespace-nowrap ${activeTab === tab.id
                            ? "border-cyan-500 text-cyan-400"
                            : "border-transparent text-neutral-400 hover:text-white"
                            }`}
                    >
                        {tab.icon}
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Content */}
            <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6 min-h-[400px]">
                {activeTab === "overview" && <OverviewTab health={healthStatus} system={systemStatus} />}
                {activeTab === "system" && <SystemTab system={systemStatus} />}
                {activeTab === "youtube" && <YouTubeTab />}
            </div>
        </div>
    );
}

// Overview Tab
function OverviewTab({ health, system }: any) {
    return (
        <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white mb-4">System Overview</h3>
            
            {/* Health Status */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard 
                    title="API Status" 
                    value={health?.status === "healthy" ? "Online" : "Offline"} 
                    color={health?.status === "healthy" ? "emerald" : "red"} 
                />
                <StatCard 
                    title="OpenAI" 
                    value={health?.services?.openai === "configured" ? "Connected" : "Not Set"} 
                    color={health?.services?.openai === "configured" ? "emerald" : "red"} 
                />
                <StatCard 
                    title="YouTube" 
                    value={health?.services?.youtube === "configured" ? "Connected" : "Not Set"} 
                    color={health?.services?.youtube === "configured" ? "emerald" : "red"} 
                />
                <StatCard 
                    title="Pexels" 
                    value={health?.services?.pexels === "configured" ? "Connected" : "Not Set"} 
                    color={health?.services?.pexels === "configured" ? "emerald" : "red"} 
                />
            </div>

            {/* System Resources */}
            {system && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                    <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                        <div className="flex items-center gap-3 mb-3">
                            <Cpu className="w-5 h-5 text-blue-400" />
                            <span className="text-neutral-400">CPU Usage</span>
                        </div>
                        <div className="text-2xl font-bold text-white">{system.cpu_percent?.toFixed(1)}%</div>
                    </div>
                    <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                        <div className="flex items-center gap-3 mb-3">
                            <Server className="w-5 h-5 text-purple-400" />
                            <span className="text-neutral-400">Memory</span>
                        </div>
                        <div className="text-2xl font-bold text-white">{system.memory_percent?.toFixed(1)}%</div>
                    </div>
                    <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                        <div className="flex items-center gap-3 mb-3">
                            <HardDrive className="w-5 h-5 text-emerald-400" />
                            <span className="text-neutral-400">Disk</span>
                        </div>
                        <div className="text-2xl font-bold text-white">{system.disk_percent?.toFixed(1)}%</div>
                    </div>
                </div>
            )}
        </div>
    );
}

// System Tab
function SystemTab({ system }: any) {
    if (!system) return <div className="text-neutral-400 text-center py-12">Loading system info...</div>;
    
    return (
        <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white mb-4">System Resources</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                    <h4 className="text-lg font-medium text-white mb-4">Resource Usage</h4>
                    <div className="space-y-4">
                        <ResourceBar label="CPU" value={system.cpu_percent} color="blue" />
                        <ResourceBar label="Memory" value={system.memory_percent} color="purple" />
                        <ResourceBar label="Disk" value={system.disk_percent} color="emerald" />
                    </div>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                    <h4 className="text-lg font-medium text-white mb-4">Server Info</h4>
                    <div className="space-y-3 text-sm">
                        <div className="flex justify-between">
                            <span className="text-neutral-400">API Port</span>
                            <span className="text-white">8002</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-neutral-400">Status</span>
                            <span className="text-emerald-400">Running</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function ResourceBar({ label, value, color }: { label: string; value: number; color: string }) {
    const colorClasses: any = {
        blue: 'bg-blue-500',
        purple: 'bg-purple-500',
        emerald: 'bg-emerald-500',
    };
    return (
        <div>
            <div className="flex justify-between text-sm mb-1">
                <span className="text-neutral-400">{label}</span>
                <span className="text-white">{value?.toFixed(1)}%</span>
            </div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                <div className={`h-full ${colorClasses[color]} rounded-full transition-all`} style={{ width: `${value}%` }} />
            </div>
        </div>
    );
}

function YouTubeTab() {
    return (
        <div className="text-center py-12 text-neutral-400">
            <Youtube className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <h3 className="text-xl font-semibold text-white mb-2">YouTube Control Center</h3>
            <p>YouTube management features coming soon.</p>

            <div className="flex justify-center mt-6 gap-6">
                <a
                    href="https://studio.youtube.com/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-purple-400 hover:text-purple-300 transition-colors bg-purple-500/10 px-4 py-2 rounded-xl"
                >
                    <BarChart3 className="w-4 h-4" />
                    Open Studio
                </a>
                <a
                    href="https://www.youtube.com/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-red-500 hover:text-red-400 transition-colors bg-red-500/10 px-4 py-2 rounded-xl"
                >
                    <ExternalLink className="w-4 h-4" />
                    View Channel
                </a>
            </div>
        </div>
    );
}

function StatCard({ title, value, color }: { title: string; value: string; color: string }) {
    const colorClasses: any = {
        purple: 'bg-purple-500/10 border-purple-500/30',
        red: 'bg-red-500/10 border-red-500/30',
        blue: 'bg-blue-500/10 border-blue-500/30',
        emerald: 'bg-emerald-500/10 border-emerald-500/30',
    };
    const textClasses: any = {
        emerald: 'text-emerald-400',
        red: 'text-red-400',
    };
    return (
        <div className={`${colorClasses[color]} border rounded-xl p-4`}>
            <div className="text-sm text-neutral-400 mb-2">{title}</div>
            <div className={`text-xl font-bold ${textClasses[color] || 'text-white'}`}>{value}</div>
        </div>
    );
}
