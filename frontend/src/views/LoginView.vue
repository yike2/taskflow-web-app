<!-- frontend/taskflow-frontend/src/views/LoginView.vue -->
<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>Welcome Back</h2>
        <p class="text-muted">Sign in to continue to TaskFlow</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        size="large"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="Username"
            prefix-icon="User"
            :disabled="loading"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="Password"
            prefix-icon="Lock"
            :disabled="loading"
            @keyup.enter="handleLogin"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p class="text-muted">
          Don't have an account?
          <router-link to="/register" class="register-link">Sign up</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Form reference
const loginFormRef = ref()

// Loading state
const loading = ref(false)

// Form data
const loginForm = reactive({
  username: '',
  password: ''
})

// Form validation rules
const loginRules = {
  username: [
    { required: true, message: 'Please enter your username', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ]
}

// Handle login submission
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    // Validate form
    await loginFormRef.value.validate()
    
    loading.value = true
    console.log('Attempting login with:', loginForm.username)

    // Attempt login
    const result = await authStore.login(loginForm)
    console.log('Login result:', result)
    
    ElMessage.success('Login successful')
    
    // Manual redirect using window.location to avoid router issues
    console.log('Redirecting to dashboard...')
    window.location.href = '/dashboard'
    
  } catch (error) {
    console.error('Login failed:', error)
    ElMessage.error(error.message || 'Login failed. Please try again.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
  z-index: 1000;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h2 {
  color: #2c3e50;
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 28px;
}

.login-form {
  margin-bottom: 24px;
}

.login-button {
  width: 100%;
  height: 44px;
  font-weight: 500;
}

.login-footer {
  text-align: center;
}

.register-link {
  color: #27ae60;
  text-decoration: none;
  font-weight: 500;
}

.register-link:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .login-card {
    padding: 24px;
  }
  
  .login-header h2 {
    font-size: 24px;
  }
}
</style>