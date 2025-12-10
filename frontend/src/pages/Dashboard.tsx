import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '../components/ui/Button'
import { useNavigate } from 'react-router-dom'
import { WaterDropCard } from '../components/dashboard/WaterDropCard'
import { PageLayout } from '../components/layout/PageLayout'
import { chatAPI, documentsAPI } from '../services/api'
import { MessageSquare, FileText, Cloud, LogOut, Sparkles } from 'lucide-react'

export const Dashboard: React.FC = () => {
    const { user, logout } = useAuth()
    const navigate = useNavigate()
    const [stats, setStats] = useState({
        totalChats: 0,
        totalDocuments: 0,
        totalMessages: 0,
        chatGrowth: 0,
        documentGrowth: 0,
        messageGrowth: 0,
    })

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    useEffect(() => {
        const loadStats = async () => {
            try {
                const [sessions, documents] = await Promise.all([
                    chatAPI.listSessions(),
                    documentsAPI.list(),
                ])
                const previousStats = JSON.parse(
                    localStorage.getItem('dashboardStats') ||
                        '{"totalChats":0,"totalDocuments":0,"totalMessages":0}'
                )
                const currentStats = {
                    totalChats: sessions.length,
                    totalDocuments: documents.length,
                    totalMessages: sessions.length + documents.length,
                }
                const calculateGrowth = (current: number, previous: number) => {
                    if (previous === 0) return current > 0 ? 100 : 0
                    return (
                        Math.round(
                            ((current - previous) / previous) * 100 * 10
                        ) / 10
                    )
                }
                setStats({
                    ...currentStats,
                    chatGrowth: calculateGrowth(
                        currentStats.totalChats,
                        previousStats.totalChats
                    ),
                    documentGrowth: calculateGrowth(
                        currentStats.totalDocuments,
                        previousStats.totalDocuments
                    ),
                    messageGrowth: calculateGrowth(
                        currentStats.totalMessages,
                        previousStats.totalMessages
                    ),
                })
                // Store current values for next visit
                localStorage.setItem(
                    'dashboardStats',
                    JSON.stringify(currentStats)
                )
            } catch (error) {
                console.error('Failed to load dashboard stats:', error)
            }
        }
        loadStats()
    }, [])

    const waterDrops = [
        {
            icon: MessageSquare,
            title: 'Chat',
            description: 'Start a conversation with AI',
            gradient:
                'bg-gradient-to-br from-purple-500 via-pink-500 to-red-500',
        },
        {
            icon: FileText,
            title: 'Documents',
            description: 'Manage your documents',
            gradient:
                'bg-gradient-to-br from-blue-500 via-cyan-500 to-teal-500',
        },
        {
            icon: Cloud,
            title: 'Weather',
            description: 'Check weather updates',
            gradient:
                'bg-gradient-to-br from-indigo-500 via-blue-500 to-sky-500',
        },
    ]

    return (
        <PageLayout
            theme="purple"
            title="Welcome Back!"
            subtitle={user?.email || ''}
            icon={<Sparkles className="w-6 h-6 text-white" />}
            actions={
                <Button
                    onClick={handleLogout}
                    variant="gradient-pink"
                    icon={LogOut}
                    iconPosition="left"
                >
                    Logout
                </Button>
            }
            showHomeButton={false}
        >
            {/* Welcome Message */}
            <div className="mb-12 text-center">
                <h2 className="text-5xl font-bold bg-gradient-to-r from-white via-purple-200 to-blue-200 bg-clip-text text-transparent mb-4 drop-shadow-lg">
                    Choose Your Action
                </h2>
                <p className="text-xl text-white/80">
                    Select one of the options below to get started
                </p>
            </div>

            {/* Water Drop Cards */}
            <div className="flex flex-wrap justify-center gap-16 items-center mb-16">
                {waterDrops.map((drop, index) => (
                    <div
                        key={index}
                        className="transform transition-all duration-500 hover:scale-110"
                        style={{
                            animation: `float ${
                                3 + index * 0.5
                            }s ease-in-out infinite`,
                            animationDelay: `${index * 0.2}s`,
                        }}
                    >
                        <WaterDropCard
                            icon={drop.icon}
                            title={drop.title}
                            description={drop.description}
                            gradient={drop.gradient}
                            onClick={() =>
                                navigate(`/${drop.title.toLowerCase()}`)
                            }
                        />
                    </div>
                ))}
            </div>

            {/* Stats Section - Enhanced */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Total Chats */}
                <div className="group relative bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-xl rounded-3xl p-6 border border-white/20 hover:border-purple-400/50 transition-all duration-300 hover:shadow-2xl hover:shadow-purple-500/50 hover:-translate-y-2">
                    <div className="absolute inset-0 bg-gradient-to-br from-purple-600/0 to-pink-600/0 group-hover:from-purple-600/10 group-hover:to-pink-600/10 rounded-3xl transition-all duration-300" />
                    <div className="relative flex items-center justify-between">
                        <div>
                            <p className="text-sm font-semibold text-white/70 uppercase tracking-wider">
                                Total Chats
                            </p>
                            <p className="text-4xl font-bold text-white mt-2">
                                {stats.totalChats}
                            </p>
                            <p className="text-xs text-purple-300 mt-1">
                                {stats.chatGrowth >= 0 ? '+' : ''}
                                {stats.chatGrowth}% from last visit
                            </p>
                        </div>
                        <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-4 rounded-2xl shadow-lg">
                            <MessageSquare className="w-8 h-8 text-white" />
                        </div>
                    </div>
                </div>

                {/* Documents */}
                <div className="group relative bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-xl rounded-3xl p-6 border border-white/20 hover:border-blue-400/50 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/50 hover:-translate-y-2">
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-600/0 to-cyan-600/0 group-hover:from-blue-600/10 group-hover:to-cyan-600/10 rounded-3xl transition-all duration-300" />
                    <div className="relative flex items-center justify-between">
                        <div>
                            <p className="text-sm font-semibold text-white/70 uppercase tracking-wider">
                                Documents
                            </p>
                            <p className="text-4xl font-bold text-white mt-2">
                                {stats.totalDocuments}
                            </p>
                            <p className="text-xs text-blue-300 mt-1">
                                {stats.documentGrowth >= 0 ? '+' : ''}
                                {stats.documentGrowth}% from last visit
                            </p>
                        </div>
                        <div className="bg-gradient-to-br from-blue-500 to-cyan-500 p-4 rounded-2xl shadow-lg">
                            <FileText className="w-8 h-8 text-white" />
                        </div>
                    </div>
                </div>

                {/* API Calls */}
                <div className="group relative bg-gradient-to-br from-indigo-500/20 to-blue-500/20 backdrop-blur-xl rounded-3xl p-6 border border-white/20 hover:border-indigo-400/50 transition-all duration-300 hover:shadow-2xl hover:shadow-indigo-500/50 hover:-translate-y-2">
                    <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/0 to-blue-600/0 group-hover:from-indigo-600/10 group-hover:to-blue-600/10 rounded-3xl transition-all duration-300" />
                    <div className="relative flex items-center justify-between">
                        <div>
                            <p className="text-sm font-semibold text-white/70 uppercase tracking-wider">
                                API Calls
                            </p>
                            <p className="text-4xl font-bold text-white mt-2">
                                {stats.totalMessages >= 1000
                                    ? `${(stats.totalMessages / 1000).toFixed(
                                          1
                                      )}k`
                                    : stats.totalMessages}
                            </p>
                            <p className="text-xs text-indigo-300 mt-1">
                                {stats.messageGrowth >= 0 ? '+' : ''}
                                {stats.messageGrowth}% from last visit
                            </p>
                        </div>
                        <div className="bg-gradient-to-br from-indigo-500 to-blue-500 p-4 rounded-2xl shadow-lg">
                            <Cloud className="w-8 h-8 text-white" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Floating Animation Keyframes */}
            <style>{`
                @keyframes float {
                    0%, 100% {
                        transform: translateY(0px);
                    }
                    50% {
                        transform: translateY(-20px);
                    }
                }
            `}</style>
        </PageLayout>
    )
}
