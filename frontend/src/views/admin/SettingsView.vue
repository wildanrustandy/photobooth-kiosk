<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { useAdminApi } from '@/composables/useAdminApi'

const router = useRouter()
const store = useAdminStore()
const { isLoading: _isLoading } = useAdminApi()

// Tabs
const activeTab = ref<'profile' | 'system'>('profile')

// Profile form
const profileForm = ref({
  username: '',
  email: '',
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// System settings
const systemSettings = ref({
  currency: 'IDR',
  timezone: 'Asia/Jakarta',
  language: 'id',
  emailNotifications: true,
  smsNotifications: false,
  autoLogout: 30
})

onMounted(() => {
  if (store.user) {
    profileForm.value.username = store.user.username
    profileForm.value.email = store.user.email || ''
  }
})

async function handleSaveProfile() {
  // TODO: Implement profile update API
  alert('Profile update functionality will be implemented')
}

async function handleSaveSystem() {
  // TODO: Implement system settings API
  alert('System settings saved')
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
        <router-link to="/admin/settings" class="bg-surface-container-highest text-primary rounded-xl px-4 py-3 flex items-center gap-3 transition-all hover:translate-x-1 duration-200">
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
        <h2 class="text-xl font-extrabold tracking-tight text-on-surface font-headline">Settings</h2>
      </div>
      <div class="flex items-center gap-4">
        <button class="p-2 hover:bg-surface-container rounded-full transition-colors relative">
          <span class="material-symbols-outlined text-primary">notifications</span>
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="ml-64 pt-24 px-10 pb-12 min-h-screen">
      <header class="mb-10">
        <h2 class="text-3xl font-extrabold text-on-surface tracking-tight mb-2 font-headline">Settings</h2>
        <p class="text-on-surface-variant">Manage your admin profile and system preferences.</p>
      </header>

      <!-- Tabs Navigation -->
      <nav class="flex gap-8 mb-10 border-b border-outline-variant/10">
        <button
          @click="activeTab = 'profile'"
          class="pb-4 px-1 transition-colors whitespace-nowrap font-medium text-sm relative"
          :class="activeTab === 'profile' ? 'text-primary font-extrabold border-b-2 border-primary' : 'text-on-surface-variant hover:text-primary'"
        >
          Profile
        </button>
        <button
          @click="activeTab = 'system'"
          class="pb-4 px-1 transition-colors whitespace-nowrap font-medium text-sm relative"
          :class="activeTab === 'system' ? 'text-primary font-extrabold border-b-2 border-primary' : 'text-on-surface-variant hover:text-primary'"
        >
          System Settings
        </button>
      </nav>

      <div class="grid grid-cols-12 gap-8">
        <!-- Left Content -->
        <div class="col-span-12 lg:col-span-8">
          <!-- Profile Tab -->
          <div v-if="activeTab === 'profile'" class="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/5 overflow-hidden">
            <div class="p-8 border-b border-outline-variant/5">
              <h3 class="text-lg font-bold text-on-surface mb-2 font-headline">Profile Information</h3>
              <p class="text-sm text-on-surface-variant">Update your account details and password.</p>
            </div>
            <div class="p-8 space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Username</label>
                  <input
                    v-model="profileForm.username"
                    type="text"
                    class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                    readonly
                  />
                </div>
                <div>
                  <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Email</label>
                  <input
                    v-model="profileForm.email"
                    type="email"
                    placeholder="admin@example.com"
                    class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                  />
                </div>
              </div>

              <div class="border-t border-outline-variant/10 pt-6">
                <h4 class="text-sm font-bold text-on-surface mb-4">Change Password</h4>
                <div class="space-y-4">
                  <div>
                    <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Current Password</label>
                    <input
                      v-model="profileForm.currentPassword"
                      type="password"
                      class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                    />
                  </div>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">New Password</label>
                      <input
                        v-model="profileForm.newPassword"
                        type="password"
                        class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Confirm New Password</label>
                      <input
                        v-model="profileForm.confirmPassword"
                        type="password"
                        class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="p-8 bg-surface-container-low flex flex-wrap items-center justify-between gap-4">
              <span class="text-sm text-on-surface-variant">Last login: {{ new Date().toLocaleDateString() }}</span>
              <div class="flex items-center gap-4">
                <button
                  @click="profileForm = { username: store.user?.username || '', email: store.user?.email || '', currentPassword: '', newPassword: '', confirmPassword: '' }"
                  class="px-6 py-2.5 rounded-xl text-sm font-bold text-on-surface-variant hover:bg-surface-container-highest transition-colors"
                >
                  Reset
                </button>
                <button
                  @click="handleSaveProfile"
                  class="px-8 py-2.5 rounded-xl text-sm font-bold bg-gradient-to-r from-primary to-primary-dim text-white shadow-lg shadow-primary/30 hover:shadow-xl hover:-translate-y-0.5 transition-all"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>

          <!-- System Tab -->
          <div v-if="activeTab === 'system'" class="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/5 overflow-hidden">
            <div class="p-8 border-b border-outline-variant/5">
              <h3 class="text-lg font-bold text-on-surface mb-2 font-headline">System Settings</h3>
              <p class="text-sm text-on-surface-variant">Configure system-wide preferences.</p>
            </div>
            <div class="p-8 space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Currency</label>
                  <div class="relative">
                    <select
                      v-model="systemSettings.currency"
                      class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none appearance-none"
                    >
                      <option value="IDR">IDR - Indonesian Rupiah</option>
                      <option value="USD">USD - US Dollar</option>
                      <option value="MYR">MYR - Malaysian Ringgit</option>
                    </select>
                    <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span>
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Timezone</label>
                  <div class="relative">
                    <select
                      v-model="systemSettings.timezone"
                      class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none appearance-none"
                    >
                      <option value="Asia/Jakarta">Asia/Jakarta (WIB)</option>
                      <option value="Asia/Makassar">Asia/Makassar (WITA)</option>
                      <option value="Asia/Jayapura">Asia/Jayapura (WIT)</option>
                    </select>
                    <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span>
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Language</label>
                  <div class="relative">
                    <select
                      v-model="systemSettings.language"
                      class="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none appearance-none"
                    >
                      <option value="id">Bahasa Indonesia</option>
                      <option value="en">English</option>
                    </select>
                    <span class="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">expand_more</span>
                  </div>
                </div>
              </div>

              <div class="border-t border-outline-variant/10 pt-6">
                <h4 class="text-sm font-bold text-on-surface mb-4">Notifications</h4>
                <div class="space-y-4">
                  <label class="flex items-center gap-4 cursor-pointer">
                    <div class="relative flex items-center">
                      <input
                        v-model="systemSettings.emailNotifications"
                        type="checkbox"
                        class="peer appearance-none w-5 h-5 rounded-md border-2 border-outline-variant checked:bg-primary checked:border-primary transition-all cursor-pointer"
                      />
                      <span class="material-symbols-outlined absolute text-white text-[16px] left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 opacity-0 peer-checked:opacity-100 transition-opacity pointer-events-none">check</span>
                    </div>
                    <div>
                      <span class="text-sm font-semibold text-on-surface">Email Notifications</span>
                      <p class="text-xs text-on-surface-variant">Receive transaction and system alerts via email</p>
                    </div>
                  </label>
                  <label class="flex items-center gap-4 cursor-pointer">
                    <div class="relative flex items-center">
                      <input
                        v-model="systemSettings.smsNotifications"
                        type="checkbox"
                        class="peer appearance-none w-5 h-5 rounded-md border-2 border-outline-variant checked:bg-primary checked:border-primary transition-all cursor-pointer"
                      />
                      <span class="material-symbols-outlined absolute text-white text-[16px] left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 opacity-0 peer-checked:opacity-100 transition-opacity pointer-events-none">check</span>
                    </div>
                    <div>
                      <span class="text-sm font-semibold text-on-surface">SMS Notifications</span>
                      <p class="text-xs text-on-surface-variant">Receive critical alerts via SMS</p>
                    </div>
                  </label>
                </div>
              </div>

              <div class="border-t border-outline-variant/10 pt-6">
                <label class="block text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-2">Auto Logout (minutes)</label>
                <input
                  v-model.number="systemSettings.autoLogout"
                  type="number"
                  min="5"
                  max="120"
                  class="w-full md:w-48 bg-surface-container-low border-none rounded-xl py-3 px-4 text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none"
                />
                <p class="text-xs text-on-surface-variant mt-2">Automatically logout after period of inactivity</p>
              </div>
            </div>
            <div class="p-8 bg-surface-container-low flex flex-wrap items-center justify-end gap-4">
              <button
                @click="handleSaveSystem"
                class="px-8 py-2.5 rounded-xl text-sm font-bold bg-gradient-to-r from-primary to-primary-dim text-white shadow-lg shadow-primary/30 hover:shadow-xl hover:-translate-y-0.5 transition-all"
              >
                Save Settings
              </button>
            </div>
          </div>
        </div>

        <!-- Right Sidebar -->
        <div class="col-span-12 lg:col-span-4 space-y-6">
          <!-- Account Info Card -->
          <div class="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-outline-variant/5">
            <div class="w-12 h-12 rounded-xl bg-tertiary/10 text-tertiary flex items-center justify-center mb-6">
              <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">badge</span>
            </div>
            <h3 class="text-lg font-bold text-on-surface mb-2 font-headline">Account Info</h3>
            <div class="space-y-4 mt-4">
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Role</label>
                <p class="text-sm text-on-surface font-semibold">{{ store.user?.role?.toUpperCase() || 'ADMIN' }}</p>
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">User ID</label>
                <p class="text-sm font-mono text-on-surface">{{ store.user?.id || '-' }}</p>
              </div>
              <div>
                <label class="block text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Created</label>
                <p class="text-sm text-on-surface">{{ store.user?.created_at ? new Date(store.user.created_at).toLocaleDateString() : '-' }}</p>
              </div>
            </div>
          </div>

          <!-- Security Info -->
          <div class="bg-primary/5 p-6 rounded-xl border border-primary/10 flex gap-4">
            <span class="material-symbols-outlined text-primary">security</span>
            <div>
              <h4 class="text-sm font-bold text-primary mb-1">Security</h4>
              <p class="text-xs text-on-surface-variant leading-relaxed">Your account is protected with JWT authentication. Change your password regularly for better security.</p>
            </div>
          </div>

          <!-- Version Info -->
          <div class="bg-surface-container-low rounded-xl p-6 text-center">
            <p class="text-xs text-on-surface-variant mb-1">Photobooth Admin Panel</p>
            <p class="text-sm font-bold text-on-surface font-headline">v1.0.0</p>
            <p class="text-[10px] text-outline mt-2">© 2024 Photobooth Kiosk</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
