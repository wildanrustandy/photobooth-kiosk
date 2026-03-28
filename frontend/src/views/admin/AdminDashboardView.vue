<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { useAdminApi } from '@/composables/useAdminApi'

const router = useRouter()
const store = useAdminStore()
const { fetchBooths, createBooth, deleteBooth, isLoading, error } = useAdminApi()

// State
const searchQuery = ref('')
const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const boothToDelete = ref<string | null>(null)

// Create booth form
const newBooth = ref({
  name: '',
  location: '',
  config: {
    price_per_print: 35000,
    timer_default: 5,
    max_print: 10,
    filters: ['Normal', 'Grayscale', 'Sepia']
  }
})

// Debug modal state
function openCreateModal() {
  console.log('Opening create modal')
  showCreateModal.value = true
}

function closeCreateModal() {
  console.log('Closing create modal')
  showCreateModal.value = false
}

// Filtered booths
const filteredBooths = computed(() => {
  if (!searchQuery.value) return store.booths
  const query = searchQuery.value.toLowerCase()
  return store.booths.filter(booth =>
    booth.name.toLowerCase().includes(query) ||
    booth.location.toLowerCase().includes(query)
  )
})

// Stats
const stats = computed(() => {
  const total = store.booths.length
  const active = store.booths.filter(b => b.status === 'active' || (b.is_active && !b.status)).length
  const maintenance = store.booths.filter(b => b.status === 'maintenance').length
  const withDevice = store.booths.filter(b => b.device_id).length
  return { total, active, maintenance, withDevice }
})

onMounted(() => {
  fetchBooths()
})

function navigateToBooth(id: string) {
  router.push(`/admin/booths/${id}`)
}

async function handleCreateBooth() {
  console.log('handleCreateBooth called', newBooth.value)
  if (!newBooth.value.name || !newBooth.value.location) {
    console.log('Validation failed: missing name or location')
    return
  }

  console.log('Creating booth...')
  const result = await createBooth(newBooth.value)
  console.log('Create booth result:', result)

  if (result) {
    showCreateModal.value = false
    newBooth.value = {
      name: '',
      location: '',
      config: {
        price_per_print: 35000,
        timer_default: 5,
        max_print: 10,
        filters: ['Normal', 'Grayscale', 'Sepia']
      }
    }
  }
}

function confirmDelete(boothId: string) {
  boothToDelete.value = boothId
  showDeleteModal.value = true
}

async function handleDelete() {
  if (!boothToDelete.value) return

  const result = await deleteBooth(boothToDelete.value)
  if (result) {
    showDeleteModal.value = false
    boothToDelete.value = null
  }
}

function getStatusColor(booth: any): string {
  // Backend returns is_active, map to status
  const status = booth.status || (booth.is_active ? 'active' : 'inactive')
  switch (status) {
    case 'active': return 'bg-primary'
    case 'maintenance': return 'bg-tertiary'
    case 'inactive': return 'bg-outline'
    default: return 'bg-outline'
  }
}

function getStatusText(booth: any): string {
  // Backend returns is_active, map to status
  const status = booth.status || (booth.is_active ? 'active' : 'inactive')
  return status.toUpperCase()
}

function logout() {
  store.logout()
  router.push('/admin/login')
}
</script>

