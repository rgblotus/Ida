import axios, { AxiosError } from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'

// Use environment variable or fallback to localhost
const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// Create axios instance
const axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor - Add auth token to requests
axiosInstance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('access_token')
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor - Handle token refresh
axiosInstance.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & {
            _retry?: boolean
        }

        // If error is 401 and we haven't retried yet
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            try {
                const refreshToken = localStorage.getItem('refresh_token')
                if (!refreshToken) {
                    // No refresh token, redirect to login
                    localStorage.removeItem('access_token')
                    localStorage.removeItem('refresh_token')
                    window.location.href = '/login'
                    return Promise.reject(error)
                }

                // Try to refresh the token
                const response = await axios.post(
                    `${API_BASE_URL}/auth/refresh`,
                    {
                        refresh_token: refreshToken,
                    }
                )

                const { access_token, refresh_token: newRefreshToken } =
                    response.data

                // Save new tokens
                localStorage.setItem('access_token', access_token)
                localStorage.setItem('refresh_token', newRefreshToken)

                // Retry original request with new token
                if (originalRequest.headers) {
                    originalRequest.headers.Authorization = `Bearer ${access_token}`
                }
                return axiosInstance(originalRequest)
            } catch (refreshError) {
                // Refresh failed, redirect to login
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                window.location.href = '/login'
                return Promise.reject(refreshError)
            }
        }

        return Promise.reject(error)
    }
)

// Chat API
export const chatAPI = {
    sendMessage: async (sessionId: number, message: string) => {
        const response = await axiosInstance.post('/chat/send', {
            session_id: sessionId,
            message,
        })
        return response.data
    },

    createSession: async (
        collectionId: number,
        llmModel: string = 'ollama_cloud',
        title: string = 'New Chat',
        aiSettings?: {
            system_prompt?: string
            custom_instructions?: string
            prompt_template?: string
            ai_personality?: string
            response_style?: string
        }
    ) => {
        const requestData = {
            collection_id: collectionId,
            llm_model: llmModel,
            title,
            ...aiSettings,
        }
        const response = await axiosInstance.post('/chat/sessions', requestData)
        return response.data
    },

    listSessions: async () => {
        const response = await axiosInstance.get('/chat/sessions')
        return response.data
    },

    getMessages: async (sessionId: number) => {
        const response = await axiosInstance.get(
            `/chat/sessions/${sessionId}/messages`
        )
        return response.data
    },

    deleteSession: async (sessionId: number) => {
        const response = await axiosInstance.delete(
            `/chat/sessions/${sessionId}`
        )
        return response.data
    },

    updateSessionTitle: async (sessionId: number, title: string) => {
        const response = await axiosInstance.patch(
            `/chat/sessions/${sessionId}/title?title=${encodeURIComponent(
                title
            )}`
        )
        return response.data
    },

    updateSessionAISettings: async (
        sessionId: number,
        aiSettings: {
            system_prompt?: string
            custom_instructions?: string
            prompt_template?: string
            ai_personality?: string
            response_style?: string
            llm_model?: string
            temperature?: number
            max_tokens?: number
            top_k?: number
            voice?: string
        }
    ) => {
        const response = await axiosInstance.patch(
            `/chat/sessions/${sessionId}/ai-settings`,
            aiSettings
        )
        return response.data
    },

    generateMessageAudio: async (messageId: number) => {
        const response = await axiosInstance.post(
            `/chat/messages/${messageId}/audio`
        )
        return response.data
    },

    translateMessage: async (messageId: number, targetLang: string = 'hi') => {
        const response = await axiosInstance.post(
            `/chat/messages/${messageId}/translate?target_lang=${targetLang}`
        )
        return response.data
    },
}

