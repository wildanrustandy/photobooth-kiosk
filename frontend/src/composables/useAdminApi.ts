import { ref } from 'vue'
import { useAdminStore } from '@/stores/admin'

const API_BASE = 'http://localhost:8000/api'

export interface LoginCredentials {
  username: string
  password: string
}

export interface CreateBoothData {
  name: string
  location: string
  config?: {
    price_per_print?: number
    timer_default?: number
    max_print?: number
    filters?: string[]
  }
}

export interface UpdateBoothData {
  name?: string
  location?: string
  is_active?: boolean
}

export interface UpdateBoothConfigData {
  price_per_print?: number
  timer_default?: number
  max_print?: number
  filters?: string[]
  payment_timeout?: number
}

export function useAdminApi() {
  const store = useAdminStore()
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  function getAuthHeaders() {
    const token = store.token
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    }
  }

  async function handleRequest<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T | null> {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...getAuthHeaders(),
          ...options.headers
        }
      })

      if (response.status === 401) {
        store.logout()
        error.value = 'Session expired. Please login again.'
        return null
      }

      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        error.value = data.detail || data.message || `Request failed: ${response.status}`
        return null
      }

      const data = await response.json()
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Network error'
      return null
    } finally {
      isLoading.value = false
    }
  }

  // Auth
  async function login(credentials: LoginCredentials) {
    const data = await handleRequest<{ access_token: string; token_type: string; admin: any }>(
      `${API_BASE}/auth/admin/login`,
      {
        method: 'POST',
        body: JSON.stringify(credentials)
      }
    )

    if (data) {
      store.setToken(data.access_token)
      // Backend returns 'admin', map to user format
      store.setUser({
        id: data.admin.id,
        username: data.admin.username,
        role: data.admin.role as 'super_admin' | 'operator',
        email: '',
        created_at: new Date().toISOString()
      })
      return true
    }
    return false
  }

  async function verifyToken() {
    const data = await handleRequest<{ valid: boolean; admin_id: string; username: string; role: string }>(
      `${API_BASE}/admin/verify`,
      { method: 'GET' }
    )

    if (data && data.valid) {
      // Map verify response to user format
      store.setUser({
        id: data.admin_id,
        username: data.username,
        role: data.role as 'super_admin' | 'operator',
        email: '',
        created_at: new Date().toISOString()
      })
      return true
    }
    return false
  }

  // Booths
  async function fetchBooths() {
    const data = await handleRequest<any[]>(
      `${API_BASE}/admin/booths`,
      { method: 'GET' }
    )

    if (data) {
      store.setBooths(data)
      return data
    }
    return null
  }

  async function fetchBooth(id: string) {
    const data = await handleRequest<any>(
      `${API_BASE}/admin/booths/${id}`,
      { method: 'GET' }
    )

    if (data) {
      store.setCurrentBooth(data)
      return data
    }
    return null
  }

  async function createBooth(data: CreateBoothData) {
    const result = await handleRequest<any>(
      `${API_BASE}/admin/booths`,
      {
        method: 'POST',
        body: JSON.stringify(data)
      }
    )

    if (result) {
      store.addBoothToList(result)
    }
    return result
  }

  async function updateBooth(id: string, data: UpdateBoothData) {
    const result = await handleRequest<any>(
      `${API_BASE}/admin/booths/${id}`,
      {
        method: 'PUT',
        body: JSON.stringify(data)
      }
    )

    if (result) {
      store.updateBoothInList(result)
      if (store.currentBooth?.id === id) {
        store.setCurrentBooth(result)
      }
    }
    return result
  }

  async function updateBoothConfig(id: string, config: UpdateBoothConfigData) {
    const result = await handleRequest<any>(
      `${API_BASE}/admin/booths/${id}/config`,
      {
        method: 'PUT',
        body: JSON.stringify(config)
      }
    )

    if (result) {
      store.updateBoothInList(result)
      if (store.currentBooth?.id === id) {
        store.setCurrentBooth(result)
      }
    }
    return result
  }

  async function deleteBooth(id: string) {
    const result = await handleRequest<{ success: boolean }>(
      `${API_BASE}/admin/booths/${id}`,
      { method: 'DELETE' }
    )

    if (result) {
      store.removeBoothFromList(id)
    }
    return result
  }

  async function assignDevice(boothId: string, deviceId: string) {
    const result = await handleRequest<any>(
      `${API_BASE}/admin/booths/${boothId}/assign`,
      {
        method: 'POST',
        body: JSON.stringify({ device_id: deviceId })
      }
    )

    if (result) {
      store.updateBoothInList(result)
      if (store.currentBooth?.id === boothId) {
        store.setCurrentBooth(result)
      }
    }
    return result
  }

  async function unassignDevice(boothId: string) {
    const result = await handleRequest<any>(
      `${API_BASE}/admin/booths/${boothId}/unassign`,
      { method: 'POST' }
    )

    if (result) {
      store.updateBoothInList(result)
      if (store.currentBooth?.id === boothId) {
        store.setCurrentBooth(result)
      }
    }
    return result
  }

  // Device Management
  async function kickDevice(deviceId: string) {
    const result = await handleRequest<{ success: boolean }>(
      `${API_BASE}/admin/devices/${deviceId}/kick`,
      { method: 'POST' }
    )
    return result
  }

  // Transactions
  async function fetchTransactions(params?: {
    booth_id?: string
    status?: string
    start_date?: string
    end_date?: string
  }) {
    const queryParams = new URLSearchParams()
    if (params?.booth_id) queryParams.append('booth_id', params.booth_id)
    if (params?.status) queryParams.append('status', params.status)
    if (params?.start_date) queryParams.append('start_date', params.start_date)
    if (params?.end_date) queryParams.append('end_date', params.end_date)

    const queryString = queryParams.toString()
    const url = `${API_BASE}/admin/transactions${queryString ? `?${queryString}` : ''}`

    const data = await handleRequest<any[]>(url, { method: 'GET' })

    if (data) {
      store.setTransactions(data)
      return data
    }
    return null
  }

  return {
    isLoading,
    error,
    // Auth
    login,
    verifyToken,
    // Booths
    fetchBooths,
    fetchBooth,
    createBooth,
    updateBooth,
    updateBoothConfig,
    deleteBooth,
    assignDevice,
    unassignDevice,
    // Devices
    kickDevice,
    // Transactions
    fetchTransactions
  }
}
