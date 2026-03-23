<script setup lang="ts">
const filters = [
  { id: 'Normal', label: 'Normal' },
  { id: 'Lembut', label: 'Lembut' },
  { id: 'Hitam-Putih', label: 'Hitam-Putih' },
  { id: 'BW2', label: 'BW-2', badge: 'Free' },
  { id: 'BW3', label: 'BW-3', badge: 'Free' },
  { id: 'Vintage', label: 'Vintage' },
  { id: 'Bright', label: 'Bright', badge: 'Free' }
]

defineProps<{
  selectedFilter: string
}>()

const emit = defineEmits<{
  select: [filterId: string]
}>()
</script>

<template>
  <div class="w-full overflow-x-auto no-scrollbar">
    <div class="flex gap-4 pb-4 px-4 min-w-max justify-center">
      <button
        v-for="filter in filters"
        :key="filter.id"
        :class="[
          'relative px-8 py-3.5 rounded-full font-bold transition-all',
          selectedFilter === filter.id
            ? 'border-2 border-primary bg-white text-primary shadow-sm'
            : 'border border-on-surface/10 bg-white text-on-surface hover:border-on-surface/30'
        ]"
        @click="emit('select', filter.id)"
      >
        {{ filter.label }}
        <span 
          v-if="filter.badge"
          :class="[
            'absolute -top-2 -right-1 text-[8px] text-white px-1.5 py-0.5 rounded-full font-black uppercase',
            filter.id === 'BW2' ? 'bg-gradient-to-r from-blue-400 to-emerald-400' :
            filter.id === 'BW3' ? 'bg-gradient-to-r from-purple-400 to-pink-400' :
            'bg-gradient-to-r from-blue-400 to-indigo-400'
          ]"
        >
          {{ filter.badge }}
        </span>
      </button>
    </div>
  </div>
</template>
