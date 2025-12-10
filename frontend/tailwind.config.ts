import type { Config } from 'tailwindcss'

export default {
    darkMode: 'class', // Use 'class' for toggling dark mode
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],

    theme: {
        container: {
            center: true,
            padding: '2rem',
            screens: {
                sm: '640px',
                md: '768px',
                lg: '1024px',
                xl: '1280px',
                '2xl': '1536px',
            },
        },

        extend: {
            // 🌈 Color System
            colors: {
                brand: {
                    50: '#f0f5ff',
                    100: '#e0e7ff',
                    200: '#c7d2fe',
                    300: '#a5b4fc',
                    400: '#818cf8',
                    500: '#6366f1',
                    600: '#4f46e5',
                    700: '#4338ca',
                    800: '#3730a3',
                    900: '#312e81',
                },
                accent: {
                    50: '#f5f3ff',
                    100: '#ede9fe',
                    200: '#ddd6fe',
                    300: '#c4b5fd',
                    400: '#a78bfa',
                    500: '#8b5cf6',
                    600: '#7e22ce',
                    700: '#6d28d9',
                    800: '#5b21b6',
                    900: '#4c1d95',
                },
                success: {
                    50: '#f0fdf4',
                    100: '#dcfce7',
                    500: '#10b981',
                    600: '#059669',
                },
                warning: {
                    50: '#fffbeb',
                    100: '#fef3c7',
                    500: '#f59e0b',
                    600: '#d97706',
                },
                danger: {
                    50: '#fef2f2',
                    100: '#fee2e2',
                    500: '#ef4444',
                    600: '#dc2626',
                },
                neutral: {
                    50: '#fafafa',
                    100: '#f5f5f5',
                    200: '#e5e5e5',
                    300: '#d4d4d4',
                    400: '#a3a3a3',
                    500: '#737373',
                    600: '#525252',
                    700: '#404040',
                    800: '#262626',
                    900: '#171717',
                    950: '#0a0a0a',
                },
                surface: 'hsl(var(--surface))',
                'surface-variant': 'hsl(var(--surface-variant))',
                overlay: 'hsl(var(--overlay))',
                textPrimary: 'hsl(var(--text-primary))',
                textSecondary: 'hsl(var(--text-secondary))',
                textTertiary: 'hsl(var(--text-tertiary))',
            },

            // 📏 Spacing Scale
            spacing: {
                '4.5': '1.125rem', // 18px
                '5.5': '1.375rem', // 22px
                '18': '4.5rem', // 72px
            },

            // ✍️ Typography
            fontFamily: {
                sans: [
                    'Inter',
                    'system-ui',
                    '-apple-system',
                    'BlinkMacSystemFont',
                    '"Segoe UI"',
                    'Roboto',
                    '"Helvetica Neue"',
                    'Arial',
                    'sans-serif',
                ],
                heading: ['Poppins', 'sans-serif'],
                mono: ['Fira Code', 'ui-monospace', 'SFMono-Regular'],
            },
            fontSize: {
                xs: [
                    '0.75rem',
                    { lineHeight: '1.25', letterSpacing: '-0.01em' },
                ],
                sm: [
                    '0.875rem',
                    { lineHeight: '1.375', letterSpacing: '-0.005em' },
                ],
                base: ['1rem', { lineHeight: '1.5', letterSpacing: '0' }],
                lg: [
                    '1.125rem',
                    { lineHeight: '1.5', letterSpacing: '-0.005em' },
                ],
                xl: [
                    '1.25rem',
                    { lineHeight: '1.5', letterSpacing: '-0.01em' },
                ],
                '2xl': [
                    '1.5rem',
                    { lineHeight: '1.33', letterSpacing: '-0.015em' },
                ],
                '3xl': [
                    '1.875rem',
                    { lineHeight: '1.2', letterSpacing: '-0.02em' },
                ],
                '4xl': [
                    '2.25rem',
                    { lineHeight: '1.15', letterSpacing: '-0.025em' },
                ],
            },
            fontWeight: {
                normal: '400',
                medium: '500',
                semibold: '600',
                bold: '700',
            },

            // 🖼️ Aspect Ratios (requires plugin)
            aspectRatio: {
                '4/3': '4 / 3',
                '16/9': '16 / 9',
                '21/9': '21 / 9',
                '1/1': '1 / 1',
                '3/4': '3 / 4',
            },

            // 🔆 Gradients
            backgroundImage: {
                'gradient-sidebar': 'linear-gradient(180deg, #4f46e5, #7e22ce)',
                'gradient-login': 'linear-gradient(135deg, #f0f5ff, #e0e7ff)',
                'gradient-card': 'linear-gradient(145deg, #ffffff, #fafafa)',
                'gradient-card-dark':
                    'linear-gradient(145deg, #1e1e2e, #181825)',
                'gradient-brand': 'linear-gradient(90deg, #6366f1, #8b5cf6)',
            },

            // 🌀 Animations & Keyframes
            animation: {
                'fade-in': 'fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards',
                'fade-in-up':
                    'fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards',
                'slide-in-left':
                    'slideInLeft 0.4s cubic-bezier(0.22, 1, 0.36, 1) forwards',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                float: 'float 6s ease-in-out infinite',
            },
            keyframes: {
                fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
                fadeInUp: {
                    '0%': { opacity: '0', transform: 'translateY(12px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                slideInLeft: {
                    '0%': { opacity: '0', transform: 'translateX(-20px)' },
                    '100%': { opacity: '1', transform: 'translateX(0)' },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-8px)' },
                },
                pulse: {
                    '0%, 100%': { opacity: '1' },
                    '50%': { opacity: '0.5' },
                },
            },

            // 📐 Max Widths
            maxWidth: {
                '80vw': '80vw',
                'screen-80': '80vw',
                '7xl': '80rem',
                '8xl': '90rem',
            },

            // ⏱ Transition timing
            transitionTimingFunction: {
                'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
                sidebar: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
            },
        },
    },

    plugins: [],
} satisfies Config
