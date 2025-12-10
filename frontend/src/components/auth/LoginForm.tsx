import React, { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { Card, CardHeader, CardContent, CardFooter } from '../ui/Card'
import { Mail, Lock, LogIn } from 'lucide-react'

interface LoginFormProps {
    onSwitchToRegister: () => void
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSwitchToRegister }) => {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const { login } = useAuth()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            await login(email, password)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed. Please check your credentials.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <Card variant="glass" className="w-full max-w-md">
            <CardHeader>
                <h2 className="text-3xl font-bold text-center bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Welcome Back
                </h2>
                <p className="text-center text-gray-600 mt-2">
                    Sign in to continue to your account
                </p>
            </CardHeader>

            <form onSubmit={handleSubmit}>
                <CardContent className="space-y-5">
                    {error && (
                        <div className="p-4 text-sm text-red-700 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3">
                            <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                            <span>{error}</span>
                        </div>
                    )}

                    <Input
                        label="Email Address"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="you@example.com"
                        icon={<Mail className="w-5 h-5" />}
                        required
                        disabled={loading}
                    />

                    <Input
                        label="Password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter your password"
                        icon={<Lock className="w-5 h-5" />}
                        required
                        disabled={loading}
                    />
                </CardContent>

                <CardFooter className="flex flex-col space-y-4 bg-transparent border-t-0">
                    <Button
                        type="submit"
                        variant="gradient-blue"
                        size="lg"
                        loading={loading}
                        disabled={loading}
                        fullWidth
                        icon={LogIn}
                        iconPosition="right"
                    >
                        {loading ? 'Signing in...' : 'Sign In'}
                    </Button>

                    <div className="text-center">
                        <span className="text-sm text-gray-600">
                            Don't have an account?{' '}
                            <button
                                type="button"
                                onClick={onSwitchToRegister}
                                className="text-blue-600 hover:text-blue-700 font-semibold hover:underline transition-colors"
                            >
                                Create one now
                            </button>
                        </span>
                    </div>
                </CardFooter>
            </form>
        </Card>
    )
}
