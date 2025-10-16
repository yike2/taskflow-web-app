import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/TasksView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/categories',  
    name: 'Categories',
    component: () => import('@/views/CategoriesView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth
  const isAuthenticated = authStore.isAuthenticated

  console.log('Route Guard:', {
    to: to.path,
    requiresAuth,
    isAuthenticated,
  })

  if (requiresAuth && !isAuthenticated) {
    console.log('Not authenticated, redirecting to /login')
    next('/login')
  }
  else if (to.path === '/login' && isAuthenticated) {
    console.log('Already authenticated, redirecting to /dashboard')
    next('/dashboard')
  }
  else {
    console.log('Access granted')
    next()
  }
})

export default router