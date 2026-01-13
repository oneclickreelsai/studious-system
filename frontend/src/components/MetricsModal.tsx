
import { motion } from 'framer-motion';
import { X, Activity, Clock, Cpu, HardDrive, Video, Loader2 } from 'lucide-react';

interface MetricsModalProps {
    onClose: () => void;
    metrics: any;
}

export function MetricsModal({ onClose, metrics }: MetricsModalProps) {
    if (!metrics) {
        return (
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6"
                onClick={onClose}
            >
                <div className="text-white">Loading metrics...</div>
            </motion.div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6"
            onClick={onClose}
        >
            <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
                className="bg-neutral-900 border border-white/10 rounded-3xl p-8 max-w-5xl w-full max-h-[90vh] overflow-y-auto"
            >
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent flex items-center gap-3">
                        <Activity className="w-8 h-8 text-cyan-400" />
                        System Metrics
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/5 rounded-full transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                    {/* Uptime */}
                    <MetricCard
                        icon={<Clock className="w-5 h-5 text-blue-400" />}
                        title="Uptime"
                        value={`${metrics.uptime.hours.toFixed(1)}h`}
                        subtitle={`Started: ${new Date(metrics.uptime.start_time).toLocaleTimeString()}`}
                        color="blue"
                    />

                    {/* CPU */}
                    <MetricCard
                        icon={<Cpu className="w-5 h-5 text-purple-400" />}
                        title="CPU Usage"
                        value={`${metrics.system.cpu_percent.toFixed(1)}%`}
                        color="purple"
                    />

                    {/* Memory */}
                    <MetricCard
                        icon={<HardDrive className="w-5 h-5 text-cyan-400" />}
                        title="Memory"
                        value={`${metrics.system.memory.percent.toFixed(1)}%`}
                        subtitle={`${metrics.system.memory.used_mb.toFixed(0)} / ${metrics.system.memory.total_mb.toFixed(0)} MB`}
                        color="cyan"
                    />

                    {/* Disk */}
                    <MetricCard
                        icon={<HardDrive className="w-5 h-5 text-emerald-400" />}
                        title="Disk Space"
                        value={`${metrics.system.disk.percent.toFixed(1)}%`}
                        subtitle={`${metrics.system.disk.free_gb.toFixed(1)} GB free`}
                        color="emerald"
                    />

                    {/* Total Requests */}
                    <MetricCard
                        icon={<Activity className="w-5 h-5 text-orange-400" />}
                        title="Total Requests"
                        value={metrics.requests.total}
                        subtitle={`One-Click: ${metrics.requests.one_click} | Script: ${metrics.requests.script_to_video} | Upload: ${metrics.requests.upload_video}`}
                        color="orange"
                    />

                    {/* Videos Generated */}
                    <MetricCard
                        icon={<Video className="w-5 h-5 text-pink-400" />}
                        title="Videos"
                        value={metrics.videos.generated}
                        subtitle={`${metrics.videos.files_on_disk} files (${metrics.videos.total_size_mb.toFixed(1)} MB)`}
                        color="pink"
                    />
                </div>

                {/* Application Status */}
                <div className="bg-neutral-800/50 border border-white/10 rounded-2xl p-6 mb-4">
                    <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                        <Loader2 className="w-5 h-5 text-cyan-400" />
                        Current Status
                    </h3>
                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <span className="text-neutral-400">State:</span>
                            <span className={`font-semibold ${metrics.application.status === 'idle' ? 'text-emerald-400' :
                                    metrics.application.status === 'running' ? 'text-cyan-400' :
                                        'text-red-400'
                                }`}>
                                {metrics.application.status.toUpperCase()}
                            </span>
                        </div>
                        {metrics.application.current_step && (
                            <div className="flex justify-between">
                                <span className="text-neutral-400">Step:</span>
                                <span className="text-white">{metrics.application.current_step}</span>
                            </div>
                        )}
                        {metrics.application.progress > 0 && (
                            <div>
                                <div className="flex justify-between mb-1">
                                    <span className="text-neutral-400">Progress:</span>
                                    <span className="text-white">{metrics.application.progress}%</span>
                                </div>
                                <div className="w-full bg-neutral-700 rounded-full h-2">
                                    <div
                                        className="bg-cyan-500 h-2 rounded-full transition-all duration-300"
                                        style={{ width: `${metrics.application.progress}%` }}
                                    />
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Environment */}
                <div className="bg-neutral-800/50 border border-white/10 rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-3">Environment</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <EnvStatus label="OpenAI" configured={metrics.environment.openai_configured} />
                        <EnvStatus label="YouTube" configured={metrics.environment.youtube_configured} />
                        <EnvStatus label="Facebook" configured={metrics.environment.facebook_configured} />
                    </div>
                </div>

                {/* Errors */}
                {metrics.errors.total > 0 && (
                    <div className="mt-4 bg-red-500/10 border border-red-500/30 rounded-2xl p-6">
                        <h3 className="text-lg font-semibold text-red-400 mb-2">
                            Errors: {metrics.errors.total}
                        </h3>
                        {metrics.errors.last_error && (
                            <p className="text-sm text-red-300">
                                Last: {metrics.errors.last_error.message}
                                <span className="text-neutral-400 ml-2">
                                    ({new Date(metrics.errors.last_error.timestamp).toLocaleString()})
                                </span>
                            </p>
                        )}
                    </div>
                )}

                <p className="text-xs text-neutral-500 mt-4 text-center">
                    Auto-refreshing every 5 seconds
                </p>
            </motion.div>
        </motion.div>
    );
}

function MetricCard({ icon, title, value, subtitle, color }: any) {
    const colorClasses: any = {
        blue: 'bg-blue-500/10 border-blue-500/30',
        purple: 'bg-purple-500/10 border-purple-500/30',
        cyan: 'bg-cyan-500/10 border-cyan-500/30',
        emerald: 'bg-emerald-500/10 border-emerald-500/30',
        orange: 'bg-orange-500/10 border-orange-500/30',
        pink: 'bg-pink-500/10 border-pink-500/30',
    };

    return (
        <div className={`${colorClasses[color]} border rounded-xl p-4`}>
            <div className="flex items-center gap-2 mb-2">
                {icon}
                <span className="text-sm text-neutral-400">{title}</span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">{value}</div>
            {subtitle && <div className="text-xs text-neutral-500">{subtitle}</div>}
        </div>
    );
}

function EnvStatus({ label, configured }: any) {
    return (
        <div className="flex items-center justify-between bg-neutral-900/50 rounded-lg p-3">
            <span className="text-sm text-neutral-400">{label}</span>
            <span className={`text-xs font-semibold px-2 py-1 rounded ${configured ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                }`}>
                {configured ? '✓ SET' : '✗ NOT SET'}
            </span>
        </div>
    );
}

