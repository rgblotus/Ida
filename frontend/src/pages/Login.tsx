import React, { useState } from 'react'
import { LoginForm } from '../components/auth/LoginForm'
import { RegisterForm } from '../components/auth/RegisterForm'
import WebGLBackground from '../components/webGL/WebGLBackground'

export const Login: React.FC = () => {
    const [isLogin, setIsLogin] = useState(true)

    return (
        <div className="min-h-screen relative flex items-center justify-center p-6 bg-gradient-to-br from-indigo-950 via-purple-900 to-blue-950">
            {/* WebGL Background - Full Screen */}
            <WebGLBackground
                particleCount={10000}
                className="fixed inset-0 w-full h-full"
                shaderName="particles"
                shape="wave"
            />

            {/* Gradient Overlay for better readability */}
            <div className="fixed inset-0 bg-gradient-to-br from-indigo-900/30 via-purple-900/20 to-blue-900/30 pointer-events-none" />

            {/* Content Container */}
            <div className="relative z-10 w-full max-w-6xl flex flex-col md:flex-row rounded-3xl overflow-hidden shadow-2xl bg-white/95 backdrop-blur-sm">
                {/* LEFT SIDE - Branding with WebGL */}
                <div className="relative w-full md:w-1/2 aspect-[3/4] md:aspect-auto md:min-h-[720px] bg-gradient-to-br from-indigo-900/90 via-purple-900/90 to-blue-900/90 p-10 md:p-14 flex flex-col justify-between overflow-hidden">
                    {/* WebGL Background in Left Card */}
                    <WebGLBackground
                        particleCount={5000}
                        className="absolute inset-0 w-full h-full opacity-60"
                        shaderName="particles"
                        shape="torus"
                    />

                    {/* Content with higher z-index */}
                    <div className="relative z-10">
                        {/* Logo/Brand */}
                        <div>
                            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
                                Niki
                            </h1>
                            <p className="text-white/90 text-lg">
                                Your AI-Powered Assistant
                            </p>
                        </div>
                    </div>

                    {/* Tagline */}
                    <div className="relative z-10 text-white text-2xl md:text-3xl font-medium max-w-md">
                        Capturing Moments,
                        <br />
                        Creating Memories
                    </div>

                    {/* Decorative Elements */}
                    <div className="absolute top-10 right-10 w-32 h-32 bg-white/10 rounded-full blur-3xl" />
                    <div className="absolute bottom-20 left-10 w-40 h-40 bg-purple-300/20 rounded-full blur-3xl" />
                </div>

                {/* RIGHT SIDE - Forms */}
                <div className="w-full md:w-1/2 p-10 md:p-14 flex flex-col justify-center bg-white">
                    {isLogin ? (
                        <LoginForm
                            onSwitchToRegister={() => setIsLogin(false)}
                        />
                    ) : (
                        <RegisterForm
                            onSwitchToLogin={() => setIsLogin(true)}
                        />
                    )}
                </div>
            </div>
        </div>
    )
}
