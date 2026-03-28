<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import QRCode from 'qrcode'
import { useSessionStore } from '@/stores/session'
import { usePayment } from '@/composables/usePayment'
import ProgressIndicator from '@/components/ProgressIndicator.vue'
import CountdownTimer from '@/components/CountdownTimer.vue'

const router = useRouter()
const store = useSessionStore()
const { 
  createPayment, 
  countdown,
  formattedCountdown,
  stopPolling,
  simulatePaymentSuccess,
  qrString
} = usePayment()

const qrCodeUrl = ref<string | null>(null)

watch(qrString, async (newVal) => {
  if (newVal && newVal !== 'demo-qr-string') {
    try {
      qrCodeUrl.value = await QRCode.toDataURL(newVal, { width: 400, margin: 1 })
    } catch (e) {
      console.error('Failed to generate QR code', e)
    }
  } else {
    qrCodeUrl.value = null
  }
})

const isDemo = import.meta.env.DEV || !import.meta.env.VITE_API_BASE

onMounted(async () => {
  await createPayment()
})

onUnmounted(() => {
  stopPolling()
})

function handleBack() {
  stopPolling()
  router.push('/print-count')
}

function handleNext() {
  if (store.paymentStatus === 'success') {
    store.nextStep()
    router.push('/photo-session')
  }
}

function handleSimulatePayment() {
  simulatePaymentSuccess()
}
</script>

