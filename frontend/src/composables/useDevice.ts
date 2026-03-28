import { ref } from 'vue'
import { useDeviceStore } from '@/stores/device'

const API_BASE = 'http://localhost:8000/api/auth/device'

export function useDevice() {
  const store = useDeviceStore()
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function registerDevice(device_name?: string): Promise<boolean> {
    isLoading.value = true
    error.value = null
    store.setRegistering(true)

    try {
      const payload: { device_name?: string } = {}
      if (device_name) {
        payload.device_name = device_name
      }

      const response = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        throw new Error(data.message || 'Failed to register device')
      }

      const data = await response.json()

      store.setDevice(data.device_id, data.device_token)

      if (data.booth) {
        store.setBooth(data.booth)
      }

      return true
    } catch (err) {
      console.error('[Device] Registration failed:', err)
      error.value = err instanceof Error ? err.message : 'Registration failed'
      return false
    } finally {
      isLoading.value = false
      store.setRegistering(false)
    }
  }

  async function checkAssignment(): Promise<boolean> {
    if (!store.device_id || !store.device_token) {
      return false
    }

    try {
      const response = await fetch(`${API_BASE}/assignment`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${store.device_token}`,
          'X-Device-ID': store.device_id
        }
      })

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          // Token invalid or device kicked
          store.clearDevice()
          return false
        }
        throw new Error('Failed to check assignment')
      }

      const data = await response.json()

      if (data.booth) {
        store.setBooth(data.booth)
        return true
      } else {
        store.setBooth(null)
        return false
      }
    } catch (err) {
      console.error('[Device] Assignment check failed:', err)
      return store.is_assigned
    }
  }

  async function sendHeartbeat(): Promise<boolean> {
    if (!store.device_id || !store.device_token) {
      return false
    }

    try {
      const response = await fetch(`${API_BASE}/heartbeat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${store.device_token}`,
          'X-Device-ID': store.device_id,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ device_id: store.device_id })
      })

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          store.clearDevice()
          return false
        }
        return false
      }

      return true
    } catch {
      return false
    }
  }

  return {
    isLoading,
    error,
    registerDevice,
    checkAssignment,
    sendHeartbeat
  }
}
