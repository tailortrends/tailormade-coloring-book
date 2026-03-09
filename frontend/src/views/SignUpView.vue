<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { signInWithPopup } from 'firebase/auth'
import { auth, googleProvider } from '@/firebase'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const authError = ref<string | null>(null)

// Reactively navigate when authentication state syncs
watch(() => authStore.isAuthenticated, (isAuth) => {
  if (isAuth) {
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.push(redirect)
  }
}, { immediate: true })

async function signUpWithGoogle() {
  authError.value = null
  try {
    await signInWithPopup(auth, googleProvider)
    // The watcher above handles the actual redirection once authStore updates
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Sign-up failed'
    authError.value = message
  }
}

function handleEmailSignup() {
  authError.value = 'Email signup is not yet configured. Please sign up with Google.'
}
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display min-h-screen flex flex-col overflow-x-hidden">
    <!-- Header -->
    <header class="w-full px-6 py-4 md:px-10 flex items-center justify-between z-10 relative bg-white/80 backdrop-blur-md dark:bg-background-dark/80 sticky top-0 border-b border-slate-100 dark:border-slate-800">
      <RouterLink to="/" class="flex items-center gap-2 group">
        <img src="/logo3.png" alt="TailorMade Coloring Book" class="h-9 w-auto dark:hidden" />
        <span class="hidden dark:inline text-xl font-bold tracking-tight" style="color: #6B9EC7;">TailorMade</span>
      </RouterLink>

      <div class="hidden md:flex flex-1 justify-end gap-8 items-center">
        <nav class="flex items-center gap-8">
          <RouterLink to="/" class="text-slate-600 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors">Home</RouterLink>
          <RouterLink to="/gallery" class="text-slate-600 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors">Gallery</RouterLink>
          <RouterLink to="/pricing" class="text-slate-600 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors">Pricing</RouterLink>
          <RouterLink to="/login" class="text-slate-600 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors">Log In</RouterLink>
        </nav>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-grow flex items-center justify-center relative p-4 md:p-8 overflow-hidden">
      <!-- Abstract Background Gradients -->
      <div class="absolute inset-0 overflow-hidden -z-10">
        <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-purple-100 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900"></div>
        <div class="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-primary/10 rounded-full blur-3xl"></div>
        <div class="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-blue-400/10 rounded-full blur-3xl"></div>
      </div>

      <!-- Floating Decorative Icons -->
      <div class="absolute top-20 left-[10%] text-primary/20 dark:text-primary/10 animate-float hidden lg:block">
        <span class="material-symbols-outlined text-6xl transform -rotate-12">edit</span>
      </div>
      <div class="absolute bottom-32 right-[15%] text-blue-400/20 dark:text-blue-400/10 animate-float hidden lg:block" style="animation-delay: 1s">
        <span class="material-symbols-outlined text-7xl transform rotate-12">star</span>
      </div>
      <div class="absolute top-40 right-[8%] text-yellow-400/20 dark:text-yellow-400/10 animate-float hidden lg:block" style="animation-delay: 2s">
        <span class="material-symbols-outlined text-5xl transform rotate-45">brush</span>
      </div>
      <div class="absolute bottom-20 left-[5%] text-pink-400/20 dark:text-pink-400/10 animate-float hidden lg:block" style="animation-delay: 1.5s">
        <span class="material-symbols-outlined text-6xl transform -rotate-6">palette</span>
      </div>

      <!-- Card Container -->
      <div class="w-full max-w-[520px] bg-white dark:bg-slate-800/90 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-100 dark:border-slate-700 overflow-hidden relative z-0">
        <div class="h-2 w-full bg-gradient-to-r from-primary via-blue-400 to-accent-purple"></div>
        
        <div class="p-8 md:p-10">
          <div class="text-center mb-8">
            <img src="/logo3.png" alt="TailorMade Coloring Book" class="h-14 w-auto mx-auto mb-4 dark:hidden" />
            <h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white tracking-tight mb-3">Join TailorMade</h1>
            <p class="text-slate-500 dark:text-slate-400 text-lg">Create personalized coloring books for your kids in seconds!</p>
          </div>

          <button @click="signUpWithGoogle" class="w-full flex items-center justify-center gap-3 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-600 text-slate-700 dark:text-white font-bold h-14 px-6 rounded-lg transition-all mb-6 group">
            <svg class="w-6 h-6" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.84z" fill="#FBBC05"></path>
              <path d="M12 4.63c1.69 0 3.26.58 4.54 1.8l3.49-3.49C17.73.95 15.18 0 12 0 7.7 0 3.99 2.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path>
            </svg>
            <span>Sign Up with Google</span>
          </button>

          <p v-if="authError" class="text-red-500 text-sm text-center font-medium mb-4">{{ authError }}</p>

          <div class="relative flex items-center gap-4 py-2 mb-6">
            <div class="h-px bg-slate-200 dark:bg-slate-600 flex-1"></div>
            <span class="text-slate-400 dark:text-slate-500 text-sm font-medium">OR</span>
            <div class="h-px bg-slate-200 dark:bg-slate-600 flex-1"></div>
          </div>

          <form class="space-y-5" @submit.prevent="handleEmailSignup">
            <div class="space-y-1.5">
              <label for="name" class="block text-slate-700 dark:text-slate-200 text-sm font-semibold ml-1">Parent's Name</label>
              <div class="relative">
                <input id="name" type="text" placeholder="e.g. Sarah Jenkins" class="w-full bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg h-12 px-4 pl-11 text-slate-900 dark:text-white placeholder:text-slate-400 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none" />
                <div class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400">
                  <span class="material-symbols-outlined text-[20px]">person</span>
                </div>
              </div>
            </div>

            <div class="space-y-1.5">
              <label for="email" class="block text-slate-700 dark:text-slate-200 text-sm font-semibold ml-1">Email Address</label>
              <div class="relative">
                <input id="email" type="email" placeholder="sarah@example.com" class="w-full bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg h-12 px-4 pl-11 text-slate-900 dark:text-white placeholder:text-slate-400 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none" />
                <div class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400">
                  <span class="material-symbols-outlined text-[20px]">mail</span>
                </div>
              </div>
            </div>

            <div class="space-y-1.5">
              <label for="password" class="block text-slate-700 dark:text-slate-200 text-sm font-semibold ml-1">Password</label>
              <div class="relative">
                <input id="password" type="password" placeholder="Create a password" class="w-full bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg h-12 px-4 pl-11 text-slate-900 dark:text-white placeholder:text-slate-400 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none" />
                <div class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400">
                  <span class="material-symbols-outlined text-[20px]">lock</span>
                </div>
              </div>
            </div>

            <div class="pt-2">
              <button type="submit" class="w-full bg-primary hover:bg-primary-dark text-white text-lg font-bold h-14 rounded-full shadow-xl shadow-primary/25 hover:shadow-primary/40 transition-all transform hover:-translate-y-0.5 flex items-center justify-center gap-2">
                <span>Create My Account</span>
                <span class="material-symbols-outlined">arrow_forward</span>
              </button>
            </div>
          </form>

          <p class="text-center mt-6 text-sm text-slate-500 dark:text-slate-400">
            Already have an account? 
            <RouterLink to="/login" class="text-primary hover:text-primary-dark font-bold hover:underline">Log in</RouterLink>
          </p>
        </div>
      </div>
    </main>
  </div>
</template>