<template>
  <div class="h-dvh w-dvw overflow-hidden flex flex-col bg-background text-on-surface">
    <header class="flex-none flex justify-between items-center px-8 py-6 bg-surface/80 backdrop-blur-sm">
      <div class="flex items-center gap-4">
        <span class="text-3xl font-black text-primary tracking-tighter font-headline">Photobooth</span>
      </div>
      <nav class="hidden md:flex items-center gap-8">
        <span class="text-primary font-extrabold border-b-4 border-primary pb-1 font-headline">
          Step 2/5
        </span>
      </nav>
      <div class="flex items-center gap-4">
        <button class="text-on-surface/60 font-medium hover:scale-105 transition-transform duration-300">
          <span class="material-symbols-outlined text-2xl">help</span>
        </button>
        <button class="text-on-surface/60 font-medium hover:scale-105 transition-transform duration-300">
          <span class="material-symbols-outlined text-2xl">settings</span>
        </button>
      </div>
    </header>
    
    <main class="flex-1 min-h-0 px-6 max-w-4xl mx-auto flex flex-col items-center overflow-hidden py-4 w-full">
      <ProgressIndicator :current-step="2" :total-steps="5" class="mb-4 flex-none" />
      
      <section class="w-full text-center mb-6 flex-none">
        <h1 class="text-4xl md:text-5xl font-extrabold text-on-surface tracking-tight mb-2 font-headline">
          Pembayaran QRIS
        </h1>
        <p class="text-on-surface-variant font-medium text-lg font-body">
          Scan QR dengan aplikasi pembayaran Anda
        </p>
      </section>
      
      <div class="grid grid-cols-1 md:grid-cols-12 gap-6 w-full flex-1 min-h-0">
        <div class="md:col-span-4 flex flex-col gap-6 order-2 md:order-1">
          <div class="bg-surface-container-low p-8 rounded-xl shadow-[0_20px_40px_rgba(36,48,54,0.06)] flex flex-col justify-between h-full">
            <div>
              <h3 class="font-headline font-bold text-xl text-primary mb-6">Ringkasan</h3>
              <div class="space-y-4">
                <div class="flex justify-between items-center">
                  <span class="text-on-surface-variant font-medium font-body">Paket Foto</span>
                  <span class="text-on-surface font-bold font-body">Standard</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-on-surface-variant font-medium font-body">Jumlah Cetak</span>
                  <span class="text-on-surface font-bold font-body">{{ store.printCount }} Lembar</span>
                </div>
                <div class="w-full h-px bg-outline-variant/20 my-2" />
                <div class="flex justify-between items-end">
                  <span class="text-on-surface-variant font-medium font-body">Total Harga</span>
                  <span class="text-2xl font-black text-on-surface font-headline">
                    {{ store.formattedTotalPrice }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="mt-8 pt-8 border-t border-outline-variant/10">
              <CountdownTimer 
                :formatted-time="formattedCountdown" 
                :is-warning="countdown <= 60" 
              />
            </div>
          </div>
        </div>
        
        <div class="md:col-span-8 order-1 md:order-2 flex items-center justify-center min-h-0">
          <div class="bg-white p-2 rounded-xl shadow-lg relative overflow-hidden flex flex-col h-full max-h-[35vh] aspect-square">
            <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent pointer-events-none" />
            
            <div class="relative bg-white border-8 border-white rounded-[1.5rem] flex flex-col items-center flex-1 justify-center min-h-0">
              <div class="w-full h-full flex items-center justify-center relative p-4 bg-surface-container-low/30 rounded-lg">
                <div class="relative w-full h-full bg-white rounded-lg p-4 shadow-inner flex items-center justify-center">
                  <img v-if="qrCodeUrl" :src="qrCodeUrl" alt="QRIS Code" class="w-full h-full object-contain" />
                  <div v-else class="w-full h-full bg-surface-container animate-pulse rounded-lg flex items-center justify-center">
                    <span class="material-symbols-outlined text-primary text-6xl">qr_code_2</span>
                  </div>
                  <div class="absolute top-0 left-0 w-full h-1 bg-primary/40 shadow-[0_0_15px_rgba(167,41,90,0.5)] rounded-full" />
                </div>
                
                <div class="absolute top-4 left-4 w-12 h-12 border-t-4 border-l-4 border-primary rounded-tl-lg" />
                <div class="absolute top-4 right-4 w-12 h-12 border-t-4 border-r-4 border-primary rounded-tr-lg" />
                <div class="absolute bottom-4 left-4 w-12 h-12 border-b-4 border-l-4 border-primary rounded-bl-lg" />
                <div class="absolute bottom-4 right-4 w-12 h-12 border-b-4 border-r-4 border-primary rounded-br-lg" />
              </div>
              
              <div class="mt-4 mb-2 flex items-center gap-4 flex-none">
                <span class="font-headline font-extrabold text-on-surface-variant tracking-widest text-sm uppercase">
                  QRIS
                </span>
                <div class="h-6 w-px bg-outline-variant" />
                <span class="font-headline font-extrabold text-on-surface-variant tracking-widest text-sm uppercase">
                  GPN
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="mt-6 mb-4 w-full grid grid-cols-1 md:grid-cols-3 gap-6 flex-none">
        <div class="flex items-start gap-4 p-4">
          <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-primary font-bold">qr_code_scanner</span>
          </div>
          <div>
            <h4 class="font-bold text-on-surface font-headline">Buka Aplikasi</h4>
            <p class="text-sm text-on-surface-variant font-body">
              Gunakan Dana, GoPay, OVO, ShopeePay, atau BCA Mobile.
            </p>
          </div>
        </div>
        <div class="flex items-start gap-4 p-4">
          <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-primary font-bold">ads_click</span>
          </div>
          <div>
            <h4 class="font-bold text-on-surface font-headline">Scan & Bayar</h4>
            <p class="text-sm text-on-surface-variant font-body">
              Pindai kode QR dan masukkan PIN keamanan Anda.
            </p>
          </div>
        </div>
        <div class="flex items-start gap-4 p-4">
          <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-primary font-bold">task_alt</span>
          </div>
          <div>
            <h4 class="font-bold text-on-surface font-headline">Konfirmasi</h4>
            <p class="text-sm text-on-surface-variant font-body">
              Layar akan otomatis beralih setelah pembayaran berhasil.
            </p>
          </div>
        </div>
      </div>
    </main>
    
<footer class="flex-none flex justify-around items-center px-10 py-6 bg-white/60 backdrop-blur-xl shadow-[0_-20px_40px_rgba(36,48,54,0.06)] rounded-t-[3rem]">
      <!-- Demo Mode Button -->
      <button 
        v-if="isDemo && store.paymentStatus === 'pending'"
        class="flex flex-col items-center justify-center bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-full px-8 py-4 shadow-lg hover:brightness-110 transition-all active:scale-90 duration-200 touch-none"
        @click="handleSimulatePayment"
      >
        <span class="material-symbols-outlined text-xl mb-1">check_circle</span>
        <span class="font-body font-bold uppercase tracking-widest text-xs">Demo: Bayar</span>
      </button>
      
      <button 
        class="flex flex-col items-center justify-center text-on-surface bg-surface-container-lowest rounded-full px-10 py-4 shadow-sm hover:brightness-110 transition-all active:scale-90 duration-200 touch-none"
        @click="handleBack"
      >
        <span class="material-symbols-outlined text-xl mb-1">arrow_back_ios</span>
        <span class="font-body font-bold uppercase tracking-widest text-xs">Batal</span>
      </button>
      
      <div v-if="store.paymentStatus === 'pending'" class="flex flex-col items-center text-on-surface-variant/40 animate-pulse">
        <span class="font-headline font-bold text-xs uppercase tracking-[0.2em]">
          Menunggu Pembayaran...
        </span>
      </div>
      
      <button 
        v-if="store.paymentStatus === 'success'"
        class="flex flex-col items-center justify-center bg-gradient-to-r from-primary to-primary-container text-white rounded-full px-12 py-4 scale-110 shadow-lg hover:brightness-110 transition-all active:scale-90 duration-200 touch-none"
        @click="handleNext"
      >
        <span class="material-symbols-outlined text-xl mb-1">arrow_forward_ios</span>
        <span class="font-body font-bold uppercase tracking-widest text-xs">Next</span>
      </button>
    </footer>
  </div>
</template>
