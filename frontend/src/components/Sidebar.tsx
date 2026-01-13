
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    LayoutDashboard,
    Zap,
    FileText,
    Newspaper,
    Share2,
    Youtube,
    Facebook,
    Instagram,
    Bot,
    Settings,
    LogOut,
    ChevronDown,
    ChevronRight,
    X,
    BarChart3,
    Music,
    Calendar,
    Activity,
    FolderOpen,
    Cloud
} from "lucide-react";
import clsx from "clsx";
import logo from "../assets/logo.png";

interface SidebarProps {
    activeView: string;
    setActiveView: (view: string) => void;
    isOpen: boolean;
    setIsOpen: (isOpen: boolean) => void;
    onLogout: () => void;
}

export function Sidebar({ activeView, setActiveView, isOpen, setIsOpen, onLogout }: SidebarProps) {
    const [socialOpen, setSocialOpen] = useState(true);

    const menuItems = [
        { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
        { id: "one-click", label: "Create Magic", icon: Zap },
        { id: "script", label: "Script Studio", icon: FileText },
        { id: "news", label: "Newsroom", icon: Newspaper },
        { id: "upload", label: "Upload Video", icon: Share2 },
        { id: "audio-studio", label: "Audio Studio", icon: Music },
        { id: "content-plan", label: "Content Plan", icon: Calendar },
        { id: "analytics", label: "Analytics", icon: BarChart3 },
        { id: "assets", label: "Asset Manager", icon: FolderOpen },
        { id: "google-drive", label: "Google Drive", icon: Cloud },
        { id: "health", label: "System Health", icon: Activity },
    ];

    const socialItems = [
        { id: "facebook", label: "Facebook Poster", icon: Facebook },
        { id: "fb-reel", label: "Facebook Reel Upload", icon: Facebook },
        { id: "instagram", label: "Instagram Reel Upload", icon: Instagram },
        { id: "youtube-dl", label: "YouTube Downloader", icon: Youtube },
        { id: "meta-dl", label: "Meta AI Downloader", icon: Bot },
    ];

    const handleNavClick = (view: string) => {
        setActiveView(view);
        if (window.innerWidth < 1024) setIsOpen(false); // Auto-close on mobile
    };

    return (
        <>
            {/* Mobile Backdrop */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setIsOpen(false)}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
                    />
                )}
            </AnimatePresence>

            {/* Sidebar Container */}
            <motion.aside
                className={clsx(
                    "fixed top-0 left-0 bottom-0 z-50 w-72 bg-[#0f0f16]/95 border-r border-white/5 backdrop-blur-xl flex flex-col transition-all duration-300",
                    isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
                )}
            >
                {/* Logo Header */}
                <div className="h-32 flex items-center justify-center border-b border-white/5 p-2 bg-gradient-to-b from-white/5 to-transparent">
                    <img src={logo} alt="OneClick Reels" className="w-full h-full object-contain drop-shadow-2xl" />
                    <button onClick={() => setIsOpen(false)} className="absolute right-4 top-4 lg:hidden text-neutral-400">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Navigation */}
                <nav className="flex-1 overflow-y-auto py-6 px-4 space-y-1 mt-2">
                    <div className="px-2 mb-2 text-xs font-bold text-neutral-500 uppercase tracking-widest">Main</div>

                    {menuItems.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => handleNavClick(item.id)}
                            className={clsx(
                                "w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
                                activeView === item.id
                                    ? "bg-gradient-to-r from-cyan-500/10 to-blue-500/10 text-cyan-400 border border-cyan-500/20"
                                    : "text-neutral-400 hover:text-white hover:bg-white/5"
                            )}
                        >
                            <item.icon className={clsx("w-5 h-5", activeView === item.id ? "text-cyan-400" : "text-neutral-500")} />
                            {item.label}
                        </button>
                    ))}

                    <div className="mt-8 px-2 mb-2 text-xs font-bold text-neutral-500 uppercase tracking-widest">Tools</div>

                    {/* Social Tools Dropdown */}
                    <div className="space-y-1">
                        <button
                            onClick={() => setSocialOpen(!socialOpen)}
                            className="w-full flex items-center justify-between px-4 py-2 text-sm font-medium text-neutral-400 hover:text-white transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <Share2 className="w-5 h-5 text-neutral-500" />
                                Social Tools
                            </div>
                            {socialOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                        </button>

                        <AnimatePresence>
                            {socialOpen && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: "auto", opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    className="overflow-hidden space-y-1 py-1"
                                >
                                    {socialItems.map((item) => (
                                        <button
                                            key={item.id}
                                            onClick={() => handleNavClick(item.id)}
                                            className={clsx(
                                                "w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 pl-12",
                                                activeView === item.id
                                                    ? "text-cyan-400 bg-white/5"
                                                    : "text-neutral-400 hover:text-white hover:bg-white/5"
                                            )}
                                        >
                                            <item.icon className="w-4 h-4" />
                                            {item.label}
                                        </button>
                                    ))}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </nav>

                {/* Footer Actions */}
                <div className="p-4 border-t border-white/5 space-y-2">
                    <button
                        onClick={() => handleNavClick("settings")}
                        className={clsx(
                            "w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
                            activeView === "settings"
                                ? "bg-white/5 text-white"
                                : "text-neutral-400 hover:text-white hover:bg-white/5"
                        )}
                    >
                        <Settings className="w-5 h-5" /> Settings
                    </button>
                    <button
                        onClick={onLogout}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-all duration-200"
                    >
                        <LogOut className="w-5 h-5" /> Logout
                    </button>
                </div>
            </motion.aside>
        </>
    );
}

