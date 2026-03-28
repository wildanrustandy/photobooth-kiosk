<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { usePrinter } from '@/composables/usePrinter'
import PhotoGrid from '@/components/PhotoGrid.vue'
import BoothNameHeader from '@/components/BoothNameHeader.vue'
import ProgressIndicator from '@/components/ProgressIndicator.vue'

const router = useRouter()
const store = useSessionStore()
const { isPrinting, print } = usePrinter()

const showConfirmModal = ref(false)
const showDownloadQR = ref(false)

const autoCloseTime = ref(180)
let timerInterval: ReturnType<typeof setInterval> | null = null

const formattedAutoCloseTime = computed(() => {
  const m = Math.floor(autoCloseTime.value / 60)
  const s = autoCloseTime.value % 60
  return `${m}:${s.toString().padStart(2, '0')}`
})

onMounted(() => {
  timerInterval = setInterval(() => {
    if (autoCloseTime.value > 0) {
      autoCloseTime.value--
    } else {
      if (timerInterval) clearInterval(timerInterval)
      confirmFinish()
    }
  }, 1000)
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})

const sortedPhotos = computed(() => {
  return [...store.photos].sort((a, b) => a.order - b.order)
})

async function handlePrint() {
  await print()
}

function handleDownload() {
  showDownloadQR.value = true
}

function handleFinish() {
  showConfirmModal.value = true
}

function confirmFinish() {
  store.completeSession()
  store.resetSession()
  router.push('/')
}
</script>

