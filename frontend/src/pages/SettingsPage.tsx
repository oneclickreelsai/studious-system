import { useState, useEffect } from 'react';
import { Settings, RefreshCw, CheckCircle, XCircle, Key, Facebook, Youtube, Cpu, Music, Bot, Loader2 } from 'lucide-react';

const API_URL = "http://localhost:8002";

interface ConfigStatus {
    has_openai_key: boolean;
    has_youtube_credentials: boolean;
    has_facebook_credentials: boolean;
    has_pexels_key: boolean;
    has_pixabay_key: boolean;
    has_perplexity_key: boolean;
    enable_caching: boolean;
    fb_page_id?: string;
}

export function SettingsPage() {
    const [config, setConfig] = useState<ConfigStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [metaLoginLoading, setMetaLoginLoading] = useState(false);
    const [metaLoginStatus, setMetaLoginStatus] = useState<string | null>(null);

    useEffect(() => {
        fetchConfig();
    }, []);

    const fetchConfig = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${API_URL}/api/settings`);
            if (res.ok) {
                const data = await res.json();
                setConfig(data);
            }
        } catch (err) {
            console.error('Failed to fetch config:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleMetaLogin = async () => {
        setMetaLoginLoading(true);
        setMetaLoginStatus(null);

        try {
            const res = await fetch(`${API_URL}/api/meta-login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ timeout: 300 })
            });

            const data = await res.json();

            if (res.ok && data.message) {
                setMetaLoginStatus('success');
            } else {
                setMetaLoginStatus('error');
            }
        } catch (err) {
            console.error('Meta login failed:', err);
            setMetaLoginStatus('error');
        } finally {
            setMetaLoginLoading(false);
        }
    };

    const ConfigItem = ({
        label,
        configured,
        icon: Icon,
        keyName
    }: {
        label: string;
        configured: boolean;
        icon: React.ElementType;
        keyName: string;
    }) => (
        <div className="bg-[#1a1a2e] border border-white/5 rounded-xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${configured ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                    <Icon className={`w-5 h-5 ${configured ? 'text-green-400' : 'text-red-400'}`} />
                </div>
                <div>
                    <p className="font-medium text-white">{label}</p>
                    <p className="text-sm text-neutral-500">{keyName}</p>
                </div>
            </div>
            <div className="flex items-center gap-2">
                {configured ? (
                    <span className="flex items-center gap-1 text-green-400 text-sm">
                        <CheckCircle className="w-4 h-4" /> Configured
                    </span>
                ) : (
                    <span className="flex items-center gap-1 text-red-400 text-sm">
                        <XCircle className="w-4 h-4" /> Missing
                    </span>
                )}
            </div>
        </div>
    );

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <RefreshCw className="w-8 h-8 text-purple-400 animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-8 max-w-4xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                        <Settings className="w-8 h-8 text-purple-400" />
                        Settings
                    </h1>
                    <p className="text-neutral-400 mt-1">Manage your API keys and configuration</p>
                </div>
                <button
                    onClick={fetchConfig}
                    className="px-4 py-2 bg-[#1a1a2e] border border-white/10 rounded-lg text-white hover:bg-[#252540] transition flex items-center gap-2"
                >
                    <RefreshCw className="w-4 h-4" />
                    Refresh
                </button>
            </div>

            {/* AI APIs */}
            <div className="space-y-4">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                    <Cpu className="w-5 h-5 text-cyan-400" />
                    AI Services
                </h2>
                <div className="grid gap-3">
                    <ConfigItem
                        label="OpenAI API"
                        configured={config?.has_openai_key || false}
                        icon={Key}
                        keyName="OPENAI_API_KEY"
                    />
                    <ConfigItem
                        label="Perplexity API"
                        configured={config?.has_perplexity_key || false}
                        icon={Key}
                        keyName="PERPLEXITY_API_KEY"
                    />
                </div>
            </div>

            {/* Social Platforms */}
            <div className="space-y-4">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                    <Facebook className="w-5 h-5 text-blue-400" />
                    Social Platforms
                </h2>
                <div className="grid gap-3">
                    <ConfigItem
                        label="YouTube API"
                        configured={config?.has_youtube_credentials || false}
                        icon={Youtube}
                        keyName="YOUTUBE_CLIENT_ID + Refresh Token"
                    />
                    <div className="bg-[#1a1a2e] border border-white/5 rounded-xl p-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${config?.has_facebook_credentials ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                                    <Facebook className={`w-5 h-5 ${config?.has_facebook_credentials ? 'text-green-400' : 'text-red-400'}`} />
                                </div>
                                <div>
                                    <p className="font-medium text-white">Facebook API</p>
                                    <p className="text-sm text-neutral-500">FB_PAGE_ID + FB_ACCESS_TOKEN</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                {config?.has_facebook_credentials ? (
                                    <span className="flex items-center gap-1 text-green-400 text-sm">
                                        <CheckCircle className="w-4 h-4" /> Configured
                                    </span>
                                ) : (
                                    <span className="flex items-center gap-1 text-red-400 text-sm">
                                        <XCircle className="w-4 h-4" /> Missing
                                    </span>
                                )}
                            </div>
                        </div>
                        {config?.fb_page_id && (
                            <div className="mt-3 pt-3 border-t border-white/5">
                                <p className="text-sm text-neutral-400">
                                    Page ID: <code className="bg-black/30 px-2 py-1 rounded text-purple-400">{config.fb_page_id}</code>
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Media APIs */}
            <div className="space-y-4">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                    <Music className="w-5 h-5 text-fuchsia-400" />
                    Media Services
                </h2>
                <div className="grid gap-3">
                    <ConfigItem
                        label="Pexels API"
                        configured={config?.has_pexels_key || false}
                        icon={Key}
                        keyName="PEXELS_API_KEY"
                    />
                    <ConfigItem
                        label="Pixabay API"
                        configured={config?.has_pixabay_key || false}
                        icon={Key}
                        keyName="PIXABAY_API_KEY"
                    />
                </div>
            </div>

            {/* Actions */}
            <div className="space-y-4">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                    <Bot className="w-5 h-5 text-blue-400" />
                    Actions
                </h2>
                <div className="bg-[#1a1a2e] border border-white/5 rounded-xl p-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                                <Bot className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <p className="font-medium text-white">Meta AI Login</p>
                                <p className="text-sm text-neutral-500">Opens browser to authenticate with Meta AI</p>
                            </div>
                        </div>
                        <button
                            onClick={handleMetaLogin}
                            disabled={metaLoginLoading}
                            className="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg font-medium hover:opacity-90 transition disabled:opacity-50 flex items-center gap-2"
                        >
                            {metaLoginLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                            {metaLoginLoading ? "Opening..." : "Setup Login"}
                        </button>
                    </div>
                    {metaLoginStatus && (
                        <div className={`mt-3 p-3 rounded-lg text-sm ${metaLoginStatus === 'success' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                            {metaLoginStatus === 'success' ? 'Browser opened! Complete login in the browser window.' : 'Failed to start login. Check server logs.'}
                        </div>
                    )}
                </div>
            </div>

            {/* Info Box */}
            <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-4">
                <p className="text-purple-300 text-sm">
                    <strong>💡 Tip:</strong> To update API keys, edit <code className="bg-black/30 px-1 rounded">config.env</code> in the project root and restart the server.
                </p>
            </div>
        </div>
    );
}
