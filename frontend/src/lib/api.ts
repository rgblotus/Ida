import { authAPI } from '../services/api'
import type { TokenResponse, User } from '../types/api'

// Re-export types for backward compatibility
export type { User }
export type AuthResponse = TokenResponse

class ApiClient {
    // Auth endpoints
    async register(email: string, password: string): Promise<AuthResponse> {
        return await authAPI.register(email, password)
    }

    async login(email: string, password: string): Promise<AuthResponse> {
        return await authAPI.login(email, password)
    }

    async getCurrentUser(): Promise<User> {
        return await authAPI.getMe()
    }

    async refreshToken(refreshToken: string): Promise<AuthResponse> {
        return await authAPI.refresh(refreshToken)
    }
}

export const apiClient = new ApiClient()

