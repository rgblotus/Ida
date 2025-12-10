import React, { createContext, useContext, useEffect, useState } from 'react'
import { apiClient } from '../lib/api'
import type { User, AuthResponse } from '../types'

interface AuthContextType {
    user: User | null
    isLoading: boolean
    login: (email: string, password: string) => Promise<void>
    register: (email: string, password: string) => Promise<void>
    logout: () => void
    isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
    children,
}) => {
    const [user, setUser] = useState<User | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem('access_token')
            if (token) {
                try {
                    const userData = await apiClient.getCurrentUser()
                    setUser(userData)
                } catch (error) {
                    localStorage.removeItem('access_token')
                    localStorage.removeItem('refresh_token')
                    localStorage.removeItem('user')
                }
            }
            setIsLoading(false)
        }

        initAuth()
    }, [])

    const login = async (email: string, password: string) => {
        const response: AuthResponse = await apiClient.login(email, password)
        localStorage.setItem('access_token', response.access_token)
        localStorage.setItem('refresh_token', response.refresh_token)
        localStorage.setItem('user', JSON.stringify(response.user))
        setUser(response.user)
    }

    const register = async (email: string, password: string) => {
        const response: AuthResponse = await apiClient.register(email, password)
        localStorage.setItem('access_token', response.access_token)
        localStorage.setItem('refresh_token', response.refresh_token)
        localStorage.setItem('user', JSON.stringify(response.user))
        setUser(response.user)
    }

    const logout = () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        setUser(null)
    }

    return (
        <AuthContext.Provider
            value={{
                user,
                isLoading,
                login,
                register,
                logout,
                isAuthenticated: !!user,
            }}
        >
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
