<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useDeviceStore } from '@/stores/device'
import BoothNameHeader from '@/components/BoothNameHeader.vue'

const router = useRouter()
const store = useSessionStore()
const deviceStore = useDeviceStore()

const currentSlide = ref(0)
const slides = ref([
  'https://lh3.googleusercontent.com/aida-public/AB6AXuCPX7bOgbiKU-qoxt7mfUPEEKEC1Lf_P1TW7duplwJV5R1VSWclOwsmbwN8tQ2UpGI3oQuvg69Txyzd0ONR-V1-6D7L8bAuX1wqDvEEh87CKUl960NPoQRTsuUGviSdFd8YO3VpqEr6FF2Qq6AnBLYUeirNCa7k1mjqhRp-7JwEcgBGdgsw1YSq7JYiGdAYgTl-nmpY9h80SjZL5z2nGVAoxGn9dKzIm1Mk1SDKxpuL27qi6gVQMZzwC2PnMizf9O4itUFHHcPo6ag',
  'https://lh3.googleusercontent.com/aida-public/AB6AXuAfQGq-nKsG1KOq9iYonhwFhrgqNCtUXiarbN8BI7ouPtbDaurpQ_bvvZRGReW0jLLekXn3I0RAZRt5vbvDA6c9ugctSbYQsbJK1pHH2-1pWnLT6Goxgip15xVx9PShUGhcgm5fIrbn4ZxIkfIeo39XefJ9RNWg0PrAYWqhKOcE9cUnWXcegFZgVVw0QZiDAHx2iklCcj49QCVoul9z2SAKveWKkwfBZk0IUMa-xEBc-odRRMrLjz9ENIWt3Hq0elxjjRIdHMyZDKg',
  'https://lh3.googleusercontent.com/aida-public/AB6AXuBZREI4zubx5R8_cLo7cmpfAFlGm9bhPVMjQK1D-Jn__Mp5OSvjYC0mdc9l1ZiXD6sKmB_uxSNBIkCtP6mEgX_C8gVxtBg8eydUpQB9TUxrmi9i78j2m_xaLJCSszsvDZd0BKlb8cY7dhZX-7Atkz3MP5MsX33TD3cKV8fpG5QI9x7R1tY4nTtGJ-6cdfm_3Qkuh3_fdGaabVGhRfMU_IbJ9SVyuJrKBPmZR0iyIy-3QlEMJKMBRWUP7EJhLiSYN0jaivZ30550aSg'
])

let slideInterval: number | null = null

onMounted(() => {
  store.resetSession()
  // Initialize session with booth config if available
  if (deviceStore.booth?.config) {
    store.initFromBoothConfig()
  }
  startSlideshow()
})

onUnmounted(() => {
  stopSlideshow()
})

function startSlideshow() {
  slideInterval = window.setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % slides.value.length
  }, 5000)
}

function stopSlideshow() {
  if (slideInterval) {
    clearInterval(slideInterval)
    slideInterval = null
  }
}

function handleStart() {
  store.setCurrentStep(1)
  router.push('/print-count')
}
</script>

