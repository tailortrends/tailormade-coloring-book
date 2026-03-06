<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { signInWithPopup } from 'firebase/auth'
import { auth, googleProvider } from '@/firebase'

const router = useRouter()
const authError = ref<string | null>(null)

async function signInWithGoogle() {
  authError.value = null
  try {
    await signInWithPopup(auth, googleProvider)
    router.push('/dashboard')
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Sign-in failed'
    authError.value = message
  }
}
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display min-h-screen flex flex-col overflow-x-hidden">
    <!-- Header -->
    <header class="flex items-center justify-between whitespace-nowrap bg-white dark:bg-background-dark border-b border-slate-100 dark:border-slate-800 px-6 py-4 md:px-10 lg:px-20 relative z-20">
      <RouterLink to="/" class="flex items-center gap-3 text-slate-900 dark:text-white">
        <div class="size-8 text-primary">
          <span class="material-symbols-outlined text-[32px]">palette</span>
        </div>
        <h2 class="text-xl font-bold leading-tight tracking-tight">ColorMagic AI</h2>
      </RouterLink>

      <div class="hidden md:flex flex-1 justify-end gap-8">
        <div class="flex items-center gap-9">
          <RouterLink to="/" class="text-slate-600 dark:text-slate-300 hover:text-primary transition-colors text-sm font-medium">Home</RouterLink>
          <RouterLink to="/community" class="text-slate-600 dark:text-slate-300 hover:text-primary transition-colors text-sm font-medium">Gallery</RouterLink>
          <RouterLink to="/pricing" class="text-slate-600 dark:text-slate-300 hover:text-primary transition-colors text-sm font-medium">Pricing</RouterLink>
        </div>
        <RouterLink to="/signup" class="flex min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-10 px-5 bg-primary hover:bg-primary-hover transition-colors text-white text-sm font-bold tracking-wide shadow-sm hover:shadow-md">
          <span>Sign Up</span>
        </RouterLink>
      </div>
      <div class="md:hidden">
        <span class="material-symbols-outlined text-slate-900 dark:text-white cursor-pointer">menu</span>
      </div>
    </header>

    <!-- Main Layout -->
    <main class="flex-grow flex items-center justify-center p-4 py-12 relative">
      <!-- Decorative background blurs -->
      <div class="absolute top-20 left-10 w-32 h-32 rounded-full bg-yellow-200 opacity-20 blur-3xl pointer-events-none"></div>
      <div class="absolute bottom-20 right-10 w-64 h-64 rounded-full bg-purple-200 opacity-20 blur-3xl pointer-events-none"></div>
      <div class="absolute top-1/2 left-1/4 w-40 h-40 rounded-full bg-primary opacity-10 blur-3xl pointer-events-none"></div>

      <!-- Card Container: Two-column split -->
      <div class="bg-white dark:bg-slate-800 rounded-lg shadow-xl w-full max-w-[1000px] overflow-hidden flex flex-col md:flex-row min-h-[600px] border border-slate-100 dark:border-slate-700 z-10">
        <!-- Left Side: Image/Banner -->
        <div class="md:w-5/12 relative bg-primary/5 hidden md:flex flex-col">
          <div class="absolute inset-0 bg-cover bg-center" style="background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuAyBitzfFDQ7RA12l9Ba08CKt0lZO4L0uVkkspOLwx3sft46Wvt3bacPL7lMDvje7rrNS58Uw3xk1u3sFZKwaHNJRGPEkrdTskAVg2ZMg4TmvhF3BVPTU_1Cr9ESFlvy6s02hZSgtFOj30UFVdaZIDGlPh3cmAA-e6XMKlwhIclLa1dHpSBGZ2f3ZWCR8ysf9VQJE-zYWtP6URE7_jQdjdNOmDrxNElr7qRwn6-azZseZ5_i5X05VlsPfubSHq41tbHSHfHtKRuKZD8');"></div>
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
          <div class="relative z-10 mt-auto p-10 text-white">
            <div class="mb-4 text-primary bg-white/90 backdrop-blur rounded-full w-12 h-12 flex items-center justify-center shadow-lg">
              <span class="material-symbols-outlined">auto_awesome</span>
            </div>
            <h3 class="text-3xl font-bold mb-2">Unleash Creativity</h3>
            <p class="text-white/90 font-medium leading-relaxed">Create personalized coloring books for your kids in seconds with the power of AI.</p>
          </div>
        </div>

        <!-- Right Side: Form -->
        <div class="md:w-7/12 p-8 md:p-12 flex flex-col justify-center bg-white dark:bg-slate-800">
          <div class="max-w-[420px] mx-auto w-full">
            <div class="mb-8">
              <h1 class="text-3xl font-bold text-slate-900 dark:text-white mb-2 tracking-tight">Welcome Back!</h1>
              <p class="text-slate-500 dark:text-slate-400 font-medium">Sign in to create more magical coloring books.</p>
            </div>

            <form class="flex flex-col gap-5" @submit.prevent="$router.push('/dashboard')">
              <!-- Google Sign In Button -->
              <button type="button" @click="signInWithGoogle" class="flex w-full items-center justify-center gap-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 p-3.5 text-slate-700 dark:text-white transition-all hover:bg-slate-50 dark:hover:bg-slate-600 hover:border-slate-300 focus:ring-4 focus:ring-slate-100">
                <svg class="w-5 h-5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.84z" fill="#FBBC05"></path>
                  <path d="M12 4.63c1.69 0 3.26.58 4.54 1.8l3.49-3.49C17.73.95 15.18 0 12 0 7.7 0 3.99 2.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path>
                </svg>
                <span class="text-sm font-bold">Sign in with Google</span>
              </button>

              <p v-if="authError" class="text-red-500 text-sm text-center font-medium">{{ authError }}</p>

              <div class="relative flex items-center gap-2 my-2">
                <span class="h-px w-full bg-slate-200 dark:bg-slate-600"></span>
                <span class="text-xs font-medium text-slate-400 uppercase">Or</span>
                <span class="h-px w-full bg-slate-200 dark:bg-slate-600"></span>
              </div>

              <!-- Email Input -->
              <label class="flex flex-col gap-1.5">
                <span class="text-slate-900 dark:text-slate-200 text-sm font-semibold">Email Address</span>
                <input type="email" placeholder="parent@example.com" class="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700/50 px-4 py-3.5 text-slate-900 dark:text-white outline-none transition-all placeholder:text-slate-400 focus:border-primary focus:bg-white dark:focus:bg-slate-700 focus:ring-4 focus:ring-primary/10" />
              </label>

              <!-- Password Input -->
              <label class="flex flex-col gap-1.5">
                <span class="text-slate-900 dark:text-slate-200 text-sm font-semibold">Password</span>
                <div class="relative">
                  <input type="password" placeholder="Enter your password" class="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700/50 px-4 py-3.5 text-slate-900 dark:text-white outline-none transition-all placeholder:text-slate-400 focus:border-primary focus:bg-white dark:focus:bg-slate-700 focus:ring-4 focus:ring-primary/10 pr-12" />
                  <button type="button" class="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300">
                    <span class="material-symbols-outlined text-[20px]">visibility_off</span>
                  </button>
                </div>
              </label>

              <!-- Remember Me & Forgot Password -->
              <div class="flex items-center justify-between">
                <label class="flex items-center gap-2.5 cursor-pointer group">
                  <div class="relative flex items-center">
                    <input type="checkbox" class="peer h-5 w-5 cursor-pointer appearance-none rounded border border-slate-300 dark:border-slate-500 bg-white dark:bg-slate-700 transition-all checked:border-primary checked:bg-primary hover:border-primary focus:ring-0 focus:ring-offset-0" />
                    <span class="material-symbols-outlined pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-[16px] text-white opacity-0 peer-checked:opacity-100">check</span>
                  </div>
                  <span class="text-sm font-medium text-slate-600 dark:text-slate-400 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">Keep me signed in</span>
                </label>
                <a href="#" class="text-sm font-semibold text-primary hover:text-primary-hover hover:underline">Forgot Password?</a>
              </div>

              <!-- Submit Button -->
              <button type="submit" class="mt-2 w-full rounded-full bg-primary py-3.5 text-sm font-bold text-white shadow-lg shadow-primary/30 transition-all hover:bg-primary-hover hover:shadow-primary/40 active:scale-[0.98]">
                Sign In
              </button>
            </form>

            <p class="mt-8 text-center text-sm font-medium text-slate-500 dark:text-slate-400">
              Don't have an account?
              <RouterLink to="/signup" class="font-bold text-primary hover:text-primary-hover hover:underline">Sign up for free</RouterLink>
            </p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
