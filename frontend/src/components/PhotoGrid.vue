<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  photos: Array<{ id: string; url: string; order: number }>
  selectedOrder?: number
}>()

const emit = defineEmits<{
  select: [order: number]
  retake: [order: number]
}>()

const sortedPhotos = computed(() => {
  return [...props.photos].sort((a, b) => a.order - b.order)
})

function handleClick(order: number) {
  emit('select', order)
}
</script>

<template>
  <div class="grid grid-cols-2 gap-3">
    <div 
      v-for="photo in sortedPhotos" 
      :key="photo.id"
      :class="[
        'aspect-square rounded-lg overflow-hidden border-2 shadow-sm cursor-pointer transition-all hover:scale-105',
        selectedOrder === photo.order 
          ? 'border-primary ring-2 ring-primary/30' 
          : 'border-white hover:border-primary/50'
      ]"
      :style="{ transform: `rotate(${(photo.order % 2 === 0 ? -1 : 1) * (photo.order)}deg)` }"
      @click="handleClick(photo.order)"
    >
      <img 
        :src="photo.url" 
        :alt="`Raw shot ${photo.order}`"
        class="w-full h-full object-cover"
      />
    </div>
    
    <div 
      v-for="i in (4 - photos.length)" 
      :key="`empty-${i}`"
      class="aspect-square rounded-lg bg-surface-container border-2 border-dashed border-outline-variant/30 flex items-center justify-center"
    >
      <span class="material-symbols-outlined text-outline-variant text-3xl">add_a_photo</span>
    </div>
  </div>
</template>
