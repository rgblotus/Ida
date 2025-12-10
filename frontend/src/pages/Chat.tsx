import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChatHistorySidebar } from '../components/sidebar/ChatHistorySidebar'
import { AISettingsSidebar } from '../components/sidebar/AISettingsSidebar'
import { ChatInterface } from '../components/chat/ChatInterface'
import { useAuth } from '../contexts/AuthContext'
import WebGLBackground from '../components/webGL/WebGLBackground'
import { chatAPI, collectionsAPI } from '../services/api'
import type { Message, ChatSession, Collection } from '../types/api'
import { Plus, Home } from 'lucide-react'

export const Chat: React.FC = () => {
    const { user } = useAuth()
    const navigate = useNavigate()
    const [leftCollapsed, setLeftCollapsed] = useState(false)
    const [rightCollapsed, setRightCollapsed] = useState(false)

    // Chat state
    const [currentSession, setCurrentSession] = useState<ChatSession | null>(
        null
    )
    const [messages, setMessages] = useState<Message[]>([])
    const [isLoading, setIsLoading] = useState(false)

    // Configuration state
    const [selectedCollection, setSelectedCollection] =
        useState<Collection | null>(null)
    const [collections, setCollections] = useState<Collection[]>([])
    const [refreshSidebarTrigger, setRefreshSidebarTrigger] = useState(0)

    // Load collections on mount
    useEffect(() => {
        loadCollections()
    }, [])

    // Load messages when session changes
    useEffect(() => {
        if (currentSession) {
            localStorage.setItem(
                'last_session_id',
                currentSession.id.toString()
            )
            loadMessages(currentSession.id)
        } else {
            setMessages([])
        }
    }, [currentSession])

    const loadCollections = async () => {
        try {
            console.log('Loading collections...')
            const data = await collectionsAPI.list()
            console.log('Collections loaded:', data)
            setCollections(data)
            if (data.length > 0 && !selectedCollection) {
                setSelectedCollection(data[0])
                console.log('Selected first collection:', data[0])
            }
        } catch (error) {
            console.error('Failed to load collections:', error)
        }
    }

    const loadMessages = async (sessionId: number) => {
        try {
            const data = await chatAPI.getMessages(sessionId)
            setMessages(data)
        } catch (error) {
            console.error('Failed to load messages:', error)
        }
    }

    const handleNewChat = async () => {
        console.log('handleNewChat called')
        console.log('selectedCollection:', selectedCollection)
        if (!selectedCollection) {
            alert('Please select a collection first')
            return
        }

        try {
            console.log('🔄 Creating session...')
            const session = await chatAPI.createSession(
                selectedCollection.id,
                'ollama_cloud', // Default model, can be changed in AI settings later
                'New Chat'
            )
            console.log('✅ API call successful, session:', session)

            console.log('🔄 Updating currentSession...')
            setCurrentSession(session)
            console.log('✅ currentSession updated')

            console.log('🔄 Clearing messages...')
            setMessages([])
            console.log('✅ messages cleared')

            console.log('🎉 New chat creation complete!')
        } catch (error) {
            console.error('❌ Failed to create session:', error)

            // Check if session was actually created despite the error
            console.log('🔍 Checking if session exists on server...')
            try {
                const sessions = (await chatAPI.listSessions()) as ChatSession[]
                const newSession = sessions.find(
                    (s: ChatSession) => s.title === 'New Chat'
                )
                if (newSession) {
                    console.log(
                        '✅ Session was created on server despite error:',
                        newSession
                    )
                    setCurrentSession(newSession)
                    setMessages([])
                    return
                } else {
                    console.log('❌ Session was not found on server')
                }
            } catch (checkError) {
                console.error(
                    '❌ Could not verify session creation:',
                    checkError
                )
            }

            alert('Failed to create chat session')
        }
    }

    const handleSendMessage = async (message: string) => {
        if (!currentSession) return

        // Check if this is the first message *before* we send it
        const isFirstMessage = messages.length === 0

        // Optimistic Update: Create a temporary user message
        const tempUserMessage: Message = {
            id: Date.now(), // Temporary ID
            role: 'user',
            content: message,
            created_at: new Date().toISOString(),
        }

        // Update state immediately
        setMessages((prev) => [...prev, tempUserMessage])

        setIsLoading(true)
        try {
            await chatAPI.sendMessage(currentSession.id, message)

            // Reload messages to get the real response (and replace our temp message with the real one)
            await loadMessages(currentSession.id)

            // If it was the first message, refresh session info now
            if (isFirstMessage) {
                setRefreshSidebarTrigger((prev) => prev + 1)
                try {
                    const sessions =
                        (await chatAPI.listSessions()) as ChatSession[]
                    const updated = sessions.find(
                        (s) => s.id === currentSession.id
                    )
                    if (updated) {
                        setCurrentSession(updated)
                    }
                } catch (e) {
                    console.error('Failed to refresh session info', e)
                }
            }
        } catch (error) {
            console.error('Failed to send message:', error)
            alert('Failed to send message')
            // Revert optimistic update on failure - reload messages to sync with server
            await loadMessages(currentSession.id)
        } finally {
            setIsLoading(false)
        }
    }

    const handleSessionDelete = (deletedSessionId: number) => {
        // If the deleted session was the current session, clear the chat area
        if (currentSession && currentSession.id === deletedSessionId) {
            setCurrentSession(null)
            setMessages([])
            localStorage.removeItem('last_session_id')
        }
    }

    const handleUpdateMessage = (
        messageId: number,
        updates: Partial<Message>
    ) => {
        setMessages((prev) =>
            prev.map((msg) =>
                msg.id === messageId ? { ...msg, ...updates } : msg
            )
        )
    }

    return (
        <div className="h-screen flex overflow-hidden relative bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
            {/* WebGL Background */}
            <WebGLBackground
                particleCount={1500}
                className="fixed inset-0 w-full h-full opacity-40"
                shaderName="particles"
                shape="sphere"
            />

            {/* Left Sidebar - Chat History */}
            <ChatHistorySidebar
                isCollapsed={leftCollapsed}
                onToggle={() => setLeftCollapsed(!leftCollapsed)}
                user={user}
                currentSessionId={currentSession?.id}
                onSessionSelect={setCurrentSession}
                onNewChat={handleNewChat}
                onSessionDelete={handleSessionDelete}
                refreshTrigger={refreshSidebarTrigger}
            />

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col overflow-hidden relative z-10">
                {/* Header */}
                <div className="bg-white/10 backdrop-blur-xl border-b border-white/20 p-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                                title="Go to Dashboard"
                            >
                                <Home className="w-5 h-5 text-white/80" />
                            </button>

                            <h1 className="text-xl font-bold text-white truncate">
                                {currentSession
                                    ? currentSession.title
                                    : 'RAG Chat'}
                            </h1>
                        </div>

                        <div className="flex items-center gap-4">
                            <select
                                value={selectedCollection?.id || ''}
                                onChange={(e) => {
                                    const collection = collections.find(
                                        (c) => c.id === parseInt(e.target.value)
                                    )
                                    if (collection)
                                        setSelectedCollection(collection)
                                }}
                                className="text-sm bg-white/10 border border-white/20 rounded px-3 py-1 text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
                            >
                                {collections.map((col) => (
                                    <option
                                        key={col.id}
                                        value={col.id}
                                        className="bg-slate-900"
                                    >
                                        {col.name}
                                    </option>
                                ))}
                            </select>

                            <button
                                onClick={handleNewChat}
                                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all duration-200"
                            >
                                <Plus className="w-5 h-5" />
                                <span>New Chat</span>
                            </button>
                        </div>
                    </div>
                </div>

                {/* Chat Interface */}
                <div className="flex-1 min-h-0">
                    <ChatInterface
                        sessionId={currentSession?.id || null}
                        messages={messages}
                        onSendMessage={handleSendMessage}
                        onUpdateMessage={handleUpdateMessage}
                        isLoading={isLoading}
                    />
                </div>
            </div>

            {/* Right Sidebar - AI Settings */}
            <AISettingsSidebar
                isCollapsed={rightCollapsed}
                onToggle={() => setRightCollapsed(!rightCollapsed)}
                currentSession={currentSession}
                onSessionUpdate={setCurrentSession}
            />
        </div>
    )
}
