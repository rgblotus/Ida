import React from 'react'
import { cn } from '../../lib/utils'

interface CardProps {
    children: React.ReactNode
    className?: string
    variant?: 'default' | 'gradient' | 'glass'
    hover?: boolean
}

export const Card: React.FC<CardProps> = ({
    children,
    className,
    variant = 'default',
    hover = false,
}) => {
    const variants = {
        default: 'bg-white border border-gray-200 shadow-sm',
        gradient: 'bg-gradient-to-br from-white to-gray-50 border border-gray-200 shadow-md',
        glass: 'bg-white/80 backdrop-blur-lg border border-white/20 shadow-xl',
    }

    return (
        <div
            className={cn(
                'rounded-2xl overflow-hidden transition-all duration-300',
                variants[variant],
                hover && 'hover:shadow-lg hover:-translate-y-1',
                className
            )}
        >
            {children}
        </div>
    )
}

interface CardHeaderProps {
    children: React.ReactNode
    className?: string
}

export const CardHeader: React.FC<CardHeaderProps> = ({ children, className }) => {
    return (
        <div className={cn('px-6 py-5 border-b border-gray-100', className)}>
            {children}
        </div>
    )
}

interface CardContentProps {
    children: React.ReactNode
    className?: string
}

export const CardContent: React.FC<CardContentProps> = ({ children, className }) => {
    return <div className={cn('px-6 py-5', className)}>{children}</div>
}

interface CardFooterProps {
    children: React.ReactNode
    className?: string
}

export const CardFooter: React.FC<CardFooterProps> = ({ children, className }) => {
    return (
        <div className={cn('px-6 py-4 bg-gray-50 border-t border-gray-100', className)}>
            {children}
        </div>
    )
}
