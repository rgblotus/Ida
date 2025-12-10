import React, { useState, useEffect } from 'react'
import {
    PanelLeftClose,
    PanelLeftOpen,
    MessageSquare,
    Plus,
    Trash2,
} from 'lucide-react'
import { cn } from '../../lib/utils'
import { chatAPI } from '../../services/api'
import type { ChatSession } from '../../types/api'

interface ChatHistorySidebarProps {
    isCollapsed: boolean
    onToggle: () => void
    user?: { id: number; email: string } | null
    currentSessionId?: number | null
    onSessionSelect: (session: ChatSession) => void
    onNewChat: () => void
    onSessionDelete?: (sessionId: number) => void
    refreshTrigger?: number
}

export const ChatHistorySidebar: React.FC<ChatHistorySidebarProps> = ({
    isCollapsed,
    onToggle,
    user,
    currentSessionId,
    onSessionSelect,
    onNewChat,
    onSessionDelete,
    refreshTrigger = 0,
}) => {
    const [sessions, setSessions] = useState<ChatSession[]>([])
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        loadSessions()
    }, [refreshTrigger])

    const loadSessions = async () => {
        setLoading(true)
        try {
            const data = (await chatAPI.listSessions()) as ChatSession[]
            setSessions(data)

            // Auto-select last active session if available
            if (!currentSessionId && data.length > 0) {
                const lastSessionId = localStorage.getItem('last_session_id')
                if (lastSessionId) {
                    const session = data.find(
                        (s: ChatSession) => s.id === parseInt(lastSessionId)
                    )
                    if (session) {
                        onSessionSelect(session)
                    }
                }
            }
        } catch (error) {
            console.error('Failed to load sessions:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleDeleteSession = async (
        sessionId: number,
        e: React.MouseEvent
    ) => {
        e.stopPropagation()
        if (!confirm('Delete this chat session?')) return

        try {
            await chatAPI.deleteSession(sessionId)
            setSessions(sessions.filter((s) => s.id !== sessionId))
            // Notify parent component about session deletion
            if (onSessionDelete) {
                onSessionDelete(sessionId)
            }
        } catch (error) {
            console.error('Failed to delete session:', error)
            alert('Failed to delete session')
        }
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString)
        const now = new Date()
        const diffMs = now.getTime() - date.getTime()
        const diffMins = Math.floor(diffMs / 60000)
        const diffHours = Math.floor(diffMs / 3600000)
        const diffDays = Math.floor(diffMs / 86400000)

        if (diffMins < 1) return 'Just now'
        if (diffMins < 60) return `${diffMins}m ago`
        if (diffHours < 24) return `${diffHours}h ago`
        if (diffDays < 7) return `${diffDays}d ago`
        return date.toLocaleDateString()
    }

    return (
        <div
            className={cn(
                'h-full bg-gradient-to-b from-slate-800 to-slate-900 text-white transition-all duration-300 ease-in-out flex flex-col shadow-2xl border-r border-white/10',
                isCollapsed ? 'items-center w-16' : 'w-80'
            )}
        >
            {/* Header */}
            <div className="p-4 border-b border-white/10">
                <div className="flex items-center justify-between">
                    {!isCollapsed && (
                        <div className="flex items-center gap-2">
                            <MessageSquare className="w-5 h-5 text-purple-400" />
                            <h2 className="text-lg font-bold">Chat History</h2>
                        </div>
                    )}
                    <button
                        onClick={onToggle}
                        className={cn(
                            'p-2 hover:bg-white/10 rounded-lg transition-colors',
                            isCollapsed ? 'mx-auto' : 'ml-auto'
                        )}
                    >
                        {isCollapsed ? (
                            <PanelLeftOpen className="w-5 h-5" />
                        ) : (
                            <PanelLeftClose className="w-5 h-5" />
                        )}
                    </button>
                </div>
            </div>

            {/* Sessions List */}
            <div className="flex-1 overflow-y-auto p-2">
                {!isCollapsed ? (
                    <div className="space-y-2">
                        {loading ? (
                            <div className="text-center py-8 text-white/60">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2" />
                                <p className="text-sm">Loading sessions...</p>
                            </div>
                        ) : sessions.length === 0 ? (
                            <div className="text-center py-8 text-white/60">
                                <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
                                <p className="text-sm">No chat sessions yet</p>
                                <p className="text-xs mt-1">
                                    Click "New Chat" to start
                                </p>
                            </div>
                        ) : (
                            sessions.map((session) => (
                                <div
                                    key={session.id}
                                    onClick={() => onSessionSelect(session)}
                                    className={cn(
                                        'w-full text-left p-3 rounded-lg transition-all duration-200 group relative cursor-pointer',
                                        currentSessionId === session.id
                                            ? 'bg-gradient-to-r from-purple-600/30 to-blue-600/30 border border-purple-500/50'
                                            : 'bg-white/5 hover:bg-white/10 border border-transparent'
                                    )}
                                    role="button"
                                    tabIndex={0}
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="flex-1 min-w-0">
                                            <h3 className="font-medium text-sm truncate mb-1">
                                                {session.title}
                                            </h3>
                                            <div className="flex items-center justify-between text-xs text-white/50 mt-1">
                                                <span
                                                    className="truncate mr-2"
                                                    title={
                                                        session.collection_name
                                                    }
                                                >
                                                    Collection:{' '}
                                                    {session.collection_name}
                                                </span>
                                                <span className="flex-shrink-0 opacity-75">
                                                    {formatDate(
                                                        session.updated_at
                                                    )}
                                                </span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={(e) =>
                                                handleDeleteSession(
                                                    session.id,
                                                    e
                                                )
                                            }
                                            className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 rounded transition-all"
                                            title="Delete session"
                                        >
                                            <Trash2 className="w-4 h-4 text-red-400" />
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-3 py-2">
                        <button
                            onClick={onNewChat}
                            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                        >
                            <Plus className="w-5 h-5" />
                        </button>
                        {sessions.slice(0, 5).map((session) => (
                            <button
                                key={session.id}
                                onClick={() => onSessionSelect(session)}
                                className={cn(
                                    'p-2 rounded-lg transition-colors',
                                    currentSessionId === session.id
                                        ? 'bg-purple-600/50'
                                        : 'hover:bg-white/10'
                                )}
                            >
                                <MessageSquare className="w-5 h-5" />
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* User Info Footer */}
            <div className="p-3 border-t border-white/10">
                {!isCollapsed ? (
                    <div className="flex items-center gap-3 p-2 bg-white/5 rounded-lg">
                        <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full flex items-center justify-center font-bold text-sm uppercase flex-shrink-0">
                            {user?.email?.charAt(0) || 'U'}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold truncate">
                                {user?.email?.split('@')[0] || 'User'}
                            </p>
                            <p className="text-xs text-white/60 truncate">
                                {user?.email}
                            </p>
                        </div>
                    </div>
                ) : (
                    <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full flex items-center justify-center font-bold text-sm uppercase mx-auto">
                        {user?.email?.charAt(0) || 'U'}
                    </div>
                )}
            </div>
        </div>
    )
}
