<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  countdown: number
  warningThreshold?: number
}>()

const isWarning = computed(() => {
  return props.countdown <= (props.warningThreshold || 60)
})

const formattedTime = computed(() => {
  const minutes = Math.floor(props.countdown / 60)
  const seconds = props.countdown % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})
</script>

<template>
  <div class="flex flex-col items-center bg-white rounded-lg p-6">
    <span class="text-on-surface-variant font-label text-xs uppercase tracking-widest font-bold mb-1">
      Sisa Waktu
    </span>
    <div 
      :class="[
        'text-4xl font-black tracking-tighter transition-colors',
        isWarning ? 'text-error animate-pulse' : 'text-primary'
      ]"
    >
      {{ formattedTime }}
    </div>
  </div>
</template>
