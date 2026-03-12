<script setup lang="ts">
import { ref, computed } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { createCheckoutSession } from '@/api/stripe'

const authStore = useAuthStore()
const loadingPlan = ref<string | null>(null)
const error = ref('')

const FAMILY_PRICE_ID = (import.meta.env.VITE_STRIPE_FAMILY_PRICE_ID as string) || ''
const TEACHER_PRICE_ID = (import.meta.env.VITE_STRIPE_TEACHER_PRICE_ID as string) || ''
const SINGLE_PRICE_ID = (import.meta.env.VITE_STRIPE_SINGLE_PRICE_ID as string) || ''

const currentTier = computed(() => authStore.tier)
const isLoggedIn = computed(() => authStore.isAuthenticated)
const isActive = computed(() => authStore.subscriptionActive)

async function subscribe(plan: string, priceId: string) {
  if (!isLoggedIn.value) {
    window.location.href = '/signup'
    return
  }
  error.value = ''
  loadingPlan.value = plan
  try {
    const base = window.location.origin
    await createCheckoutSession(priceId, `${base}/billing?success=1`, `${base}/pricing?canceled=1`)
  } catch (e: any) {
    error.value = e?.body?.detail || 'Something went wrong. Please try again.'
    loadingPlan.value = null
  }
}
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-white min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-grow flex flex-col items-center justify-start py-12 px-4 md:px-10">
      <!-- Header Section -->
      <div class="max-w-[800px] text-center mb-12">
        <h1 class="text-slate-900 dark:text-white tracking-tight text-4xl md:text-5xl font-extrabold leading-tight mb-4">
          Choose the Perfect Plan for Your <span class="text-primary">Little Artist</span>
        </h1>
        <p class="text-slate-500 dark:text-slate-400 text-lg font-normal leading-relaxed max-w-2xl mx-auto">
          Unlock creativity with AI-generated coloring books tailored to your child's imagination. Start for free, or upgrade for unlimited magic and instant downloads.
        </p>
      </div>

      <!-- Error Banner -->
      <div v-if="error" class="mb-6 w-full max-w-[1280px] bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl px-6 py-4 text-red-700 dark:text-red-400 text-sm font-medium flex items-center gap-3">
        <span class="material-symbols-outlined text-red-500">error</span>
        {{ error }}
        <button @click="error = ''" class="ml-auto text-red-400 hover:text-red-600"><span class="material-symbols-outlined text-lg">close</span></button>
      </div>

      <!-- Pricing Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full max-w-[1280px]">

        <!-- Card 1 — Free Starter -->
        <div class="flex flex-col gap-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-sm hover:shadow-md transition-shadow"
             :class="{ 'ring-2 ring-primary': isLoggedIn && currentTier === 'free' && !isActive }">
          <div class="flex flex-col gap-2">
            <h3 class="text-slate-900 dark:text-white text-xl font-bold leading-tight">Free Starter</h3>
            <p class="text-slate-500 dark:text-slate-400 text-sm">Try the magic, no commitment.</p>
            <div class="flex items-baseline gap-1 mt-2">
              <span class="text-slate-900 dark:text-white text-5xl font-black tracking-tight">$0</span>
            </div>
            <p class="text-slate-400 dark:text-slate-500 text-xs font-medium">One free book, yours to keep</p>
          </div>
          <RouterLink v-if="!isLoggedIn" to="/signup" class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-900 dark:text-white text-sm font-bold transition-colors">
            Get Started Free
          </RouterLink>
          <button v-else disabled class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500 text-sm font-bold cursor-not-allowed">
            {{ currentTier === 'free' && !isActive ? 'Current Plan' : 'Free Tier' }}
          </button>
          <div class="w-full h-px bg-slate-200 dark:bg-slate-800 my-2"></div>
          <div class="flex flex-col gap-4">
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-green-500 text-[20px]">check_circle</span>
              1 free book (no expiry)
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-green-500 text-[20px]">check_circle</span>
              6 pages per book
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-green-500 text-[20px]">check_circle</span>
              Printable PDF
            </div>
            <div class="text-sm font-medium text-slate-400 dark:text-slate-600 flex gap-3 items-center">
              <span class="material-symbols-outlined text-[20px]">cancel</span>
              Includes watermark
            </div>
            <div class="text-sm font-medium text-slate-400 dark:text-slate-600 flex gap-3 items-center">
              <span class="material-symbols-outlined text-[20px]">cancel</span>
              6 page limit
            </div>
          </div>
        </div>

        <!-- Card 2 — Single Masterpiece -->
        <div class="flex flex-col gap-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex flex-col gap-2">
            <h3 class="text-slate-900 dark:text-white text-xl font-bold leading-tight">Single Masterpiece</h3>
            <p class="text-slate-500 dark:text-slate-400 text-sm">One perfect book, yours forever.</p>
            <div class="flex items-baseline gap-1 mt-2">
              <span class="text-slate-900 dark:text-white text-5xl font-black tracking-tight">$7.99</span>
            </div>
            <span class="inline-flex items-center self-start bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-bold px-2.5 py-1 rounded-full">One-time &middot; No subscription</span>
          </div>
          <button
            @click="subscribe('single', SINGLE_PRICE_ID)"
            :disabled="loadingPlan === 'single'"
            class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-200 text-white dark:text-slate-900 text-sm font-bold transition-colors disabled:opacity-50"
          >
            <span v-if="loadingPlan === 'single'" class="material-symbols-outlined animate-spin text-lg mr-2">progress_activity</span>
            Buy One Book
          </button>
          <div class="w-full h-px bg-slate-200 dark:bg-slate-800 my-2"></div>
          <div class="flex flex-col gap-4">
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-green-500 text-[20px]">check_circle</span>
              1 high-resolution book
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-green-500 text-[20px]">check_circle</span>
              Up to 15 pages (your choice)
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-green-500 text-[20px]">check_circle</span>
              No watermark
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-green-500 text-[20px]">check_circle</span>
              HD PDF — print unlimited times
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-green-500 text-[20px]">check_circle</span>
              Lifetime access to your PDF
            </div>
          </div>
        </div>

        <!-- Card 3 — Family Plan (Most Popular) -->
        <div class="relative flex flex-col gap-6 rounded-2xl border-2 bg-white dark:bg-slate-900 p-8 shadow-xl lg:scale-105 z-10"
             :class="isLoggedIn && currentTier === 'family' && isActive ? 'border-green-500 shadow-green-500/10' : 'border-primary shadow-primary/10'">
          <div class="absolute -top-4 left-1/2 -translate-x-1/2 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-lg"
               :class="isLoggedIn && currentTier === 'family' && isActive ? 'bg-green-500' : 'bg-primary'">
            {{ isLoggedIn && currentTier === 'family' && isActive ? 'Your Plan' : 'Most Popular' }}
          </div>
          <div class="flex flex-col gap-2">
            <h3 class="text-primary text-xl font-bold leading-tight">Family Plan</h3>
            <p class="text-slate-500 dark:text-slate-400 text-sm">Perfect for siblings and busy families.</p>
            <div class="flex items-baseline gap-1 mt-2">
              <span class="text-slate-900 dark:text-white text-5xl font-black tracking-tight">$19.99</span>
              <span class="text-slate-500 dark:text-slate-400 text-base font-bold">/mo</span>
            </div>
          </div>
          <button
            v-if="!(isLoggedIn && currentTier === 'family' && isActive)"
            @click="subscribe('family', FAMILY_PRICE_ID)"
            :disabled="loadingPlan === 'family'"
            class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-primary hover:bg-blue-600 text-white text-sm font-bold transition-colors shadow-lg shadow-primary/30 disabled:opacity-50"
          >
            <span v-if="loadingPlan === 'family'" class="material-symbols-outlined animate-spin text-lg mr-2">progress_activity</span>
            Start Family Plan
          </button>
          <RouterLink v-else to="/billing" class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-green-500 text-white text-sm font-bold transition-colors">
            Manage Subscription
          </RouterLink>
          <div class="w-full h-px bg-slate-200 dark:bg-slate-800 my-2"></div>
          <div class="flex flex-col gap-4">
            <div class="text-sm font-medium text-slate-900 dark:text-white flex gap-3 items-center">
              <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
              <strong>12 books</strong>&nbsp;per month
            </div>
            <div class="text-sm font-medium text-slate-900 dark:text-white flex gap-3 items-center">
              <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
              Up to 15 pages per book (your choice)
            </div>
            <div class="text-sm font-medium text-slate-900 dark:text-white flex gap-3 items-center">
              <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
              No watermark
            </div>
            <div class="text-sm font-medium text-slate-900 dark:text-white flex gap-3 items-center">
              <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
              HD PDF downloads
            </div>
            <div class="text-sm font-medium text-slate-900 dark:text-white flex gap-3 items-center">
              <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
              <strong>Priority</strong>&nbsp;generation speed
            </div>
            <div class="text-sm font-medium text-slate-900 dark:text-white flex gap-3 items-center">
              <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
              All themes unlocked
            </div>
            <div class="text-sm font-medium text-slate-900 dark:text-white flex gap-3 items-center">
              <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
              Cancel anytime
            </div>
          </div>
        </div>

        <!-- Card 4 — Teacher Edition (Amber accent) -->
        <div class="relative flex flex-col gap-6 rounded-2xl border-2 bg-white dark:bg-slate-900 p-8 shadow-sm hover:shadow-md transition-shadow"
             :class="isLoggedIn && currentTier === 'teacher' && isActive ? 'border-green-500' : 'border-amber-500'">
          <div class="absolute -top-4 left-1/2 -translate-x-1/2 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-lg"
               :class="isLoggedIn && currentTier === 'teacher' && isActive ? 'bg-green-500' : 'bg-amber-500'">
            {{ isLoggedIn && currentTier === 'teacher' && isActive ? 'Your Plan' : 'Classroom License Included' }}
          </div>
          <div class="flex flex-col gap-2">
            <h3 class="text-amber-500 text-xl font-bold leading-tight">Teacher Edition</h3>
            <p class="text-slate-500 dark:text-slate-400 text-sm">One theme. Thirty students. Zero prep.</p>
            <div class="flex items-baseline gap-1 mt-2">
              <span class="text-slate-900 dark:text-white text-5xl font-black tracking-tight">$39.99</span>
              <span class="text-slate-500 dark:text-slate-400 text-base font-bold">/mo</span>
            </div>
          </div>
          <button
            v-if="!(isLoggedIn && currentTier === 'teacher' && isActive)"
            @click="subscribe('teacher', TEACHER_PRICE_ID)"
            :disabled="loadingPlan === 'teacher'"
            class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-amber-500 hover:bg-amber-600 text-white text-sm font-bold transition-colors shadow-lg shadow-amber-500/30 disabled:opacity-50"
          >
            <span v-if="loadingPlan === 'teacher'" class="material-symbols-outlined animate-spin text-lg mr-2">progress_activity</span>
            Get Teacher Plan
          </button>
          <RouterLink v-else to="/billing" class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-green-500 text-white text-sm font-bold transition-colors">
            Manage Subscription
          </RouterLink>
          <div class="w-full h-px bg-slate-200 dark:bg-slate-800 my-2"></div>
          <div class="flex flex-col gap-4">
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-amber-500 text-[20px]">check_circle</span>
              <strong>25 books</strong>&nbsp;per month
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-amber-500 text-[20px]">check_circle</span>
              Up to 12 pages per book
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-amber-500 text-[20px]">check_circle</span>
              Classroom print &amp; distribute license
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-amber-500 text-[20px]">check_circle</span>
              No watermark
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-amber-500 text-[20px]">check_circle</span>
              Bulk ZIP download of all PDFs
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-amber-500 text-[20px]">check_circle</span>
              Priority support
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-amber-500 text-[20px]">check_circle</span>
              Perfect for classes of 30+ students
            </div>
          </div>
        </div>
      </div>

      <!-- FAQ Section -->
      <div class="mt-20 max-w-4xl w-full">
        <h2 class="text-2xl font-bold text-center text-slate-900 dark:text-white mb-8">Frequently Asked Questions</h2>
        <div class="grid md:grid-cols-2 gap-8">
          <div class="flex flex-col gap-2">
            <h4 class="font-bold text-slate-900 dark:text-white">Can I cancel anytime?</h4>
            <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">Yes, you can cancel your subscription at any time. Your access will remain active until the end of the billing period.</p>
          </div>
          <div class="flex flex-col gap-2">
            <h4 class="font-bold text-slate-900 dark:text-white">What format are the books?</h4>
            <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">All coloring books are generated as high-quality, printable PDFs, perfectly sized for standard A4 or Letter paper.</p>
          </div>
          <div class="flex flex-col gap-2">
            <h4 class="font-bold text-slate-900 dark:text-white">Is it safe for kids?</h4>
            <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">Absolutely. Our AI is tuned with strict safety filters to ensure all generated content is age-appropriate and family-friendly.</p>
          </div>
          <div class="flex flex-col gap-2">
            <h4 class="font-bold text-slate-900 dark:text-white">Do you offer refunds?</h4>
            <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">We offer a 7-day money-back guarantee if you're not completely satisfied with your TailorMade Coloring Book experience.</p>
          </div>
        </div>
      </div>
    </main>

    <AppFooter />
  </div>
</template>
