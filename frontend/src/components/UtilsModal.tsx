
import { motion } from 'framer-motion';
import { X, Wrench } from 'lucide-react';

interface UtilsModalProps {
    onClose: () => void;
}

export function UtilsModal({ onClose }: UtilsModalProps) {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6"
            onClick={onClose}
        >
            <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                onClick={(e) => e.stopPropagation()}
                className="bg-neutral-900 border border-white/10 rounded-3xl p-8 max-w-lg w-full"
            >
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Wrench className="w-6 h-6 text-yellow-400" />
                        Utilities
                    </h2>
                    <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full">
                        <X className="w-5 h-5" />
                    </button>
                </div>
                <p className="text-neutral-400">Utility tools coming soon...</p>
            </motion.div>
        </motion.div>
    );
}
