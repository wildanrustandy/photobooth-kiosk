<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDeviceStore } from '@/stores/device'
import { useDevice } from '@/composables/useDevice'
import { useWebSocket } from '@/composables/useWebSocket'

const router = useRouter()
const store = useDeviceStore()
const { registerDevice, checkAssignment, isLoading, error } = useDevice()
const { connect } = useWebSocket()

const deviceName = ref('')
const showError = ref(false)

onMounted(async () => {
  // If device already registered, check assignment and navigate accordingly
  if (store.has_device) {
    const assigned = await checkAssignment()
    if (assigned) {
      connect()
      router.replace('/')
    } else {
      router.replace('/waiting-assignment')
    }
    return
  }

  // Auto-register with generated device name
  const generatedName = `Kiosk-${Math.random().toString(36).substring(2, 8).toUpperCase()}`
  deviceName.value = generatedName

  const success = await registerDevice(generatedName)

  if (success) {
    // Small delay to show success state
    setTimeout(() => {
      if (store.is_assigned) {
        connect()
        router.replace('/')
      } else {
        router.replace('/waiting-assignment')
      }
    }, 1500)
  } else {
    showError.value = true
  }
})
</script>

<template>
  <div class="h-dvh w-dvw overflow-hidden relative flex flex-col bg-background">
    <!-- Background -->
    <div class="absolute inset-0 z-0">
      <div
        class="absolute inset-0"
        style="background-color: #faf4ff; background-image: radial-gradient(at 0% 0%, #e2d7ff 0px, transparent 50%), radial-gradient(at 100% 0%, #ff8eaf15 0px, transparent 50%), radial-gradient(at 100% 100%, #9795ff20 0px, transparent 50%), radial-gradient(at 0% 100%, #ede4ff 0px, transparent 50%);"
      />
    </div>

    <!-- Geometric Decorative Elements -->
    <div class="absolute inset-0 pointer-events-none z-0 overflow-hidden">
      <div class="absolute top-20 left-[10%] w-64 h-64 border-[32px] border-surface-container-highest rounded-full opacity-30" />
      <div class="absolute bottom-20 right-[5%] w-96 h-96 border-[48px] border-primary-container/20 rounded-[4rem] rotate-12 opacity-20" />
      <div class="absolute top-1/2 right-[15%] w-12 h-12 bg-tertiary-container/30 rounded-xl rotate-45" />
      <div class="absolute bottom-1/3 left-[8%] w-8 h-8 bg-secondary-container/40 rounded-full" />
    </div>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col items-center justify-center px-6 z-10">
      <div class="flex flex-col items-center gap-8 max-w-md w-full text-center">
        <!-- Loading Icon -->
        <div class="relative">
          <div class="absolute inset-0 bg-primary/20 rounded-full blur-2xl animate-pulse" />
          <div class="relative w-24 h-24 bg-gradient-to-br from-primary to-primary-dim rounded-2xl flex items-center justify-center shadow-lg">
            <span v-if="isLoading" class="material-symbols-outlined text-white text-5xl animate-spin" style="font-variation-settings: 'FILL' 1;">sync</span>
            <span v-else-if="error" class="material-symbols-outlined text-white text-5xl" style="font-variation-settings: 'FILL' 1;">error</span>
            <span v-else class="material-symbols-outlined text-white text-5xl" style="font-variation-settings: 'FILL' 1;">check</span>
          </div>
        </div>

        <!-- Status Text -->
        <div class="space-y-3">
          <h1 class="font-headline font-extrabold text-3xl text-on-surface tracking-tight">
            {{ isLoading ? 'Mendaftarkan Perangkat' : error ? 'Registrasi Gagal' : 'Perangkat Terdaftar' }}
          </h1>
          <p class="font-body text-on-surface-variant text-base font-medium">
            {{ isLoading ? 'Silakan tunggu sebentar...' : error ? error : 'Mengalihkan ke halaman utama...' }}
          </p>
        </div>

        <!-- Device Name (if registered) -->
        <div v-if="!isLoading && !error && store.device_id" class="bg-surface-container-lowest/80 backdrop-blur-sm border border-white/40 rounded-2xl px-8 py-4 shadow-lg">
          <p class="text-xs font-bold uppercase tracking-widest text-on-surface-variant mb-1">Device ID</p>
          <p class="font-mono font-bold text-xl text-primary tracking-wider">{{ store.device_id }}</p>
        </div>

        <!-- Error Retry Button -->
        <button
          v-if="error"
          @click="() => { showError = false; registerDevice(deviceName) }"
          class="bg-gradient-to-r from-primary to-primary-dim hover:from-primary-dim hover:to-primary text-white font-headline font-extrabold text-lg px-10 py-4 rounded-full shadow-lg shadow-primary/20 active:scale-[0.98] transition-all duration-200"
        >
          Coba Lagi
        </button>

        <!-- Progress Indicator -->
        <div v-if="isLoading" class="flex items-center gap-2">
          <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 0ms" />
          <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 150ms" />
          <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 300ms" />
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="flex-none px-6 py-4 z-10">
      <p class="text-center text-[10px] text-outline font-medium tracking-tight">
        Photobooth Kiosk v1.0.0 • Device Setup
      </p>
    </footer>
  </div>
</template>
