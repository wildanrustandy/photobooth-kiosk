<script setup lang="ts">
defineProps<{
  formattedTime: string
  isWarning?: boolean
}>()
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
