<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { useAdminApi } from '@/composables/useAdminApi'

const router = useRouter()
const store = useAdminStore()
const { fetchTransactions, isLoading } = useAdminApi()

// Filters
const dateRange = ref('7d')
const statusFilter = ref('all')
const boothFilter = ref('all')

// Pagination
const currentPage = ref(1)
const itemsPerPage = 10

onMounted(() => {
  loadTransactions()
})

async function loadTransactions() {
  const params: any = {}

  // Date range
  const endDate = new Date()
  const startDate = new Date()

  switch (dateRange.value) {
    case '7d':
      startDate.setDate(endDate.getDate() - 7)
      break
    case '30d':
      startDate.setDate(endDate.getDate() - 30)
      break
    case 'month':
      startDate.setDate(1)
      break
  }

  params.start_date = startDate.toISOString().split('T')[0]
  params.end_date = endDate.toISOString().split('T')[0]

  if (statusFilter.value !== 'all') {
    params.status = statusFilter.value
  }

  if (boothFilter.value !== 'all') {
    params.booth_id = boothFilter.value
  }

  await fetchTransactions(params)
}

// Computed
const filteredTransactions = computed(() => {
  let result = store.transactions

  if (boothFilter.value !== 'all') {
    result = result.filter(t => t.booth_id === boothFilter.value)
  }

  if (statusFilter.value !== 'all') {
    result = result.filter(t => t.status === statusFilter.value)
  }

  return result
})

const paginatedTransactions = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredTransactions.value.slice(start, end)
})

const totalPages = computed(() => Math.ceil(filteredTransactions.value.length / itemsPerPage))

const totalRevenue = computed(() => {
  return filteredTransactions.value
    .filter(t => t.status === 'success')
    .reduce((sum, t) => sum + t.amount, 0)
})

const totalTransactions = computed(() => filteredTransactions.value.length)

const successRate = computed(() => {
  if (filteredTransactions.value.length === 0) return 0
  const success = filteredTransactions.value.filter(t => t.status === 'success').length
  return Math.round((success / filteredTransactions.value.length) * 100)
})

// Unique booths for filter
const uniqueBooths = computed(() => {
  const boothMap = new Map()
  store.transactions.forEach(t => {
    if (!boothMap.has(t.booth_id)) {
      boothMap.set(t.booth_id, { id: t.booth_id, name: t.booth_name })
    }
  })
  return Array.from(boothMap.values())
})

