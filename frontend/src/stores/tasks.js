import { defineStore } from 'pinia'
import { api } from './auth'

export const useTaskStore = defineStore('tasks', {
    state: () => ({
        tasks: [],
        categories: [],
        stats: {},
        loading: false,
    }),

    getters: {
        pendingTasks: (state) => state.tasks.filter(task => task.status === 'pending'),
        inProgressTasks: (state) => state.tasks.filter(task => task.status === 'in_progress'),
        completedTasks: (state) => state.tasks.filter(task => task.status === 'completed'),

        tasksByCategory: (state) => {
            const grouped = {}
            state.tasks.forEach(task => {
                const category = task.category_name || 'Uncategorized'
                if (!grouped[category]) grouped[category] = []
                grouped[category].push(task)
            })
            return grouped
        },
    },

    actions: {
        // Fetch all tasks
        async fetchTasks() {
            try {
                this.loading = true
                const response = await api.get('/api/tasks/')
                this.tasks = response.data.results || response.data
                return this.tasks
            } catch (error) {
                console.error('Fetch tasks error:', error)
                throw new Error('Failed to fetch tasks')
            } finally {
                this.loading = false
            }
        },

        // Fetch task statistics
        async fetchStats() {
            try {
                const response = await api.get('/api/tasks/statistics/')
                this.stats = response.data
                return this.stats
            } catch (error) {
                console.error('Fetch stats error:', error)
                // Don't throw error for stats, just log it
                this.stats = {
                    total_tasks: 0,
                    pending_tasks: 0,
                    in_progress_tasks: 0,
                    completed_tasks: 0
                }
            }
        },

        // Create new task
        async createTask(taskData) {
            try {
                const response = await api.post('/api/tasks/', taskData)
                this.tasks.unshift(response.data)
                return response.data
            } catch (error) {
                console.error('Create task error:', error)
                const message = error.response?.data?.detail ||
                    error.response?.data?.message ||
                    'Failed to create task'
                throw new Error(message)
            }
        },

        // Update existing task
        async updateTask(taskId, updates) {
            try {
                const response = await api.put(`/api/tasks/${taskId}/`, updates)
                const index = this.tasks.findIndex(task => task.id === taskId)
                if (index !== -1) {
                    this.tasks[index] = response.data
                }
                return response.data
            } catch (error) {
                console.error('Update task error:', error)
                const message = error.response?.data?.detail ||
                    error.response?.data?.message ||
                    'Failed to update task'
                throw new Error(message)
            }
        },

        // Delete task
        async deleteTask(taskId) {
            try {
                await api.delete(`/api/tasks/${taskId}/`)
                this.tasks = this.tasks.filter(task => task.id !== taskId)
            } catch (error) {
                console.error('Delete task error:', error)
                const message = error.response?.data?.detail ||
                    error.response?.data?.message ||
                    'Failed to delete task'
                throw new Error(message)
            }
        },

        // Mark task as completed
        async markCompleted(taskId) {
            try {
                const response = await api.post(`/api/tasks/${taskId}/mark_completed/`)
                const index = this.tasks.findIndex(task => task.id === taskId)
                if (index !== -1) {
                    this.tasks[index] = response.data
                }
                return response.data
            } catch (error) {
                console.error('Mark completed error:', error)
                throw new Error('Failed to mark task as completed')
            }
        },

        // Fetch categories
        async fetchCategories() {
            try {
                const response = await api.get('/api/categories/')
                this.categories = response.data.results || response.data
                return this.categories
            } catch (error) {
                console.error('Fetch categories error:', error)
                throw new Error('Failed to fetch categories')
            }
        },

        // Create new category
        async createCategory(categoryData) {
            try {
                const response = await api.post('/api/categories/', categoryData)
                this.categories.unshift(response.data)
                return response.data
            } catch (error) {
                console.error('Create category error:', error)
                const message = error.response?.data?.detail ||
                    error.response?.data?.message ||
                    'Failed to create category'
                throw new Error(message)
            }
        },

        // Get tasks due today
        async getTodayTasks() {
            try {
                const response = await api.get('/api/tasks/today/')
                return response.data
            } catch (error) {
                console.error('Get today tasks error:', error)
                return []
            }
        },

        // Get overdue tasks
        async getOverdueTasks() {
            try {
                const response = await api.get('/api/tasks/overdue/')
                return response.data
            } catch (error) {
                console.error('Get overdue tasks error:', error)
                return []
            }
        },
    },
})