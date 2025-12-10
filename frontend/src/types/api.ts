// User types
export interface User {
    id: number
    email: string
}

export interface TokenResponse {
    access_token: string
    refresh_token: string
    token_type: string
    user: User
}

// Collection types
export interface Collection {
    id: number
    name: string
    description?: string
    document_count: number
    created_at: string
    updated_at: string
}

export interface CollectionStats {
    id: number
    name: string
    document_count: number
    total_chunks: number
    milvus_entities: number
    status: string
}

// Document types
export interface Document {
    id: number
    filename: string
    file_type?: string
    file_size?: number
    collection_id: number
    collection_name: string
    status: string
    chunk_count: number
    error_message?: string
    created_at: string
    processed_at?: string
}

export interface UploadResponse {
    message: string
    document_ids: number[]
    collection_name: string
}

// Chat types
export interface ChatSession {
    id: number
    title: string
    collection_id: number
    collection_name: string
    llm_model: string
    temperature: number
    max_tokens: number
    top_k: number
    created_at: string
    updated_at: string
    // AI Settings
    system_prompt?: string
    custom_instructions?: string
    prompt_template?: string
    ai_personality?: string
    response_style?: string
    voice?: string
}

export interface Message {
    id: number
    role: 'user' | 'assistant' | 'system'
    content: string
    sources?: Array<{
        content: string
        metadata?: Record<string, any>
        score?: number
    }>
    llm_used?: string
    created_at: string
    audio_url?: string
    translated_content?: string
}

export interface ChatMessageResponse {
    message_id: number
    content: string
    sources: Array<{
        content: string
        metadata?: Record<string, any>
        score?: number
    }>
    llm_used: string
    created_at: string
    audio_url?: string
    translated_content?: string
}

// LLM types
export interface LLMStatus {
    available_llms: string[]
    ollama_model: string
    primary: string
}

// Weather types
export interface WeatherCurrent {
    city: string
    temperature: number
    feels_like: number
    humidity: number
    pressure: number
    wind_speed: number
    description: string
    icon: string
    timestamp: string
}

export interface WeatherForecast {
    city: string
    forecast: Array<{
        date: string
        temperature: number
        min_temperature: number
        max_temperature: number
        humidity: number
        description: string
        icon: string
    }>
}

// API Error types
export interface APIError {
    detail: string
    status_code?: number
}
