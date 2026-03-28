import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface BoothConfig {
  price_per_print: number
  timer_default: number
  max_print: number
  filters: string[]
}

export interface Booth {
  id: string
  name: string
  location?: string
  is_active?: boolean
  config?: BoothConfig
}

const DEVICE_ID_KEY = 'kiosk_device_id'
const DEVICE_TOKEN_KEY = 'kiosk_device_token'

export const useDeviceStore = defineStore('device', () => {
  // State
  const device_id = ref<string | null>(localStorage.getItem(DEVICE_ID_KEY))
  const device_token = ref<string | null>(localStorage.getItem(DEVICE_TOKEN_KEY))
  const booth = ref<Booth | null>(null)
  const is_connected = ref(false)
  const is_registering = ref(false)

  // Computed
  const is_assigned = computed(() => booth.value !== null)

  const has_device = computed(() => device_id.value !== null && device_token.value !== null)

  // Actions
  function setDevice(id: string, token: string) {
    device_id.value = id
    device_token.value = token
    localStorage.setItem(DEVICE_ID_KEY, id)
    localStorage.setItem(DEVICE_TOKEN_KEY, token)
  }

  function setBooth(newBooth: Booth | null) {
    booth.value = newBooth
  }

  function setConnected(connected: boolean) {
    is_connected.value = connected
  }

  function setRegistering(registering: boolean) {
    is_registering.value = registering
  }

  function clearDevice() {
    device_id.value = null
    device_token.value = null
    booth.value = null
    is_connected.value = false
    localStorage.removeItem(DEVICE_ID_KEY)
    localStorage.removeItem(DEVICE_TOKEN_KEY)
  }

  return {
    device_id,
    device_token,
    booth,
    is_connected,
    is_registering,
    is_assigned,
    has_device,
    setDevice,
    setBooth,
    setConnected,
    setRegistering,
    clearDevice
  }
})
