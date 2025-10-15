<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Dashboard</h1>
      <button class="btn-primary" @click="showAddTask = true">
        Add Task
      </button>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">Total Tasks</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-value">{{ stats.pending }}</div>
        <div class="stat-label">Pending</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-value">{{ stats.inProgress }}</div>
        <div class="stat-label">In Progress</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-value">{{ stats.completed }}</div>
        <div class="stat-label">Completed</div>
      </div>
    </div>

    <div class="content-section">
      <div class="section-header">
        <h2>Recent Tasks</h2>
        <router-link to="/tasks" class="link">View all</router-link>
      </div>
      
      <div v-if="loading" class="loading">Loading tasks...</div>
      
      <div v-else-if="recentTasks.length === 0" class="empty-state">
        <p>No tasks yet.</p>
        <button class="btn-secondary" @click="showAddTask = true">
          Create your first task
        </button>
      </div>
      
      <div v-else class="task-list">
        <div 
          v-for="task in recentTasks" 
          :key="task.id"
          class="task-item"
        >
          <div class="task-content">
            <h3>{{ task.title }}</h3>
            <p v-if="task.description">{{ task.description }}</p>
          </div>
          <div class="task-meta">
            <span class="task-status" :class="task.status">
              {{ task.status_display }}
            </span>
            <span class="task-priority">
              Priority: {{ task.priority }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="actions">
      <button @click="testConnection" class="btn-outline">
        Test API
      </button>
      <button @click="handleLogout" class="btn-outline">
        Logout
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const showAddTask = ref(false)
const recentTasks = ref([])

const stats = reactive({
  total: 0,
  pending: 0,
  inProgress: 0,
  completed: 0
})

const loadDashboardData = async () => {
  try {
    loading.value = true
    
    const [tasksResponse, statsResponse] = await Promise.all([
      api.get('/api/tasks/'),
      api.get('/api/tasks/statistics/')
    ])
    
    recentTasks.value = tasksResponse.data.slice(0, 5)
    
    stats.total = statsResponse.data.total_tasks
    stats.pending = statsResponse.data.pending_tasks
    stats.inProgress = statsResponse.data.in_progress_tasks
    stats.completed = statsResponse.data.completed_tasks
    
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  } finally {
    loading.value = false
  }
}

const testConnection = async () => {
  try {
    const response = await api.get('/api/tasks/')
    alert(`API works! Found ${response.data.length} tasks`)
  } catch (error) {
    alert('API error: ' + error.message)
  }
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.dashboard-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
}

.stat-value {
  font-size: 36px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
}

.content-section {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 14px;
}

.link:hover {
  text-decoration: underline;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

.empty-state {
  text-align: center;
  padding: 40px;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 16px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.task-item:hover {
  background: #f9fafb;
}

.task-content h3 {
  font-size: 16px;
  font-weight: 500;
  color: #1a1a1a;
  margin: 0 0 4px 0;
}

.task-content p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.task-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.task-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.task-status.pending {
  background: #fef3c7;
  color: #92400e;
}

.task-status.in_progress {
  background: #dbeafe;
  color: #1e40af;
}

.task-status.completed {
  background: #d1fae5;
  color: #065f46;
}

.task-priority {
  font-size: 13px;
  color: #6b7280;
}

.actions {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #f3f4f6;
  color: #1a1a1a;
  border: 1px solid #e5e7eb;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-outline {
  background: white;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.btn-outline:hover {
  background: #f9fafb;
}
</style>