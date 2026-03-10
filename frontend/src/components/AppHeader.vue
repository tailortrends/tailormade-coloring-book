<script setup lang="ts">
import { RouterLink, useRouter } from 'vue-router'
import { signOut } from 'firebase/auth'
import { auth } from '@/firebase'
import { useAuthStore } from '@/stores/auth'
import { useProfilesStore } from '@/stores/profiles'
import { useBookQuota } from '@/composables/useBookQuota'

const router = useRouter()
const authStore = useAuthStore()
const profilesStore = useProfilesStore()
const { booksRemaining, booksLimit, isAtLimit } = useBookQuota()

async function handleSignOut() {
  await signOut(auth)
  authStore.clearUser()
  router.push('/')
}
</script>

<template>
  <header class="sticky top-0 z-50 w-full bg-white/80 dark:bg-background-dark/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 py-3 lg:px-10 transition-all duration-300">
    <div class="mx-auto flex max-w-7xl items-center justify-between">
      <RouterLink to="/dashboard" class="flex items-center flex-shrink-0 group cursor-pointer border border-transparent">
        <img src="/logo.png" alt="TailorMade Coloring Book" class="h-10 w-auto max-w-[180px] sm:max-w-[160px] object-contain" />
      </RouterLink>

      <nav class="hidden md:flex items-center gap-8">
        <RouterLink to="/community" class="text-slate-600 dark:text-slate-300 text-sm font-semibold hover:text-primary transition-colors">Gallery</RouterLink>
        <a href="/#how-it-works" class="text-slate-600 dark:text-slate-300 text-sm font-semibold hover:text-primary transition-colors">How it works</a>
        <RouterLink to="/pricing" class="text-slate-600 dark:text-slate-300 text-sm font-semibold hover:text-primary transition-colors">Pricing</RouterLink>
      </nav>

      <!-- Authenticated: show quota pill + user info + sign out -->
      <div v-if="authStore.isAuthenticated" class="flex items-center gap-4">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold border cursor-pointer transition-colors select-none"
          :class="isAtLimit ? 'bg-red-50 border-red-200 text-red-700 dark:bg-red-900/30' : 'bg-sky-50 border-sky-200 text-sky-700 dark:bg-sky-900/30'"
          @click="router.push('/pricing')"
        >
          📚 
          <span v-if="!isAtLimit" class="hidden sm:inline">
            {{ booksRemaining }} 
            {{ booksRemaining === 1 ? 'book' : 'books' }} left
          </span>
          <span v-else class="hidden sm:inline">Upgrade to create more</span>
        </div>
        <!-- Active child profile pill -->
        <RouterLink
          v-if="profilesStore.activeProfile"
          to="/profiles"
          class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-primary/50 transition-colors"
        >
          <div
            class="size-6 rounded-full flex items-center justify-center text-white text-[10px] font-bold"
            :style="{ backgroundColor: profilesStore.activeProfile.avatar_color }"
          >
            {{ profilesStore.activeProfile.name.charAt(0).toUpperCase() }}
          </div>
          <span class="text-xs font-semibold text-slate-700 dark:text-slate-200 max-w-[80px] truncate">{{ profilesStore.activeProfile.name }}</span>
        </RouterLink>
        <RouterLink to="/dashboard" class="hidden sm:flex items-center gap-2 text-slate-700 dark:text-slate-200 hover:text-primary transition-colors">
          <div class="size-8 rounded-full bg-primary/10 flex items-center justify-center overflow-hidden border border-primary/20">
            <img v-if="authStore.photoURL" :src="authStore.photoURL" alt="Avatar" class="w-full h-full object-cover" />
            <span v-else class="text-primary font-bold text-sm">{{ authStore.displayName.charAt(0).toUpperCase() }}</span>
          </div>
          <span class="text-sm font-semibold">{{ authStore.displayName }}</span>
        </RouterLink>
        <button
          @click="handleSignOut"
          class="flex items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors px-4 py-2 text-slate-700 dark:text-slate-200 text-sm font-semibold"
        >
          Sign Out
        </button>
      </div>

      <!-- Not authenticated: show login + signup -->
      <div v-else class="flex items-center gap-4">
        <RouterLink to="/login" class="hidden sm:block text-slate-900 dark:text-white text-sm font-semibold hover:text-primary transition-colors">
          Log in
        </RouterLink>
        <RouterLink to="/signup" class="flex items-center justify-center rounded-full bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-200 transition-all px-6 py-2.5 text-white dark:text-slate-900 text-sm font-bold shadow-lg shadow-slate-900/20">
          <span class="truncate">Sign Up Free</span>
        </RouterLink>
      </div>
    </div>
  </header>
</template>
