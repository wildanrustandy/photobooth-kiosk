<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import ProgressIndicator from '@/components/ProgressIndicator.vue'
import BoothNameHeader from '@/components/BoothNameHeader.vue'

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
  <div class="h-dvh w-dvw overflow-hidden flex flex-col bg-background">
    <div class="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary-container/10 pointer-events-none" />

    <!-- Header -->
    <header class="flex-none flex justify-between items-center px-6 lg:px-8 py-4 lg:py-6 bg-surface/80 backdrop-blur-sm z-50">
      <BoothNameHeader />
      <nav class="hidden md:flex items-center gap-8">
        <span class="text-primary font-extrabold border-b-2 lg:border-b-4 border-primary pb-1 font-headline text-sm lg:text-base">
          Step 1/4
        </span>
      </nav>
      <div class="flex items-center gap-2 lg:gap-3">
        <button class="text-primary hover:scale-105 transition-transform duration-300 active:scale-95">
          <span class="material-symbols-outlined text-xl lg:text-2xl">help</span>
        </button>
        <button class="text-primary hover:scale-105 transition-transform duration-300 active:scale-95">
          <span class="material-symbols-outlined text-xl lg:text-2xl">settings</span>
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 min-h-0 flex flex-col items-center px-6 py-4 lg:py-6 relative z-10 overflow-hidden">
      <div class="flex-none mb-4 lg:mb-6">
        <ProgressIndicator :current-step="1" />
      </div>

      <h1 class="flex-none font-headline text-3xl md:text-4xl lg:text-5xl font-black text-on-surface text-center mb-6 lg:mb-8 tracking-tight leading-tight">
        Mau cetak berapa lembar?
      </h1>

      <div class="flex-1 min-h-0 w-full max-w-4xl flex flex-col md:flex-row gap-6 lg:gap-8 items-stretch overflow-hidden">
        <!-- Sample Photo -->
        <div class="flex-1 min-h-0 bg-surface-container-lowest rounded-xl p-4 lg:p-6 shadow-[0_20px_40px_rgba(36,48,54,0.06)] flex flex-col items-center justify-center relative overflow-hidden group">
          <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-50" />
          <div class="relative w-full max-w-[180px] lg:max-w-[220px] aspect-[3/4] rounded-lg overflow-hidden border-4 lg:border-8 border-white shadow-lg rotate-[-2deg] group-hover:rotate-0 transition-transform duration-500">
            <img
              alt="Sample photobooth strip"
              class="w-full h-full object-cover bg-surface-container"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuDdq6jrNXK7j5BULFeaoh9oS-jXiQZEf0x49j6s8nqA7N5h1fqwHqPBR3b-SpRhhUzZ1phFHpWJ9WuvT8hATQh5yrw7OpqU0vQRk5mblnXOeCqp-_3RZ7r79ZThjhrPDMfXyeS3SbxXRKdk-7X3O7o3-upsiK1Jobrj9nKwjgA6fpksDcTfVPNdOeNA61Owdox7b3hPJNXfrJQY284JmIAOSLi00pBiUjVnqVMn9idvZe8XMXe8tHzWpi8ufuhCnopC6PjvPzYTHyY"
            />
          </div>
          <div class="mt-4 lg:mt-6 text-center relative z-10">
            <p class="font-label text-xs lg:text-sm font-bold text-primary tracking-widest uppercase mb-1">
              Standard Glossy
            </p>
            <p class="font-body text-xs lg:text-sm text-on-surface-variant">4x6 inch • 300dpi</p>
          </div>
        </div>

        <!-- Quantity Selection -->
        <div class="flex-1 min-h-0 bg-surface-container-low rounded-xl p-6 lg:p-8 flex flex-col justify-between shadow-[0_20px_40px_rgba(36,48,54,0.04)] overflow-hidden">
          <div class="flex-none">
            <div class="flex items-center justify-between mb-4 lg:mb-6">
              <span class="font-label text-base lg:text-lg font-bold text-on-surface">Quantity</span>
              <div class="bg-secondary-container text-on-secondary-container px-3 lg:px-4 py-1 rounded-full font-bold text-xs lg:text-sm">
                {{ store.formattedPricePerSheet }} / lembar
              </div>
            </div>

            <div class="flex items-center justify-between bg-surface-container-lowest rounded-full p-1.5 lg:p-2 shadow-sm mb-6 lg:mb-8 border border-outline-variant/10">
              <button
                class="w-12 h-12 lg:w-14 lg:h-14 flex items-center justify-center rounded-full bg-surface-container hover:bg-surface-container-high text-primary transition-all active:scale-90"
                :disabled="store.printCount <= store.MIN_PRINT_COUNT"
                @click="store.decrementPrintCount"
              >
                <span class="material-symbols-outlined font-bold text-2xl lg:text-3xl">remove</span>
              </button>

              <span class="font-headline text-4xl lg:text-5xl font-black text-on-surface">
                {{ store.printCount.toString().padStart(2, '0') }}
              </span>

              <button
                class="w-12 h-12 lg:w-14 lg:h-14 flex items-center justify-center rounded-full bg-primary text-on-primary hover:brightness-110 transition-all active:scale-90 shadow-md"
                :disabled="store.printCount >= store.MAX_PRINT_COUNT"
                @click="store.incrementPrintCount"
              >
                <span class="material-symbols-outlined font-bold text-2xl lg:text-3xl">add</span>
              </button>
            </div>
          </div>

          <div class="flex-none space-y-3 lg:space-y-4">
            <div class="flex justify-between items-end border-b border-outline-variant/20 pb-3 lg:pb-4">
              <span class="text-on-surface-variant font-medium text-sm lg:text-base">Subtotal</span>
              <span class="text-on-surface font-bold text-lg lg:text-xl tracking-tight">
                {{ store.formattedTotalPrice }}
              </span>
            </div>
            <div class="flex justify-between items-baseline pt-1 lg:pt-2">
              <span class="text-on-surface font-bold text-base lg:text-lg">Total Payment</span>
              <span class="text-primary font-black text-2xl lg:text-4xl tracking-tighter">
                {{ store.formattedTotalPrice }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="flex-none flex justify-around items-center px-8 lg:px-10 py-4 lg:py-5 bg-white/60 backdrop-blur-xl rounded-t-[2rem] lg:rounded-t-[3rem] shadow-[0_-20px_40px_rgba(36,48,54,0.06)]">
      <button
        class="flex flex-col items-center justify-center text-on-surface bg-surface-container-lowest rounded-full px-8 lg:px-10 py-3 lg:py-4 shadow-sm hover:brightness-110 transition-all active:scale-90 duration-200 touch-none"
        @click="handleBack"
      >
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-xs lg:text-sm font-bold">arrow_back_ios</span>
          <span class="font-body font-bold uppercase tracking-widest text-[10px] lg:text-xs">Back</span>
        </div>
      </button>

      <button
        :class="[
          'flex flex-col items-center justify-center rounded-full px-10 lg:px-12 py-3 lg:py-4 transition-all active:scale-90 duration-200 touch-none',
          store.canProceed
            ? 'bg-gradient-to-r from-primary to-primary-container text-white scale-105 lg:scale-110 shadow-lg hover:brightness-110'
            : 'bg-surface-container text-on-surface-variant cursor-not-allowed'
        ]"
        :disabled="!store.canProceed"
        @click="handleNext"
      >
        <div class="flex items-center gap-2">
          <span class="font-body font-bold uppercase tracking-widest text-[10px] lg:text-xs">LANJUTKAN</span>
          <span class="material-symbols-outlined text-xs lg:text-sm font-bold">arrow_forward_ios</span>
        </div>
      </button>
    </footer>
  </div>
</template>
