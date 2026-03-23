<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps<{
  qrString?: string
  amount: string
}>()

const qrDataUrl = ref<string>('')

onMounted(() => {
  if (props.qrString) {
    generateQRCode(props.qrString)
  }
})

async function generateQRCode(data: string) {
  try {
    const QRCode = await import('qrcode')
    qrDataUrl.value = await QRCode.default.toDataURL(data, {
      width: 300,
      margin: 2,
      color: {
        dark: '#243036',
        light: '#ffffff'
      }
    })
  } catch (err) {
    console.error('QR generation error:', err)
  }
}
</script>

<template>
  <div class="bg-white p-2 rounded-xl shadow-lg relative overflow-hidden group">
    <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent pointer-events-none" />
    
    <div class="relative bg-white border-[1.5rem] border-white rounded-[2rem] flex flex-col items-center">
      <div class="w-full aspect-square max-w-[300px] flex items-center justify-center relative p-4 bg-surface-container-low/30 rounded-lg">
        <div class="relative w-full h-full bg-white rounded-lg p-4 shadow-inner">
          <img 
            v-if="qrDataUrl" 
            :src="qrDataUrl" 
            alt="QRIS Code" 
            class="w-full h-full object-contain mix-blend-multiply"
          />
          <div v-else class="w-full h-full bg-surface-container animate-pulse rounded" />
          
          <div class="absolute top-0 left-0 w-full h-1 bg-primary/40 shadow-[0_0_15px_rgba(167,41,90,0.5)] rounded-full" />
        </div>
        
        <div class="absolute top-4 left-4 w-12 h-12 border-t-4 border-l-4 border-primary rounded-tl-lg" />
        <div class="absolute top-4 right-4 w-12 h-12 border-t-4 border-r-4 border-primary rounded-tr-lg" />
        <div class="absolute bottom-4 left-4 w-12 h-12 border-b-4 border-l-4 border-primary rounded-bl-lg" />
        <div class="absolute bottom-4 right-4 w-12 h-12 border-b-4 border-r-4 border-primary rounded-br-lg" />
      </div>
      
      <div class="mt-6 mb-4 flex items-center gap-4">
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
</template>