<template>
  <div class="min-h-screen w-full bg-surface text-on-surface">
    <!-- SideNavBar -->
    <aside class="h-screen w-64 fixed left-0 top-0 overflow-y-auto bg-surface-container-low shadow-[32px_0_32px_-8px_rgba(87,61,166,0.06)] flex flex-col py-6 gap-2 z-50">
      <div class="px-6 mb-8">
        <h1 class="text-2xl font-black text-on-surface tracking-tighter font-headline">Photobooth</h1>
        <div class="mt-4 flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center overflow-hidden">
            <span class="material-symbols-outlined text-on-primary-container">person</span>
          </div>
          <div>
            <p class="font-headline text-sm font-semibold text-on-surface">{{ store.user?.username || 'Admin' }}</p>
            <p class="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">{{ store.user?.role || 'Admin' }}</p>
          </div>
        </div>
      </div>

      <nav class="flex-1 space-y-1 px-2">
        <router-link to="/admin/dashboard" class="bg-surface-container-highest text-primary rounded-xl px-4 py-3 flex items-center gap-3 transition-all hover:translate-x-1 duration-200">
          <span class="material-symbols-outlined">settings_input_component</span>
          <span class="font-headline text-sm font-semibold">Kiosk Management</span>
        </router-link>
        <router-link to="/admin/transactions" class="text-on-surface-variant hover:bg-surface-container-high/50 rounded-xl px-4 py-3 flex items-center gap-3 transition-all hover:translate-x-1 duration-200">
          <span class="material-symbols-outlined">payments</span>
          <span class="font-headline text-sm font-semibold">Transactions</span>
        </router-link>
        <router-link to="/admin/settings" class="text-on-surface-variant hover:bg-surface-container-high/50 rounded-xl px-4 py-3 flex items-center gap-3 transition-all hover:translate-x-1 duration-200">
          <span class="material-symbols-outlined">settings</span>
          <span class="font-headline text-sm font-semibold">Settings</span>
        </router-link>
      </nav>

      <div class="border-t border-primary/5 mt-4 pt-4 px-2">
        <button @click="logout" class="text-on-surface-variant hover:bg-surface-container-high/50 rounded-xl px-4 py-3 flex items-center gap-3 transition-all w-full">
          <span class="material-symbols-outlined">logout</span>
          <span class="font-headline text-sm font-semibold">Logout</span>
        </button>
      </div>
    </aside>

    <!-- TopNavBar -->
    <header class="fixed top-0 right-0 left-64 h-16 z-40 bg-surface/80 backdrop-blur-xl flex justify-between items-center px-8">
      <div class="flex items-center gap-8">
        <div class="relative">
          <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-lg">search</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search kiosks..."
            class="bg-surface-container-highest border-none rounded-full py-2 pl-10 pr-4 text-sm w-64 focus:ring-2 focus:ring-primary/30 transition-all outline-none"
          />
        </div>
      </div>
      <div class="flex items-center gap-4">
        <button class="p-2 hover:bg-surface-container rounded-full transition-colors relative">
          <span class="material-symbols-outlined text-primary">notifications</span>
          <span class="absolute top-2 right-2 w-2 h-2 bg-tertiary rounded-full border-2 border-surface" />
        </button>
        <div class="h-8 w-px bg-outline-variant/20 mx-2" />
        <button
          @click="openCreateModal"
          class="bg-primary text-white px-4 py-2 rounded-xl text-sm font-bold shadow-sm hover:shadow-md transition-all flex items-center gap-2"
        >
          <span class="material-symbols-outlined text-sm">add</span>
          Create New
        </button>
      </div>
    </header>

    <!-- Main Content Canvas -->
    <main class="ml-64 pt-24 pb-12 px-8">
      <!-- Header Section -->
      <div class="flex justify-between items-end mb-10">
        <div>
          <h2 class="text-3xl font-extrabold text-on-surface tracking-tight mb-2 font-headline">Kiosk Management</h2>
          <p class="text-on-surface-variant text-sm font-medium">Monitor and control your fleet of photobooths across all locations.</p>
        </div>
        <button
          @click="openCreateModal"
          class="flex items-center gap-2 bg-white text-primary px-6 py-3 rounded-xl font-bold shadow-[0_8px_32px_-8px_rgba(87,61,166,0.1)] hover:shadow-[0_12px_40px_-8px_rgba(87,61,166,0.15)] transition-all active:scale-95"
        >
          <span class="material-symbols-outlined">add_circle</span>
          Add New Kiosk
        </button>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="mb-6 p-4 bg-error-container/20 rounded-xl text-error text-sm font-medium">
        {{ error }}
      </div>

      <!-- Metric Overview - Bento Style -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        <div class="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-outline-variant/5">
          <div class="flex justify-between items-start mb-4">
            <span class="material-symbols-outlined text-primary bg-primary-container/20 p-2 rounded-lg">devices</span>
            <span class="text-[10px] font-bold text-tertiary bg-tertiary/10 px-2 py-1 rounded-full">TOTAL</span>
          </div>
          <h4 class="text-on-surface-variant text-xs font-bold uppercase tracking-wider mb-1">Total Kiosks</h4>
          <p class="text-3xl font-black text-on-surface tracking-tight font-headline">{{ stats.total }}</p>
        </div>
        <div class="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-outline-variant/5">
          <div class="flex justify-between items-start mb-4">
            <span class="material-symbols-outlined text-primary bg-primary-container/20 p-2 rounded-lg">photo_camera</span>
          </div>
          <h4 class="text-on-surface-variant text-xs font-bold uppercase tracking-wider mb-1">Active</h4>
          <p class="text-3xl font-black text-on-surface tracking-tight font-headline">{{ stats.active }}</p>
        </div>
        <div class="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-outline-variant/5">
          <div class="flex justify-between items-start mb-4">
            <span class="material-symbols-outlined text-tertiary bg-tertiary/10 p-2 rounded-lg">warning</span>
          </div>
          <h4 class="text-on-surface-variant text-xs font-bold uppercase tracking-wider mb-1">Maintenance</h4>
          <p class="text-3xl font-black text-on-surface tracking-tight font-headline">{{ stats.maintenance }}</p>
        </div>
        <div class="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-outline-variant/5">
          <div class="flex justify-between items-start mb-4">
            <span class="material-symbols-outlined text-primary bg-primary-container/20 p-2 rounded-lg">signal_cellular_alt</span>
          </div>
          <h4 class="text-on-surface-variant text-xs font-bold uppercase tracking-wider mb-1">With Device</h4>
          <p class="text-3xl font-black text-on-surface tracking-tight font-headline">{{ stats.withDevice }}</p>
        </div>
      </div>

      <!-- Kiosk List -->
      <div class="bg-surface-container-low rounded-xl p-1 overflow-hidden">
        <div class="bg-surface-container-lowest rounded-[10px] shadow-sm">
          <!-- Table Header -->
          <div class="grid grid-cols-12 gap-4 px-8 py-4 bg-surface-container-highest/30 border-b border-outline-variant/10">
            <div class="col-span-3 text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Machine ID & Status</div>
            <div class="col-span-3 text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Location</div>
            <div class="col-span-2 text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Device</div>
            <div class="col-span-2 text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Last Active</div>
            <div class="col-span-2 text-right text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Actions</div>
          </div>

          <!-- Loading State -->
          <div v-if="isLoading" class="px-8 py-12 text-center">
            <span class="material-symbols-outlined text-4xl text-primary animate-spin">refresh</span>
            <p class="mt-4 text-on-surface-variant text-sm">Loading kiosks...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="filteredBooths.length === 0" class="px-8 py-12 text-center">
            <span class="material-symbols-outlined text-4xl text-on-surface-variant">devices_off</span>
            <p class="mt-4 text-on-surface-variant text-sm">No kiosks found</p>
          </div>

          <!-- List Items -->
          <div v-else class="divide-y divide-outline-variant/5">
            <div
              v-for="(booth, index) in filteredBooths"
              :key="booth.id"
              class="grid grid-cols-12 gap-4 px-8 py-5 items-center hover:bg-surface-container-low transition-colors group"
            >
              <div class="col-span-3">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary font-bold text-sm">
                    {{ String(index + 1).padStart(2, '0') }}
                  </div>
                  <div>
                    <div class="font-bold text-on-surface font-headline">{{ booth.name }}</div>
                    <div class="flex items-center gap-1 text-[10px] font-bold" :class="(booth.status || (booth.is_active ? 'active' : 'inactive')) === 'active' ? 'text-primary' : (booth.status || (booth.is_active ? 'active' : 'inactive')) === 'maintenance' ? 'text-tertiary' : 'text-outline'">
                      <span class="w-1.5 h-1.5 rounded-full" :class="[getStatusColor(booth), (booth.status || (booth.is_active ? 'active' : 'inactive')) === 'active' ? 'animate-pulse' : '']" />
                      {{ getStatusText(booth) }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-span-3">
                <div class="flex items-center gap-2 text-on-surface-variant">
                  <span class="material-symbols-outlined text-sm">location_on</span>
                  <span class="text-sm font-medium">{{ booth.location }}</span>
                </div>
              </div>
              <div class="col-span-2">
                <div v-if="booth.device_id" class="text-sm font-bold text-primary">Connected</div>
                <div v-else class="text-sm text-on-surface-variant">Not assigned</div>
              </div>
              <div class="col-span-2">
                <div class="text-sm font-medium text-on-surface-variant">{{ booth.last_active_at ? new Date(booth.last_active_at).toLocaleDateString() : 'Never' }}</div>
              </div>
              <div class="col-span-2 flex justify-end gap-2">
                <button
                  @click="navigateToBooth(booth.id)"
                  class="p-2 hover:bg-primary-container/20 rounded-lg text-primary transition-colors"
                  title="Settings"
                >
                  <span class="material-symbols-outlined">settings</span>
                </button>
                <button
                  @click="confirmDelete(booth.id)"
                  class="p-2 hover:bg-error-container/20 rounded-lg text-error transition-colors"
                  title="Delete"
                >
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-8 py-4 bg-surface-container-low/30 flex justify-between items-center text-xs font-bold text-on-surface-variant">
            <div>Showing {{ filteredBooths.length }} of {{ store.booths.length }} Kiosks</div>
          </div>
        </div>
      </div>
    </main>

    <!-- Create Modal -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-inverse-surface/50 backdrop-blur-sm" @click="closeCreateModal" />
        <div class="relative bg-surface-container-lowest rounded-2xl p-8 w-full max-w-lg shadow-2xl">
          <h3 class="text-xl font-bold text-on-surface mb-6 font-headline">Create New Kiosk</h3>
          <form @submit.prevent="handleCreateBooth" class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Kiosk Name</label>
              <input
                v-model="newBooth.name"
                type="text"
                placeholder="e.g., Grand Indonesia Booth"
                class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                required
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Location</label>
              <input
                v-model="newBooth.location"
                type="text"
                placeholder="e.g., Grand Indonesia Mall, East Wing"
                class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                required
              />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Price per Print (IDR)</label>
                <input
                  v-model.number="newBooth.config.price_per_print"
                  type="number"
                  class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                />
              </div>
              <div>
                <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Default Timer (sec)</label>
                <input
                  v-model.number="newBooth.config.timer_default"
                  type="number"
                  min="3"
                  max="10"
                  class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                />
              </div>
            </div>
            <div class="flex justify-end gap-4 pt-4">
              <button
                type="button"
                @click="closeCreateModal"
                class="px-6 py-2.5 rounded-xl text-sm font-bold text-on-surface-variant hover:bg-surface-container-highest transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="isLoading"
                class="px-8 py-2.5 rounded-xl text-sm font-bold bg-primary text-white shadow-lg shadow-primary/30 hover:shadow-xl hover:-translate-y-0.5 transition-all disabled:opacity-50"
              >
                {{ isLoading ? 'Creating...' : 'Create Kiosk' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <div v-if="showDeleteModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-inverse-surface/50 backdrop-blur-sm" @click="showDeleteModal = false" />
        <div class="relative bg-surface-container-lowest rounded-2xl p-8 w-full max-w-md shadow-2xl text-center">
          <div class="w-16 h-16 bg-error-container/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="material-symbols-outlined text-3xl text-error">warning</span>
          </div>
          <h3 class="text-xl font-bold text-on-surface mb-2 font-headline">Delete Kiosk?</h3>
          <p class="text-on-surface-variant text-sm mb-6">This action cannot be undone. All associated data will be permanently removed.</p>
          <div class="flex justify-center gap-4">
            <button
              @click="showDeleteModal = false"
              class="px-6 py-2.5 rounded-xl text-sm font-bold text-on-surface-variant hover:bg-surface-container-highest transition-colors"
            >
              Cancel
            </button>
            <button
              @click="handleDelete"
              :disabled="isLoading"
              class="px-8 py-2.5 rounded-xl text-sm font-bold bg-error text-white shadow-lg shadow-error/30 hover:shadow-xl hover:-translate-y-0.5 transition-all disabled:opacity-50"
            >
              {{ isLoading ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
