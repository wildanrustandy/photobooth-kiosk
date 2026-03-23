import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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
    }
  ]
})

export default router
