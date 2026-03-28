<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDeviceStore } from '@/stores/device'
import { useDevice } from '@/composables/useDevice'
import { useWebSocket } from '@/composables/useWebSocket'

const router = useRouter()
const store = useDeviceStore()
const { checkAssignment } = useDevice()
const { connect, isConnecting } = useWebSocket()

const isChecking = ref(false)
const lastChecked = ref<Date | null>(null)
let pollInterval: number | null = null

const formattedDeviceId = computed(() => {
  if (!store.device_id) return '—'
  // Format device ID with dashes for readability
  return store.device_id
})

const formattedLastChecked = computed(() => {
  if (!lastChecked.value) return 'Baru saja'
  const seconds = Math.floor((Date.now() - lastChecked.value.getTime()) / 1000)
  if (seconds < 5) return 'Baru saja'
  return `${seconds} detik lalu`
})

onMounted(() => {
  // Start WebSocket connection for real-time updates
  if (store.device_id) {
    connect()
  }

  // Start polling for assignment status
  pollInterval = window.setInterval(async () => {
    isChecking.value = true
    lastChecked.value = new Date()

    const assigned = await checkAssignment()

    if (assigned) {
      stopPolling()
      router.replace('/')
    }

    isChecking.value = false
  }, 5000) // Poll every 5 seconds
})

onUnmounted(() => {
  stopPolling()
})

function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

function goToSetup() {
  store.clearDevice()
  router.replace('/device-setup')
}
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

    <!-- Pulsing Connection Indicator -->
    <div class="absolute top-6 right-6 z-20">
      <div class="flex items-center gap-2 bg-surface-container-lowest/80 backdrop-blur-sm border border-white/40 rounded-full px-4 py-2">
        <div
          :class="[
            'w-2.5 h-2.5 rounded-full transition-colors duration-300',
            isConnecting ? 'bg-green-500 animate-pulse' : 'bg-outline'
          ]"
        />
        <span class="text-xs font-bold text-on-surface-variant">
          {{ isConnecting ? 'Terhubung' : 'Offline' }}
        </span>
      </div>
    </div>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col items-center justify-center px-6 z-10">
      <div class="flex flex-col items-center gap-8 max-w-lg w-full text-center">
        <!-- Animated Waiting Icon -->
        <div class="relative">
          <div class="absolute inset-0 bg-primary/20 rounded-full blur-2xl animate-pulse" />
          <div class="relative w-32 h-32 bg-gradient-to-br from-primary to-primary-dim rounded-full flex items-center justify-center shadow-lg shadow-primary/30">
            <span class="material-symbols-outlined text-white text-7xl animate-pulse" style="font-variation-settings: 'FILL' 1;">hourglass</span>
          </div>
          <!-- Orbit dots -->
          <div class="absolute inset-0 animate-spin" style="animation-duration: 3s;">
            <div class="absolute top-0 left-1/2 -translate-x-1/2 w-3 h-3 bg-primary-fixed rounded-full" />
          </div>
        </div>

        <!-- Title & Description -->
        <div class="space-y-3">
          <h1 class="font-headline font-extrabold text-4xl text-on-surface tracking-tight">
            Menunggu Penugasan
          </h1>
          <p class="font-body text-on-surface-variant text-lg font-medium max-w-sm mx-auto">
            Perangkat ini belum ditugaskan ke booth manapun. Harap hubungi administrator untuk penugasan.
          </p>
        </div>

        <!-- Device ID Card -->
        <div class="bg-surface-container-lowest/80 backdrop-blur-sm border border-white/40 rounded-3xl px-10 py-6 shadow-lg w-full max-w-sm">
          <p class="text-xs font-bold uppercase tracking-widest text-on-surface-variant mb-2">Device ID</p>
          <p class="font-mono font-extrabold text-2xl lg:text-3xl text-primary tracking-wider break-all">
            {{ formattedDeviceId }}
          </p>
          <p class="text-xs text-outline mt-3">
            Tunjukkan ID ini kepada administrator untuk penugasan booth
          </p>
        </div>

        <!-- Assignment Status -->
        <div class="bg-surface-container-low/60 backdrop-blur-sm border border-white/40 rounded-2xl px-6 py-4 flex items-center gap-4 w-full max-w-sm">
          <div class="w-10 h-10 bg-tertiary-container rounded-xl flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-tertiary text-xl" style="font-variation-settings: 'FILL' 1;">info</span>
          </div>
          <div class="text-left flex-1 min-w-0">
            <p class="text-sm font-bold text-on-surface">Status</p>
            <p class="text-xs text-on-surface-variant truncate">
              {{ isChecking ? 'Memeriksa...' : `Terakhir dicek: ${formattedLastChecked}` }}
            </p>
          </div>
          <div v-if="isChecking" class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin shrink-0" />
          <span v-else class="material-symbols-outlined text-primary text-xl" style="font-variation-settings: 'FILL' 1;">refresh</span>
        </div>

        <!-- Booting Animation -->
        <div class="flex items-center gap-3 text-on-surface-variant">
          <span class="material-symbols-outlined text-sm animate-bounce" style="animation-delay: 0ms;">radio_button_checked</span>
          <span class="text-xs font-medium">Auto-refresh aktif</span>
        </div>

        <!-- Re-setup Button -->
        <button
          @click="goToSetup"
          class="mt-4 text-sm font-bold text-on-surface-variant hover:text-primary transition-colors underline underline-offset-4"
        >
          Daftar ulang perangkat
        </button>
      </div>
    </main>

    <!-- Footer -->
    <footer class="flex-none px-6 py-4 z-10">
      <p class="text-center text-[10px] text-outline font-medium tracking-tight">
        Photobooth Kiosk v1.0.0 • Menunggu Penugasan
      </p>
    </footer>
  </div>
</template>
