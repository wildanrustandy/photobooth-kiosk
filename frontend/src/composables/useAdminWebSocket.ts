import { ref, onUnmounted } from 'vue'
import { useAdminStore } from '@/stores/admin'

const WS_BASE = 'ws://localhost:8000/ws/admin'
const RECONNECT_DELAY = 3000 // 3 seconds

export function useAdminWebSocket() {
  const store = useAdminStore()

  let ws: WebSocket | null = null
  let reconnectTimeout: ReturnType<typeof setTimeout> | null = null

  const isConnected = ref(false)
  const lastMessage = ref<any>(null)

  function connect() {
    if (isConnected.value) return

    // Close existing connection if any
    disconnect()

    try {
      ws = new WebSocket(WS_BASE)

      ws.onopen = () => {
        console.log('[AdminWS] Connected')
        isConnected.value = true
      }

      ws.onclose = (event) => {
        console.log('[AdminWS] Disconnected', event.code, event.reason)
        isConnected.value = false
        scheduleReconnect()
      }

      ws.onerror = (error) => {
        console.error('[AdminWS] Error:', error)
        isConnected.value = false
      }

      ws.onmessage = (event) => {
        handleMessage(event.data)
      }
    } catch (err) {
      console.error('[AdminWS] Connection failed:', err)
      isConnected.value = false
      scheduleReconnect()
    }
  }

  function handleMessage(data: string) {
    try {
      const message = JSON.parse(data)
      lastMessage.value = message

      switch (message.type) {
        case 'connected':
          console.log('[AdminWS] Admin connected to WebSocket')
          break

        case 'transaction_update':
          console.log('[AdminWS] Transaction update received:', message.data)
          // Update transaction in store
          if (message.data) {
            updateTransactionInStore(message.data)
          }
          break

        case 'pong':
          // Heartbeat response
          break

        default:
          console.log('[AdminWS] Unknown message type:', message.type, message)
      }
    } catch (err) {
      console.error('[AdminWS] Failed to parse message:', data, err)
    }
  }

  function updateTransactionInStore(transaction: any) {
    console.log('[AdminWS] Updating transaction in store:', transaction.id, 'status:', transaction.status)

    // Format the transaction for the store
    const formattedTransaction = {
      id: transaction.id,
      session_id: transaction.session_id,
      reference_id: transaction.reference_id,
      transaction_id: transaction.transaction_id,
      booth_id: transaction.booth_id,
      booth_name: transaction.booth_name || 'Unknown',
      amount: transaction.amount,
      print_count: transaction.print_count || 1,
      status: transaction.status,
      payment_method: transaction.provider || 'qris',
      created_at: transaction.created_at,
      updated_at: transaction.paid_at || transaction.created_at,
    }

    // Use the store's updateTransaction function
    store.updateTransaction(formattedTransaction)
    console.log('[AdminWS] Transaction updated successfully')
  }

  function scheduleReconnect() {
    if (reconnectTimeout) return

    reconnectTimeout = setTimeout(() => {
      reconnectTimeout = null
      if (store.token) {
        console.log('[AdminWS] Attempting to reconnect...')
        connect()
      }
    }, RECONNECT_DELAY)
  }

  function disconnect() {
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }

    if (ws) {
      ws.close(1000, 'Normal closure')
      ws = null
    }

    isConnected.value = false
  }

  function sendPing() {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }))
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    lastMessage,
    connect,
    disconnect,
    sendPing
  }
}
