
import { useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { SystemHealth } from "./components/SystemHealth";
import { Menu, Bell, Search, User } from "lucide-react";
import { motion } from "framer-motion";

interface LayoutProps {
    children: React.ReactNode;
    activeView: string;
    setActiveView: (view: string) => void;
    isAuthenticated: boolean;
    onLogout: () => void;
}

export function Layout({ children, activeView, setActiveView, isAuthenticated, onLogout }: LayoutProps) {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="min-h-screen bg-[#0a0a0f] text-white flex overflow-hidden">

            {/* Sidebar */}
            <Sidebar
                activeView={activeView}
                setActiveView={setActiveView}
                isOpen={sidebarOpen}
                setIsOpen={setSidebarOpen}
                onLogout={onLogout}
            />

            {/* Main Content Wrapper */}
            <div className="flex-1 flex flex-col min-w-0 lg:pl-72 transition-all duration-300">

                {/* Top Header */}
                <header className="h-20 border-b border-white/5 bg-[#0a0a0f]/80 backdrop-blur-md sticky top-0 z-30 px-6 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button onClick={() => setSidebarOpen(true)} className="lg:hidden p-2 -ml-2 text-neutral-400 hover:text-white">
                            <Menu className="w-6 h-6" />
                        </button>
                        <div className="hidden md:flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/5 w-64 focus-within:border-cyan-500/50 focus-within:ring-1 focus-within:ring-cyan-500/50 transition-all">
                            <Search className="w-4 h-4 text-neutral-500" />
                            <input
                                type="text"
                                placeholder="Search tools..."
                                className="bg-transparent border-none outline-none text-sm w-full placeholder-neutral-600 font-medium"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-4 md:gap-6">
                        <SystemHealth />

                        <button className="relative text-neutral-400 hover:text-white transition-colors">
                            <Bell className="w-5 h-5" />
                            <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full ring-2 ring-[#0a0a0f]" />
                        </button>

                        <div className="w-px h-8 bg-white/10 mx-2 hidden md:block" />

                        {isAuthenticated ? (
                            <button className="flex items-center gap-3 group">
                                <div className="text-right hidden md:block">
                                    <p className="text-sm font-semibold text-white group-hover:text-cyan-400 transition-colors">Admin User</p>
                                    <p className="text-xs text-neutral-500">Pro Plan</p>
                                </div>
                                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-500 to-cyan-500 p-[1px]">
                                    <div className="w-full h-full rounded-[11px] bg-[#111] flex items-center justify-center overflow-hidden">
                                        {/* Placeholder Avatar */}
                                        <User className="w-5 h-5 text-white" />
                                    </div>
                                </div>
                            </button>
                        ) : (
                            <button className="px-5 py-2 rounded-lg bg-white text-black font-semibold text-sm hover:bg-neutral-200 transition-colors">
                                Login
                            </button>
                        )}
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto overflow-x-hidden p-6 md:p-10 relative scroll-smooth">

                    {/* Background Ambient Glow */}
                    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
                        <div className="absolute top-[-10%] left-[10%] w-[500px] h-[500px] bg-purple-600/5 rounded-full blur-[120px] mix-blend-screen" />
                        <div className="absolute bottom-[-10%] right-[5%] w-[600px] h-[600px] bg-cyan-600/5 rounded-full blur-[120px] mix-blend-screen" />
                        <div className="absolute top-[40%] left-[60%] w-[300px] h-[300px] bg-blue-600/5 rounded-full blur-[100px] mix-blend-screen" />
                    </div>

                    <motion.div
                        key={activeView}
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.3, ease: "easeOut" }}
                        className="relative z-10 max-w-7xl mx-auto"
                    >
                        {children}
                    </motion.div>

                </main>
            </div>
        </div>
    );
}

