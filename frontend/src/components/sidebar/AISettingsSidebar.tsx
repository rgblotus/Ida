import React, { useState, useEffect, startTransition } from 'react'
import {
    PanelRightClose,
    PanelRightOpen,
    Brain,
    MessageSquare,
    Sparkles,
    Bot,
    FileText,
    Palette,
    Mic,
} from 'lucide-react'
import { cn } from '../../lib/utils'
import { chatAPI } from '../../services/api'
import type { ChatSession } from '../../types/api'

interface AISettingsSidebarProps {
    isCollapsed: boolean
    onToggle: () => void
    currentSession?: ChatSession | null
    onSessionUpdate?: (updatedSession: ChatSession) => void
}

// Combined AI Style options (reduces redundancy between personality and response style)
const AI_STYLES = [
    {
        id: 'professional',
        name: 'Professional',
        description: 'Formal, expert, structured responses',
        icon: '👔',
    },
    {
        id: 'friendly',
        name: 'Friendly',
        description: 'Warm, approachable, conversational',
        icon: '😊',
    },
    {
        id: 'creative',
        name: 'Creative',
        description: 'Imaginative, innovative, detailed',
        icon: '🎨',
    },
    {
        id: 'concise',
        name: 'Concise',
        description: 'Brief, direct, efficient',
        icon: '📝',
    },
]

const PROMPT_TEMPLATES = [
    {
        id: 'default',
        name: 'General Assistant',
        description: 'Balanced, versatile responses',
        icon: '🤖',
    },
    {
        id: 'technical',
        name: 'Technical Expert',
        description: 'Deep technical and analytical focus',
        icon: '⚙️',
    },
    {
        id: 'business',
        name: 'Business Professional',
        description: 'Professional business insights',
        icon: '💼',
    },
]

const VOICE_OPTIONS = [
    {
        id: 'auto',
        name: 'Auto Select',
        description: 'Default voice (US English)',
        icon: '🎯',
    },
    {
        id: 'en-us',
        name: 'US English',
        description: 'American English pronunciation',
        icon: '🇺🇸',
    },
    {
        id: 'en-gb',
        name: 'British English',
        description: 'British English pronunciation',
        icon: '🇬🇧',
    },
]

