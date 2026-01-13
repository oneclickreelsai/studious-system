import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Video, Upload, Eye, Clock, RefreshCw, Calendar } from 'lucide-react';

const API_URL = "http://localhost:8002";

interface AnalyticsData {
    total_videos: number;
    total_uploads: number;
    total_views: number;
    recent_uploads: Array<{
        id: string;
        title: string;
        platform: string;
        created_at: string;
        views?: number;
    }>;
    daily_stats: Array<{
        date: string;
        videos: number;
        uploads: number;
    }>;
}

export function AnalyticsPage() {
    const [data, setData] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [days, setDays] = useState(30);

    useEffect(() => {
        fetchAnalytics();
    }, [days]);

    const fetchAnalytics = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${API_URL}/api/analytics?days=${days}`);
            if (res.ok) {
                const result = await res.json();
                setData(result);
            } else {
                // If no data, use mock data for display
                setData({
                    total_videos: 0,
                    total_uploads: 0,
                    total_views: 0,
                    recent_uploads: [],
                    daily_stats: []
                });
            }
        } catch (err) {
            console.error('Failed to fetch analytics:', err);
            setData({
                total_videos: 0,
                total_uploads: 0,
                total_views: 0,
                recent_uploads: [],
                daily_stats: []
            });
        } finally {
            setLoading(false);
        }
    };

    const StatCard = ({
        icon: Icon,
        label,
        value,
        trend,
        color
    }: {
        icon: React.ElementType;
        label: string;
        value: number | string;
        trend?: string;
        color: string;
    }) => (
        <div className="bg-[#1a1a2e] border border-white/5 rounded-2xl p-6">
            <div className="flex items-start justify-between">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
                    <Icon className="w-6 h-6 text-white" />
                </div>
                {trend && (
                    <span className="flex items-center gap-1 text-green-400 text-sm">
                        <TrendingUp className="w-4 h-4" />
                        {trend}
                    </span>
                )}
            </div>
            <div className="mt-4">
                <p className="text-3xl font-bold text-white">{value}</p>
                <p className="text-neutral-500 text-sm mt-1">{label}</p>
            </div>
        </div>
    );

    const SimpleBarChart = ({ data }: { data: Array<{ date: string; videos: number; uploads: number }> }) => {
        if (!data || data.length === 0) {
            return (
                <div className="h-48 flex items-center justify-center text-neutral-500">
                    No data available
                </div>
            );
        }

        const maxValue = Math.max(...data.map(d => Math.max(d.videos, d.uploads)), 1);

        return (
            <div className="h-48 flex items-end gap-2">
                {data.slice(-14).map((item, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center gap-1">
                        <div className="w-full flex gap-0.5 items-end justify-center" style={{ height: '140px' }}>
                            <div
                                className="w-2 bg-gradient-to-t from-purple-600 to-purple-400 rounded-t"
                                style={{ height: `${(item.videos / maxValue) * 100}%`, minHeight: item.videos > 0 ? '4px' : '0' }}
                            />
                            <div
                                className="w-2 bg-gradient-to-t from-cyan-600 to-cyan-400 rounded-t"
                                style={{ height: `${(item.uploads / maxValue) * 100}%`, minHeight: item.uploads > 0 ? '4px' : '0' }}
                            />
                        </div>
                        <span className="text-[10px] text-neutral-600 mt-1">
                            {new Date(item.date).getDate()}
                        </span>
                    </div>
                ))}
            </div>
        );
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <RefreshCw className="w-8 h-8 text-purple-400 animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-8 max-w-6xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                        <BarChart3 className="w-8 h-8 text-purple-400" />
                        Analytics
                    </h1>
                    <p className="text-neutral-400 mt-1">Track your content performance</p>
                </div>
                <div className="flex items-center gap-3">
                    <select
                        value={days}
                        onChange={(e) => setDays(Number(e.target.value))}
                        className="bg-[#1a1a2e] border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
                    >
                        <option value={7}>Last 7 days</option>
                        <option value={30}>Last 30 days</option>
                        <option value={90}>Last 90 days</option>
                    </select>
                    <button
                        onClick={fetchAnalytics}
                        className="px-4 py-2 bg-[#1a1a2e] border border-white/10 rounded-lg text-white hover:bg-[#252540] transition flex items-center gap-2"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    icon={Video}
                    label="Videos Created"
                    value={data?.total_videos || 0}
                    color="bg-gradient-to-br from-purple-500 to-purple-700"
                />
                <StatCard
                    icon={Upload}
                    label="Total Uploads"
                    value={data?.total_uploads || 0}
                    color="bg-gradient-to-br from-cyan-500 to-cyan-700"
                />
                <StatCard
                    icon={Eye}
                    label="Total Views"
                    value={data?.total_views || 0}
                    color="bg-gradient-to-br from-green-500 to-green-700"
                />
                <StatCard
                    icon={Calendar}
                    label="Period"
                    value={`${days} days`}
                    color="bg-gradient-to-br from-orange-500 to-orange-700"
                />
            </div>

            {/* Chart */}
            <div className="bg-[#1a1a2e] border border-white/5 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-lg font-semibold text-white">Activity Overview</h2>
                    <div className="flex items-center gap-4 text-sm">
                        <span className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded bg-purple-500" />
                            <span className="text-neutral-400">Videos</span>
                        </span>
                        <span className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded bg-cyan-500" />
                            <span className="text-neutral-400">Uploads</span>
                        </span>
                    </div>
                </div>
                <SimpleBarChart data={data?.daily_stats || []} />
            </div>

            {/* Recent Uploads Table */}
            <div className="bg-[#1a1a2e] border border-white/5 rounded-2xl overflow-hidden">
                <div className="p-6 border-b border-white/5">
                    <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                        <Clock className="w-5 h-5 text-neutral-500" />
                        Recent Uploads
                    </h2>
                </div>
                <div className="overflow-x-auto">
                    {data?.recent_uploads && data.recent_uploads.length > 0 ? (
                        <table className="w-full">
                            <thead>
                                <tr className="text-left text-neutral-500 text-sm border-b border-white/5">
                                    <th className="px-6 py-3">Title</th>
                                    <th className="px-6 py-3">Platform</th>
                                    <th className="px-6 py-3">Date</th>
                                    <th className="px-6 py-3">Views</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.recent_uploads.map((upload, i) => (
                                    <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                                        <td className="px-6 py-4 text-white">{upload.title}</td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${upload.platform === 'youtube' ? 'bg-red-500/20 text-red-400' :
                                                    upload.platform === 'facebook' ? 'bg-blue-500/20 text-blue-400' :
                                                        'bg-neutral-500/20 text-neutral-400'
                                                }`}>
                                                {upload.platform}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-neutral-400">
                                            {new Date(upload.created_at).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 text-neutral-400">{upload.views || '-'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <div className="p-12 text-center text-neutral-500">
                            <Video className="w-12 h-12 mx-auto mb-4 opacity-30" />
                            <p>No uploads yet</p>
                            <p className="text-sm mt-1">Start creating content to see analytics</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