// Documents API
export const documentsAPI = {
    upload: async (files: File[], collectionName: string = 'default') => {
        const formData = new FormData()
        files.forEach((file) => formData.append('files', file))

        const response = await axiosInstance.post(
            `/documents/upload?collection_name=${encodeURIComponent(
                collectionName
            )}`,
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            }
        )
        return response.data
    },

    list: async (collectionName?: string, status?: string) => {
        const params = new URLSearchParams()
        if (collectionName) params.append('collection_name', collectionName)
        if (status) params.append('status', status)

        const response = await axiosInstance.get(
            `/documents/list?${params.toString()}`
        )
        return response.data
    },

    get: async (documentId: number) => {
        const response = await axiosInstance.get(`/documents/${documentId}`)
        return response.data
    },

    delete: async (documentId: number) => {
        const response = await axiosInstance.delete(`/documents/${documentId}`)
        return response.data
    },

    batchProcess: async (documentIds: number[]) => {
        const response = await axiosInstance.post('/documents/batch-process', {
            document_ids: documentIds,
        })
        return response.data
    },

    visualize: async (documentId: number) => {
        const response = await axiosInstance.get(
            `/documents/${documentId}/visualize`
        )
        return response.data
    },
}

// Collections API
export const collectionsAPI = {
    create: async (name: string, description?: string) => {
        const response = await axiosInstance.post('/collections/', {
            name,
            description,
        })
        return response.data
    },

    list: async () => {
        const response = await axiosInstance.get('/collections/')
        return response.data
    },

    get: async (collectionId: number) => {
        const response = await axiosInstance.get(`/collections/${collectionId}`)
        return response.data
    },

    getStats: async (collectionId: number) => {
        const response = await axiosInstance.get(
            `/collections/${collectionId}/stats`
        )
        return response.data
    },

    delete: async (collectionId: number, deleteVectors: boolean = true) => {
        const response = await axiosInstance.delete(
            `/collections/${collectionId}?delete_vectors=${deleteVectors}`
        )
        return response.data
    },

    update: async (
        collectionId: number,
        name?: string,
        description?: string
    ) => {
        const params = new URLSearchParams()
        if (name) params.append('name', name)
        if (description) params.append('description', description)

        const response = await axiosInstance.patch(
            `/collections/${collectionId}?${params.toString()}`
        )
        return response.data
    },
}

// LLM Status API
export const llmAPI = {
    getStatus: async () => {
        const response = await axiosInstance.get('/llm/status')
        return response.data
    },
}

// Auth API
export const authAPI = {
    login: async (email: string, password: string) => {
        const response = await axiosInstance.post('/auth/login', {
            email,
            password,
        })
        return response.data
    },

    register: async (email: string, password: string) => {
        const response = await axiosInstance.post('/auth/register', {
            email,
            password,
        })
        return response.data
    },

    refresh: async (refreshToken: string) => {
        const response = await axiosInstance.post('/auth/refresh', {
            refresh_token: refreshToken,
        })
        return response.data
    },

    getMe: async () => {
        const response = await axiosInstance.get('/auth/me')
        return response.data
    },
}

// Weather API
export const weatherAPI = {
    getCurrent: async (city?: string) => {
        const params = city ? `?city=${encodeURIComponent(city)}` : ''
        const response = await axiosInstance.get(`/weather/current${params}`)
        return response.data
    },

    getForecast: async (city?: string, days: number = 5) => {
        const params = new URLSearchParams()
        if (city) params.append('city', city)
        params.append('days', days.toString())
        const response = await axiosInstance.get(
            `/weather/forecast?${params.toString()}`
        )
        return response.data
    },
}

// Settings API
export const settingsAPI = {
    getAISettings: async () => {
        const response = await axiosInstance.get('/settings/ai-settings')
        return response.data
    },

    updateAISettings: async (settings: {
        llm_model: string
        embedding_model: string
        temperature: number
        max_tokens: number
        top_k: number
    }) => {
        const response = await axiosInstance.put(
            '/settings/ai-settings',
            settings
        )
        return response.data
    },

    resetAISettings: async () => {
        const response = await axiosInstance.post('/settings/ai-settings/reset')
        return response.data
    },
}

export default {
    chat: chatAPI,
    documents: documentsAPI,
    collections: collectionsAPI,
    llm: llmAPI,
    auth: authAPI,
    weather: weatherAPI,
    settings: settingsAPI,
}
