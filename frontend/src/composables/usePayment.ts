import { ref, computed } from 'vue'
import { useSessionStore } from '@/stores/session'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export function usePayment() {
  const store = useSessionStore()
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const qrString = ref<string | null>(null)
  const expiresAt = ref<Date | null>(null)
  const countdown = ref<number>(300)

  let pollInterval: number | null = null

  async function createPayment() {
    if (!store.sessionId) {
      error.value = 'Session not found'
      return
    }

    isLoading.value = true
    error.value = null

    try {
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
      
      startPolling()
    } catch (err) {
      error.value = 'Gagal membuat pembayaran'
      console.error('Payment error:', err)
    } finally {
      isLoading.value = false
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
      } else if (data.status === 'failed') {
        store.setPaymentStatus('failed')
        stopPolling()
      }
    } catch (err) {
      console.error('Status check error:', err)
    }
  }

  function startPolling() {
    if (pollInterval) return
    
    pollInterval = window.setInterval(() => {
      checkPaymentStatus()
      countdown.value--
      
      if (countdown.value <= 0) {
        stopPolling()
        store.setPaymentStatus('failed')
      }
    }, 1000)
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  const formattedCountdown = computed(() => {
    const minutes = Math.floor(countdown.value / 60)
    const seconds = countdown.value % 60
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
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
    stopPolling
  }
}
