<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { useAdminApi } from '@/composables/useAdminApi'

const route = useRoute()
const router = useRouter()
const store = useAdminStore()
const {
  fetchBooth,
  updateBooth,
  updateBoothConfig,
  assignDevice,
  unassignDevice,
  isLoading,
  error
} = useAdminApi()

const boothId = route.params.id as string

// Tabs
const activeTab = ref<'general' | 'config' | 'device'>('general')

// Forms
const boothForm = ref({
  name: '',
  location: '',
  status: 'active' as 'active' | 'inactive' | 'maintenance'
})

const configForm = ref({
  price_per_print: 35000,
  timer_default: 5,
  max_print: 10,
  filters: ['Normal', 'Grayscale', 'Sepia'],
  payment_timeout: 5
})

const deviceIdInput = ref('')

// Available filters
const availableFilters = ['Normal', 'Grayscale', 'Sepia', 'Vintage', 'Bright', 'Warm']

// Computed
const booth = computed(() => store.currentBooth)

const hasChanges = computed(() => {
  if (!booth.value) return false
  const currentStatus = booth.value.status || (booth.value.is_active ? 'active' : 'inactive')
  return (
    boothForm.value.name !== booth.value.name ||
    boothForm.value.location !== (booth.value.location || '') ||
    boothForm.value.status !== currentStatus
  )
})

const hasConfigChanges = computed(() => {
  if (!booth.value) return false
  return (
    configForm.value.price_per_print !== booth.value.config.price_per_print ||
    configForm.value.timer_default !== booth.value.config.timer_default ||
    configForm.value.max_print !== booth.value.config.max_print ||
    configForm.value.payment_timeout !== booth.value.config.payment_timeout ||
    JSON.stringify(configForm.value.filters) !== JSON.stringify(booth.value.config.filters)
  )
})

onMounted(async () => {
  const data = await fetchBooth(boothId)
  if (data) {
    // Map is_active to status
    const status = data.status || (data.is_active ? 'active' : 'inactive')
    boothForm.value = {
      name: data.name,
      location: data.location || '',
      status: status as 'active' | 'inactive' | 'maintenance'
    }
    configForm.value = { ...data.config }
  }
})

async function handleSaveGeneral() {
  // Map status to is_active for backend
  const updateData = {
    name: boothForm.value.name,
    location: boothForm.value.location,
    is_active: boothForm.value.status === 'active'
  }
  await updateBooth(boothId, updateData)
}

async function handleSaveConfig() {
  await updateBoothConfig(boothId, configForm.value)
}

async function handleAssignDevice() {
  if (!deviceIdInput.value) return
  await assignDevice(boothId, deviceIdInput.value)
  deviceIdInput.value = ''
}

async function handleUnassignDevice() {
  await unassignDevice(boothId)
}

function toggleFilter(filter: string) {
  const index = configForm.value.filters.indexOf(filter)
  if (index === -1) {
    configForm.value.filters.push(filter)
  } else {
    configForm.value.filters.splice(index, 1)
  }
}

