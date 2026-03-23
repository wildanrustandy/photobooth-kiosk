<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useCamera } from '@/composables/useCamera'
import FilterSelector from '@/components/FilterSelector.vue'

const router = useRouter()
const store = useSessionStore()
const { videoRef, startCamera, stopCamera, capturePhoto, isActive, error } = useCamera()

console.debug('Camera initialized', videoRef)

const isCapturing = ref(false)
const currentPhotoIndex = ref(0)
const showCountdown = ref(false)
const countdownValue = ref(0)
const shutterSound = ref<HTMLAudioElement | null>(null)
const showRetakeModal = ref(false)
const retakePhotoIndex = ref<number | null>(null)

const filters = [
  { id: 'Normal', label: 'Normal', css: '' },
  { id: 'Lembut', label: 'Lembut', css: 'brightness(1.05) contrast(0.95) saturate(0.9)' },
  { id: 'Hitam-Putih', label: 'Hitam-Putih', css: 'grayscale(100%)' },
  { id: 'BW2', label: 'BW-2', css: 'grayscale(100%) contrast(1.2)' },
  { id: 'BW3', label: 'BW-3', css: 'grayscale(100%) brightness(1.1) contrast(1.3)' },
  { id: 'Vintage', label: 'Vintage', css: 'sepia(40%) contrast(1.1) brightness(1.05)' },
  { id: 'Bright', label: 'Bright', css: 'brightness(1.15) contrast(1.05)' }
]

const currentFilter = computed(() => {
  return filters.find(f => f.id === store.selectedFilter) || filters[0]
})

onMounted(async () => {
  await startCamera()
  shutterSound.value = new Audio('/sounds/shutter.mp3')
})

function playShutterSound() {
  if (shutterSound.value) {
    shutterSound.value.currentTime = 0
    shutterSound.value.play().catch(() => {})
  }
}

async function startPhotoSession() {
  if (isCapturing.value || !isActive.value) return
  
  isCapturing.value = true
  currentPhotoIndex.value = 0
  
  for (let i = 0; i < 4; i++) {
    currentPhotoIndex.value = i
    await startCountdown()
    await captureCurrentPhoto(i + 1)
  }
  
  isCapturing.value = false
}

async function startCountdown() {
  showCountdown.value = true
  countdownValue.value = store.timer
  
  return new Promise<void>(resolve => {
    const interval = setInterval(() => {
      countdownValue.value--
      if (countdownValue.value <= 0) {
        clearInterval(interval)
        showCountdown.value = false
        resolve()
      }
    }, 1000)
  })
}

async function captureCurrentPhoto(order: number) {
  const blob = await capturePhoto()
  if (blob) {
    playShutterSound()
    const url = URL.createObjectURL(blob)
    store.addPhoto({
      id: `photo-${Date.now()}`,
      url,
      order,
      blob
    })
  }
}

async function retakePhoto(order: number) {
  store.removePhoto(order)
  retakePhotoIndex.value = order
  showRetakeModal.value = false
  
  await startCountdown()
  await captureCurrentPhoto(order)
}

async function retakeAll() {
  store.clearPhotos()
  await startPhotoSession()
}

function handleNext() {
  if (store.allPhotosTaken) {
    stopCamera()
    store.nextStep()
    router.push('/preview')
  }
}

function handleBack() {
  stopCamera()
  router.push('/payment')
}

function openRetakeModal(order: number) {
  retakePhotoIndex.value = order
  showRetakeModal.value = true
}
</script>