<template>
  <div class="h-dvh w-dvw overflow-hidden relative flex flex-col bg-background">
    <!-- Background Images -->
    <div class="absolute inset-0 z-0 flex items-center justify-center">
      <div class="flex flex-wrap justify-center gap-3 p-4 opacity-40">
        <div
          v-for="(slide, index) in slides"
          :key="index"
          :class="[
            'rounded-xl overflow-hidden aspect-[3/4] transition-opacity duration-1000 w-32 lg:w-48'
          ]"
          :style="{
            transform: `rotate(${(index % 3 - 1) * 5}deg) translateY(${index * 10}px)`,
            opacity: currentSlide === index ? 1 : 0.3
          }"
        >
          <img :src="slide" :alt="`Slide ${index + 1}`" class="w-full h-full object-cover" />
        </div>
      </div>
    </div>

    <!-- Overlay Effects -->
    <div class="absolute inset-0 bg-grain pointer-events-none" />
    <div class="absolute inset-0 bg-gradient-to-b from-surface/20 via-transparent to-surface/80 pointer-events-none" />

    <!-- Decorative Icons -->
    <div class="absolute inset-0 pointer-events-none z-10 overflow-hidden">
      <span class="material-symbols-outlined absolute top-1/4 left-1/4 text-primary opacity-40 text-3xl lg:text-4xl" style="font-variation-settings: 'FILL' 1;">auto_awesome</span>
      <span class="material-symbols-outlined absolute bottom-1/3 right-1/4 text-secondary opacity-30 text-4xl lg:text-5xl" style="font-variation-settings: 'FILL' 1;">favorite</span>
      <span class="material-symbols-outlined absolute top-1/3 right-10 text-primary-container opacity-50 text-2xl lg:text-3xl" style="font-variation-settings: 'FILL' 1;">stars</span>
      <span class="material-symbols-outlined absolute bottom-16 left-10 text-tertiary opacity-40 text-5xl lg:text-6xl" style="font-variation-settings: 'FILL' 1;">celebration</span>
    </div>

    <!-- Header -->
    <header class="flex-none flex justify-between items-center px-6 lg:px-8 py-4 lg:py-6 bg-surface/80 backdrop-blur-sm z-50">
      <BoothNameHeader />
      <div class="flex items-center gap-2 lg:gap-4">
        <button class="material-symbols-outlined text-on-surface/60 text-xl lg:text-2xl font-medium hover:scale-105 transition-transform duration-300">
          help
        </button>
        <button class="material-symbols-outlined text-on-surface/60 text-xl lg:text-2xl font-medium hover:scale-105 transition-transform duration-300">
          settings
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 min-h-0 flex flex-col items-center justify-center px-6 z-20">
      <div class="flex flex-col items-center gap-8 lg:gap-10 text-center max-w-2xl w-full">
        <div class="space-y-3 lg:space-y-4">
          <h2 class="font-headline font-black text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-primary tracking-tighter drop-shadow-sm">
            Photobooth
          </h2>
          <p class="font-body text-on-surface-variant text-sm sm:text-base md:text-lg lg:text-xl font-medium max-w-md mx-auto">
            Siap untuk pose terbaikmu? Ayo buat momen seru hari ini!
          </p>
        </div>

        <div class="relative group">
          <div class="absolute -inset-3 lg:-inset-4 bg-gradient-to-r from-primary to-primary-container rounded-full blur-xl lg:blur-2xl opacity-30 group-hover:opacity-50 transition-opacity duration-500" />
          <button
            class="relative bg-gradient-to-r from-primary to-primary-container text-on-primary font-headline font-extrabold text-xl sm:text-2xl md:text-3xl lg:text-4xl tracking-widest px-10 sm:px-12 md:px-16 lg:px-20 py-5 sm:py-6 md:py-7 lg:py-8 rounded-full shadow-[0_20px_40px_rgba(167,41,90,0.25)] hover:scale-105 active:scale-95 transition-all duration-300"
            @click="handleStart"
          >
            MULAI
          </button>
        </div>

        <div class="bg-white/60 backdrop-blur-xl border border-white/40 p-3 lg:p-4 rounded-xl shadow-lg rotate-2 flex items-center gap-3 lg:gap-4">
          <div class="w-10 h-10 lg:w-12 lg:h-12 rounded-full overflow-hidden border-2 border-primary/20 bg-surface-container flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-primary text-2xl lg:text-3xl" style="font-variation-settings: 'FILL' 1;">photo_camera</span>
          </div>
          <div class="text-left">
            <p class="font-headline font-bold text-on-surface text-xs lg:text-sm">Update Terbaru!</p>
            <p class="font-body text-[10px] lg:text-xs text-on-surface-variant">Filter Rose Glow baru saja ditambahkan</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
