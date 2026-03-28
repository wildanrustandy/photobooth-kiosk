<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goToSetup() {
  router.push('/device-setup')
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

    <!-- Main Content -->
    <main class="flex-1 flex flex-col items-center justify-center px-6 z-10">
      <div class="flex flex-col items-center gap-8 max-w-md w-full text-center">
        <!-- Error Icon -->
        <div class="relative">
          <div class="absolute inset-0 bg-error/20 rounded-full blur-2xl animate-pulse" />
          <div class="relative w-32 h-32 bg-gradient-to-br from-error to-error-dim rounded-full flex items-center justify-center shadow-lg shadow-error/30">
            <span class="material-symbols-outlined text-white text-7xl" style="font-variation-settings: 'FILL' 1;">cancel</span>
          </div>
        </div>

        <!-- Title & Description -->
        <div class="space-y-3">
          <h1 class="font-headline font-extrabold text-4xl text-on-surface tracking-tight">
            Sesi Diambil
          </h1>
          <p class="font-body text-on-surface-variant text-lg font-medium max-w-sm mx-auto">
            Perangkat lain telah mengambil alih booth ini. Perangkat ini tidak dapat melanjutkan operasi photobooth.
          </p>
        </div>

        <!-- Info Card -->
        <div class="bg-surface-container-low/60 backdrop-blur-sm border border-white/40 rounded-2xl px-8 py-6 w-full max-w-sm">
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 bg-tertiary-container rounded-xl flex items-center justify-center shrink-0">
              <span class="material-symbols-outlined text-tertiary text-2xl" style="font-variation-settings: 'FILL' 1;">info</span>
            </div>
            <div class="text-left">
              <p class="text-sm font-bold text-on-surface mb-1">Apa yang terjadi?</p>
              <p class="text-xs text-on-surface-variant leading-relaxed">
                Booth ini telah ditugaskan ke perangkat lain oleh administrator. Ini adalah tindakan keamanan untuk mencegah akses tidak sah.
              </p>
            </div>
          </div>
        </div>

        <!-- Action Button -->
        <div class="relative group">
          <div class="absolute -inset-3 bg-gradient-to-r from-primary to-primary-container rounded-full blur-xl opacity-30 group-hover:opacity-50 transition-opacity duration-500" />
          <button
            @click="goToSetup"
            class="relative bg-gradient-to-r from-primary to-primary-container text-on-primary font-headline font-extrabold text-xl px-12 py-5 rounded-full shadow-lg shadow-primary/25 hover:scale-105 active:scale-95 transition-all duration-300 flex items-center gap-3"
          >
            <span class="material-symbols-outlined text-2xl" style="font-variation-settings: 'FILL' 1;">settings</span>
            Kembali ke Setup
          </button>
        </div>

        <!-- Contact Info -->
        <div class="mt-4 flex items-center gap-2 text-on-surface-variant">
          <span class="material-symbols-outlined text-sm">support_agent</span>
          <span class="text-xs font-medium">
            Hubungi administrator jika masalah berlanjut
          </span>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="flex-none px-6 py-4 z-10">
      <p class="text-center text-[10px] text-outline font-medium tracking-tight">
        Photobooth Kiosk v1.0.0 • Akses Ditolak
      </p>
    </footer>
  </div>
</template>
