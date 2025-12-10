import { type ClassValue, clsx } from 'clsx'

/* =============================
   Tailwind Class Helpers
============================= */

/**
 * Modern className helper
 * Supports:
 * - Conditional classes
 * - Dark mode / light mode variants
 * - Responsive prefixes (sm:, md:, lg:, etc.)
 */
export function cn(...inputs: ClassValue[]): string {
    return clsx(inputs)
}

/**
 * Variant helper
 * Usage: cn(variant({ 'bg-blue-500': isActive, 'text-white': isActive }))
 */
export type VariantProps = Record<string, string | boolean | undefined>

export function variant(variants: VariantProps): string {
    return Object.entries(variants)
        .filter(([_, value]) => !!value)
        .map(([key]) => key)
        .join(' ')
}

/**
 * Dark / Light mode helpers
 * Usage: cn(dark('bg-gray-900 text-white'), light('bg-white text-gray-900'))
 */
export function dark(classes: string): string {
    return `dark:${classes}`
}

export function light(classes: string): string {
    return classes
}

/**
 * Responsive helper
 * Usage: responsive({ sm: 'p-2', md: 'p-4', lg: 'p-6' })
 */
export function responsive(sizes: Record<string, string>): string {
    return Object.entries(sizes)
        .map(([breakpoint, className]) => `${breakpoint}:${className}`)
        .join(' ')
}

/* =============================
   Date & Text Utilities
============================= */

/**
 * Format ISO date string to human-readable format
 */
export function formatDate(date: string): string {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    })
}

/**
 * Truncate text to maxLength and add ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + '...'
}

/* =============================
   File Utilities
============================= */

/**
 * Convert bytes to human-readable format
 */
export function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/* =============================
   Function Utilities
============================= */

/**
 * Debounce any function
 */
export function debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout
    return (...args: Parameters<T>) => {
        clearTimeout(timeout)
        timeout = setTimeout(() => func(...args), wait)
    }
}

/* =============================
   Example Usage
============================= */

// const buttonClass = cn(
//   'rounded-lg px-4 py-2 font-medium',
//   variant({ 'bg-blue-500 text-white': isActive }),
//   dark('bg-gray-800 text-gray-100'),
//   responsive({ sm: 'p-2', md: 'p-4', lg: 'p-6' })
// )
