import api from './axios'

export interface SignupData {
  email: string
  password: string
  firstName: string
  lastName: string
}

export interface LoginData {
  email: string
  password: string
}

export interface SignupResponse {
  id: string
  email: string
  firstName: string
  lastName: string
  isActive: boolean
  createdAt: string
  lastLoginAt: string | null
}

export interface LoginResponse {
  access_token: string
  token_type: string
  email: string
  firstName: string
  lastName: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  email: string
  firstName: string
  lastName: string
}

export const authApi = {
  signup: async (data: SignupData): Promise<SignupResponse> => {
    const response = await api.post<SignupResponse>('/api/auth/register', data)
    return response.data
  },

  login: async (data: LoginData): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/api/auth/login', data)
    return response.data
  },

  logout: async (): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/api/auth/logout')
    return response.data
  },
}