<template>
  <div class="min-h-screen w-full bg-surface text-on-surface font-body overflow-x-hidden">
    <main class="min-h-screen w-full flex flex-col items-center px-4 py-12 lg:px-24">
      <div class="w-full max-w-6xl flex flex-col items-center justify-center">
        <section class="w-full flex flex-col items-center">
          <div class="w-full max-w-4xl aspect-[4/3] relative rounded-[2.5rem] overflow-hidden bg-gray-100 shadow-2xl border-8 border-white">
            <video 
              ref="videoRef"
              autoplay 
              playsinline
              muted
              :style="{ filter: currentFilter.css }"
              class="w-full h-full object-cover transform scale-x-[-1]"
            />
            
            <div v-if="!isActive && !error" class="absolute inset-0 flex items-center justify-center bg-surface-container">
              <span class="material-symbols-outlined text-primary text-6xl animate-pulse">photo_camera</span>
            </div>
            
            <div v-if="error" class="absolute inset-0 flex flex-col items-center justify-center bg-error-container">
              <span class="material-symbols-outlined text-error text-6xl mb-4">error</span>
              <p class="text-error font-bold">{{ error }}</p>
              <button 
                class="mt-4 px-6 py-2 bg-surface-container-lowest rounded-full font-bold text-on-surface"
                @click="startCamera"
              >
                Coba Lagi
              </button>
            </div>
            
            <div class="absolute top-6 left-1/2 -translate-x-1/2 z-10">
              <div class="bg-white/90 backdrop-blur-md rounded-full px-2 py-2 flex items-center gap-1 shadow-lg border border-white/50">
                <span class="material-symbols-outlined text-primary text-xl ml-3 mr-1">timer</span>
                <button 
                  v-for="t in [3, 5, 10]" 
                  :key="t"
                  :class="[
                    'w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all',
                    store.timer === t ? 'bg-primary text-white' : 'text-on-surface hover:bg-black/5'
                  ]"
                  :disabled="isCapturing"
                  @click="store.setTimer(t)"
                >
                  {{ t }}s
                </button>
              </div>
            </div>
            
            <div v-if="showCountdown" class="absolute inset-0 bg-black/50 flex items-center justify-center z-20">
              <span class="font-headline font-black text-white text-[12rem] animate-pulse drop-shadow-2xl">
                {{ countdownValue }}
              </span>
            </div>
            
            <div v-if="isCapturing && !showCountdown" class="absolute bottom-6 left-1/2 -translate-x-1/2 z-10">
              <div class="bg-white/90 backdrop-blur-md rounded-full px-6 py-3 shadow-lg">
                <span class="font-headline font-bold text-primary">
                  Foto {{ currentPhotoIndex + 1 }}/4
                </span>
              </div>
            </div>
          </div>
          
          <div class="w-full mt-12 flex flex-col items-center gap-6">
            <p class="text-sm font-bold text-on-surface/80">Pilih filter</p>
            <FilterSelector 
              :selected-filter="store.selectedFilter"
              @select="store.setFilter"
            />
            
            <div class="flex gap-4 mt-4">
              <button 
                v-if="!isCapturing && !store.allPhotosTaken"
                class="flex items-center justify-center gap-4 bg-primary text-white px-20 py-6 rounded-full shadow-[0_15px_40px_rgba(244,100,142,0.3)] hover:scale-[1.02] transition-all active:scale-95"
                @click="startPhotoSession"
              >
                <span class="material-symbols-outlined text-3xl" style="font-variation-settings: 'FILL' 1">photo_camera</span>
                <span class="font-headline font-extrabold text-2xl tracking-tight">Mulai Foto</span>
              </button>
              
              <button 
                v-if="store.allPhotosTaken"
                class="flex items-center justify-center gap-4 bg-gradient-to-r from-primary to-primary-container text-white px-20 py-6 rounded-full shadow-[0_15px_40px_rgba(167,41,90,0.3)] hover:scale-[1.02] transition-all active:scale-95"
                @click="handleNext"
              >
                <span class="font-headline font-extrabold text-2xl tracking-tight">Berikutnya</span>
                <span class="material-symbols-outlined text-3xl">arrow_forward</span>
              </button>
            </div>
            
            <div v-if="store.photosTaken > 0 && store.photosTaken < 4" class="flex gap-2 mt-4">
              <div 
                v-for="i in 4" 
                :key="i"
                :class="[
                  'w-16 h-16 rounded-lg overflow-hidden border-2 cursor-pointer transition-all',
                  i <= store.photosTaken ? 'border-primary' : 'border-outline-variant/30 bg-surface-container'
                ]"
                @click="i <= store.photosTaken && openRetakeModal(i)"
              >
                <img 
                  v-if="store.photos[i-1]" 
                  :src="store.photos[i-1].url" 
                  class="w-full h-full object-cover"
                />
              </div>
            </div>
            
            <button 
              v-if="store.allPhotosTaken"
              class="text-on-surface-variant font-medium hover:text-primary transition-colors"
              @click="retakeAll"
            >
              <span class="material-symbols-outlined text-sm align-middle mr-1">refresh</span>
              Retake Semua
            </button>
          </div>
        </section>
      </div>
    </main>
    
    <div v-if="showRetakeModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-surface-container-lowest rounded-2xl p-8 max-w-md mx-4 shadow-2xl">
        <h3 class="font-headline font-bold text-xl text-on-surface mb-4">Retake Foto?</h3>
        <p class="text-on-surface-variant mb-6">Apakah ingin mengulang foto ini?</p>
        <div class="flex gap-4">
          <button 
            class="flex-1 py-3 rounded-full border border-outline-variant text-on-surface font-bold hover:bg-surface-container transition-all"
            @click="showRetakeModal = false"
          >
            Batal
          </button>
          <button 
            class="flex-1 py-3 rounded-full bg-primary text-white font-bold hover:brightness-110 transition-all"
            @click="retakePhotoIndex && retakePhoto(retakePhotoIndex)"
          >
            Ya, Retake
          </button>
        </div>
      </div>
    </div>
    
    <footer class="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-10 pb-12 pt-6 bg-white/60 backdrop-blur-xl rounded-t-[3rem] shadow-[0_-20px_40px_rgba(36,48,54,0.06)]">
      <button 
        class="flex flex-col items-center justify-center text-on-surface bg-surface-container-lowest rounded-full px-10 py-4 shadow-sm hover:brightness-110 transition-all active:scale-90 duration-200 touch-none"
        @click="handleBack"
      >
        <span class="material-symbols-outlined text-xl mb-1">arrow_back_ios</span>
        <span class="font-body font-bold uppercase tracking-widest text-xs">Back</span>
      </button>
    </footer>
  </div>
</template>
