import React, { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { Card, CardHeader, CardContent, CardFooter } from '../ui/Card'
import { Mail, Lock, UserPlus } from 'lucide-react'

interface RegisterFormProps {
    onSwitchToLogin: () => void
}

export const RegisterForm: React.FC<RegisterFormProps> = ({
    onSwitchToLogin,
}) => {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        passwordConfirm: '',
    })
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const { register } = useAuth()

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData((prev) => ({
            ...prev,
            [e.target.name]: e.target.value,
        }))
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        
        // Validate passwords match
        if (formData.password !== formData.passwordConfirm) {
            setError('Passwords do not match')
            return
        }

        // Validate password length
        if (formData.password.length < 6) {
            setError('Password must be at least 6 characters long')
            return
        }
        
        setLoading(true)

        try {
            await register(formData.email, formData.password)
        } catch (err: any) {
            // Handle validation errors from backend
            if (err.response?.data?.detail) {
                const detail = err.response.data.detail
                // If detail is an array of validation errors
                if (Array.isArray(detail)) {
                    const errorMessages = detail.map((e: any) => e.msg).join(', ')
                    setError(errorMessages)
                } else if (typeof detail === 'string') {
                    setError(detail)
                } else {
                    setError('Registration failed. Please try again.')
                }
            } else {
                setError('Registration failed. Please try again.')
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <Card variant="glass" className="w-full max-w-md">
            <CardHeader>
                <h2 className="text-3xl font-bold text-center bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                    Create Account
                </h2>
                <p className="text-center text-gray-600 mt-2">
                    Join us and start your journey
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
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="you@example.com"
                        icon={<Mail className="w-5 h-5" />}
                        required
                        disabled={loading}
                    />

                    <Input
                        label="Password"
                        name="password"
                        type="password"
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="Create a strong password"
                        icon={<Lock className="w-5 h-5" />}
                        helperText="Must be at least 6 characters"
                        required
                        disabled={loading}
                        minLength={6}
                    />

                    <Input
                        label="Confirm Password"
                        name="passwordConfirm"
                        type="password"
                        value={formData.passwordConfirm}
                        onChange={handleChange}
                        placeholder="Re-enter your password"
                        icon={<Lock className="w-5 h-5" />}
                        required
                        disabled={loading}
                        minLength={6}
                    />
                </CardContent>

                <CardFooter className="flex flex-col space-y-4 bg-transparent border-t-0">
                    <Button
                        type="submit"
                        variant="gradient-purple"
                        size="lg"
                        loading={loading}
                        disabled={loading}
                        fullWidth
                        icon={UserPlus}
                        iconPosition="right"
                    >
                        {loading ? 'Creating Account...' : 'Create Account'}
                    </Button>

                    <div className="text-center">
                        <span className="text-sm text-gray-600">
                            Already have an account?{' '}
                            <button
                                type="button"
                                onClick={onSwitchToLogin}
                                className="text-purple-600 hover:text-purple-700 font-semibold hover:underline transition-colors"
                            >
                                Sign in instead
                            </button>
                        </span>
                    </div>
                </CardFooter>
            </form>
        </Card>
    )
}