function goBack() {
  router.push('/admin/dashboard')
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
        <router-link to="/admin/dashboard" class="text-on-surface-variant hover:bg-surface-container-high/50 rounded-xl px-4 py-3 flex items-center gap-3 transition-all hover:translate-x-1 duration-200">
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
      <div class="flex items-center gap-4">
        <button
          @click="goBack"
          class="p-2 hover:bg-surface-container rounded-full transition-colors"
        >
          <span class="material-symbols-outlined text-on-surface-variant">arrow_back</span>
        </button>
        <h2 class="text-xl font-extrabold tracking-tight text-on-surface font-headline">Booth Settings</h2>
      </div>
      <div class="flex items-center gap-4">
        <button class="p-2 hover:bg-surface-container rounded-full transition-colors relative">
          <span class="material-symbols-outlined text-primary">notifications</span>
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="ml-64 pt-24 px-8 pb-12">
      <!-- Header -->
      <header class="mb-10">
        <div class="flex items-center gap-4 mb-2">
          <h2 class="text-3xl font-extrabold text-on-surface tracking-tight font-headline">{{ booth?.name || 'Loading...' }}</h2>
          <span
            class="text-[10px] font-bold px-3 py-1 rounded-full"
            :class="(booth?.status || (booth?.is_active ? 'active' : 'inactive')) === 'active' ? 'bg-primary-container/20 text-primary' : (booth?.status || (booth?.is_active ? 'active' : 'inactive')) === 'maintenance' ? 'bg-tertiary/10 text-tertiary' : 'bg-outline/10 text-outline'"
          >
            {{ (booth?.status || (booth?.is_active ? 'active' : 'inactive'))?.toUpperCase() }}
          </span>
        </div>
        <p class="text-on-surface-variant">Manage booth configuration and device settings.</p>
      </header>

      <!-- Error Message -->
      <div v-if="error" class="mb-6 p-4 bg-error-container/20 rounded-xl text-error text-sm font-medium">
        {{ error }}
      </div>

      <!-- Tabs -->
      <nav class="flex gap-8 mb-10 border-b border-outline-variant/10">
        <button
          @click="activeTab = 'general'"
          class="pb-4 px-1 transition-colors whitespace-nowrap font-medium text-sm relative"
          :class="activeTab === 'general' ? 'text-primary font-extrabold border-b-2 border-primary' : 'text-on-surface-variant hover:text-primary'"
        >
          General Information
        </button>
        <button
          @click="activeTab = 'config'"
          class="pb-4 px-1 transition-colors whitespace-nowrap font-medium text-sm relative"
          :class="activeTab === 'config' ? 'text-primary font-extrabold border-b-2 border-primary' : 'text-on-surface-variant hover:text-primary'"
        >
          Configuration
        </button>
        <button
          @click="activeTab = 'device'"
          class="pb-4 px-1 transition-colors whitespace-nowrap font-medium text-sm relative"
          :class="activeTab === 'device' ? 'text-primary font-extrabold border-b-2 border-primary' : 'text-on-surface-variant hover:text-primary'"
        >
          Device Assignment
        </button>
      </nav>

      <div class="grid grid-cols-12 gap-8">
        <!-- Left Content -->
        <div class="col-span-12 lg:col-span-8">
          <!-- General Tab -->
          <div v-if="activeTab === 'general'" class="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/5 overflow-hidden">
            <div class="p-8 border-b border-outline-variant/5">
              <h3 class="text-lg font-bold text-on-surface mb-2 font-headline">General Information</h3>
              <p class="text-sm text-on-surface-variant">Basic booth details and status settings.</p>
            </div>
            <div class="p-8 space-y-6">
              <div>
                <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Booth Name</label>
                <input
                  v-model="boothForm.name"
                  type="text"
                  class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                />
              </div>
              <div>
                <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Location</label>
                <input
                  v-model="boothForm.location"
                  type="text"
                  class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                />
              </div>
              <div>
                <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Status</label>
                <div class="relative">
                  <select
                    v-model="boothForm.status"
                    class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none appearance-none"
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="maintenance">Maintenance</option>
                  </select>
                  <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span>
                </div>
              </div>
            </div>
            <div class="p-8 bg-surface-container-low flex flex-wrap items-center justify-between gap-4">
              <span class="text-sm text-on-surface-variant">Last updated: {{ booth?.updated_at ? new Date(booth.updated_at).toLocaleString() : 'Never' }}</span>
              <div class="flex items-center gap-4">
                <button
                  @click="boothForm = { name: booth?.name || '', location: booth?.location || '', status: (booth?.status || (booth?.is_active ? 'active' : 'inactive')) as 'active' | 'inactive' | 'maintenance' }"
                  class="px-6 py-2.5 rounded-xl text-sm font-bold text-on-surface-variant hover:bg-surface-container-highest transition-colors"
                >
                  Reset
                </button>
                <button
                  @click="handleSaveGeneral"
                  :disabled="!hasChanges || isLoading"
                  class="px-8 py-2.5 rounded-xl text-sm font-bold bg-gradient-to-r from-primary to-primary-dim text-white shadow-lg shadow-primary/30 hover:shadow-xl hover:-translate-y-0.5 transition-all disabled:opacity-50"
                >
                  {{ isLoading ? 'Saving...' : 'Save Changes' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Config Tab -->
          <div v-if="activeTab === 'config'" class="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/5 overflow-hidden">
            <div class="p-8 border-b border-outline-variant/5">
              <h3 class="text-lg font-bold text-on-surface mb-2 font-headline">Booth Configuration</h3>
              <p class="text-sm text-on-surface-variant">Set pricing, timer, and available filters.</p>
            </div>
            <div class="p-8 space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Price per Print (IDR)</label>
                  <div class="relative">
                    <span class="absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant font-medium">Rp</span>
                    <input
                      v-model.number="configForm.price_per_print"
                      type="number"
                      class="w-full bg-surface-container-low border-none rounded-xl py-3 pl-10 pr-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                    />
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Default Timer (sec)</label>
                  <input
                    v-model.number="configForm.timer_default"
                    type="number"
                    min="3"
                    max="10"
                    class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                  />
                </div>
                <div>
                  <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Max Prints</label>
                  <input
                    v-model.number="configForm.max_print"
                    type="number"
                    min="1"
                    max="50"
                    class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                  />
                </div>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Payment Timeout (min)</label>
                  <div class="relative">
                    <select
                      v-model.number="configForm.payment_timeout"
                      class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none appearance-none"
                    >
                      <option :value="3">3 Menit</option>
                      <option :value="5">5 Menit</option>
                    </select>
                    <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span>
                  </div>
                  <p class="text-xs text-on-surface-variant mt-2">QRIS Payment Time Limit</p>
                </div>
              </div>
              <div>
                <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-3">Available Filters</label>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="filter in availableFilters"
                    :key="filter"
                    @click="toggleFilter(filter)"
                    class="px-4 py-2 rounded-full text-sm font-medium transition-all"
                    :class="configForm.filters.includes(filter) ? 'bg-primary text-white' : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container'"
                  >
                    {{ filter }}
                  </button>
                </div>
              </div>
            </div>
            <div class="p-8 bg-surface-container-low flex flex-wrap items-center justify-between gap-4">
              <span class="text-sm text-on-surface-variant">Changes apply to new sessions immediately</span>
              <div class="flex items-center gap-4">
                <button
                  @click="configForm = booth?.config ? { ...booth.config } : { price_per_print: 35000, timer_default: 5, max_print: 10, filters: ['Normal'], payment_timeout: 5 }"
                  class="px-6 py-2.5 rounded-xl text-sm font-bold text-on-surface-variant hover:bg-surface-container-highest transition-colors"
                >
                  Reset
                </button>
                <button
                  @click="handleSaveConfig"
                  :disabled="!hasConfigChanges || isLoading"
                  class="px-8 py-2.5 rounded-xl text-sm font-bold bg-gradient-to-r from-primary to-primary-dim text-white shadow-lg shadow-primary/30 hover:shadow-xl hover:-translate-y-0.5 transition-all disabled:opacity-50"
                >
                  {{ isLoading ? 'Saving...' : 'Save Changes' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Device Tab -->
          <div v-if="activeTab === 'device'" class="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/5 overflow-hidden">
            <div class="p-8 border-b border-outline-variant/5">
              <h3 class="text-lg font-bold text-on-surface mb-2 font-headline">Device Assignment</h3>
              <p class="text-sm text-on-surface-variant">Manage the device connected to this booth.</p>
            </div>
            <div class="p-8 space-y-6">
              <!-- Current Device -->
              <div v-if="booth?.device_id" class="p-6 bg-surface-container-low rounded-xl">
                <div class="flex items-center justify-between">
                  <div>
                    <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Assigned Device</label>
                    <p class="text-lg font-bold text-on-surface font-mono">{{ booth.device_id }}</p>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="w-2 h-2 bg-primary rounded-full animate-pulse" />
                    <span class="text-sm font-bold text-primary">ONLINE</span>
                  </div>
                </div>
              </div>

              <!-- No Device -->
              <div v-else class="p-6 bg-surface-container-low rounded-xl text-center">
                <span class="material-symbols-outlined text-4xl text-on-surface-variant mb-2">devices_off</span>
                <p class="text-on-surface-variant">No device assigned to this booth</p>
              </div>

              <!-- Assign New Device -->
              <div class="pt-4 border-t border-outline-variant/10">
                <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">
                  {{ booth?.device_id ? 'Reassign Device' : 'Assign Device' }}
                </label>
                <div class="flex gap-2">
                  <input
                    v-model="deviceIdInput"
                    type="text"
                    placeholder="Enter device ID"
                    class="flex-1 bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                  />
                  <button
                    @click="handleAssignDevice"
                    :disabled="!deviceIdInput || isLoading"
                    class="bg-primary text-white px-6 rounded-xl font-bold text-sm shadow-lg shadow-primary/20 hover:shadow-xl transition-all disabled:opacity-50"
                  >
                    Assign
                  </button>
                </div>
              </div>

              <!-- Unassign Button -->
              <div v-if="booth?.device_id" class="pt-4">
                <button
                  @click="handleUnassignDevice"
                  :disabled="isLoading"
                  class="w-full py-3 rounded-xl border-2 border-dashed border-error/30 text-error font-bold text-sm hover:border-error hover:bg-error-container/10 transition-all disabled:opacity-50"
                >
                  {{ isLoading ? 'Processing...' : 'Unassign Current Device' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Sidebar -->
        <div class="col-span-12 lg:col-span-4 space-y-6">
          <!-- Booth Info Card -->
          <div class="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-outline-variant/5">
            <div class="w-12 h-12 rounded-xl bg-tertiary/10 text-tertiary flex items-center justify-center mb-6">
              <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">info</span>
            </div>
            <h3 class="text-lg font-bold text-on-surface mb-2 font-headline">Booth Details</h3>
            <div class="space-y-4 mt-4">
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Booth ID</label>
                <p class="text-sm font-mono text-on-surface">{{ booth?.id || '-' }}</p>
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Created</label>
                <p class="text-sm text-on-surface">{{ booth?.created_at ? new Date(booth.created_at).toLocaleDateString() : '-' }}</p>
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Current Price</label>
                <p class="text-sm font-bold text-primary">Rp {{ booth?.config?.price_per_print?.toLocaleString() || '-' }}</p>
              </div>
            </div>
          </div>

          <!-- Sync Info -->
          <div class="bg-primary/5 p-6 rounded-xl border border-primary/10 flex gap-4">
            <span class="material-symbols-outlined text-primary">sync</span>
            <div>
              <h4 class="text-sm font-bold text-primary mb-1">Auto Sync</h4>
              <p class="text-xs text-on-surface-variant leading-relaxed">Configuration changes are automatically synced to the booth within 30 seconds.</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
