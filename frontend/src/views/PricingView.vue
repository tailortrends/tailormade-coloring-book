<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { RouterLink } from 'vue-router'
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

      <!-- Pricing Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-[1200px]">
        <!-- Free Starter Card -->
        <div class="flex flex-col gap-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex flex-col gap-2">
            <h3 class="text-slate-900 dark:text-white text-xl font-bold leading-tight">Free Starter</h3>
            <p class="text-slate-500 dark:text-slate-400 text-sm">Perfect for trying out the magic.</p>
            <div class="flex items-baseline gap-1 mt-2">
              <span class="text-slate-900 dark:text-white text-5xl font-black tracking-tight">$0</span>
              <span class="text-slate-500 dark:text-slate-400 text-base font-bold">/mo</span>
            </div>
          </div>
          <RouterLink to="/signup" class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-900 dark:text-white text-sm font-bold transition-colors">
            Get Started Free
          </RouterLink>
          <div class="w-full h-px bg-slate-200 dark:bg-slate-800 my-2"></div>
          <div class="flex flex-col gap-4">
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-green-500 text-[20px]">check_circle</span>
              2 Books per month
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-green-500 text-[20px]">check_circle</span>
              Standard generation speed
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-green-500 text-[20px]">check_circle</span>
              10 Pages per book
            </div>
            <div class="text-sm font-medium text-slate-400 dark:text-slate-600 flex gap-3 items-center">
              <span class="material-symbols-outlined text-[20px]">cancel</span>
              Includes watermarks
            </div>
          </div>
        </div>

        <!-- Pro Artist Card (Highlighted) -->
        <div class="relative flex flex-col gap-6 rounded-2xl border-2 border-primary bg-white dark:bg-slate-900 p-8 shadow-xl shadow-primary/10 scale-105 z-10">
          <div class="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-lg">
            Most Popular
          </div>
          <div class="flex flex-col gap-2">
            <h3 class="text-primary text-xl font-bold leading-tight">Pro Artist</h3>
            <p class="text-slate-500 dark:text-slate-400 text-sm">For the dedicated young creator.</p>
            <div class="flex items-baseline gap-1 mt-2">
              <span class="text-slate-900 dark:text-white text-5xl font-black tracking-tight">$7.99</span>
              <span class="text-slate-500 dark:text-slate-400 text-base font-bold">/mo</span>
            </div>
          </div>
          <button class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-primary hover:bg-blue-600 text-white text-sm font-bold transition-colors shadow-lg shadow-primary/30">
            Upgrade to Pro
          </button>
          <div class="w-full h-px bg-slate-200 dark:bg-slate-800 my-2"></div>
          <div class="flex flex-col gap-4">
            <div class="text-sm font-medium text-slate-900 dark:text-white flex gap-3 items-center">
              <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
              <strong>10 Books</strong>&nbsp;per month
            </div>
            <div class="text-sm font-medium text-slate-900 dark:text-white flex gap-3 items-center">
              <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
              <strong>Priority</strong>&nbsp;generation speed
            </div>
            <div class="text-sm font-medium text-slate-900 dark:text-white flex gap-3 items-center">
              <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
              30 Pages per book
            </div>
            <div class="text-sm font-medium text-slate-900 dark:text-white flex gap-3 items-center">
              <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
              No watermarks
            </div>
            <div class="text-sm font-medium text-slate-900 dark:text-white flex gap-3 items-center">
              <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
              HD PDF Downloads
            </div>
          </div>
        </div>

        <!-- Premium Unlimited Card -->
        <div class="flex flex-col gap-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex flex-col gap-2">
            <h3 class="text-slate-900 dark:text-white text-xl font-bold leading-tight">Premium Unlimited</h3>
            <p class="text-slate-500 dark:text-slate-400 text-sm">Limitless fun for the whole family.</p>
            <div class="flex items-baseline gap-1 mt-2">
              <span class="text-slate-900 dark:text-white text-5xl font-black tracking-tight">$14.99</span>
              <span class="text-slate-500 dark:text-slate-400 text-base font-bold">/mo</span>
            </div>
          </div>
          <button class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-200 text-white dark:text-slate-900 text-sm font-bold transition-colors">
            Get Unlimited
          </button>
          <div class="w-full h-px bg-slate-200 dark:bg-slate-800 my-2"></div>
          <div class="flex flex-col gap-4">
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-accent-purple text-[20px]">verified</span>
              <strong>Unlimited Books</strong>
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-accent-purple text-[20px]">verified</span>
              <strong>Instant</strong>&nbsp;generation
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-accent-purple text-[20px]">verified</span>
              50 Pages per book
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-accent-purple text-[20px]">verified</span>
              No watermarks
            </div>
            <div class="text-sm font-medium text-slate-700 dark:text-slate-300 flex gap-3 items-center">
              <span class="material-symbols-outlined text-accent-purple text-[20px]">verified</span>
              Priority Support 24/7
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
            <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">We offer a 7-day money-back guarantee if you're not completely satisfied with your ColorMagic AI experience.</p>
          </div>
        </div>
      </div>
    </main>

    <AppFooter />
  </div>
</template>