<template>
  <div class="h-screen bg-background font-body text-on-surface flex flex-col selection:bg-primary/20 bg-confetti">
    <header class="flex-none flex justify-between items-center px-6 lg:px-8 py-4 bg-white/50 backdrop-blur-sm border-b border-surface-container">
      <BoothNameHeader />
      <ProgressIndicator :current-step="4" />
      <div class="flex items-center gap-1 lg:gap-2">
        <button class="p-2 text-primary hover:bg-white/50 rounded-full transition-all">
          <span class="material-symbols-outlined text-xl lg:text-2xl">help</span>
        </button>
        <button class="p-2 text-primary hover:bg-white/50 rounded-full transition-all">
          <span class="material-symbols-outlined text-xl lg:text-2xl">settings</span>
        </button>
      </div>
    </header>

    <main class="flex-grow flex flex-col px-6 overflow-hidden">
      <div class="flex-none py-4 text-center">
        <h1 class="font-headline font-extrabold text-4xl text-on-surface tracking-tighter">
          You look <span class="text-primary italic">stunning!</span>
        </h1>
      </div>

      <div class="flex-grow grid grid-cols-12 gap-6 items-center overflow-hidden pb-6">
        <div class="col-span-3 h-full flex flex-col justify-center">
          <div class="bg-surface-container-high/60 backdrop-blur-md p-6 rounded-2xl">
            <h3 class="font-headline font-bold text-on-surface mb-4 text-center">The Raw Cuts</h3>
            <PhotoGrid :photos="store.photos" />
          </div>
        </div>

        <div class="col-span-6 h-full flex flex-col justify-center items-center overflow-hidden">
          <div class="bg-surface-container-lowest p-4 rounded-xl shadow-[0_20px_40px_rgba(36,48,54,0.1)] h-full max-h-[75vh] w-auto aspect-[1/2.5] flex flex-col gap-2 transform hover:scale-[1.02] transition-transform">
            <div class="text-center">
              <span class="text-primary font-headline font-black tracking-widest uppercase text-[10px] opacity-40">
                The Social Glow • 2024
              </span>
            </div>
            <div class="flex-grow grid grid-rows-4 gap-2 overflow-hidden">
              <div
                v-for="photo in sortedPhotos"
                :key="photo.id"
                class="w-full h-full bg-surface-container rounded overflow-hidden"
              >
                <img
                  :src="photo.url"
                  :alt="`Shot ${photo.order}`"
                  class="w-full h-full object-cover"
                />
              </div>
            </div>
            <div class="text-center pt-2 border-t border-dashed border-surface-container">
              <span class="font-body text-[10px] font-bold text-on-surface-variant tracking-widest">
                MOMENTS CAPTURED
              </span>
            </div>
          </div>
        </div>

        <div class="col-span-3 h-full flex flex-col justify-center gap-4">
          <div class="bg-white/60 backdrop-blur-xl border border-white/40 p-5 rounded-2xl shadow-lg text-center">
            <h3 class="font-headline font-bold text-on-surface text-lg mb-1">Get Digital Copy</h3>
            <p class="text-on-surface-variant text-xs mb-4">Scan for instant download</p>
            <div class="bg-white p-3 rounded-lg inline-block shadow-sm border border-surface-container-low mb-3">
              <div class="w-32 h-32 bg-on-surface flex items-center justify-center p-2 rounded">
                <div class="grid grid-cols-4 grid-rows-4 gap-1 w-full h-full">
                  <div class="bg-white" /><div class="bg-on-surface" /><div class="bg-white" /><div class="bg-white" />
                  <div class="bg-white" /><div class="bg-white" /><div class="bg-on-surface" /><div class="bg-white" />
                  <div class="bg-on-surface" /><div class="bg-on-surface" /><div class="bg-white" /><div class="bg-on-surface" />
                  <div class="bg-white" /><div class="bg-on-surface" /><div class="bg-on-surface" /><div class="bg-white" />
                </div>
              </div>
            </div>
          </div>

          <div class="flex flex-col gap-3">
            <button
              :class="[
                'w-full py-4 rounded-full shadow-lg hover:brightness-110 active:scale-95 transition-all flex items-center justify-center gap-3 text-white',
                isPrinting ? 'bg-on-surface-variant cursor-wait' : 'bg-primary'
              ]"
              :disabled="isPrinting"
              @click="handlePrint"
            >
              <span v-if="isPrinting" class="material-symbols-outlined animate-spin">sync</span>
              <span v-else class="material-symbols-outlined">print</span>
              <span class="font-headline font-extrabold uppercase tracking-widest">
                {{ isPrinting ? 'Printing...' : 'Print Now' }}
              </span>
            </button>

            <button
              class="w-full bg-surface-container-low py-4 rounded-full border border-surface-container hover:bg-surface-container transition-all active:scale-95 flex items-center justify-center gap-3"
              @click="handleDownload"
            >
              <span class="material-symbols-outlined text-on-surface">download</span>
              <span class="font-label font-bold text-on-surface text-sm uppercase tracking-wider">
                Download
              </span>
            </button>
          </div>
        </div>
      </div>
    </main>

    <footer class="flex-none bg-white/60 backdrop-blur-xl px-12 py-6 flex justify-between items-center border-t border-surface-container">
      <div class="w-[120px] invisible" />

      <div class="flex flex-col items-center">
        <p class="text-on-surface-variant text-[10px] font-bold uppercase tracking-[0.2em] mb-1">
          Otomatis selesai dalam <span class="text-error">{{ formattedAutoCloseTime }}</span>
        </p>
        <button
          class="flex items-center gap-3 bg-gradient-to-r from-primary to-primary-container text-white rounded-full px-16 py-4 shadow-xl hover:brightness-105 active:scale-95 transition-all"
          @click="handleFinish"
        >
          <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">check_circle</span>
          <span class="font-headline font-extrabold uppercase tracking-[0.15em] text-lg">SELESAI</span>
        </button>
      </div>

      <div class="w-[120px] invisible" />
    </footer>

    <div v-if="showConfirmModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-surface-container-lowest rounded-2xl p-8 max-w-md mx-4 shadow-2xl">
        <h3 class="font-headline font-bold text-xl text-on-surface mb-4">Akhiri Sesi?</h3>
        <p class="text-on-surface-variant mb-6">Apakah yakin ingin mengakhiri sesi ini?</p>
        <div class="flex gap-4">
          <button
            class="flex-1 py-3 rounded-full border border-outline-variant text-on-surface font-bold hover:bg-surface-container transition-all"
            @click="showConfirmModal = false"
          >
            Batal
          </button>
          <button
            class="flex-1 py-3 rounded-full bg-primary text-white font-bold hover:brightness-110 transition-all"
            @click="confirmFinish"
          >
            Ya, Selesai
          </button>
        </div>
      </div>
    </div>

    <div v-if="showDownloadQR" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click="showDownloadQR = false">
      <div class="bg-surface-container-lowest rounded-2xl p-8 max-w-sm mx-4 shadow-2xl" @click.stop>
        <h3 class="font-headline font-bold text-xl text-on-surface mb-2 text-center">Download Foto</h3>
        <p class="text-on-surface-variant text-sm mb-6 text-center">Scan QR untuk download foto Anda</p>

        <div class="bg-white p-4 rounded-xl shadow-inner mb-4">
          <div class="w-48 h-48 mx-auto bg-surface-container flex items-center justify-center rounded-lg">
            <span class="material-symbols-outlined text-primary text-6xl">qr_code_2</span>
          </div>
        </div>

        <p class="text-on-surface-variant text-xs text-center">
          Link valid selama 7 hari
        </p>

        <button
          class="w-full mt-6 py-3 rounded-full border border-outline-variant text-on-surface font-bold hover:bg-surface-container transition-all"
          @click="showDownloadQR = false"
        >
          Tutup
        </button>
      </div>
    </div>
  </div>
</template>
