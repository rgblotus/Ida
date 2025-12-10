import React from 'react'
import {
    BrowserRouter as Router,
    Routes,
    Route,
    Navigate,
} from 'react-router-dom'

import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { Chat } from './pages/Chat'
import { Documents } from './pages/Documents'
import { Weather } from './pages/Weather'
import { AuthProvider, useAuth } from './contexts/AuthContext'

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({
    children,
}) => {
    const { isAuthenticated, isLoading } = useAuth()

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4" />
                    <p className="text-gray-600 font-medium">Loading...</p>
                </div>
            </div>
        )
    }

    return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { isAuthenticated, isLoading } = useAuth()

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4" />
                    <p className="text-gray-600 font-medium">Loading...</p>
                </div>
            </div>
        )
    }

    return !isAuthenticated ? <>{children}</> : <Navigate to="/dashboard" />
}

function AppRoutes() {
    return (
        <Router>
            <Routes>
                <Route
                    path="/login"
                    element={
                        <PublicRoute>
                            <Login />
                        </PublicRoute>
                    }
                />
                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute>
                            <Dashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/chat"
                    element={
                        <ProtectedRoute>
                            <Chat />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/documents"
                    element={
                        <ProtectedRoute>
                            <Documents />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/weather"
                    element={
                        <ProtectedRoute>
                            <Weather />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/"
                    element={<Navigate to="/dashboard" replace />}
                />
            </Routes>
        </Router>
    )
}

export default function App() {
    return (
        <AuthProvider>
            <AppRoutes />
        </AuthProvider>
    )
}
