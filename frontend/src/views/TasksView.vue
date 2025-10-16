<template>
  <div class="tasks-page">
    <div class="page-header">
      <h1>Tasks</h1>
      <button class="btn-primary" @click="showAddDialog = true">
        Add Task
      </button>
    </div>

    <div class="filters">
      <div class="filter-group">
        <label>Status:</label>
        <select v-model="filters.status" @change="loadTasks">
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Priority:</label>
        <select v-model="filters.priority" @change="loadTasks">
          <option value="">All</option>
          <option value="1">Low</option>
          <option value="2">Medium</option>
          <option value="3">High</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Category:</label>
        <select v-model="filters.category" @change="loadTasks">
            <option value="">All</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
        </select>
       </div>

      <div class="search-group">
        <input 
          v-model="searchQuery"
          type="text"
          placeholder="Search tasks..."
          @input="handleSearch"
        />
      </div>
    </div>

    <div v-if="loading" class="loading">
      Loading tasks...
    </div>

    <div v-else-if="tasks.length === 0" class="empty-state">
      <p>No tasks found.</p>
      <button class="btn-secondary" @click="showAddDialog = true">
        Create your first task
      </button>
    </div>

    <div v-else class="tasks-table">
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Status</th>
            <th>Category</th>
            <th>Priority</th>
            <th>Due Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in tasks" :key="task.id">
            <td>
              <div class="task-title">
                {{ task.title }}
                <span v-if="task.description" class="task-desc">
                  {{ task.description.substring(0, 50) }}{{ task.description.length > 50 ? '...' : '' }}
                </span>
              </div>
            </td>
            <td>
              <span class="status-badge" :class="task.status">
                {{ task.status_display }}
              </span>
            </td>
            <td>
                <span v-if="task.category_name" class="category-badge">
                    {{ task.category_name }}
                </span>
                <span v-else class="no-category">-</span>
                </td>
            <td>
              <span class="priority-badge" :class="`priority-${task.priority}`">
                {{ task.priority_display }}
              </span>
            </td>
            <td>
              {{ formatDate(task.due_date) }}
            </td>
            <td>
              <div class="actions">
                <button @click="editTask(task)" class="btn-icon" title="Edit">
                  ✏️
                </button>
                <button @click="toggleComplete(task)" class="btn-icon" :title="task.status === 'completed' ? 'Mark Pending' : 'Mark Complete'">
                  {{ task.status === 'completed' ? '↩️' : '✓' }}
                </button>
                <button @click="deleteTask(task)" class="btn-icon delete" title="Delete">
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Task Dialog -->
    <div v-if="showAddDialog" class="dialog-overlay" @click="showAddDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>Add New Task</h2>
          <button @click="showAddDialog = false" class="close-btn">×</button>
        </div>
        <form @submit.prevent="handleAddTask">
          <div class="form-group">
            <label>Title *</label>
            <input v-model="newTask.title" type="text" required />
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea v-model="newTask.description" rows="3"></textarea>
          </div>

          <div class="form-group">
            <label>Category</label>
            <select v-model="newTask.category">
              <option :value="null">No Category</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Status</label>
              <select v-model="newTask.status">
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <div class="form-group">
              <label>Priority</label>
              <select v-model="newTask.priority">
                <option :value="1">Low</option>
                <option :value="2">Medium</option>
                <option :value="3">High</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Due Date</label>
            <input v-model="newTask.due_date" type="datetime-local" />
          </div>

          <div class="dialog-actions">
            <button type="button" @click="showAddDialog = false" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="submitting">
              {{ submitting ? 'Adding...' : 'Add Task' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Task Dialog (similar structure) -->
    <div v-if="showEditDialog" class="dialog-overlay" @click="showEditDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>Edit Task</h2>
          <button @click="showEditDialog = false" class="close-btn">×</button>
        </div>
        <form @submit.prevent="handleEditTask">
          <div class="form-group">
            <label>Title *</label>
            <input v-model="editingTask.title" type="text" required />
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea v-model="editingTask.description" rows="3"></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Status</label>
              <select v-model="editingTask.status">
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <div class="form-group">
              <label>Priority</label>
              <select v-model="editingTask.priority">
                <option :value="1">Low</option>
                <option :value="2">Medium</option>
                <option :value="3">High</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Due Date</label>
            <input v-model="editingTask.due_date" type="datetime-local" />
          </div>

          <div class="dialog-actions">
            <button type="button" @click="showEditDialog = false" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="submitting">
              {{ submitting ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'

const loading = ref(false)
const submitting = ref(false)
const tasks = ref([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const searchQuery = ref('')
const categories = ref([])

const filters = reactive({
  status: '',
  priority: '',
  category: ''
})

const newTask = reactive({
  title: '',
  description: '',
  status: 'pending',
  priority: 2,
  category: null,
  due_date: ''
})

const editingTask = reactive({
  id: null,
  title: '',
  description: '',
  status: '',
  priority: 2,
  category: null,
  due_date: ''
})

const loadCategories = async () => {
  try {
    const response = await api.get('/api/categories/')
    categories.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const loadTasks = async () => {
  try {
    loading.value = true
    const params = new URLSearchParams()
    
    if (filters.status) params.append('status', filters.status)
    if (filters.priority) params.append('priority', filters.priority)
    if (filters.category) params.append('category', filters.category)
    if (searchQuery.value) params.append('search', searchQuery.value)
    
    const response = await api.get(`/api/tasks/?${params}`)
    
    console.log('Tasks loaded:', response.data)
    
    if (response.data.results) {
      tasks.value = response.data.results
    } else if (Array.isArray(response.data)) {
      tasks.value = response.data
    } else {
      tasks.value = []
    }
    
  } catch (error) {
    console.error('Failed to load tasks:', error)
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const handleAddTask = async () => {
  try {
    submitting.value = true
    console.log('Sending task data:', newTask)
    await api.post('/api/tasks/', newTask)
    
    showAddDialog.value = false
    Object.assign(newTask, {
      title: '',
      description: '',
      status: 'pending',
      priority: 2,
      due_date: ''
    })
    
    await loadTasks()
  } catch (error) {
    console.error('Failed to add task:', error)
    alert('Failed to add task: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

const editTask = (task) => {
  if (!task || !task.id) {
    console.error('Invalid task:', task)
    return
  }
  
  Object.assign(editingTask, {
    id: task.id,
    title: task.title || '',
    description: task.description || '',
    status: task.status || 'pending',
    priority: task.priority || 2,
    due_date: task.due_date ? task.due_date.substring(0, 16) : ''
  })
  showEditDialog.value = true
}

const handleEditTask = async () => {
  try {
    submitting.value = true
    const { id, ...data } = editingTask
    await api.patch(`/api/tasks/${id}/`, data)
    
    showEditDialog.value = false
    await loadTasks()
  } catch (error) {
    console.error('Failed to update task:', error)
    alert('Failed to update task: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

const toggleComplete = async (task) => {
  if (!task || !task.id) return
  
  try {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed'
    await api.patch(`/api/tasks/${task.id}/`, { status: newStatus })
    await loadTasks()
  } catch (error) {
    console.error('Failed to update task:', error)
    alert('Failed to update task status')
  }
}

const deleteTask = async (task) => {
  if (!task || !task.id) return
  if (!confirm(`Delete task "${task.title}"?`)) return
  
  try {
    await api.delete(`/api/tasks/${task.id}/`)
    await loadTasks()
  } catch (error) {
    console.error('Failed to delete task:', error)
    alert('Failed to delete task')
  }
}

const handleSearch = () => {
  loadTasks()
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString()
  } catch {
    return '-'
  }
}

onMounted(() => {
  loadTasks()
  loadCategories()
})
</script>

<style scoped>
.tasks-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
}

.search-group {
  flex: 1;
  max-width: 300px;
}

.search-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
}

.loading,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 16px;
}

.tasks-table {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

th {
  text-align: left;
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
}

td {
  padding: 16px;
  border-bottom: 1px solid #f3f4f6;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover {
  background: #f9fafb;
}

.task-title {
  font-weight: 500;
  color: #1a1a1a;
}

.task-desc {
  display: block;
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.status-badge,
.priority-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.in_progress {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.priority-badge.priority-1 {
  background: #f3f4f6;
  color: #6b7280;
}

.priority-badge.priority-2 {
  background: #fef3c7;
  color: #92400e;
}

.priority-badge.priority-3 {
  background: #fee2e2;
  color: #991b1b;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.btn-icon:hover {
  background: #f3f4f6;
}

.btn-icon.delete:hover {
  background: #fee2e2;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.dialog-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.close-btn:hover {
  background: #f3f4f6;
}

form {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}

.form-group textarea {
  resize: vertical;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
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

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.category-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: #f3f4f6;
  color: #374151;
}

.no-category {
  color: #9ca3af;
  font-size: 14px;
}
</style>