function getStatusBadgeClass(status: string): string {
  switch (status) {
    case 'success':
      return 'bg-primary-container/20 text-on-primary-container'
    case 'pending':
      return 'bg-secondary-container text-on-secondary-container'
    case 'failed':
      return 'bg-error-container/20 text-error'
    default:
      return 'bg-surface-container text-on-surface-variant'
  }
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('id-ID').format(amount)
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
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
        <router-link to="/admin/transactions" class="bg-surface-container-highest text-primary rounded-xl px-4 py-3 flex items-center gap-3 transition-all hover:translate-x-1 duration-200">
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
        <h2 class="text-xl font-extrabold tracking-tight text-on-surface font-headline">Transactions</h2>
      </div>
      <div class="flex items-center gap-4">
        <button class="p-2 hover:bg-surface-container rounded-full transition-colors relative">
          <span class="material-symbols-outlined text-primary">notifications</span>
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="ml-64 pt-24 px-8 pb-12">
      <!-- Filter Bar -->
      <section class="bg-surface-container-lowest rounded-[2rem] p-6 shadow-sm border border-outline-variant/10 mb-8">
        <div class="flex flex-wrap items-center gap-4">
          <div class="flex-1 min-w-[200px]">
            <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1.5 ml-1">Date Range</label>
            <div class="relative">
              <select
                v-model="dateRange"
                @change="loadTransactions"
                class="w-full appearance-none bg-surface-container-low border-none rounded-xl px-4 py-3 text-sm font-medium text-on-surface focus:ring-2 focus:ring-primary/20 transition-all cursor-pointer outline-none"
              >
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="month">This Month</option>
              </select>
              <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span>
            </div>
          </div>
          <div class="flex-1 min-w-[200px]">
            <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1.5 ml-1">Status</label>
            <div class="relative">
              <select
                v-model="statusFilter"
                @change="currentPage = 1"
                class="w-full appearance-none bg-surface-container-low border-none rounded-xl px-4 py-3 text-sm font-medium text-on-surface focus:ring-2 focus:ring-primary/20 transition-all cursor-pointer outline-none"
              >
                <option value="all">All Status</option>
                <option value="success">Success</option>
                <option value="pending">Pending</option>
                <option value="failed">Failed</option>
              </select>
              <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span>
            </div>
          </div>
          <div class="flex-1 min-w-[200px]">
            <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1.5 ml-1">Booth</label>
            <div class="relative">
              <select
                v-model="boothFilter"
                @change="currentPage = 1"
                class="w-full appearance-none bg-surface-container-low border-none rounded-xl px-4 py-3 text-sm font-medium text-on-surface focus:ring-2 focus:ring-primary/20 transition-all cursor-pointer outline-none"
              >
                <option value="all">All Booths</option>
                <option v-for="booth in uniqueBooths" :key="booth.id" :value="booth.id">{{ booth.name }}</option>
              </select>
              <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span>
            </div>
          </div>
          <div class="self-end pb-0.5">
            <button
              @click="loadTransactions"
              class="bg-primary text-white h-[46px] px-6 rounded-xl font-bold flex items-center gap-2 hover:bg-primary-dim transition-colors shadow-lg shadow-primary/10"
            >
              <span class="material-symbols-outlined text-sm">refresh</span>
              Refresh
            </button>
          </div>
        </div>
      </section>

      <div class="grid grid-cols-12 gap-8">
        <!-- Transactions Table -->
        <div class="col-span-12 lg:col-span-9 space-y-6">
          <!-- Stats Cards -->
          <div class="grid grid-cols-3 gap-4 mb-6">
            <div class="bg-surface-container-lowest p-5 rounded-xl shadow-sm border border-outline-variant/5">
              <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Total Revenue</p>
              <p class="text-2xl font-black text-primary font-headline">Rp {{ formatCurrency(totalRevenue) }}</p>
            </div>
            <div class="bg-surface-container-lowest p-5 rounded-xl shadow-sm border border-outline-variant/5">
              <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Transactions</p>
              <p class="text-2xl font-black text-on-surface font-headline">{{ totalTransactions }}</p>
            </div>
            <div class="bg-surface-container-lowest p-5 rounded-xl shadow-sm border border-outline-variant/5">
              <p class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Success Rate</p>
              <p class="text-2xl font-black text-primary font-headline">{{ successRate }}%</p>
            </div>
          </div>

          <!-- Table -->
          <div class="bg-surface-container-lowest rounded-[2rem] overflow-hidden shadow-sm border border-outline-variant/10">
            <div class="p-6 border-b border-surface-container flex justify-between items-center">
              <h3 class="text-lg font-bold text-on-surface font-headline">Recent Transactions</h3>
              <span class="text-xs font-medium text-on-surface-variant bg-surface-container-low px-3 py-1 rounded-full">{{ filteredTransactions.length }} results</span>
            </div>

            <!-- Loading State -->
            <div v-if="isLoading" class="px-8 py-12 text-center">
              <span class="material-symbols-outlined text-4xl text-primary animate-spin">refresh</span>
              <p class="mt-4 text-on-surface-variant text-sm">Loading transactions...</p>
            </div>

            <!-- Empty State -->
            <div v-else-if="filteredTransactions.length === 0" class="px-8 py-12 text-center">
              <span class="material-symbols-outlined text-4xl text-on-surface-variant">receipt_long</span>
              <p class="mt-4 text-on-surface-variant text-sm">No transactions found</p>
            </div>

            <!-- Table Content -->
            <div v-else class="overflow-x-auto">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="bg-surface-container-low/50">
                    <th class="px-6 py-4 text-[10px] font-extrabold text-on-surface-variant uppercase tracking-widest">ID Sesi</th>
                    <th class="px-6 py-4 text-[10px] font-extrabold text-on-surface-variant uppercase tracking-widest">Reference</th>
                    <th class="px-6 py-4 text-[10px] font-extrabold text-on-surface-variant uppercase tracking-widest">Waktu</th>
                    <th class="px-6 py-4 text-[10px] font-extrabold text-on-surface-variant uppercase tracking-widest">Cetak</th>
                    <th class="px-6 py-4 text-[10px] font-extrabold text-on-surface-variant uppercase tracking-widest">Total</th>
                    <th class="px-6 py-4 text-[10px] font-extrabold text-on-surface-variant uppercase tracking-widest">Status</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-surface-container">
                  <tr
                    v-for="transaction in paginatedTransactions"
                    :key="transaction.id"
                    class="hover:bg-surface-container-low/30 transition-colors"
                  >
                    <td class="px-6 py-5">
                      <span class="text-primary font-bold font-mono">{{ transaction.session_id }}</span>
                    </td>
                    <td class="px-6 py-5 text-sm font-medium text-on-surface-variant font-mono">{{ transaction.reference_id }}</td>
                    <td class="px-6 py-5 text-sm text-on-surface-variant">{{ formatDate(transaction.created_at) }}</td>
                    <td class="px-6 py-5 text-sm font-semibold">{{ transaction.print_count }}</td>
                    <td class="px-6 py-5 text-sm font-bold">Rp {{ formatCurrency(transaction.amount) }}</td>
                    <td class="px-6 py-5">
                      <span
                        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold"
                        :class="getStatusBadgeClass(transaction.status)"
                      >
                        {{ transaction.status.toUpperCase() }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Pagination -->
            <div v-if="filteredTransactions.length > 0" class="p-6 bg-surface-container-low/30 flex justify-between items-center">
              <div class="text-xs font-bold text-on-surface-variant">
                Showing {{ ((currentPage - 1) * itemsPerPage) + 1 }}-{{ Math.min(currentPage * itemsPerPage, filteredTransactions.length) }} of {{ filteredTransactions.length }}
              </div>
              <div class="flex gap-2">
                <button
                  @click="currentPage--"
                  :disabled="currentPage === 1"
                  class="px-3 py-1 bg-surface-container-highest rounded-lg hover:bg-primary-container hover:text-primary transition-all disabled:opacity-50 text-xs font-bold"
                >
                  Prev
                </button>
                <button
                  v-for="page in totalPages"
                  :key="page"
                  @click="currentPage = page"
                  class="px-3 py-1 rounded-lg text-xs font-bold transition-all"
                  :class="currentPage === page ? 'bg-primary text-white shadow-sm' : 'bg-surface-container-highest hover:bg-primary-container hover:text-primary'"
                >
                  {{ page }}
                </button>
                <button
                  @click="currentPage++"
                  :disabled="currentPage === totalPages"
                  class="px-3 py-1 bg-surface-container-highest rounded-lg hover:bg-primary-container hover:text-primary transition-all disabled:opacity-50 text-xs font-bold"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Sidebar -->
        <div class="col-span-12 lg:col-span-3 space-y-6">
          <!-- Popular Booths -->
          <div class="bg-surface-container-lowest rounded-[2rem] p-6 shadow-sm border border-outline-variant/5">
            <div class="flex items-center justify-between mb-8">
              <h3 class="font-bold text-on-surface font-headline">Top Booths</h3>
              <span class="material-symbols-outlined text-tertiary" style="font-variation-settings: 'FILL' 1;">star</span>
            </div>
            <div class="space-y-4">
              <div v-for="booth in uniqueBooths.slice(0, 3)" :key="booth.id" class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-bold text-on-surface">{{ booth.name }}</p>
                  <p class="text-[10px] text-on-surface-variant">
                    {{ filteredTransactions.filter(t => t.booth_id === booth.id && t.status === 'success').length }} transactions
                  </p>
                </div>
                <span class="text-sm font-black text-primary">
                  Rp {{ formatCurrency(filteredTransactions.filter(t => t.booth_id === booth.id && t.status === 'success').reduce((s, t) => s + t.amount, 0)) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Support Card -->
          <div class="bg-surface-container-low rounded-[2rem] p-6 text-center">
            <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-sm">
              <span class="material-symbols-outlined text-primary">support_agent</span>
            </div>
            <h4 class="font-bold text-on-surface mb-2 font-headline">Need Assistance?</h4>
            <p class="text-xs text-on-surface-variant mb-6 leading-relaxed px-4">Our support team is available 24/7 for technical issues.</p>
            <a href="#" class="inline-block text-xs font-extrabold text-primary uppercase tracking-widest border-b-2 border-primary pb-1 hover:text-primary-dim hover:border-primary-dim transition-all">
              Chat with Support
            </a>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
