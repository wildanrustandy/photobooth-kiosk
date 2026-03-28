<script setup lang="ts">
const steps = [
  'Pilih Jumlah',
  'Pembayaran',
  'Sesi Foto',
  'Cetak'
]

defineProps<{
  currentStep: number
}>()
</script>

<template>
  <div class="flex items-center justify-center gap-2 flex-wrap">
    <template v-for="(step, index) in steps" :key="index">
      <span
        :class="[
          'font-headline font-bold text-sm lg:text-base transition-all duration-300',
          index + 1 === currentStep
            ? 'text-primary'
            : index + 1 < currentStep
              ? 'text-on-surface/60'
              : 'text-on-surface/30'
        ]"
      >
        {{ step }}
      </span>
      <span
        v-if="index < steps.length - 1"
        :class="[
          'material-symbols-outlined text-lg transition-all duration-300',
          index + 1 < currentStep ? 'text-on-surface/60' : 'text-on-surface/30'
        ]"
      >
        chevron_right
      </span>
    </template>
  </div>
</template>
