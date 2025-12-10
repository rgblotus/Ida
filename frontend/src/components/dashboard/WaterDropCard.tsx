import React from 'react'
import type { LucideIcon } from 'lucide-react'
import { cn } from '../../lib/utils'

interface WaterDropCardProps {
    icon: LucideIcon
    title: string
    description: string
    gradient: string
    onClick?: () => void
}

export const WaterDropCard: React.FC<WaterDropCardProps> = ({
    icon: Icon,
    title,
    description,
    gradient,
    onClick,
}) => {
    return (
        <button
            onClick={onClick}
            className={cn(
                'relative group cursor-pointer transition-all duration-500 hover:scale-105',
                'w-64 h-80'
            )}
        >
            {/* Water Drop Shape */}
            <div
                className={cn(
                    'absolute inset-0 rounded-t-full rounded-b-[50%] shadow-2xl',
                    'transition-all duration-500 group-hover:shadow-3xl',
                    gradient
                )}
                style={{
                    clipPath: 'path("M 128 0 C 128 0, 256 100, 256 200 C 256 280, 198 320, 128 320 C 58 320, 0 280, 0 200 C 0 100, 128 0, 128 0 Z")',
                }}
            >
                {/* Shine Effect */}
                <div className="absolute top-8 left-8 w-16 h-16 bg-white/20 rounded-full blur-2xl" />
                
                {/* Content */}
                <div className="relative h-full flex flex-col items-center justify-center p-8 text-white">
                    <div className="bg-white/20 backdrop-blur-sm p-6 rounded-full mb-6 group-hover:scale-110 transition-transform duration-300">
                        <Icon className="w-12 h-12" />
                    </div>
                    <h3 className="text-2xl font-bold mb-3">{title}</h3>
                    <p className="text-sm text-white/80 text-center">{description}</p>
                </div>

                {/* Ripple Effect on Hover */}
                <div 
                    className="absolute inset-0 rounded-t-full rounded-b-[50%] opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                    style={{
                        clipPath: 'path("M 128 0 C 128 0, 256 100, 256 200 C 256 280, 198 320, 128 320 C 58 320, 0 280, 0 200 C 0 100, 128 0, 128 0 Z")',
                    }}
                >
                    <div className="absolute inset-0 bg-white/10 animate-pulse" />
                </div>
            </div>
        </button>
    )
}
