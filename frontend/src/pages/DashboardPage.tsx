
import { motion } from "framer-motion";
import { Card } from "../components/Card";
import { Wand2, Newspaper, Bot, Copy, Music, Calendar, Activity, CheckCircle, XCircle, Youtube, Cloud } from "lucide-react";
import banner from "../assets/banner.png";

interface StatsType {
    status?: string;
    services?: {
        openai?: string;
        youtube?: string;
    };
}

interface DashboardPageProps {
    onNavigate: (view: string) => void;
    stats: StatsType | null;
}

export function DashboardPage({ onNavigate, stats }: DashboardPageProps) {
    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const item = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0 }
    };

    return (
        <div className="space-y-12">
            {/* Hero Image - Clean */}
            <div className="relative w-full rounded-3xl overflow-hidden shadow-2xl shadow-cyan-900/10 group z-10 border border-white/5">
                <img
                    src={banner}
                    alt="OneClick Reels AI"
                    className="w-full h-auto object-cover max-h-[350px]"
                />
            </div>

            {/* Welcome Text Section */}
            <div className="text-center pb-2 relative">
                <h1 className="text-3xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-cyan-100 to-neutral-400 mb-2 tracking-tight">
                    Welcome back, Creator.
                </h1>
                <p className="text-neutral-400 text-lg md:text-xl font-light">
                    Ready to generate your next <span className="text-cyan-400 font-normal">viral hit</span>?
                </p>
            </div>

            <motion.div
                variants={container}
                initial="hidden"
                animate="show"
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
            >
                <motion.div variants={item}>
                    <Card
                        icon={<Wand2 className="w-6 h-6 text-purple-400" />}
                        title="One-Click Magic"
                        desc="Instant viral reels from a single keyword."
                        color="group-hover:border-purple-500/50"
                        iconColor="bg-purple-500/10 text-purple-400"
                        onClick={() => onNavigate("one-click")}
                    />
                </motion.div>
                <motion.div variants={item}>
                    <Card
                        icon={<Newspaper className="w-6 h-6 text-orange-400" />}
                        title="News Generator"
                        desc="Fetch trending news & create content."
                        color="group-hover:border-orange-500/50"
                        iconColor="bg-orange-500/10 text-orange-400"
                        onClick={() => onNavigate("news")}
                    />
                </motion.div>
                <motion.div variants={item}>
                    <Card
                        icon={<Bot className="w-6 h-6 text-blue-400" />}
                        title="Meta AI Videos"
                        desc="Download high-quality AI videos."
                        color="group-hover:border-blue-500/50"
                        iconColor="bg-blue-500/10 text-blue-400"
                        onClick={() => onNavigate("meta-dl")}
                    />
                </motion.div>
                <motion.div variants={item}>
                    <Card
                        icon={<Copy className="w-6 h-6 text-cyan-400" />}
                        title="Script Studio"
                        desc="Turn text scripts into videos."
                        color="group-hover:border-cyan-500/50"
                        iconColor="bg-cyan-500/10 text-cyan-400"
                        onClick={() => onNavigate("script")}
                    />
                </motion.div>
                <motion.div variants={item}>
                    <Card
                        icon={<Music className="w-6 h-6 text-fuchsia-400" />}
                        title="Audio Studio"
                        desc="Add music to mute videos."
                        color="group-hover:border-fuchsia-500/50"
                        iconColor="bg-fuchsia-500/10 text-fuchsia-400"
                        onClick={() => onNavigate("audio-studio")}
                    />
                </motion.div>
                <motion.div variants={item}>
                    <Card
                        icon={<Calendar className="w-6 h-6 text-green-400" />}
                        title="Content Plan"
                        desc="Daily viral content ideas."
                        color="group-hover:border-green-500/50"
                        iconColor="bg-green-500/10 text-green-400"
                        onClick={() => onNavigate("content-plan")}
                    />
                </motion.div>
                <motion.div variants={item}>
                    <Card
                        icon={<Cloud className="w-6 h-6 text-sky-400" />}
                        title="Google Drive"
                        desc="Backup & sync to cloud."
                        color="group-hover:border-sky-500/50"
                        iconColor="bg-sky-500/10 text-sky-400"
                        onClick={() => onNavigate("google-drive")}
                    />
                </motion.div>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <StatusCard
                    title="API Status"
                    value={stats?.status === "healthy" ? "Online" : "Offline"}
                    icon={<Activity className="w-6 h-6" />}
                    color="cyan"
                    isOnline={stats?.status === "healthy"}
                />
                <StatusCard
                    title="OpenAI"
                    value={stats?.services?.openai === "configured" ? "Connected" : "Not Set"}
                    icon={<Wand2 className="w-6 h-6" />}
                    color="purple"
                    isOnline={stats?.services?.openai === "configured"}
                />
                <StatusCard
                    title="YouTube"
                    value={stats?.services?.youtube === "configured" ? "Connected" : "Not Set"}
                    icon={<Youtube className="w-6 h-6" />}
                    color="red"
                    isOnline={stats?.services?.youtube === "configured"}
                />
            </div>
        </div>
    );
}

interface StatusCardProps {
    title: string;
    value: string;
    icon: React.ReactNode;
    color: string;
    isOnline: boolean;
}

function StatusCard({ title, value, icon, color, isOnline }: StatusCardProps) {
    // Dynamic color classes need to be safelisted or full strings used.
    // Simplifying for Tailwind JIT: use generic styles with conditional borders/text.

    let colorClass = "text-neutral-400 bg-neutral-500/10";
    if (color === "cyan") colorClass = "text-cyan-400 bg-cyan-500/10";
    if (color === "purple") colorClass = "text-purple-400 bg-purple-500/10";
    if (color === "red") colorClass = "text-red-400 bg-red-500/10";

    return (
        <div className="bg-[#13131c] border border-white/5 p-6 rounded-2xl flex items-center justify-between hover:border-white/10 transition-colors">
            <div>
                <p className="text-neutral-500 text-sm font-medium mb-1">{title}</p>
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    {isOnline ? <CheckCircle className="w-5 h-5 text-green-400" /> : <XCircle className="w-5 h-5 text-red-400" />}
                    {value}
                </h3>
            </div>
            <div className={`w-12 h-12 rounded-full flex items-center justify-center ${colorClass}`}>
                {icon}
            </div>
        </div>
    );
}

