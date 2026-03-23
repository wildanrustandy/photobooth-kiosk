<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'

const router = useRouter()
const store = useSessionStore()

const currentSlide = ref(0)
const slides = ref([
  'https://lh3.googleusercontent.com/aida-public/AB6AXuCPX7bOgbiKU-qoxt7mfUPEEKEC1Lf_P1TW7duplwJV5R1VSWclOwsmbwN8tQ2UpGI3oQuvg69Txyzd0ONR-V1-6D7L8bAuX1wqDvEEh87CKUl960NPoQRTsuUGviSdFd8YO3VpqEr6FF2Qq6AnBLYUeirNCa7k1mjqhRp-7JwEcgBGdgsw1YSq7JYiGdAYgTl-nmpY9h80SjZL5z2nGVAoxGn9dKzIm1Mk1SDKxpuL27qi6gVQMZzwC2PnMizf9O4itUFHHcPo6ag',
  'https://lh3.googleusercontent.com/aida-public/AB6AXuAfQGq-nKsG1KOq9iYonhwFhrgqNCtUXiarbN8BI7ouPtbDaurpQ_bvvZRGReW0jLLekXn3I0RAZRt5vbvDA6c9ugctSbYQsbJK1pHH2-1pWnLT6Goxgip15xVx9PShUGhcgm5fIrbn4ZxIkfIeo39XefJ9RNWg0PrAYWqhKOcE9cUnWXcegFZgVVw0QZiDAHx2iklCcj49QCVoul9z2SAKveWKkwfBZk0IUMa-xEBc-odRRMrLjz9ENIWt3Hq0elxjjRIdHMyZDKg',
  'https://lh3.googleusercontent.com/aida-public/AB6AXuBZREI4zubx5R8_cLo7cmpfAFlGm9bhPVMjQK1D-Jn__Mp5OSvjYC0mdc9l1ZiXD6sKmB_uxSNBIkCtP6mEgX_C8gVxtBg8eydUpQB9TUxrmi9i78j2m_xaLJCSszsvDZd0BKlb8cY7dhZX-7Atkz3MP5MsX33TD3cKV8fpG5QI9x7R1tY4nTtGJ-6cdfm_3Qkuh3_fdGaabVGhRfMU_IbJ9SVyuJrKBPmZR0iyIy-3QlEMJKMBRWUP7EJhLiSYN0jaivZ30550aSg'
])

let slideInterval: number | null = null

onMounted(() => {
  store.resetSession()
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
  <div class="relative h-screen w-screen overflow-hidden">
    <div class="absolute inset-0 z-0 grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 p-4 opacity-40 scale-105">
      <div 
        v-for="(slide, index) in slides" 
        :key="index"
        :class="[
          'rounded-xl overflow-hidden aspect-[3/4] transition-opacity duration-1000',
          currentSlide === index ? 'opacity-100' : 'opacity-30'
        ]"
        :style="{ transform: `rotate(${(index % 3 - 1) * 5}deg) translateY(${index * 10}px)` }"
      >
        <img :src="slide" :alt="`Slide ${index + 1}`" class="w-full h-full object-cover" />
      </div>
    </div>
    
    <div class="absolute inset-0 bg-grain pointer-events-none" />
    <div class="absolute inset-0 bg-gradient-to-b from-surface/20 via-transparent to-surface/80 pointer-events-none" />
    
    <div class="absolute inset-0 pointer-events-none z-10 overflow-hidden">
      <span class="material-symbols-outlined absolute top-1/4 left-1/4 text-primary opacity-40 text-4xl" style="font-variation-settings: 'FILL' 1;">auto_awesome</span>
      <span class="material-symbols-outlined absolute bottom-1/3 right-1/4 text-secondary opacity-30 text-5xl" style="font-variation-settings: 'FILL' 1;">favorite</span>
      <span class="material-symbols-outlined absolute top-1/3 right-10 text-primary-container opacity-50 text-3xl" style="font-variation-settings: 'FILL' 1;">stars</span>
      <span class="material-symbols-outlined absolute bottom-20 left-10 text-tertiary opacity-40 text-6xl" style="font-variation-settings: 'FILL' 1;">celebration</span>
    </div>
    
    <div class="relative z-20 flex flex-col items-center justify-center h-full gap-12 text-center max-w-2xl px-6">
      <div class="space-y-4">
        <h2 class="font-headline font-black text-6xl md:text-8xl text-primary tracking-tighter drop-shadow-sm">
          Photobooth
        </h2>
        <p class="font-body text-on-surface-variant text-lg md:text-xl font-medium max-w-md mx-auto">
          Siap untuk pose terbaikmu? Ayo buat momen seru hari ini!
        </p>
      </div>
      
      <div class="relative group">
        <div class="absolute -inset-4 bg-gradient-to-r from-primary to-primary-container rounded-full blur-2xl opacity-30 group-hover:opacity-50 transition-opacity duration-500" />
        <button 
          class="relative bg-gradient-to-r from-primary to-primary-container text-on-primary font-headline font-extrabold text-3xl md:text-4xl tracking-widest px-20 py-8 rounded-full shadow-[0_20px_40px_rgba(167,41,90,0.25)] hover:scale-105 active:scale-95 transition-all duration-300"
          @click="handleStart"
        >
          MULAI
        </button>
      </div>
      
      <div class="mt-8 bg-white/60 backdrop-blur-xl border border-white/40 p-4 rounded-xl shadow-lg rotate-2 flex items-center gap-4">
        <div class="w-12 h-12 rounded-full overflow-hidden border-2 border-primary/20 bg-surface-container">
          <span class="material-symbols-outlined text-primary text-3xl" style="font-variation-settings: 'FILL' 1;">photo_camera</span>
        </div>
        <div class="text-left">
          <p class="font-headline font-bold text-on-surface text-sm">Update Terbaru!</p>
          <p class="font-body text-xs text-on-surface-variant">Filter Rose Glow baru saja ditambahkan</p>
        </div>
      </div>
    </div>
    
    <header class="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-8 py-6 bg-surface/80 backdrop-blur-sm">
      <div class="text-3xl font-black text-primary tracking-tighter font-headline">
        Photobooth
      </div>
      <div class="flex items-center gap-6">
        <button class="material-symbols-outlined text-on-surface/60 font-medium hover:scale-105 transition-transform duration-300">
          help
        </button>
        <button class="material-symbols-outlined text-on-surface/60 font-medium hover:scale-105 transition-transform duration-300">
          settings
        </button>
      </div>
    </header>
  </div>
</template>
