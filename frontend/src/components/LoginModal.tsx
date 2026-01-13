
import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, User, Loader2 } from 'lucide-react';
import logo from '../assets/logo.png';

interface LoginModalProps {
    onClose: () => void;
    onLogin: (u: string, p: string) => Promise<boolean>;
}

export function LoginModal({ onClose, onLogin }: LoginModalProps) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async () => {
        if (!username.trim() || !password.trim()) {
            setError("Please enter username and password");
            return;
        }

        setLoading(true);
        setError("");

        const success = await onLogin(username, password);

        if (!success) {
            setError("Invalid username or password");
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleSubmit();
        }
    };

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
                className="bg-neutral-900 border border-white/10 rounded-3xl p-8 max-w-md w-full"
            >
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <img src={logo} alt="Logo" className="h-14 w-auto object-contain drop-shadow-[0_0_5px_rgba(255,255,255,0.7)]" />
                        <h2 className="text-3xl font-bold bg-gradient-to-r from-green-400 to-cyan-500 bg-clip-text text-transparent">
                            Admin Login
                        </h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/5 rounded-full transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-neutral-300 mb-2">
                            Username
                        </label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Enter username"
                            autoFocus
                            className="w-full bg-neutral-800/50 border border-white/10 rounded-xl p-4 text-white placeholder-neutral-500 focus:border-green-500/50 focus:outline-none focus:ring-2 focus:ring-green-500/20 transition-all"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-neutral-300 mb-2">
                            Password
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Enter password"
                            className="w-full bg-neutral-800/50 border border-white/10 rounded-xl p-4 text-white placeholder-neutral-500 focus:border-green-500/50 focus:outline-none focus:ring-2 focus:ring-green-500/20 transition-all"
                        />
                    </div>

                    {error && (
                        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <button
                        onClick={handleSubmit}
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-green-500 to-cyan-500 hover:from-green-600 hover:to-cyan-600 text-white font-medium py-4 rounded-xl transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Logging in...
                            </>
                        ) : (
                            <>
                                <User className="w-5 h-5" />
                                Login
                            </>
                        )}
                    </button>

                    <div className="text-center text-xs text-neutral-500 mt-4">
                        Default credentials: admin / admin123
                    </div>
                </div>
            </motion.div>
        </motion.div>
    );
}

