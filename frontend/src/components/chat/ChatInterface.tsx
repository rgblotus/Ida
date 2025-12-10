import React, { useState, useEffect, useRef } from 'react'
import {
    Send,
    Loader2,
    FileText,
    AlertCircle,
    Volume2,
    Languages,
    Copy,
    Edit,
    Check,
    ChevronDown,
    ChevronRight,
} from 'lucide-react'
import { Typewriter } from '../ui/Typewriter'
import type { Message } from '../../types/api'
import { chatAPI } from '../../services/api'

interface ChatInterfaceProps {
    sessionId: number | null
    messages: Message[]
    onSendMessage: (message: string) => Promise<void>
    onUpdateMessage?: (messageId: number, updates: Partial<Message>) => void
    isLoading: boolean
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
    sessionId,
    messages,
    onSendMessage,
    onUpdateMessage,
    isLoading,
}) => {
    const [input, setInput] = useState('')
    const [playingAudioId, setPlayingAudioId] = useState<number | null>(null)
    const [showTranslationIds, setShowTranslationIds] = useState<Set<number>>(
        new Set()
    )
    const [expandedSourceIds, setExpandedSourceIds] = useState<Set<number>>(
        new Set()
    )
    const [copiedId, setCopiedId] = useState<number | null>(null)
    const [noAnimateIds, setNoAnimateIds] = useState<Set<number>>(new Set())
    const audioRef = useRef<HTMLAudioElement | null>(null)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const prevMessagesLengthRef = useRef(0)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        // Detect bulk loads (history) vs new single messages
        if (messages.length > prevMessagesLengthRef.current + 1) {
            // Bulk load: Mark all new messages as "no animate"
            React.startTransition(() => {
                const newIds = messages.map((m) => m.id)
                setNoAnimateIds((prev) => {
                    const next = new Set(prev)
                    newIds.forEach((id) => next.add(id))
                    return next
                })
            })
        }
        prevMessagesLengthRef.current = messages.length

        scrollToBottom()
    }, [messages])

    const handleTypewriterComplete = (id: number) => {
        setNoAnimateIds((prev) => {
            const next = new Set(prev)
            next.add(id)
            return next
        })
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim() || isLoading || !sessionId) return

        const message = input.trim()
        setInput('')
        await onSendMessage(message)
    }

    const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSubmit(e as unknown as React.FormEvent)
        }
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInput(e.target.value)
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto'
            textareaRef.current.style.height =
                textareaRef.current.scrollHeight + 'px'
        }
    }

    const handleCopy = async (text: string, id: number) => {
        await navigator.clipboard.writeText(text)
        setCopiedId(id)
        setTimeout(() => setCopiedId(null), 2000)
    }

    const handleEdit = (text: string) => {
        setInput(text)
    }

    const toggleTranslation = async (id: number) => {
        const newSet = new Set(showTranslationIds)
        const wasVisible = newSet.has(id)

        if (!wasVisible) {
            // Check if translation exists, generate if not
            const message = messages.find((m) => m.id === id)
            if (message && !message.translated_content) {
                try {
                    const result = await chatAPI.translateMessage(id)
                    if (onUpdateMessage && result.translated_content) {
                        onUpdateMessage(id, {
                            translated_content: result.translated_content,
                        })
                    }
                } catch (error) {
                    console.error('Failed to translate message:', error)
                    return
                }
            }
        }

        if (newSet.has(id)) {
            newSet.delete(id)
        } else {
            newSet.add(id)
        }
        setShowTranslationIds(newSet)
    }

    const toggleSources = (id: number) => {
        const newSet = new Set(expandedSourceIds)
        if (newSet.has(id)) {
            newSet.delete(id)
        } else {
            newSet.add(id)
        }
        setExpandedSourceIds(newSet)
    }

    const toggleAudio = async (url: string | undefined, id: number) => {
        let audioUrl = url

        // Generate audio if not available
        if (!audioUrl) {
            try {
                const result = await chatAPI.generateMessageAudio(id)
                audioUrl = result.audio_url
                if (onUpdateMessage && audioUrl) {
                    onUpdateMessage(id, { audio_url: audioUrl })
                }
            } catch (error) {
                console.error('Failed to generate audio:', error)
                return
            }
        }

        if (!audioUrl) return

        if (playingAudioId === id) {
            audioRef.current?.pause()
            setPlayingAudioId(null)
        } else {
            if (audioRef.current) {
                audioRef.current.pause()
            }
            const audio = new Audio(audioUrl)
            audioRef.current = audio
            audio.onended = () => setPlayingAudioId(null)
            audio.play().catch((e) => console.error('Audio play failed', e))
            setPlayingAudioId(id)
        }
    }

    return (
        <div className="flex flex-col h-full">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.length === 0 ? (
                    <div className="flex items-center justify-center h-full">
                        <div className="text-center text-white/60">
                            <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
                            <p className="text-lg">No messages yet</p>
                            <p className="text-sm mt-2">
                                Start a conversation by typing below
                            </p>
                        </div>
                    </div>
                ) : (
                    messages.map((message, idx) => (
                        <div
                            key={message.id}
                            className={`flex gap-3 ${
                                message.role === 'user'
                                    ? 'justify-end'
                                    : 'justify-start'
                            }`}
                        >
                            <div
                                className={`max-w-[90%] rounded-2xl px-6 py-4 relative group ${
                                    message.role === 'user'
                                        ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                                        : 'bg-white/10 backdrop-blur-lg border border-white/20 text-white'
                                }`}
                            >
                                <div className="flex-1">
                                    {message.role === 'assistant' &&
                                    !noAnimateIds.has(message.id) &&
                                    idx === messages.length - 1 ? (
                                        <Typewriter
                                            text={message.content}
                                            onComplete={() =>
                                                handleTypewriterComplete(
                                                    message.id
                                                )
                                            }
                                            onUpdate={scrollToBottom}
                                        />
                                    ) : (
                                        <p className="whitespace-pre-wrap break-words">
                                            {message.content}
                                        </p>
                                    )}

                                    {/* Translation */}
                                    {message.role === 'assistant' &&
                                        showTranslationIds.has(message.id) &&
                                        message.translated_content && (
                                            <div className="mt-2 pt-2 border-t border-white/20">
                                                <p className="text-sm text-yellow-300 mb-1 font-semibold">
                                                    Hindi Translation:
                                                </p>
                                                <p className="whitespace-pre-wrap break-words text-white/90">
                                                    {message.translated_content}
                                                </p>
                                            </div>
                                        )}

                                    {/* Sources (Collapsible) */}
                                    {message.role === 'assistant' &&
                                        message.sources &&
                                        message.sources.length > 0 && (
                                            <div className="mt-4 pt-4 border-t border-white/20">
                                                <button
                                                    onClick={() =>
                                                        toggleSources(
                                                            message.id
                                                        )
                                                    }
                                                    className="flex items-center gap-1 text-xs font-semibold mb-2 text-white/70 hover:text-white transition-colors"
                                                >
                                                    {expandedSourceIds.has(
                                                        message.id
                                                    ) ? (
                                                        <ChevronDown className="w-4 h-4" />
                                                    ) : (
                                                        <ChevronRight className="w-4 h-4" />
                                                    )}
                                                    <span>
                                                        Sources (
                                                        {message.sources.length}
                                                        )
                                                    </span>
                                                </button>

                                                {expandedSourceIds.has(
                                                    message.id
                                                ) && (
                                                    <div className="space-y-2 animate-in fade-in slide-in-from-top-1 duration-200">
                                                        {message.sources.map(
                                                            (source, idx) => (
                                                                <div
                                                                    key={idx}
                                                                    className="text-xs bg-white/5 rounded-lg p-2 border border-white/10"
                                                                >
                                                                    <p className="font-medium text-white/80 mb-1">
                                                                        {source
                                                                            .metadata
                                                                            ?.filename ||
                                                                            'Unknown'}
                                                                        {source
                                                                            .metadata
                                                                            ?.chunk_index !==
                                                                            undefined &&
                                                                            source
                                                                                .metadata
                                                                                ?.total_chunks && (
                                                                                <span className="text-white/50 ml-2">
                                                                                    (Chunk{' '}
                                                                                    {(source
                                                                                        .metadata
                                                                                        .chunk_index as number) +
                                                                                        1}

                                                                                    /
                                                                                    {
                                                                                        source
                                                                                            .metadata
                                                                                            .total_chunks
                                                                                    }

                                                                                    )
                                                                                </span>
                                                                            )}
                                                                    </p>
                                                                    <p className="text-white/60 line-clamp-2">
                                                                        {
                                                                            source.content
                                                                        }
                                                                    </p>
                                                                </div>
                                                            )
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                    {/* LLM Used */}
                                    {message.role === 'assistant' &&
                                        message.llm_used && (
                                            <p className="text-xs text-white/50 mt-2">
                                                Model: {message.llm_used}
                                            </p>
                                        )}
                                </div>
                            </div>
                            <div className="flex flex-col gap-2 pt-2">
                                <button
                                    onClick={() =>
                                        handleCopy(message.content, message.id)
                                    }
                                    className="p-2 hover:bg-white/20 rounded-lg transition-colors opacity-60 hover:opacity-100"
                                    title="Copy message"
                                >
                                    {copiedId === message.id ? (
                                        <Check className="w-4 h-4 text-green-300" />
                                    ) : (
                                        <Copy className="w-4 h-4 text-white/70 hover:text-white" />
                                    )}
                                </button>
                                {message.role === 'user' && (
                                    <button
                                        onClick={() =>
                                            handleEdit(message.content)
                                        }
                                        className="p-2 hover:bg-white/20 rounded-lg transition-colors opacity-60 hover:opacity-100"
                                        title="Edit message"
                                    >
                                        <Edit className="w-4 h-4 text-white/70 hover:text-white" />
                                    </button>
                                )}
                                {message.role === 'assistant' && (
                                    <button
                                        onClick={() =>
                                            toggleAudio(
                                                message.audio_url,
                                                message.id
                                            )
                                        }
                                        className={`p-2 rounded-lg transition-colors opacity-60 hover:opacity-100 ${
                                            playingAudioId === message.id
                                                ? 'bg-green-500/20 text-green-300'
                                                : 'hover:bg-white/20 text-white/70 hover:text-white'
                                        }`}
                                        title="Play/Pause Audio"
                                    >
                                        <Volume2 className="w-4 h-4" />
                                    </button>
                                )}
                                {message.role === 'assistant' && (
                                    <button
                                        onClick={() =>
                                            toggleTranslation(message.id)
                                        }
                                        className={`p-2 rounded-lg transition-colors opacity-60 hover:opacity-100 ${
                                            showTranslationIds.has(message.id)
                                                ? 'bg-yellow-500/20 text-yellow-300'
                                                : 'hover:bg-white/20 text-white/70 hover:text-white'
                                        }`}
                                        title="Translate to Hindi (Offline dictionary)"
                                    >
                                        <Languages className="w-4 h-4" />
                                    </button>
                                )}
                            </div>
                        </div>
                    ))
                )}

                {/* Loading Indicator */}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl px-6 py-4">
                            <div className="flex items-center gap-3">
                                <Loader2 className="w-5 h-5 animate-spin text-purple-400" />
                                <span className="text-white/70">
                                    Thinking...
                                </span>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-white/20 bg-white/5 backdrop-blur-lg p-4">
                {!sessionId ? (
                    <div className="flex items-center justify-center gap-2 text-white/60 py-4">
                        <AlertCircle className="w-5 h-5" />
                        <span>Please create a chat session first</span>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit} className="flex gap-3">
                        <textarea
                            ref={textareaRef}
                            value={input}
                            onChange={handleInputChange}
                            onKeyPress={handleKeyPress}
                            placeholder="Type your message... (Shift+Enter for new line)"
                            className="flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                            rows={1}
                            style={{
                                minHeight: '48px',
                                maxHeight: '200px',
                                height: '48px',
                            }}
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
                        >
                            <Send className="w-5 h-5" />
                            <span>Send</span>
                        </button>
                    </form>
                )}
            </div>
        </div>
    )
}
