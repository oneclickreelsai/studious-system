
import { useState } from 'react';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';

interface ScriptModalProps {
    onClose: () => void;
    onSubmit: (script: string, theme: string, voice: boolean) => void;
}

export function ScriptModal({ onClose, onSubmit }: ScriptModalProps) {
    const [script, setScript] = useState("");
    const [visualTheme, setVisualTheme] = useState("");
    const [useVoiceover, setUseVoiceover] = useState(true);

    const handleSubmit = () => {
        if (!script.trim()) {
            alert("Please enter a script");
            return;
        }
        onSubmit(script, visualTheme, useVoiceover);
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
                className="bg-neutral-900 border border-white/10 rounded-3xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                        Script to Video
                    </h2>
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
                            Script Text *
                        </label>
                        <textarea
                            value={script}
                            onChange={(e) => setScript(e.target.value)}
                            placeholder="Enter your video script here..."
                            className="w-full h-48 bg-neutral-800/50 border border-white/10 rounded-xl p-4 text-white placeholder-neutral-500 focus:border-cyan-500/50 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all resize-none"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-neutral-300 mb-2">
                            Visual Theme (Optional)
                        </label>
                        <input
                            type="text"
                            value={visualTheme}
                            onChange={(e) => setVisualTheme(e.target.value)}
                            placeholder="e.g., motivation, fitness, tech..."
                            className="w-full bg-neutral-800/50 border border-white/10 rounded-xl p-4 text-white placeholder-neutral-500 focus:border-cyan-500/50 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
                        />
                    </div>

                    <div className="flex items-center gap-3">
                        <input
                            type="checkbox"
                            id="voiceover"
                            checked={useVoiceover}
                            onChange={(e) => setUseVoiceover(e.target.checked)}
                            className="w-5 h-5 rounded bg-neutral-800 border-white/10 text-cyan-500 focus:ring-cyan-500/20"
                        />
                        <label htmlFor="voiceover" className="text-neutral-300">
                            Generate AI Voiceover
                        </label>
                    </div>

                    <button
                        onClick={handleSubmit}
                        className="w-full mt-6 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold py-4 rounded-xl transition-all hover:shadow-lg hover:shadow-cyan-500/25"
                    >
                        Generate Video
                    </button>
                </div>
            </motion.div>
        </motion.div>
    );
}

