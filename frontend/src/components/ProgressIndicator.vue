<script setup lang="ts">
defineProps<{
  currentStep: number
  totalSteps?: number
}>()
</script>

<template>
  <div class="flex gap-3 justify-center">
    <div 
      v-for="step in (totalSteps || 5)" 
      :key="step"
      :class="[
        'h-3 rounded-full transition-all duration-300',
        step === currentStep 
          ? 'w-12 bg-primary shadow-sm shadow-primary/30' 
          : 'w-3 bg-surface-container-highest'
      ]"
    />
  </div>
</template>
