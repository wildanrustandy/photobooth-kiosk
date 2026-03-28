import { ref, computed, onUnmounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import { useDeviceStore } from '@/stores/device'

const API_BASE = 'http://localhost:8000/api/payment'

// Default payment timeout in seconds (5 minutes)
const DEFAULT_PAYMENT_TIMEOUT = 300

const countdown = ref<number>(DEFAULT_PAYMENT_TIMEOUT)
let pollInterval: number | null = null
let countdownInterval: number | null = null

export function usePayment() {
  const store = useSessionStore()
  const deviceStore = useDeviceStore()
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const qrString = ref<string | null>(null)
  const referenceId = ref<string | null>(null)
  const expiresAt = ref<Date | null>(null)
  const isDemoMode = ref(false)

  // Get payment timeout from booth config (in minutes), convert to seconds
  const paymentTimeoutSeconds = computed(() => {
    const timeoutMinutes = deviceStore.booth?.config?.payment_timeout || 5
    return timeoutMinutes * 60
  })

  async function createPayment() {
    isLoading.value = true
    error.value = null
    isDemoMode.value = false

    try {
      if (!store.sessionId) {
        store.setSessionId(`session-${Date.now()}`)
      }

      const payload = {
        amount: store.totalPrice.toString(),
        product_name: 'Photobooth Standard',
        qty: store.printCount.toString(),
        print_count: store.printCount
      }

      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      }

      // Add device token for authentication
      if (deviceStore.device_token) {
        headers['Authorization'] = `Bearer ${deviceStore.device_token}`
      }

      console.log('[DEBUG] Creating payment with payload:', payload)

      const response = await fetch(`${API_BASE}/create`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error('[ERROR] Payment creation failed:', response.status, errorData)
        throw new Error(errorData.detail || `Failed to create payment: ${response.status}`)
      }

      const data = await response.json()
      console.log('[DEBUG] iPaymu response:', data)

      // iPaymu returns QrString, TransactionId, and ReferenceId
      if (!data.QrString) {
        console.error('[ERROR] No QrString in response:', data)
        throw new Error('No QR code received from payment provider')
      }

      qrString.value = data.QrString
      referenceId.value = data.ReferenceId
      console.log('[DEBUG] ReferenceId:', data.ReferenceId)
      store.setPaymentId(data.TransactionId)
      store.setPaymentStatus('pending')

      startCountdown()
      startPolling()
    } catch (err) {
      console.error('[ERROR] createPayment error:', err)
      error.value = err instanceof Error ? err.message : 'Failed to load QRIS'
      isDemoMode.value = true
      qrString.value = 'demo-qr-string'
      referenceId.value = `DEMO-${Date.now()}`
      store.setPaymentId(`demo-payment-${Date.now()}`)
      store.setPaymentStatus('pending')

      startCountdown()
      startPolling()
    } finally {
      isLoading.value = false
    }
  }

  function startCountdown() {
    if (countdownInterval) return

    // Use payment timeout from booth config (default 5 minutes)
    countdown.value = paymentTimeoutSeconds.value
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
    if (!store.paymentId || String(store.paymentId).startsWith('demo')) return

    try {
      const headers: Record<string, string> = {}

      // Add device token for authentication
      if (deviceStore.device_token) {
        headers['Authorization'] = `Bearer ${deviceStore.device_token}`
      }

      const response = await fetch(`${API_BASE}/status/${store.paymentId}`, {
        headers
      })

      if (!response.ok) throw new Error('Failed to check status')

      const data = await response.json()

      // iPaymu Status -> 1=Berhasil, 6=Settlement
      if (data.Status === 1 || data.Status === 6) {
        store.setPaymentStatus('success')
        stopPolling()
        stopCountdown()
      } else if (data.Status === -2 || data.Status === 2) {
        // Expired or Failed
        store.setPaymentStatus('failed')
        stopPolling()
        stopCountdown()
      }
    } catch {
      console.log('Payment status check skipped or failed')
    }
  }

  function startPolling() {
    if (pollInterval) return

    pollInterval = window.setInterval(() => {
      checkPaymentStatus()
    }, 3000) // Poll every 3 seconds for iPaymu
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  async function simulatePaymentSuccess() {
    // For demo mode, create a real payment record in database
    await createDemoPayment()
  }

  async function createDemoPayment() {
    try {
      const payload = {
        amount: store.totalPrice.toString(),
        product_name: 'Photobooth Standard',
        qty: store.printCount.toString(),
        print_count: store.printCount
      }

      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      }

      if (deviceStore.device_token) {
        headers['Authorization'] = `Bearer ${deviceStore.device_token}`
      }

      const response = await fetch(`${API_BASE}/demo/create`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload)
      })

      if (!response.ok) throw new Error('Failed to create demo payment')

      const data = await response.json()
      console.log('[DEBUG] Demo payment created:', data)

      store.setPaymentId(data.TransactionId)
      store.setPaymentStatus('success')
      stopPolling()
      stopCountdown()
    } catch (err) {
      console.error('Demo payment error:', err)
      // Fallback to local success
      store.setPaymentStatus('success')
      stopPolling()
      stopCountdown()
    }
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
    referenceId,
    expiresAt,
    countdown,
    formattedCountdown,
    isDemoMode,
    createPayment,
    checkPaymentStatus,
    startPolling,
    stopPolling,
    simulatePaymentSuccess,
    createDemoPayment
  }
}
