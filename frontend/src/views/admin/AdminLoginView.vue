<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminApi } from '@/composables/useAdminApi'

const router = useRouter()
const { login, isLoading, error } = useAdminApi()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)

async function handleSubmit() {
  if (!username.value || !password.value) return

  const success = await login({
    username: username.value,
    password: password.value
  })

  if (success) {
    router.push('/admin/dashboard')
  }
}
</script>

<template>
  <div class="min-h-screen w-full bg-surface flex flex-col items-center justify-center p-6 relative overflow-hidden">
    <!-- Background Pattern -->
    <div class="fixed inset-0 pointer-events-none z-0">
      <div
        class="absolute inset-0"
        style="background-color: #faf4ff; background-image: radial-gradient(at 0% 0%, #e2d7ff 0px, transparent 50%), radial-gradient(at 100% 0%, #ff8eaf15 0px, transparent 50%), radial-gradient(at 100% 100%, #9795ff20 0px, transparent 50%), radial-gradient(at 0% 100%, #ede4ff 0px, transparent 50%);"
      />
    </div>

    <!-- Geometric Decorative Elements -->
    <div class="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      <div class="absolute top-20 left-[10%] w-64 h-64 border-[32px] border-surface-container-highest rounded-full opacity-30" />
      <div class="absolute bottom-20 right-[5%] w-96 h-96 border-[48px] border-primary-container/20 rounded-[4rem] rotate-12 opacity-20" />
      <div class="absolute top-1/2 right-[15%] w-12 h-12 bg-tertiary-container/30 rounded-xl rotate-45" />
      <div class="absolute bottom-1/3 left-[8%] w-8 h-8 bg-secondary-container/40 rounded-full" />
    </div>

    <!-- Login Container -->
    <main class="w-full max-w-[480px] flex flex-col gap-8 relative z-10">
      <!-- Identity Section -->
      <header class="flex flex-col items-center text-center space-y-4">
        <div class="w-16 h-16 bg-gradient-to-br from-primary to-primary-dim rounded-2xl flex items-center justify-center shadow-lg transform -rotate-3 hover:rotate-0 transition-transform duration-500">
          <span class="material-symbols-outlined text-white text-4xl" style="font-variation-settings: 'FILL' 1;">photo_camera</span>
        </div>
        <div class="space-y-1">
          <h1 class="text-3xl font-extrabold tracking-tight text-on-surface font-headline leading-tight">Admin Portal</h1>
          <p class="text-on-surface-variant text-sm font-medium tracking-wide">Photobooth Management System</p>
        </div>
      </header>

      <!-- Login Card -->
      <section class="bg-surface-container-lowest rounded-[2rem] p-10 shadow-[0_8px_32px_0_rgba(87,61,166,0.06)] border border-white/40 backdrop-blur-sm relative overflow-hidden">
        <!-- Asymmetric Accent -->
        <div class="absolute -top-12 -right-12 w-32 h-32 bg-tertiary/5 rounded-full blur-3xl" />

        <form @submit.prevent="handleSubmit" class="space-y-6 relative z-10">
          <!-- Error Message -->
          <div v-if="error" class="p-4 bg-error-container/20 rounded-xl text-error text-sm font-medium">
            {{ error }}
          </div>

          <!-- Username/Email -->
          <div class="space-y-2">
            <label class="text-xs font-bold uppercase tracking-widest text-on-surface-variant px-1" for="identifier">Username</label>
            <div class="relative group">
              <div class="absolute inset-y-0 left-4 flex items-center text-on-surface-variant group-focus-within:text-primary transition-colors">
                <span class="material-symbols-outlined text-xl">alternate_email</span>
              </div>
              <input
                id="identifier"
                v-model="username"
                type="text"
                placeholder="admin"
                class="w-full pl-12 pr-4 py-4 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/20 focus:bg-white transition-all outline-none text-on-surface placeholder:text-outline-variant font-medium"
                required
              />
            </div>
          </div>

          <!-- Password -->
          <div class="space-y-2">
            <label class="text-xs font-bold uppercase tracking-widest text-on-surface-variant px-1" for="password">Password</label>
            <div class="relative group">
              <div class="absolute inset-y-0 left-4 flex items-center text-on-surface-variant group-focus-within:text-primary transition-colors">
                <span class="material-symbols-outlined text-xl">lock</span>
              </div>
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                class="w-full pl-12 pr-12 py-4 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-primary/20 focus:bg-white transition-all outline-none text-on-surface placeholder:text-outline-variant font-medium"
                required
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-4 flex items-center text-on-surface-variant hover:text-primary transition-colors"
              >
                <span class="material-symbols-outlined text-xl">{{ showPassword ? 'visibility_off' : 'visibility' }}</span>
              </button>
            </div>
          </div>

          <!-- Utilities -->
          <div class="flex items-center justify-between px-1">
            <label class="flex items-center gap-3 cursor-pointer group">
              <div class="relative flex items-center">
                <input
                  v-model="rememberMe"
                  type="checkbox"
                  class="peer appearance-none w-5 h-5 rounded-md border-2 border-outline-variant checked:bg-primary checked:border-primary transition-all cursor-pointer"
                />
                <span class="material-symbols-outlined absolute text-white text-[16px] left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 opacity-0 peer-checked:opacity-100 transition-opacity pointer-events-none">check</span>
              </div>
              <span class="text-sm font-semibold text-on-surface-variant group-hover:text-on-surface transition-colors">Keep me signed in</span>
            </label>
            <a href="#" class="text-sm font-bold text-primary hover:text-primary-dim transition-colors">Forgot Password?</a>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="isLoading || !username || !password"
            class="w-full bg-gradient-to-r from-primary to-primary-dim hover:from-primary-dim hover:to-primary text-white py-4 rounded-xl font-extrabold text-lg flex items-center justify-center gap-3 shadow-lg shadow-primary/20 active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="material-symbols-outlined animate-spin">refresh</span>
            <template v-else>
              Masuk
              <span class="material-symbols-outlined">arrow_forward</span>
            </template>
          </button>
        </form>
      </section>

      <!-- Secondary Action (Pink Accent) -->
      <div class="text-center">
        <p class="text-sm text-on-surface-variant font-medium">
          Not an admin?
          <router-link to="/" class="text-tertiary font-bold hover:underline underline-offset-4 ml-1">Kiosk Access</router-link>
        </p>
      </div>

      <!-- Footer Links -->
      <footer class="mt-8">
        <nav class="flex flex-wrap items-center justify-center gap-x-8 gap-y-2">
          <a href="#" class="text-xs font-bold uppercase tracking-widest text-on-surface-variant hover:text-primary transition-colors">Privacy Policy</a>
          <a href="#" class="text-xs font-bold uppercase tracking-widest text-on-surface-variant hover:text-primary transition-colors">Terms of Service</a>
          <a href="#" class="text-xs font-bold uppercase tracking-widest text-on-surface-variant hover:text-primary transition-colors">Support</a>
        </nav>
        <p class="text-center text-[10px] mt-8 text-outline font-medium tracking-tight">
          © 2024 Photobooth Kiosk. All rights reserved. Professional Photobooth Management v1.0.0
        </p>
      </footer>
    </main>
  </div>
</template>
