import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface AdminUser {
  id: string
  username: string
  email: string
  role: 'super_admin' | 'operator'
  created_at: string
}

export interface Booth {
  id: string
  name: string
  location: string
  is_active: boolean
  status?: 'active' | 'inactive' | 'maintenance'
  device_id: string | null
  device_token: string | null
  config: BoothConfig
  last_active_at: string | null
  created_at: string
  updated_at: string
}

export interface BoothConfig {
  price_per_print: number
  timer_default: number
  max_print: number
  filters: string[]
  payment_timeout: number  // Payment timeout in minutes (3 or 5)
}

export interface Transaction {
  id: string
  session_id: string
  reference_id: string | null
  transaction_id: string | null
  booth_id: string
  booth_name: string
  amount: number
  print_count: number
  status: 'success' | 'pending' | 'failed'
  payment_method: string
  created_at: string
  updated_at: string | null
}

export const useAdminStore = defineStore('admin', () => {
  // Constants
  const API_BASE = 'http://localhost:8000/api'
  const TOKEN_KEY = 'admin_token'

  // State
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const user = ref<AdminUser | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const booths = ref<Booth[]>([])
  const transactions = ref<Transaction[]>([])
  const currentBooth = ref<Booth | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isSuperuser = computed(() => user.value?.role === 'super_admin')

  // Actions
  function setToken(newToken: string | null) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem(TOKEN_KEY, newToken)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
  }

  function setUser(adminUser: AdminUser | null) {
    user.value = adminUser
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  function setError(err: string | null) {
    error.value = err
  }

  function setBooths(newBooths: Booth[]) {
    booths.value = newBooths
  }

function setTransactions(newTransactions: Transaction[]) {
  transactions.value = newTransactions
}

function updateTransaction(updatedTransaction: Transaction) {
  const index = transactions.value.findIndex(t => t.id === updatedTransaction.id)

  if (index !== -1) {
    // Update existing transaction
    transactions.value[index] = {
      ...transactions.value[index],
      ...updatedTransaction,
    }
  } else {
    // Add new transaction to the beginning
    transactions.value.unshift(updatedTransaction)
  }
}

function setCurrentBooth(booth: Booth | null) {
  currentBooth.value = booth
}

  function updateBoothInList(updatedBooth: Booth) {
    const index = booths.value.findIndex(b => b.id === updatedBooth.id)
    if (index !== -1) {
      booths.value[index] = updatedBooth
    }
  }

  function removeBoothFromList(boothId: string) {
    booths.value = booths.value.filter(b => b.id !== boothId)
  }

  function addBoothToList(booth: Booth) {
    booths.value.push(booth)
  }

  function logout() {
    setToken(null)
    setUser(null)
    setCurrentBooth(null)
    booths.value = []
    transactions.value = []
    error.value = null
  }

  // Initialize from localStorage
  async function initializeAuth() {
    const storedToken = localStorage.getItem(TOKEN_KEY)
    if (storedToken) {
      token.value = storedToken
      // Verify token validity
      try {
        const response = await fetch(`${API_BASE}/admin/verify`, {
          headers: {
            'Authorization': `Bearer ${storedToken}`
          }
        })
        if (!response.ok) {
          logout()
          return false
        }
        const data = await response.json()
        setUser(data.user)
        return true
      } catch {
        logout()
        return false
      }
    }
    return false
  }

  return {
    // State
    token,
    user,
    isLoading,
    error,
    booths,
    transactions,
    currentBooth,
    // Getters
    isAuthenticated,
    isSuperuser,
    // Actions
    setToken,
    setUser,
    setLoading,
    setError,
    setBooths,
    setTransactions,
    updateTransaction,
    setCurrentBooth,
    updateBoothInList,
    removeBoothFromList,
    addBoothToList,
    logout,
    initializeAuth
  }
})
