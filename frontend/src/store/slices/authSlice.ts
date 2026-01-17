import { createSlice } from '@reduxjs/toolkit'

interface AuthState {
  accessToken: string | null
  isInitialized: boolean
  email: string | null
}

const initialState: AuthState = {
  accessToken: null,
  isInitialized: false,
  email: null,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setAccessToken: (state, action) => {
      // Handle string, or objects with jwt_token (refresh) or access_token (login)
      const payload = action.payload as string | { jwt_token?: string; access_token?: string }
      if (typeof payload === 'string') {
        state.accessToken = payload
      } else if (payload.jwt_token) {
        state.accessToken = payload.jwt_token
      } else if (payload.access_token) {
        state.accessToken = payload.access_token
      }
      state.isInitialized = true
    },
    clearAccessToken: (state) => {
      state.accessToken = null
      state.email = null
      state.isInitialized = true
    },
    setUserData: (state, action) => {
      state.email = action.payload.email || null
    },
    setInitialized: (state) => {
      state.isInitialized = true
    },
  },
})

export const { setAccessToken, clearAccessToken, setUserData, setInitialized } = authSlice.actions
export default authSlice.reducer
