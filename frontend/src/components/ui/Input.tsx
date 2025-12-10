import React, { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import { cn } from '../../lib/utils'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string
    error?: string
    icon?: React.ReactNode
    trailing?: React.ReactNode
    helperText?: string
}

export const Input: React.FC<InputProps> = ({
    label,
    error,
    icon,
    trailing,
    helperText,
    className = '',
    type,
    ...props
}) => {
    const [showPassword, setShowPassword] = useState(false)
    const isPassword = type === 'password'
    const inputType = isPassword && showPassword ? 'text' : type

    return (
        <div className="w-full">
            {label && (
                <label
                    htmlFor={props.id}
                    className="block text-sm font-semibold text-gray-700 mb-2"
                >
                    {label}
                </label>
            )}

            <div className="relative group">
                {/* Leading Icon */}
                {icon && (
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400 group-focus-within:text-blue-600 transition-colors">
                        {icon}
                    </div>
                )}

                {/* Input */}
                <input
                    {...props}
                    type={inputType}
                    className={cn(
                        'w-full py-2.5 px-4',
                        'bg-white',
                        'border-2 rounded-xl',
                        'text-gray-900 placeholder-gray-400',
                        'transition-all duration-200',
                        'focus:outline-none focus:ring-4 focus:ring-blue-100',
                        icon && 'pl-10',
                        (trailing || isPassword) && 'pr-10',
                        error
                            ? 'border-red-300 focus:border-red-500'
                            : 'border-gray-200 focus:border-blue-500 hover:border-gray-300',
                        'disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed',
                        className
                    )}
                />

                {/* Password Toggle or Trailing Element */}
                {isPassword ? (
                    <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        {showPassword ? (
                            <EyeOff className="w-5 h-5" />
                        ) : (
                            <Eye className="w-5 h-5" />
                        )}
                    </button>
                ) : trailing ? (
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                        {trailing}
                    </div>
                ) : null}
            </div>

            {/* Helper Text or Error */}
            {error && (
                <p className="mt-1.5 text-sm text-red-600 flex items-center gap-1">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    {error}
                </p>
            )}
            {!error && helperText && (
                <p className="mt-1.5 text-sm text-gray-500">{helperText}</p>
            )}
        </div>
    )
}
