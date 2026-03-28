import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useDeviceStore } from './device'

export type PaymentStatus = 'idle' | 'pending' | 'success' | 'failed'
export type SessionStatus = 'idle' | 'pending' | 'paid' | 'completed' | 'cancelled'

export interface Photo {
  id: string
  url: string
  order: number
  blob?: Blob
}

export const useSessionStore = defineStore('session', () => {
  // Constants - defined first
  const DEFAULT_PRICE_PER_SHEET = 35000
  const MIN_PRINT_COUNT = 1
  const MAX_PRINT_COUNT = 10

  // Get device store for booth config
  const deviceStore = useDeviceStore()

  // Computed price from booth config
  const pricePerSheet = computed(() => {
    return deviceStore.booth?.config?.price_per_print || DEFAULT_PRICE_PER_SHEET
  })

  // State
  const sessionId = ref<string | null>(null)
  const printCount = ref<number>(1)
  const totalPrice = ref<number>(DEFAULT_PRICE_PER_SHEET)  // Initialize with default price (1 sheet)
  const paymentStatus = ref<PaymentStatus>('idle')
  const sessionStatus = ref<SessionStatus>('idle')
  const photos = ref<Photo[]>([])
  const selectedFilter = ref<string>('Normal')
  const timer = ref<number>(5)
  const currentStep = ref<number>(0)
  const paymentId = ref<string | null>(null)
  const downloadToken = ref<string | null>(null)

  const formattedTotalPrice = computed(() => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(totalPrice.value)
  })

  const formattedPricePerSheet = computed(() => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(pricePerSheet.value)
  })

  const canProceed = computed(() => {
    return printCount.value >= MIN_PRINT_COUNT && printCount.value <= MAX_PRINT_COUNT
  })

  const photosTaken = computed(() => photos.value.length)

  const allPhotosTaken = computed(() => photos.value.length === 4)

  // Initialize price when booth config is loaded
  function initFromBoothConfig() {
    const config = deviceStore.booth?.config
    if (config) {
      timer.value = config.timer_default || 5
      selectedFilter.value = config.filters?.[0] || 'Normal'
      totalPrice.value = printCount.value * (config.price_per_print || DEFAULT_PRICE_PER_SHEET)
    }
  }

  function setPrintCount(count: number) {
    if (count >= MIN_PRINT_COUNT && count <= MAX_PRINT_COUNT) {
      printCount.value = count
      totalPrice.value = count * pricePerSheet.value
    }
  }

  function incrementPrintCount() {
    if (printCount.value < MAX_PRINT_COUNT) {
      printCount.value++
      totalPrice.value = printCount.value * pricePerSheet.value
    }
  }

  function decrementPrintCount() {
    if (printCount.value > MIN_PRINT_COUNT) {
      printCount.value--
      totalPrice.value = printCount.value * pricePerSheet.value
    }
  }

  function setFilter(filter: string) {
    selectedFilter.value = filter
  }

  function setTimer(seconds: number) {
    timer.value = seconds
  }

  function addPhoto(photo: Photo) {
    photos.value.push(photo)
  }

  function removePhoto(order: number) {
    photos.value = photos.value.filter(p => p.order !== order)
  }

  function clearPhotos() {
    photos.value = []
  }

  function setPaymentStatus(status: PaymentStatus) {
    paymentStatus.value = status
    if (status === 'success') {
      sessionStatus.value = 'paid'
    }
  }

  function setSessionId(id: string) {
    sessionId.value = id
    sessionStatus.value = 'pending'
  }

  function setPaymentId(id: string) {
    paymentId.value = id
  }

  function setDownloadToken(token: string) {
    downloadToken.value = token
  }

  function setCurrentStep(step: number) {
    currentStep.value = step
  }

  function nextStep() {
    currentStep.value++
  }

  function prevStep() {
    if (currentStep.value > 0) {
      currentStep.value--
    }
  }

  function completeSession() {
    sessionStatus.value = 'completed'
  }

  function resetSession() {
    sessionId.value = null
    printCount.value = 1
    totalPrice.value = pricePerSheet.value
    paymentStatus.value = 'idle'
    sessionStatus.value = 'idle'
    photos.value = []
    selectedFilter.value = deviceStore.booth?.config?.filters?.[0] || 'Normal'
    timer.value = deviceStore.booth?.config?.timer_default || 5
    currentStep.value = 0
    paymentId.value = null
    downloadToken.value = null
  }

  return {
    sessionId,
    printCount,
    totalPrice,
    paymentStatus,
    sessionStatus,
    photos,
    selectedFilter,
    timer,
    currentStep,
    paymentId,
    downloadToken,
    formattedTotalPrice,
    formattedPricePerSheet,
    pricePerSheet,
    canProceed,
    photosTaken,
    allPhotosTaken,
    PRICE_PER_SHEET: DEFAULT_PRICE_PER_SHEET,
    MIN_PRINT_COUNT,
    MAX_PRINT_COUNT,
    initFromBoothConfig,
    setPrintCount,
    incrementPrintCount,
    decrementPrintCount,
    setFilter,
    setTimer,
    addPhoto,
    removePhoto,
    clearPhotos,
    setPaymentStatus,
    setSessionId,
    setPaymentId,
    setDownloadToken,
    setCurrentStep,
    nextStep,
    prevStep,
    completeSession,
    resetSession
  }
})
