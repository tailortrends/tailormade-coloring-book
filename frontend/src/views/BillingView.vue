<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { useAuthStore } from '@/stores/auth'
import { createPortalSession } from '@/api/stripe'
import { api } from '@/api/client'
import { RouterLink } from 'vue-router'

const authStore = useAuthStore()
const loading = ref(false)
const portalLoading = ref(false)
const error = ref('')

const tier = computed(() => authStore.tier)
const subscriptionActive = computed(() => authStore.subscriptionActive)
const booksThisMonth = computed(() => authStore.booksGeneratedThisMonth)
const booksTotal = computed(() => authStore.booksGeneratedTotal)
const credits = computed(() => authStore.creditsRemaining)

const planName = computed(() => {
  const names: Record<string, string> = {
    free: 'Free Starter',
    single: 'Single Masterpiece',
    family: 'Family Plan',
    teacher: 'Teacher Edition',
  }
  return names[tier.value] || 'Free Starter'
})

const monthlyLimit = computed(() => {
  if (tier.value === 'teacher') return 25
  if (tier.value === 'family') return 12
  return null
})

const statusLabel = computed(() => {
  if (!subscriptionActive.value) return 'Inactive'
  return 'Active'
})

const statusColor = computed(() => {
  return subscriptionActive.value
    ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
    : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400'
})

const statusDotColor = computed(() => {
  return subscriptionActive.value ? 'bg-green-500' : 'bg-slate-400'
})

const planPrice = computed(() => {
  if (tier.value === 'teacher') return '$39.99/mo'
  if (tier.value === 'family') return '$19.99/mo'
  return 'Free'
})

// Refresh subscription data on mount
onMounted(async () => {
  loading.value = true
  try {
    const data = await api.get<Record<string, unknown>>('/api/v1/auth/me')
    authStore.syncFromMe(data)
  } catch {
    // silent — we already have cached data
  } finally {
    loading.value = false
  }
})

async function openPortal() {
  error.value = ''
  portalLoading.value = true
  try {
    await createPortalSession()
  } catch (e: any) {
    error.value = e?.body?.detail || 'Failed to open subscription portal. Please try again.'
    portalLoading.value = false
  }
}
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-1 w-full max-w-[1200px] mx-auto px-6 py-10 md:px-10 lg:py-12">
      <!-- Header -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 mb-10">
        <div class="flex flex-col gap-3 max-w-2xl">
          <h1 class="text-slate-900 dark:text-white text-3xl md:text-4xl font-extrabold tracking-tight">Billing &amp; Subscription</h1>
          <p class="text-slate-500 dark:text-slate-400 text-lg">Manage your plan and track your usage.</p>
        </div>
      </div>

      <!-- Error Banner -->
      <div v-if="error" class="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl px-6 py-4 text-red-700 dark:text-red-400 text-sm font-medium flex items-center gap-3">
        <span class="material-symbols-outlined text-red-500">error</span>
        {{ error }}
        <button @click="error = ''" class="ml-auto text-red-400 hover:text-red-600"><span class="material-symbols-outlined text-lg">close</span></button>
      </div>

      <!-- Cards Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
        <!-- Current Plan Card -->
        <div class="lg:col-span-2 bg-white dark:bg-slate-900 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col md:flex-row justify-between gap-8 relative overflow-hidden">
          <div class="absolute -right-10 -top-10 w-40 h-40 bg-primary/5 rounded-full blur-3xl"></div>
          <div class="flex flex-col justify-between gap-6 z-10">
            <div>
              <div class="flex items-center gap-3 mb-2">
                <span class="material-symbols-outlined text-primary">verified</span>
                <p class="text-slate-500 dark:text-slate-400 text-sm font-bold uppercase tracking-wider">Current Plan</p>
              </div>
              <h3 class="text-3xl font-bold mb-1">{{ planName }}</h3>
              <p class="text-slate-500 dark:text-slate-400 text-lg">{{ planPrice }}</p>
            </div>
          </div>
          <div class="flex flex-col justify-end items-start md:items-end gap-4 z-10">
            <span :class="statusColor" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide">
              <span :class="statusDotColor" class="size-2 rounded-full"></span>
              {{ statusLabel }}
            </span>
            <div class="flex gap-3">
              <RouterLink to="/pricing" class="h-10 px-5 rounded-full border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-bold text-sm hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors flex items-center">
                Change Plan
              </RouterLink>
              <button
                v-if="subscriptionActive && (tier === 'family' || tier === 'teacher')"
                @click="openPortal"
                :disabled="portalLoading"
                class="h-10 px-5 rounded-full bg-primary hover:bg-primary-dark text-white font-bold text-sm transition-colors shadow-lg shadow-primary/20 flex items-center gap-2 disabled:opacity-50"
              >
                <span v-if="portalLoading" class="material-symbols-outlined animate-spin text-lg">progress_activity</span>
                Manage Subscription
              </button>
            </div>
          </div>
        </div>

        <!-- Usage Card -->
        <div class="bg-white dark:bg-slate-900 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col justify-between gap-6">
          <div>
            <div class="flex items-center gap-3 mb-6">
              <div class="size-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <span class="material-symbols-outlined">auto_stories</span>
              </div>
              <p class="text-lg font-bold">Usage This Month</p>
            </div>

            <!-- Monthly usage for subscribers -->
            <div v-if="monthlyLimit" class="mb-4">
              <div class="flex justify-between text-sm mb-2">
                <span class="text-slate-500 dark:text-slate-400">Books generated</span>
                <span class="font-bold">{{ booksThisMonth }} / {{ monthlyLimit }}</span>
              </div>
              <div class="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                <div
                  class="h-full bg-primary rounded-full transition-all duration-500"
                  :style="{ width: `${Math.min(100, (booksThisMonth / monthlyLimit) * 100)}%` }"
                ></div>
              </div>
            </div>

            <!-- Free tier usage -->
            <div v-else class="mb-4">
              <div class="flex justify-between text-sm mb-2">
                <span class="text-slate-500 dark:text-slate-400">Books generated (lifetime)</span>
                <span class="font-bold">{{ booksTotal }} / 1</span>
              </div>
              <div class="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                <div
                  class="h-full bg-primary rounded-full transition-all duration-500"
                  :style="{ width: `${Math.min(100, booksTotal * 100)}%` }"
                ></div>
              </div>
            </div>

            <!-- One-time credits -->
            <div v-if="credits > 0" class="flex justify-between text-sm mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
              <span class="text-slate-500 dark:text-slate-400">One-time credits remaining</span>
              <span class="font-bold text-green-600 dark:text-green-400">{{ credits }}</span>
            </div>
          </div>

          <RouterLink
            v-if="!subscriptionActive || tier === 'free'"
            to="/pricing"
            class="w-full h-10 flex items-center justify-center gap-2 rounded-full bg-primary text-white text-sm font-bold hover:bg-blue-600 transition-colors"
          >
            <span class="material-symbols-outlined text-lg">upgrade</span>
            Upgrade Plan
          </RouterLink>
        </div>
      </div>
    </main>

    <AppFooter />
  </div>
</template>
