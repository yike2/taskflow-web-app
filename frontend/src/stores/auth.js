import { defineStore } from 'pinia'
import api from '@/api'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        token: null,
        loading: false,
    }),

    getters: {
        isAuthenticated: (state) => !!state.token,
        currentUser: (state) => state.user,
        username: (state) => state.user?.username || '',
    },

    actions: {
        initializeAuth() {
            try {
                const token = localStorage.getItem('token')
                const userStr = localStorage.getItem('user')

                if (token && userStr) {
                    this.token = token
                    this.user = JSON.parse(userStr)
                    console.log('Auth restored from localStorage:', this.user.username)
                } else {
                    console.log('No stored auth data found')
                }
            } catch (error) {
                console.error('Failed to initialize auth:', error)
                this.clearAuth()
            }
        },

        async login(credentials) {
            try {
                this.loading = true
                console.log('Login attempt:', credentials.username)

                const response = await api.post('/api/auth/login/', {
                    username: credentials.username,
                    password: credentials.password,
                })

                console.log('Login response:', response.status)
                console.log('Login data:', response.data)

                const { user, token } = response.data

                if (!token || !user) {
                    throw new Error('Token or user data missing from response')
                }

                this.user = user
                this.token = token
                localStorage.setItem('token', token)
                localStorage.setItem('user', JSON.stringify(user))

                console.log('Login successful:', user.username)
                return response.data
            } catch (error) {
                console.error('Login error:', error)
                const message =
                    error.response?.data?.detail ||
                    error.response?.data?.message ||
                    error.message ||
                    'Login failed'
                throw new Error(message)
            } finally {
                this.loading = false
            }
        },

        async logout() {
            try {
                this.loading = true
                console.log('Logout attempt')

                await api.post('/api/auth/logout/')

                console.log('Logout successful')
            } catch (error) {
                console.error('Logout API error:', error)
            } finally {
                this.clearAuth()
                this.loading = false
            }
        },

        clearAuth() {
            this.user = null
            this.token = null
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            console.log('Auth data cleared')
        },

        async checkAuth() {
            if (!this.token) {
                return false
            }

            try {
                const response = await api.get('/api/auth/profile/')
                this.user = response.data
                return true
            } catch (error) {
                console.error('Token validation failed:', error)
                this.clearAuth()
                return false
            }
        },
    },
})