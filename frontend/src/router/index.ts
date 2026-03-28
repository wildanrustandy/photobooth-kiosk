import { createRouter, createWebHistory } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { useDeviceStore } from '@/stores/device'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Device Setup Routes
    {
      path: '/device-setup',
      name: 'device-setup',
      component: () => import('@/views/DeviceSetupView.vue'),
      meta: { requiresDevice: false }
    },
    {
      path: '/waiting-assignment',
      name: 'waiting-assignment',
      component: () => import('@/views/WaitingAssignmentView.vue'),
      meta: { requiresDevice: true, requiresAssignment: false }
    },
    {
      path: '/session-taken',
      name: 'session-taken',
      component: () => import('@/views/SessionTakenView.vue')
    },
    // Photobooth Kiosk Routes
    {
      path: '/',
      name: 'landing',
      component: () => import('@/views/LandingView.vue')
    },
    {
      path: '/print-count',
      name: 'print-count',
      component: () => import('@/views/PrintCountView.vue')
    },
    {
      path: '/payment',
      name: 'payment',
      component: () => import('@/views/PaymentView.vue')
    },
    {
      path: '/photo-session',
      name: 'photo-session',
      component: () => import('@/views/PhotoSessionView.vue')
    },
    {
      path: '/preview',
      name: 'preview',
      component: () => import('@/views/PreviewView.vue')
    },
    // Admin Panel Routes
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/admin/AdminLoginView.vue'),
      meta: { requiresGuest: true, layout: 'admin' }
    },
    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: () => import('@/views/admin/AdminDashboardView.vue'),
      meta: { requiresAuth: true, layout: 'admin' }
    },
    {
      path: '/admin/booths/:id',
      name: 'admin-booth-detail',
      component: () => import('@/views/admin/BoothDetailView.vue'),
      meta: { requiresAuth: true, layout: 'admin' }
    },
    {
      path: '/admin/transactions',
      name: 'admin-transactions',
      component: () => import('@/views/admin/TransactionsView.vue'),
      meta: { requiresAuth: true, layout: 'admin' }
    },
    {
      path: '/admin/settings',
      name: 'admin-settings',
      component: () => import('@/views/admin/SettingsView.vue'),
      meta: { requiresAuth: true, layout: 'admin' }
    },
    {
      path: '/admin',
      redirect: '/admin/dashboard'
    }
  ]
})

// Navigation guards
router.beforeEach(async (to, _from, next) => {
  // Initialize device store
  const deviceStore = useDeviceStore()

  // Handle admin routes
  if (to.path.startsWith('/admin')) {
    const adminStore = useAdminStore()

    // Initialize auth state if not already done
    if (!adminStore.isAuthenticated && localStorage.getItem('admin_token')) {
      await adminStore.initializeAuth()
    }

    // Check if route requires authentication
    if (to.meta.requiresAuth && !adminStore.isAuthenticated) {
      next('/admin/login')
      return
    }

    // Check if route requires guest (not authenticated)
    if (to.meta.requiresGuest && adminStore.isAuthenticated) {
      next('/admin/dashboard')
      return
    }
  }

  // Handle photobooth kiosk routes (excluding device setup routes)
  if (!to.path.startsWith('/admin') &&
      !to.path.startsWith('/device-setup') &&
      !to.path.startsWith('/waiting-assignment') &&
      !to.path.startsWith('/session-taken')) {

    // Check if device exists
    if (!deviceStore.has_device) {
      next('/device-setup')
      return
    }

    // Check if device is assigned to a booth
    if (!deviceStore.is_assigned) {
      next('/waiting-assignment')
      return
    }
  }

  // Allow device setup routes even without device
  if (to.meta.requiresDevice === false) {
    next()
    return
  }

  next()
})

export default router
