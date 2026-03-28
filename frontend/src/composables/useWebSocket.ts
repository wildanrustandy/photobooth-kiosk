import { ref, onUnmounted } from 'vue'
import { useDeviceStore } from '@/stores/device'
import { useRouter } from 'vue-router'

const WS_BASE = 'ws://localhost:8000/ws/device'
const HEARTBEAT_INTERVAL = 30000 // 30 seconds
const RECONNECT_DELAY = 3000 // 3 seconds

export function useWebSocket() {
  const store = useDeviceStore()
  const router = useRouter()

  let ws: WebSocket | null = null
  let heartbeatInterval: number | null = null
  let reconnectTimeout: number | null = null

  const isConnecting = ref(false)

  function connect() {
    if (!store.device_id || isConnecting.value) return

    // Close existing connection if any
    disconnect()

    isConnecting.value = true

    try {
      ws = new WebSocket(`${WS_BASE}/${store.device_id}`)

      ws.onopen = () => {
        console.log('[WebSocket] Connected')
        store.setConnected(true)
        isConnecting.value = false
        startHeartbeat()
      }

      ws.onclose = (event) => {
        console.log('[WebSocket] Disconnected', event.code, event.reason)
        store.setConnected(false)
        isConnecting.value = false
        stopHeartbeat()

        // Don't reconnect if closed due to being kicked (code 4000)
        if (event.code !== 4000) {
          scheduleReconnect()
        }
      }

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error)
        isConnecting.value = false
      }

      ws.onmessage = (event) => {
        handleMessage(event.data)
      }
    } catch (err) {
      console.error('[WebSocket] Connection failed:', err)
      isConnecting.value = false
      scheduleReconnect()
    }
  }

  function handleMessage(data: string) {
    try {
      const message = JSON.parse(data)

      switch (message.event) {
        case 'kicked':
          console.log('[WebSocket] Device kicked')
          store.clearDevice()
          router.push('/session-taken')
          break

        case 'booth_update':
          console.log('[WebSocket] Booth update:', message.data)
          if (message.data) {
            store.setBooth(message.data)
          }
          break

        case 'heartbeat_ack':
          console.log('[WebSocket] Heartbeat acknowledged')
          break

        default:
          console.log('[WebSocket] Unknown event:', message.event, message.data)
      }
    } catch {
      console.error('[WebSocket] Failed to parse message:', data)
    }
  }

  function startHeartbeat() {
    stopHeartbeat()

    heartbeatInterval = window.setInterval(() => {
      sendHeartbeat()
    }, HEARTBEAT_INTERVAL)
  }

  function stopHeartbeat() {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
  }

  function sendHeartbeat() {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ event: 'heartbeat' }))
    }
  }

  function scheduleReconnect() {
    if (reconnectTimeout) return

    reconnectTimeout = window.setTimeout(() => {
      reconnectTimeout = null
      if (store.device_id) {
        console.log('[WebSocket] Attempting to reconnect...')
        connect()
      }
    }, RECONNECT_DELAY)
  }

  function disconnect() {
    stopHeartbeat()

    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }

    if (ws) {
      ws.close(1000, 'Normal closure')
      ws = null
    }

    store.setConnected(false)
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnecting,
    connect,
    disconnect
  }
}
