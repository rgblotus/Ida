import React, { useEffect } from 'react'
import { X } from 'lucide-react'
import { cn } from '../../lib/utils'

interface ModalProps {
    isOpen: boolean
    onClose: () => void
    title?: string
    children: React.ReactNode
    size?: 'sm' | 'md' | 'lg' | 'xl' | 'max'
    fullContent?: boolean
}

const sizeClasses = {
    sm: 'max-w-md aspect-[4/3]',
    md: 'max-w-2xl aspect-[4/3]',
    lg: 'max-w-4xl aspect-[4/3]',
    xl: 'max-w-6xl aspect-[4/3]',
    max: 'w-[70vmin] aspect-[4/3] max-w-none',
}

export const Modal: React.FC<ModalProps> = ({
    isOpen,
    onClose,
    title,
    children,
    size = 'md',
    fullContent = false,
}) => {
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose()
        }
        document.addEventListener('keydown', handleEscape)
        return () => document.removeEventListener('keydown', handleEscape)
    }, [onClose])

    if (!isOpen) return null

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center px-4 py-4"
            role="dialog"
            aria-modal="true"
        >
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-gradient-to-br from-slate-900/80 via-purple-900/60 to-indigo-900/80 backdrop-blur-xl transition-opacity"
                onClick={onClose}
            />

            {/* Modal */}
            <div
                className={cn(
                    'relative bg-gradient-to-br from-slate-800/95 via-slate-900/95 to-slate-900/98 backdrop-blur-xl rounded-xl shadow-2xl border border-white/10 w-full mx-auto transform transition-transform duration-300 scale-100 flex flex-col',
                    sizeClasses[size]
                )}
            >
                {/* Header */}
                {title && (
                    <div className="flex items-center justify-between p-3 border-b border-white/10">
                        <h2 className="text-lg font-semibold text-white truncate">
                            {title}
                        </h2>
                        <button
                            onClick={onClose}
                            className="p-1 hover:bg-white/10 rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors"
                            aria-label="Close modal"
                        >
                            <X className="w-4 h-4 text-white/70 hover:text-white" />
                        </button>
                    </div>
                )}

                {/* Content */}
                <div className={fullContent ? 'flex-1 min-h-0' : 'p-6'}>
                    {children}
                </div>
            </div>
        </div>
    )
}
