import { ref, computed, onUnmounted } from 'vue'
import { useSessionStore } from '@/stores/session'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const countdown = ref<number>(300)
let pollInterval: number | null = null
let countdownInterval: number | null = null

export function usePayment() {
  const store = useSessionStore()
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const qrString = ref<string | null>(null)
  const expiresAt = ref<Date | null>(null)

  async function createPayment() {
    isLoading.value = true
    error.value = null

    try {
      if (!store.sessionId) {
        store.setSessionId(`demo-session-${Date.now()}`)
      }

      const response = await fetch(`${API_BASE}/payments/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: store.sessionId })
      })

      if (!response.ok) throw new Error('Failed to create payment')

      const data = await response.json()
      qrString.value = data.qr_string
      expiresAt.value = new Date(data.expires_at)
      store.setPaymentId(data.payment_id)
      store.setPaymentStatus('pending')
    } catch (err) {
      qrString.value = 'demo-qr-string'
      store.setPaymentId(`demo-payment-${Date.now()}`)
      store.setPaymentStatus('pending')
      console.log('Demo mode: Payment simulation enabled')
    } finally {
      isLoading.value = false
      startCountdown()
      startPolling()
    }
  }

  function startCountdown() {
    if (countdownInterval) return
    
    countdown.value = 300
    countdownInterval = window.setInterval(() => {
      countdown.value--
      
      if (countdown.value <= 0) {
        stopCountdown()
        stopPolling()
        store.setPaymentStatus('failed')
      }
    }, 1000)
  }

  function stopCountdown() {
    if (countdownInterval) {
      clearInterval(countdownInterval)
      countdownInterval = null
    }
  }

  async function checkPaymentStatus() {
    if (!store.paymentId) return

    try {
      const response = await fetch(`${API_BASE}/payments/${store.paymentId}/status`)
      
      if (!response.ok) throw new Error('Failed to check status')

      const data = await response.json()
      
      if (data.status === 'success') {
        store.setPaymentStatus('success')
        stopPolling()
        stopCountdown()
      } else if (data.status === 'failed') {
        store.setPaymentStatus('failed')
        stopPolling()
        stopCountdown()
      }
    } catch {
      console.log('Demo mode: Payment status check skipped')
    }
  }

  function startPolling() {
    if (pollInterval) return
    
    pollInterval = window.setInterval(() => {
      checkPaymentStatus()
    }, 2000)
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  function simulatePaymentSuccess() {
    store.setPaymentStatus('success')
    stopPolling()
    stopCountdown()
  }

  const formattedCountdown = computed(() => {
    const minutes = Math.floor(countdown.value / 60)
    const seconds = countdown.value % 60
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  })

  onUnmounted(() => {
    stopPolling()
    stopCountdown()
  })

  return {
    isLoading,
    error,
    qrString,
    expiresAt,
    countdown,
    formattedCountdown,
    createPayment,
    checkPaymentStatus,
    startPolling,
    stopPolling,
    simulatePaymentSuccess
  }
}
