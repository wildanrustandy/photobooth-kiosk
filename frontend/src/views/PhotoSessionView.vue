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
const showRetakeAllModal = ref(false)
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
  showRetakeAllModal.value = true
}

async function confirmRetakeAll() {
  showRetakeAllModal.value = false
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
  <div class="h-dvh w-dvw overflow-hidden flex flex-col bg-surface text-on-surface font-body">
    <header class="flex-none flex justify-between items-center px-8 py-4 bg-white/50 backdrop-blur-sm">
      <div class="text-2xl font-black text-primary tracking-tighter font-headline">Photobooth</div>
      <span class="text-primary font-extrabold font-headline">Step 4/5</span>
    </header>
    
    <main class="flex-1 min-h-0 w-full flex flex-col overflow-y-auto">
      <!-- Title -->
      <h1 class="font-headline text-4xl font-black text-on-surface text-center py-6">
        {{ store.allPhotosTaken ? 'Foto Selesai!' : 'Sesi Foto' }}
      </h1>
      
      <div class="flex-1 min-h-0 w-full max-w-5xl mx-auto flex flex-col lg:flex-row gap-6 items-start px-6">
        <!-- Camera Preview -->
        <div class="flex-1 min-h-0 w-full flex flex-col">
          <div class="aspect-[4/3] relative rounded-[2rem] overflow-hidden bg-surface-container shadow-xl border-4 border-white">
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
            
            <!-- Timer Selection -->
            <div class="absolute top-4 left-1/2 -translate-x-1/2 z-10">
              <div class="bg-white/90 backdrop-blur-md rounded-full px-2 py-2 flex items-center gap-1 shadow-lg">
                <span class="material-symbols-outlined text-primary text-lg ml-2 mr-1">timer</span>
                <button 
                  v-for="t in [3, 5, 10]" 
                  :key="t"
                  :class="[
                    'w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all',
                    store.timer === t ? 'bg-primary text-white' : 'text-on-surface hover:bg-black/5'
                  ]"
                  :disabled="isCapturing"
                  @click="store.setTimer(t)"
                >
                  {{ t }}s
                </button>
              </div>
            </div>
            
            <!-- Countdown Overlay -->
            <div v-if="showCountdown" class="absolute inset-0 bg-black/60 flex items-center justify-center z-20">
              <div class="text-center">
                <span class="font-headline font-black text-white text-[8rem] leading-none drop-shadow-2xl">
                  {{ countdownValue }}
                </span>
                <p class="text-white/80 text-xl font-bold mt-4">Foto {{ currentPhotoIndex + 1 }}/4</p>
              </div>
            </div>
            
            <!-- Progress During Capture -->
            <div v-if="isCapturing && !showCountdown" class="absolute bottom-4 left-1/2 -translate-x-1/2 z-10">
              <div class="bg-white/90 backdrop-blur-md rounded-full px-6 py-2 shadow-lg">
                <span class="font-headline font-bold text-primary">
                  Memotret {{ currentPhotoIndex + 1 }}/4...
                </span>
              </div>
            </div>
          </div>
          
          <!-- Filter Selection -->
          <div class="mt-6">
            <p class="text-sm font-bold text-on-surface/60 text-center mb-3">Pilih Filter</p>
            <FilterSelector 
              :selected-filter="store.selectedFilter"
              @select="store.setFilter"
            />
          </div>
          
          <!-- Action Buttons -->
          <div class="mt-6 flex justify-center gap-4">
            <button 
              v-if="!isCapturing && !store.allPhotosTaken"
              class="flex items-center justify-center gap-3 bg-primary text-white px-16 py-5 rounded-full shadow-lg hover:scale-[1.02] transition-all active:scale-95"
              @click="startPhotoSession"
            >
              <span class="material-symbols-outlined text-2xl" style="font-variation-settings: 'FILL' 1">photo_camera</span>
              <span class="font-headline font-extrabold text-xl">Mulai Foto</span>
            </button>
            
            <button 
              v-if="store.allPhotosTaken"
              class="flex items-center justify-center gap-3 bg-gradient-to-r from-primary to-primary-container text-white px-16 py-5 rounded-full shadow-lg hover:scale-[1.02] transition-all active:scale-95"
              @click="handleNext"
            >
              <span class="font-headline font-extrabold text-xl">Berikutnya</span>
              <span class="material-symbols-outlined text-2xl">arrow_forward</span>
            </button>
          </div>
        </div>
        
        <!-- Photo Preview Grid -->
        <div class="w-full lg:w-80 shrink-0 min-h-0 flex flex-col">
          <div class="bg-surface-container-low rounded-2xl p-6 shadow-lg">
            <h3 class="font-headline font-bold text-on-surface mb-4 text-center">Preview</h3>
            
            <div class="grid grid-cols-2 gap-3">
              <!-- Photo 1 -->
              <div 
                :class="[
                  'aspect-square rounded-xl overflow-hidden border-4 transition-all cursor-pointer relative group',
                  store.photosTaken >= 1 ? 'border-white shadow-md hover:border-primary' : 'border-outline-variant/20 bg-surface-container'
                ]"
                @click="store.photosTaken >= 1 && openRetakeModal(1)"
              >
                <img 
                  v-if="store.photos.find(p => p.order === 1)" 
                  :src="store.photos.find(p => p.order === 1)?.url" 
                  class="w-full h-full object-cover"
                />
                <div v-else class="w-full h-full flex items-center justify-center">
                  <span class="text-on-surface-variant/30 font-headline font-black text-3xl">1</span>
                </div>
                <div v-if="store.photosTaken >= 1" class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <span class="material-symbols-outlined text-white text-2xl">refresh</span>
                </div>
              </div>
              
              <!-- Photo 2 -->
              <div 
                :class="[
                  'aspect-square rounded-xl overflow-hidden border-4 transition-all cursor-pointer relative group',
                  store.photosTaken >= 2 ? 'border-white shadow-md hover:border-primary' : 'border-outline-variant/20 bg-surface-container'
                ]"
                @click="store.photosTaken >= 2 && openRetakeModal(2)"
              >
                <img 
                  v-if="store.photos.find(p => p.order === 2)" 
                  :src="store.photos.find(p => p.order === 2)?.url" 
                  class="w-full h-full object-cover"
                />
                <div v-else class="w-full h-full flex items-center justify-center">
                  <span class="text-on-surface-variant/30 font-headline font-black text-3xl">2</span>
                </div>
                <div v-if="store.photosTaken >= 2" class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <span class="material-symbols-outlined text-white text-2xl">refresh</span>
                </div>
              </div>
              
              <!-- Photo 3 -->
              <div 
                :class="[
                  'aspect-square rounded-xl overflow-hidden border-4 transition-all cursor-pointer relative group',
                  store.photosTaken >= 3 ? 'border-white shadow-md hover:border-primary' : 'border-outline-variant/20 bg-surface-container'
                ]"
                @click="store.photosTaken >= 3 && openRetakeModal(3)"
              >
                <img 
                  v-if="store.photos.find(p => p.order === 3)" 
                  :src="store.photos.find(p => p.order === 3)?.url" 
                  class="w-full h-full object-cover"
                />
                <div v-else class="w-full h-full flex items-center justify-center">
                  <span class="text-on-surface-variant/30 font-headline font-black text-3xl">3</span>
                </div>
                <div v-if="store.photosTaken >= 3" class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <span class="material-symbols-outlined text-white text-2xl">refresh</span>
                </div>
              </div>
              
              <!-- Photo 4 -->
              <div 
                :class="[
                  'aspect-square rounded-xl overflow-hidden border-4 transition-all cursor-pointer relative group',
                  store.photosTaken >= 4 ? 'border-white shadow-md hover:border-primary' : 'border-outline-variant/20 bg-surface-container'
                ]"
                @click="store.photosTaken >= 4 && openRetakeModal(4)"
              >
                <img 
                  v-if="store.photos.find(p => p.order === 4)" 
                  :src="store.photos.find(p => p.order === 4)?.url" 
                  class="w-full h-full object-cover"
                />
                <div v-else class="w-full h-full flex items-center justify-center">
                  <span class="text-on-surface-variant/30 font-headline font-black text-3xl">4</span>
                </div>
                <div v-if="store.photosTaken >= 4" class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <span class="material-symbols-outlined text-white text-2xl">refresh</span>
                </div>
              </div>
            </div>
            
            <!-- Progress Info -->
            <div class="mt-4 text-center">
              <p class="text-sm text-on-surface-variant">
                {{ store.photosTaken }}/4 foto selesai
              </p>
            </div>
            
            <!-- Retake All Button -->
            <button 
              v-if="store.allPhotosTaken"
              class="mt-4 w-full py-3 rounded-full border-2 border-outline-variant text-on-surface-variant font-bold hover:bg-surface-container transition-all flex items-center justify-center gap-2"
              @click="retakeAll"
            >
              <span class="material-symbols-outlined text-lg">refresh</span>
              Retake Semua
            </button>
          </div>
        </div>
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
    
    <!-- Retake All Modal -->
    <div v-if="showRetakeAllModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-surface-container-lowest rounded-2xl p-8 max-w-md mx-4 shadow-2xl">
        <h3 class="font-headline font-bold text-xl text-on-surface mb-4">Retake Semua Foto?</h3>
        <p class="text-on-surface-variant mb-6">Apakah Anda yakin ingin mengulang semua foto dari awal? Semua foto saat ini akan terhapus.</p>
        <div class="flex gap-4">
          <button 
            class="flex-1 py-3 rounded-full border border-outline-variant text-on-surface font-bold hover:bg-surface-container transition-all"
            @click="showRetakeAllModal = false"
          >
            Batal
          </button>
          <button 
            class="flex-1 py-3 rounded-full bg-error text-white font-bold hover:brightness-110 transition-all"
            @click="confirmRetakeAll"
          >
            Ya, Retake Semua
          </button>
        </div>
      </div>
    </div>
    
    <footer class="flex-none flex justify-around items-center px-10 pb-12 pt-6 bg-white/60 backdrop-blur-xl rounded-t-[3rem] shadow-[0_-20px_40px_rgba(36,48,54,0.06)]">
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
