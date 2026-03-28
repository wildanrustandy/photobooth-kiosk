import { createRouter, createWebHistory } from 'vue-router'
import { useAdminStore } from '@/stores/admin'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/admin/AdminLoginView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: () => import('@/views/admin/AdminDashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/booths/:id',
      name: 'admin-booth-detail',
      component: () => import('@/views/admin/BoothDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/transactions',
      name: 'admin-transactions',
      component: () => import('@/views/admin/TransactionsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/settings',
      name: 'admin-settings',
      component: () => import('@/views/admin/SettingsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      redirect: '/admin/dashboard'
    }
  ]
})

// Navigation guards
router.beforeEach(async (to, _from, next) => {
  const store = useAdminStore()

  // Initialize auth state if not already done
  if (!store.isAuthenticated && localStorage.getItem('admin_token')) {
    await store.initializeAuth()
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !store.isAuthenticated) {
    next('/admin/login')
    return
  }

  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && store.isAuthenticated) {
    next('/admin/dashboard')
    return
  }

  next()
})

export default router
