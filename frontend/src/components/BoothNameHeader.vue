<script setup lang="ts">
import { useDeviceStore } from '@/stores/device'
import { computed } from 'vue'

const deviceStore = useDeviceStore()

const hasLocation = computed(() => {
  return deviceStore.booth?.location && deviceStore.booth.location.trim() !== ''
})

const isOnline = computed(() => {
  return deviceStore.is_connected && deviceStore.booth?.is_active !== false
})
</script>

<template>
  <div class="flex items-center gap-3 lg:gap-4">
    <!-- Logo/Icon Badge -->
    <div class="relative">
      <div
        class="w-10 h-10 lg:w-12 lg:h-12 rounded-xl lg:rounded-2xl bg-gradient-to-br from-primary to-primary-container flex items-center justify-center shadow-lg shadow-primary/25"
      >
        <span
          class="material-symbols-outlined text-on-primary text-xl lg:text-2xl"
          style="font-variation-settings: 'FILL' 1, 'wght' 700"
        >
          photo_camera
        </span>
      </div>
      <!-- Status Indicator Dot -->
      <div
        :class="[
          'absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 lg:w-4 lg:h-4 rounded-full border-2 border-surface flex items-center justify-center transition-all duration-300',
          isOnline ? 'bg-green-500' : 'bg-amber-500'
        ]"
      >
        <span
          :class="[
            'w-1.5 h-1.5 lg:w-2 lg:h-2 rounded-full bg-white animate-pulse',
            !isOnline && 'opacity-50'
          ]"
        />
      </div>
    </div>

    <!-- Text Content -->
    <div class="flex flex-col">
      <!-- Main Brand Name -->
      <div class="flex items-center gap-2">
        <span class="text-xl lg:text-2xl font-black text-primary tracking-tighter font-headline leading-none">
          Photobooth
        </span>
        <!-- Premium Badge -->
        <div
          class="hidden sm:flex items-center gap-1 px-2 py-0.5 rounded-full bg-gradient-to-r from-secondary-container to-tertiary-container text-secondary-dim text-[10px] font-bold uppercase tracking-wider"
        >
          <span class="material-symbols-outlined text-[12px]" style="font-variation-settings: 'FILL' 1">stars</span>
          <span>Premium</span>
        </div>
      </div>

      <!-- Booth Name & Location -->
      <div class="flex items-center gap-1.5 mt-0.5">
        <template v-if="deviceStore.booth">
          <span class="text-xs lg:text-sm font-semibold text-on-surface-variant">
            {{ deviceStore.booth.name }}
          </span>
          <template v-if="hasLocation">
            <span class="text-on-surface-variant/40">•</span>
            <span class="text-xs lg:text-sm text-on-surface-variant/70 flex items-center gap-1">
              <span class="material-symbols-outlined text-[10px] lg:text-xs">location_on</span>
              {{ deviceStore.booth.location }}
            </span>
          </template>
        </template>
        <template v-else>
          <span class="text-xs lg:text-sm text-on-surface-variant/50 italic">
            Setup Required
          </span>
        </template>
      </div>
    </div>
  </div>
</template>
