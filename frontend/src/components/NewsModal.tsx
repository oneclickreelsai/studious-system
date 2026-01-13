
import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Newspaper, Globe, Cpu, Coins, Trophy } from 'lucide-react';

interface NewsModalProps {
    onClose: () => void;
    onSubmit: (category: string) => void;
}

export function NewsModal({ onClose, onSubmit }: NewsModalProps) {
    const [category, setCategory] = useState("Technology");

    const categories = [
        { id: "Technology", label: "Tech & AI", icon: <Cpu className="w-5 h-5 text-cyan-400" /> },
        { id: "Finance", label: "Crypto & Finance", icon: <Coins className="w-5 h-5 text-yellow-400" /> },
        { id: "World", label: "Global News", icon: <Globe className="w-5 h-5 text-blue-400" /> },
        { id: "Sports", label: "Sports", icon: <Trophy className="w-5 h-5 text-orange-400" /> },
    ];

    const handleSubmit = () => {
        onSubmit(category);
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
                className="bg-neutral-900 border border-white/10 rounded-3xl p-8 max-w-xl w-full"
            >
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-orange-400 to-red-500 bg-clip-text text-transparent flex items-center gap-3">
                        <Newspaper className="w-8 h-8 text-orange-400" />
                        News Generator
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/5 rounded-full transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <p className="text-neutral-400 mb-6">
                    Select a category to automatically fetch the latest viral news, write a script, and generate a video.
                </p>

                <div className="grid grid-cols-2 gap-4 mb-8">
                    {categories.map((cat) => (
                        <button
                            key={cat.id}
                            onClick={() => setCategory(cat.id)}
                            className={`p-4 rounded-xl border transition-all flex flex-col items-center gap-3 ${category === cat.id
                                    ? 'bg-white/10 border-orange-500/50 shadow-lg shadow-orange-500/20'
                                    : 'bg-neutral-800/50 border-white/5 hover:bg-neutral-800 hover:border-white/20'
                                }`}
                        >
                            <div className={`p-3 rounded-full bg-neutral-900 ${category === cat.id ? 'scale-110' : ''} transition-transform`}>
                                {cat.icon}
                            </div>
                            <span className={`font-medium ${category === cat.id ? 'text-white' : 'text-neutral-400'}`}>
                                {cat.label}
                            </span>
                        </button>
                    ))}
                </div>

                <button
                    onClick={handleSubmit}
                    className="w-full bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-400 hover:to-red-500 text-white font-semibold py-4 rounded-xl transition-all hover:shadow-lg hover:shadow-orange-500/25 flex items-center justify-center gap-2"
                >
                    Generate News Reel
                </button>
            </motion.div>
        </motion.div>
    );
}

