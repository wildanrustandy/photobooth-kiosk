<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import ProgressIndicator from '@/components/ProgressIndicator.vue'

const router = useRouter()
const store = useSessionStore()

function handleBack() {
  router.push('/')
}

function handleNext() {
  if (store.canProceed) {
    store.nextStep()
    router.push('/payment')
  }
}
</script>

<template>
  <div class="min-h-screen w-full bg-background">
    <div class="fixed inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary-container/10 pointer-events-none" />
    
    <header class="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-8 py-6 bg-surface/80 backdrop-blur-sm">
      <div class="text-3xl font-black text-primary tracking-tighter font-headline">
        Photobooth
      </div>
      <nav class="hidden md:flex items-center gap-8">
        <span class="text-primary font-extrabold border-b-4 border-primary pb-1 font-headline">
          Step 1/5
        </span>
      </nav>
      <div class="flex items-center gap-4">
        <button class="text-primary hover:scale-105 transition-transform duration-300 active:scale-95">
          <span class="material-symbols-outlined text-2xl">help</span>
        </button>
        <button class="text-primary hover:scale-105 transition-transform duration-300 active:scale-95">
          <span class="material-symbols-outlined text-2xl">settings</span>
        </button>
      </div>
    </header>
    
    <main class="pt-32 pb-48 px-6 max-w-4xl mx-auto flex flex-col items-center relative z-10">
      <ProgressIndicator :current-step="1" :total-steps="5" class="mb-12" />
      
      <h1 class="font-headline text-5xl md:text-6xl font-black text-on-surface text-center mb-16 tracking-tight leading-tight">
        Mau cetak berapa lembar?
      </h1>
      
      <div class="w-full flex flex-col md:flex-row gap-8 items-stretch">
        <div class="flex-1 bg-surface-container-lowest rounded-xl p-6 shadow-[0_20px_40px_rgba(36,48,54,0.06)] flex flex-col items-center justify-center relative overflow-hidden group">
          <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-50" />
          <div class="relative w-full aspect-[3/4] rounded-lg overflow-hidden border-8 border-white shadow-lg rotate-[-2deg] group-hover:rotate-0 transition-transform duration-500">
            <img 
              alt="Sample photobooth strip" 
              class="w-full h-full object-cover bg-surface-container"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuDdq6jrNXK7j5BULFeaoh9oS-jXiQZEf0x49j6s8nqA7N5h1fqwHqPBR3b-SpRhhUzZ1phFHpWJ9WuvT8hATQh5yrw7OpqU0vQRk5mblnXOeCqp-_3RZ7r79ZThjhrPDMfXyeS3SbxXRKdk-7X3O7o3-upsiK1Jobrj9nKwjgA6fpksDcTfVPNdOeNA61Owdox7b3hPJNXfrJQY284JmIAOSLi00pBiUjVnqVMn9idvZe8XMXe8tHzWpi8ufuhCnopC6PjvPzYTHyY"
            />
          </div>
          <div class="mt-8 text-center relative z-10">
            <p class="font-label text-sm font-bold text-primary tracking-widest uppercase mb-1">
              Standard Glossy
            </p>
            <p class="font-body text-on-surface-variant">4x6 inch • 300dpi</p>
          </div>
        </div>
        
        <div class="flex-1 bg-surface-container-low rounded-xl p-10 flex flex-col justify-between shadow-[0_20px_40px_rgba(36,48,54,0.04)]">
          <div>
            <div class="flex items-center justify-between mb-8">
              <span class="font-label text-lg font-bold text-on-surface">Quantity</span>
              <div class="bg-secondary-container text-on-secondary-container px-4 py-1 rounded-full font-bold text-sm">
                Rp 35.000 / lembar
              </div>
            </div>
            
            <div class="flex items-center justify-between bg-surface-container-lowest rounded-full p-2 shadow-sm mb-12 border border-outline-variant/10">
              <button 
                class="w-16 h-16 flex items-center justify-center rounded-full bg-surface-container hover:bg-surface-container-high text-primary transition-all active:scale-90"
                :disabled="store.printCount <= store.MIN_PRINT_COUNT"
                @click="store.decrementPrintCount"
              >
                <span class="material-symbols-outlined font-bold text-3xl">remove</span>
              </button>
              
              <span class="font-headline text-5xl font-black text-on-surface">
                {{ store.printCount.toString().padStart(2, '0') }}
              </span>
              
              <button 
                class="w-16 h-16 flex items-center justify-center rounded-full bg-primary text-on-primary hover:brightness-110 transition-all active:scale-90 shadow-md"
                :disabled="store.printCount >= store.MAX_PRINT_COUNT"
                @click="store.incrementPrintCount"
              >
                <span class="material-symbols-outlined font-bold text-3xl">add</span>
              </button>
            </div>
          </div>
          
          <div class="space-y-4">
            <div class="flex justify-between items-end border-b border-outline-variant/20 pb-4">
              <span class="text-on-surface-variant font-medium">Subtotal</span>
              <span class="text-on-surface font-bold text-xl tracking-tight">
                {{ store.formattedTotalPrice }}
              </span>
            </div>
            <div class="flex justify-between items-baseline pt-2">
              <span class="text-on-surface font-bold text-lg">Total Payment</span>
              <span class="text-primary font-black text-4xl tracking-tighter">
                {{ store.formattedTotalPrice }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <footer class="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-10 pb-12 pt-6 bg-white/60 backdrop-blur-xl rounded-t-[3rem] shadow-[0_-20px_40px_rgba(36,48,54,0.06)]">
      <button 
        class="flex flex-col items-center justify-center text-on-surface bg-surface-container-lowest rounded-full px-10 py-4 shadow-sm hover:brightness-110 transition-all active:scale-90 duration-200 touch-none"
        @click="handleBack"
      >
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-sm font-bold">arrow_back_ios</span>
          <span class="font-body font-bold uppercase tracking-widest text-xs">Back</span>
        </div>
      </button>
      
      <button 
        :class="[
          'flex flex-col items-center justify-center rounded-full px-12 py-4 transition-all active:scale-90 duration-200 touch-none',
          store.canProceed 
            ? 'bg-gradient-to-r from-primary to-primary-container text-white scale-110 shadow-lg hover:brightness-110' 
            : 'bg-surface-container text-on-surface-variant cursor-not-allowed'
        ]"
        :disabled="!store.canProceed"
        @click="handleNext"
      >
        <div class="flex items-center gap-2">
          <span class="font-body font-bold uppercase tracking-widest text-xs">LANJUTKAN</span>
          <span class="material-symbols-outlined text-sm font-bold">arrow_forward_ios</span>
        </div>
      </button>
    </footer>
  </div>
</template>
