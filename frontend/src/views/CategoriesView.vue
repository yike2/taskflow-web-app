<template>
  <div class="categories-page">
    <div class="page-header">
      <h1>Categories</h1>
      <button class="btn-primary" @click="showAddDialog = true">
        Add Category
      </button>
    </div>

    <div v-if="loading" class="loading">
      Loading categories...
    </div>

    <div v-else-if="categories.length === 0" class="empty-state">
      <p>No categories yet.</p>
      <button class="btn-secondary" @click="showAddDialog = true">
        Create your first category
      </button>
    </div>

    <div v-else class="categories-grid">
      <div 
        v-for="category in categories" 
        :key="category.id"
        class="category-card"
      >
        <div class="category-header">
          <div class="category-info">
            <div 
              class="category-color" 
              :style="{ backgroundColor: category.color }"
            ></div>
            <h3>{{ category.name }}</h3>
          </div>
          <span class="task-count">{{ category.task_count || 0 }} tasks</span>
        </div>
        <div class="category-actions">
          <button @click="editCategory(category)" class="btn-icon">
            Edit
          </button>
          <button @click="deleteCategory(category)" class="btn-icon delete">
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Add Category Dialog -->
    <div v-if="showAddDialog" class="dialog-overlay" @click="showAddDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>Add New Category</h2>
          <button @click="showAddDialog = false" class="close-btn">×</button>
        </div>
        <form @submit.prevent="handleAddCategory">
          <div class="form-group">
            <label>Name *</label>
            <input v-model="newCategory.name" type="text" required />
          </div>

          <div class="form-group">
            <label>Color</label>
            <div class="color-picker">
              <input v-model="newCategory.color" type="color" />
              <span class="color-value">{{ newCategory.color }}</span>
            </div>
          </div>

          <div class="dialog-actions">
            <button type="button" @click="showAddDialog = false" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="submitting">
              {{ submitting ? 'Adding...' : 'Add Category' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Category Dialog -->
    <div v-if="showEditDialog" class="dialog-overlay" @click="showEditDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>Edit Category</h2>
          <button @click="showEditDialog = false" class="close-btn">×</button>
        </div>
        <form @submit.prevent="handleEditCategory">
          <div class="form-group">
            <label>Name *</label>
            <input v-model="editingCategory.name" type="text" required />
          </div>

          <div class="form-group">
            <label>Color</label>
            <div class="color-picker">
              <input v-model="editingCategory.color" type="color" />
              <span class="color-value">{{ editingCategory.color }}</span>
            </div>
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
const categories = ref([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)

const newCategory = reactive({
  name: '',
  color: '#3b82f6'
})

const editingCategory = reactive({
  id: null,
  name: '',
  color: ''
})

const loadCategories = async () => {
  try {
    loading.value = true
    const response = await api.get('/api/categories/')
    categories.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load categories:', error)
    categories.value = []
  } finally {
    loading.value = false
  }
}

const handleAddCategory = async () => {
  try {
    submitting.value = true
    await api.post('/api/categories/', newCategory)
    
    showAddDialog.value = false
    Object.assign(newCategory, {
      name: '',
      color: '#3b82f6'
    })
    
    await loadCategories()
  } catch (error) {
    console.error('Failed to add category:', error)
    alert('Failed to add category: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

const editCategory = (category) => {
  Object.assign(editingCategory, {
    id: category.id,
    name: category.name,
    color: category.color
  })
  showEditDialog.value = true
}

const handleEditCategory = async () => {
  try {
    submitting.value = true
    const { id, ...data } = editingCategory
    await api.patch(`/api/categories/${id}/`, data)
    
    showEditDialog.value = false
    await loadCategories()
  } catch (error) {
    console.error('Failed to update category:', error)
    alert('Failed to update category: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

const deleteCategory = async (category) => {
  if (!confirm(`Delete category "${category.name}"?`)) return
  
  try {
    await api.delete(`/api/categories/${category.id}/`)
    await loadCategories()
  } catch (error) {
    console.error('Failed to delete category:', error)
    alert('Failed to delete category')
  }
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.categories-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
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

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.category-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-color {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 2px solid #ffffff;
  box-shadow: 0 0 0 1px #e5e7eb;
}

.category-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.task-count {
  font-size: 14px;
  color: #6b7280;
}

.category-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
}

.btn-icon:hover {
  background: #e5e7eb;
}

.btn-icon.delete:hover {
  background: #fee2e2;
  border-color: #fecaca;
  color: #dc2626;
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

.form-group input[type="text"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}

.color-picker {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-picker input[type="color"] {
  width: 60px;
  height: 40px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
}

.color-value {
  font-size: 14px;
  color: #6b7280;
  font-family: monospace;
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
</style>