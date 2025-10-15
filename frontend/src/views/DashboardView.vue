<!-- frontend/taskflow-frontend/src/views/DashboardView.vue -->
<template>
  <div style="padding: 40px; background: white; min-height: 100vh;">
    <h1>Dashboard Loaded Successfully!</h1>
    
    <div style="margin: 20px 0; padding: 20px; background: #f0f8ff; border-radius: 8px;">
      <h3>Debug Information:</h3>
      <p><strong>Authentication Status:</strong> {{ authData.isAuthenticated ? 'Logged In' : 'Not Logged In' }}</p>
      <p><strong>Current User:</strong> {{ authData.username || 'None' }}</p>
      <p><strong>Token Present:</strong> {{ authData.hasToken ? 'Yes' : 'No' }}</p>
      <p><strong>Page Load Time:</strong> {{ loadTime }}</p>
    </div>

    <div style="margin: 20px 0;">
      <button 
        @click="testAPI" 
        style="background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 4px; margin-right: 10px;"
      >
        Test API Connection
      </button>
      
      <button 
        @click="logout" 
        style="background: #e74c3c; color: white; padding: 10px 20px; border: none; border-radius: 4px;"
      >
        Logout
      </button>
    </div>

    <div style="margin: 20px 0;">
      <h3>Console Logs:</h3>
      <div 
        v-for="(log, index) in logs" 
        :key="index"
        style="background: #f8f9fa; padding: 8px; margin: 4px 0; border-radius: 4px; font-family: monospace; font-size: 12px;"
      >
        {{ log }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const authStore = useAuthStore()

// Component state
const loadTime = ref('')
const logs = ref([])

// Auth data
const authData = reactive({
  isAuthenticated: false,
  username: '',
  hasToken: false
})

// Methods
const addLog = (message) => {
  const timestamp = new Date().toLocaleTimeString()
  logs.value.unshift(`[${timestamp}] ${message}`)
  console.log(message)
}

const updateAuthData = () => {
  authData.isAuthenticated = authStore.isAuthenticated
  authData.username = authStore.currentUser?.username || ''
  authData.hasToken = !!authStore.token
}

const testAPI = async () => {
  addLog('Testing API connection...')
  try {
    const response = await api.get('/api/tasks/')
    addLog(`API test successful: ${response.data.length || 0} tasks found`)
  } catch (error) {
    addLog(`API test failed: ${error.message}`)
  }
}

const logout = async () => {
  addLog('Logging out...')
  try {
    await authStore.logout()
    addLog('Logout successful')
    window.location.href = '/login'
  } catch (error) {
    addLog(`Logout failed: ${error.message}`)
  }
}

// Lifecycle
onMounted(() => {
  const startTime = Date.now()
  loadTime.value = new Date().toLocaleString()
  
  addLog('Dashboard component mounted')
  
  // Initialize auth
  authStore.initializeAuth()
  updateAuthData()
  
  addLog(`Authentication initialized: ${authData.isAuthenticated}`)
  addLog(`Current user: ${authData.username}`)
  addLog(`Token present: ${authData.hasToken}`)
  
  const endTime = Date.now()
  addLog(`Component loaded in ${endTime - startTime}ms`)
  
  // Check if we're being redirected
  setTimeout(() => {
    if (window.location.pathname === '/dashboard') {
      addLog('Still on dashboard page - no redirect detected')
    } else {
      addLog(`Redirected to: ${window.location.pathname}`)
    }
  }, 1000)
})
</script>