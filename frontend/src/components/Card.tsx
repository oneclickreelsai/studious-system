
import React from 'react';

interface CardProps {
    icon: React.ReactNode;
    title: string;
    desc: string;
    color: string;
    iconColor: string;
    onClick: () => void;
    disabled?: boolean;
}

export function Card({ icon, title, desc, color, iconColor, onClick, disabled }: CardProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`group p-8 rounded-3xl border border-white/5 bg-neutral-900/50 backdrop-blur-sm transition-all duration-300 cursor-pointer hover:-translate-y-1 hover:shadow-2xl ${color} disabled:opacity-50 disabled:cursor-not-allowed text-left w-full`}
        >
            <div className={`mb-6 p-4 w-fit rounded-2xl ${iconColor} transition-transform group-hover:scale-110`}>
                {icon}
            </div>
            <h3 className="text-2xl font-bold mb-3 text-neutral-100">{title}</h3>
            <p className="text-neutral-400 leading-relaxed text-sm">{desc}</p>
        </button>
    )
}
