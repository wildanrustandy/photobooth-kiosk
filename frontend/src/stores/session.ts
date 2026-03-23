import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export type PaymentStatus = 'idle' | 'pending' | 'success' | 'failed'
export type SessionStatus = 'idle' | 'pending' | 'paid' | 'completed' | 'cancelled'

export interface Photo {
  id: string
  url: string
  order: number
  blob?: Blob
}

export const useSessionStore = defineStore('session', () => {
  const sessionId = ref<string | null>(null)
  const printCount = ref<number>(1)
  const totalPrice = ref<number>(0)
  const paymentStatus = ref<PaymentStatus>('idle')
  const sessionStatus = ref<SessionStatus>('idle')
  const photos = ref<Photo[]>([])
  const selectedFilter = ref<string>('Normal')
  const timer = ref<number>(5)
  const currentStep = ref<number>(0)
  const paymentId = ref<string | null>(null)
  const downloadToken = ref<string | null>(null)

  const PRICE_PER_SHEET = 35000
  const MIN_PRINT_COUNT = 1
  const MAX_PRINT_COUNT = 10

  const formattedTotalPrice = computed(() => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(totalPrice.value)
  })

  const canProceed = computed(() => {
    return printCount.value >= MIN_PRINT_COUNT && printCount.value <= MAX_PRINT_COUNT
  })

  const photosTaken = computed(() => photos.value.length)

  const allPhotosTaken = computed(() => photos.value.length === 4)

  function setPrintCount(count: number) {
    if (count >= MIN_PRINT_COUNT && count <= MAX_PRINT_COUNT) {
      printCount.value = count
      totalPrice.value = count * PRICE_PER_SHEET
    }
  }

  function incrementPrintCount() {
    if (printCount.value < MAX_PRINT_COUNT) {
      printCount.value++
      totalPrice.value = printCount.value * PRICE_PER_SHEET
    }
  }

  function decrementPrintCount() {
    if (printCount.value > MIN_PRINT_COUNT) {
      printCount.value--
      totalPrice.value = printCount.value * PRICE_PER_SHEET
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
    totalPrice.value = PRICE_PER_SHEET
    paymentStatus.value = 'idle'
    sessionStatus.value = 'idle'
    photos.value = []
    selectedFilter.value = 'Normal'
    timer.value = 5
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
    canProceed,
    photosTaken,
    allPhotosTaken,
    PRICE_PER_SHEET,
    MIN_PRINT_COUNT,
    MAX_PRINT_COUNT,
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