export const AISettingsSidebar: React.FC<AISettingsSidebarProps> = ({
    isCollapsed,
    onToggle,
    currentSession,
    onSessionUpdate,
}) => {
    const [systemPrompt, setSystemPrompt] = useState('')
    const [customInstructions, setCustomInstructions] = useState('')
    const [selectedTemplate, setSelectedTemplate] = useState('default')
    const [selectedStyle, setSelectedStyle] = useState('professional')
    const [selectedLLMModel, setSelectedLLMModel] = useState('ollama_cloud')
    const [temperature, setTemperature] = useState(7)
    const [maxTokens, setMaxTokens] = useState(2000)
    const [topK, setTopK] = useState(5)
    const [selectedVoice, setSelectedVoice] = useState('auto')
    const [saveStatus, setSaveStatus] = useState<
        'idle' | 'saving' | 'saved' | 'error'
    >('idle')

    // Load session AI settings when session changes
    useEffect(() => {
        if (currentSession) {
            // Batch state updates to avoid cascading renders
            startTransition(() => {
                setSystemPrompt(currentSession.system_prompt || '')
                setCustomInstructions(currentSession.custom_instructions || '')
                setSelectedTemplate(currentSession.prompt_template || 'default')
                setSelectedStyle(
                    currentSession.ai_personality || 'professional'
                )
                setSelectedLLMModel(currentSession.llm_model || 'ollama_cloud')
                setTemperature(currentSession.temperature || 7)
                setMaxTokens(currentSession.max_tokens || 2000)
                setTopK(currentSession.top_k || 5)
                setSelectedVoice(currentSession.voice || 'auto')
            })
        } else {
            // Reset to defaults when no session
            startTransition(() => {
                setSystemPrompt('')
                setCustomInstructions('')
                setSelectedTemplate('default')
                setSelectedStyle('professional')
                setSelectedLLMModel('ollama_cloud')
                setTemperature(7)
                setMaxTokens(2000)
                setTopK(5)
                setSelectedVoice('auto')
            })
        }
    }, [currentSession?.id])

    const saveSettings = async () => {
        if (!currentSession) return

        setSaveStatus('saving')
        try {
            await chatAPI.updateSessionAISettings(currentSession.id, {
                system_prompt: systemPrompt || undefined,
                custom_instructions: customInstructions || undefined,
                prompt_template: selectedTemplate,
                ai_personality: selectedStyle,
                response_style: selectedStyle, // Map style to both for compatibility
                llm_model: selectedLLMModel,
                temperature: temperature / 10, // Convert from UI scale (0-20) to API scale (0-2)
                max_tokens: maxTokens,
                top_k: topK,
                voice: selectedVoice,
            })

            // Update the session in parent component
            const updatedSession = {
                ...currentSession,
                system_prompt: systemPrompt || undefined,
                custom_instructions: customInstructions || undefined,
                prompt_template: selectedTemplate,
                ai_personality: selectedStyle,
                response_style: selectedStyle,
                llm_model: selectedLLMModel,
                temperature: temperature, // Keep in UI scale (0-20), backend handles conversion
                max_tokens: maxTokens,
                top_k: topK,
                voice: selectedVoice,
            }
            onSessionUpdate?.(updatedSession)

            setSaveStatus('saved')
            setTimeout(() => setSaveStatus('idle'), 2000)
        } catch (error) {
            console.error('Failed to save AI settings:', error)
            setSaveStatus('error')
            setTimeout(() => setSaveStatus('idle'), 2000)
        }
    }

    const resetToDefaults = () => {
        setSystemPrompt('')
        setCustomInstructions('')
        setSelectedTemplate('default')
        setSelectedStyle('professional')
        setSelectedLLMModel('ollama_cloud')
        setTemperature(7)
        setMaxTokens(2000)
        setTopK(5)
        setSelectedVoice('auto')
    }

    return (
        <div
            className={cn(
                'h-full bg-gradient-to-b from-indigo-600 to-purple-700 text-white transition-all duration-300 ease-in-out flex flex-col shadow-2xl border-l border-white/10',
                isCollapsed ? 'items-center w-16' : 'w-80'
            )}
        >
            {/* Header */}
            <div className="p-4 border-b border-white/10">
                <div className="flex items-center justify-between">
                    <button
                        onClick={onToggle}
                        className={cn(
                            'p-2 hover:bg-white/10 rounded-lg transition-colors',
                            isCollapsed ? 'mx-auto' : ''
                        )}
                    >
                        {isCollapsed ? (
                            <PanelRightOpen className="w-5 h-5" />
                        ) : (
                            <PanelRightClose className="w-5 h-5" />
                        )}
                    </button>
                    {!isCollapsed && (
                        <div className="flex items-center gap-2">
                            <Sparkles className="w-5 h-5 text-purple-300" />
                            <h2 className="text-lg font-bold">AI Settings</h2>
                        </div>
                    )}
                </div>
            </div>

            {/* Body */}
            <div className="flex-1 p-4 overflow-y-auto">
                {!isCollapsed ? (
                    <div className="space-y-4">
                        {/* Session Info */}
                        {currentSession && (
                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 border border-white/20">
                                <div className="flex items-center gap-2 mb-2">
                                    <MessageSquare className="w-4 h-4 text-blue-300" />
                                    <span className="text-xs font-semibold">
                                        Current Session
                                    </span>
                                </div>
                                <p className="text-xs text-white/80 truncate mb-1">
                                    {currentSession.title}
                                </p>
                                <div className="space-y-1 text-xs text-white/60">
                                    <p>
                                        <strong>Collection:</strong>{' '}
                                        {currentSession.collection_name}
                                    </p>
                                    <p>
                                        <strong>LLM Model:</strong>{' '}
                                        {currentSession.llm_model}
                                    </p>
                                    <p>
                                        <strong>AI Style:</strong>{' '}
                                        {currentSession.ai_personality ||
                                            'Not set'}
                                    </p>
                                    <p>
                                        <strong>Temperature:</strong>{' '}
                                        {currentSession.temperature / 10}
                                    </p>
                                    <p>
                                        <strong>Max Tokens:</strong>{' '}
                                        {currentSession.max_tokens}
                                    </p>
                                    <p>
                                        <strong>Top K:</strong>{' '}
                                        {currentSession.top_k}
                                    </p>
                                    <p>
                                        <strong>Voice:</strong>{' '}
                                        {currentSession.voice || 'Not set'}
                                    </p>
                                </div>
                            </div>
                        )}

                        {/* System Prompt */}
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                            <h3 className="text-sm font-bold text-white/90 mb-3 flex items-center gap-2">
                                <Bot className="w-4 h-4" />
                                System Prompt
                            </h3>
                            <textarea
                                value={systemPrompt}
                                onChange={(e) =>
                                    setSystemPrompt(e.target.value)
                                }
                                placeholder="Enter custom system instructions for the AI..."
                                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/50 resize-none"
                                rows={3}
                                disabled={!currentSession}
                            />
                            <p className="text-xs text-white/60 mt-2">
                                Define the AI's core behavior and personality
                            </p>
                        </div>

                        {/* Custom Instructions */}
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                            <h3 className="text-sm font-bold text-white/90 mb-3 flex items-center gap-2">
                                <FileText className="w-4 h-4" />
                                Custom Instructions
                            </h3>
                            <textarea
                                value={customInstructions}
                                onChange={(e) =>
                                    setCustomInstructions(e.target.value)
                                }
                                placeholder="Additional instructions or context..."
                                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/50 resize-none"
                                rows={2}
                                disabled={!currentSession}
                            />
                            <p className="text-xs text-white/60 mt-2">
                                Extra guidelines for this specific chat
                            </p>
                        </div>

                        {/* AI Style */}
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                            <h3 className="text-sm font-bold text-white/90 mb-3 flex items-center gap-2">
                                <Sparkles className="w-4 h-4" />
                                AI Style
                            </h3>
                            <div className="grid grid-cols-1 gap-2">
                                {AI_STYLES.map((style) => (
                                    <label
                                        key={style.id}
                                        className={cn(
                                            'flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-colors',
                                            selectedStyle === style.id
                                                ? 'bg-purple-500/30 border border-purple-400'
                                                : 'hover:bg-white/10'
                                        )}
                                    >
                                        <input
                                            type="radio"
                                            name="aiStyle"
                                            value={style.id}
                                            checked={selectedStyle === style.id}
                                            onChange={(e) =>
                                                setSelectedStyle(e.target.value)
                                            }
                                            disabled={!currentSession}
                                            className="text-purple-400 focus:ring-purple-400"
                                        />
                                        <div className="flex items-center gap-2">
                                            <span className="text-lg">
                                                {style.icon}
                                            </span>
                                            <div>
                                                <div className="text-sm font-medium">
                                                    {style.name}
                                                </div>
                                                <div className="text-xs text-white/60">
                                                    {style.description}
                                                </div>
                                            </div>
                                        </div>
                                    </label>
                                ))}
                            </div>
                        </div>

                        {/* Prompt Template */}
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                            <h3 className="text-sm font-bold text-white/90 mb-3 flex items-center gap-2">
                                <Brain className="w-4 h-4" />
                                Prompt Template
                            </h3>
                            <select
                                value={selectedTemplate}
                                onChange={(e) =>
                                    setSelectedTemplate(e.target.value)
                                }
                                disabled={!currentSession}
                                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-white/50"
                            >
                                {PROMPT_TEMPLATES.map((template) => (
                                    <option
                                        key={template.id}
                                        value={template.id}
                                        className="bg-indigo-900"
                                    >
                                        {template.icon} {template.name} -{' '}
                                        {template.description}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Model Settings */}
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                            <h3 className="text-sm font-bold text-white/90 mb-3 flex items-center gap-2">
                                <Bot className="w-4 h-4" />
                                Model Settings
                            </h3>
                            <div className="space-y-3">
                                {/* LLM Model */}
                                <div>
                                    <label className="block text-xs text-white/80 mb-1">
                                        LLM Model
                                    </label>
                                    <select
                                        value={selectedLLMModel}
                                        onChange={(e) =>
                                            setSelectedLLMModel(e.target.value)
                                        }
                                        disabled={!currentSession}
                                        className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-white/50"
                                    >
                                        <option
                                            value="ollama_cloud"
                                            className="bg-indigo-900"
                                        >
                                            Ollama Cloud
                                        </option>
                                        <option
                                            value="ollama_local"
                                            className="bg-indigo-900"
                                        >
                                            Ollama Local
                                        </option>
                                        <option
                                            value="openai"
                                            className="bg-indigo-900"
                                        >
                                            OpenAI
                                        </option>
                                    </select>
                                </div>

                                {/* Temperature */}
                                <div>
                                    <label className="block text-xs text-white/80 mb-1">
                                        Temperature:{' '}
                                        {(temperature / 10).toFixed(1)}
                                    </label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="20"
                                        value={temperature}
                                        onChange={(e) =>
                                            setTemperature(
                                                Number(e.target.value)
                                            )
                                        }
                                        disabled={!currentSession}
                                        className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
                                    />
                                    <div className="flex justify-between text-xs text-white/60 mt-1">
                                        <span>0.0</span>
                                        <span>2.0</span>
                                    </div>
                                </div>

                                {/* Max Tokens */}
                                <div>
                                    <label className="block text-xs text-white/80 mb-1">
                                        Max Tokens
                                    </label>
                                    <input
                                        type="number"
                                        min="100"
                                        max="8000"
                                        value={maxTokens}
                                        onChange={(e) =>
                                            setMaxTokens(Number(e.target.value))
                                        }
                                        disabled={!currentSession}
                                        className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-white/50"
                                    />
                                </div>

                                {/* Top K */}
                                <div>
                                    <label className="block text-xs text-white/80 mb-1">
                                        Top K
                                    </label>
                                    <input
                                        type="number"
                                        min="1"
                                        max="20"
                                        value={topK}
                                        onChange={(e) =>
                                            setTopK(Number(e.target.value))
                                        }
                                        disabled={!currentSession}
                                        className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-white/50"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Voice Settings */}
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                            <h3 className="text-sm font-bold text-white/90 mb-3 flex items-center gap-2">
                                <Mic className="w-4 h-4" />
                                Voice Settings
                            </h3>
                            <div className="space-y-2">
                                <label className="block text-xs text-white/80 mb-2">
                                    Text-to-Speech Voice
                                </label>
                                <select
                                    value={selectedVoice}
                                    onChange={(e) =>
                                        setSelectedVoice(e.target.value)
                                    }
                                    disabled={!currentSession}
                                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-white/50"
                                >
                                    {VOICE_OPTIONS.map((voice) => (
                                        <option
                                            key={voice.id}
                                            value={voice.id}
                                            className="bg-indigo-900"
                                        >
                                            {voice.icon} {voice.name} -{' '}
                                            {voice.description}
                                        </option>
                                    ))}
                                </select>
                                <p className="text-xs text-white/60">
                                    Choose the voice for AI speech responses
                                    (espeak TTS)
                                </p>
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="space-y-2">
                            <button
                                onClick={saveSettings}
                                disabled={
                                    !currentSession || saveStatus === 'saving'
                                }
                                className={cn(
                                    'w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg transition-all font-medium border',
                                    saveStatus === 'saved'
                                        ? 'bg-green-600 border-green-500'
                                        : saveStatus === 'error'
                                        ? 'bg-red-600 border-red-500'
                                        : !currentSession
                                        ? 'bg-gray-600 border-gray-500 cursor-not-allowed'
                                        : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 border-transparent'
                                )}
                            >
                                {saveStatus === 'saving' && (
                                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                )}
                                {saveStatus === 'saved' && (
                                    <Sparkles className="w-4 h-4" />
                                )}
                                <span className="text-sm">
                                    {saveStatus === 'saving'
                                        ? 'Saving...'
                                        : saveStatus === 'saved'
                                        ? 'Saved!'
                                        : saveStatus === 'error'
                                        ? 'Error!'
                                        : !currentSession
                                        ? 'Select a Chat'
                                        : 'Save Settings'}
                                </span>
                            </button>

                            <button
                                onClick={resetToDefaults}
                                disabled={!currentSession}
                                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors border border-white/20 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <PanelRightClose className="w-4 h-4" />
                                <span className="text-sm font-medium">
                                    Reset to Defaults
                                </span>
                            </button>
                        </div>

                        {/* Status Message */}
                        {!currentSession && (
                            <div className="bg-yellow-500/20 backdrop-blur-sm rounded-xl p-3 border border-yellow-500/30">
                                <p className="text-xs text-yellow-200 text-center">
                                    Select or create a chat session to customize
                                    AI settings
                                </p>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-4 py-2">
                        <div className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                            <Brain className="w-5 h-5" />
                        </div>
                        <div className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                            <Sparkles className="w-5 h-5" />
                        </div>
                        <div className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                            <Bot className="w-5 h-5" />
                        </div>
                        <div className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                            <Mic className="w-5 h-5" />
                        </div>
                        <div className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                            <Palette className="w-5 h-5" />
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
