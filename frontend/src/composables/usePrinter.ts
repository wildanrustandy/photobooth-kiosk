import { ref } from 'vue'
import { useSessionStore } from '@/stores/session'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export type PrintStatusType = 'idle' | 'queued' | 'printing' | 'done'

export function usePrinter() {
  const store = useSessionStore()
  const isPrinting = ref(false)
  const error = ref<string | null>(null)
  const printStatus = ref<PrintStatusType>('idle')

  async function print() {
    if (!store.sessionId) {
      error.value = 'Session not found'
      return false
    }

    isPrinting.value = true
    error.value = null
    printStatus.value = 'queued'

    try {
      const response = await fetch(`${API_BASE}/print`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          session_id: store.sessionId,
          print_count: store.printCount
        })
      })

      if (!response.ok) throw new Error('Failed to print')

      const data = await response.json()
      const status = data.status as PrintStatusType
      printStatus.value = status
      
      if (status === 'done') {
        return true
      }

      await pollPrintStatus()
      return printStatus.value === 'done'
    } catch (err) {
      error.value = 'Gagal mencetak. Silakan coba lagi.'
      console.error('Print error:', err)
      return false
    } finally {
      isPrinting.value = false
    }
  }

  async function pollPrintStatus() {
    const maxAttempts = 60
    let attempts = 0

    while (attempts < maxAttempts && printStatus.value !== 'done') {
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      try {
        const response = await fetch(`${API_BASE}/print/${store.sessionId}/status`)
        if (response.ok) {
          const data = await response.json()
          printStatus.value = data.status as PrintStatusType
        }
      } catch (err) {
        console.error('Print status check error:', err)
      }
      
      attempts++
    }
  }

  return {
    isPrinting,
    error,
    printStatus,
    print
  }
}
