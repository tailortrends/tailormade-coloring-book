<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import ComingSoonModal from '@/components/ComingSoonModal.vue'
import { RouterLink } from 'vue-router'

const showModal = ref(false)
const selectedPlan = ref('')

function openModal(planName: string) {
  selectedPlan.value = planName
  showModal.value = true
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

      <!-- Pricing Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full max-w-[1280px]">

        <!-- Card 1 — Free Starter -->
        <div class="flex flex-col gap-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex flex-col gap-2">
            <h3 class="text-slate-900 dark:text-white text-xl font-bold leading-tight">Free Starter</h3>
            <p class="text-slate-500 dark:text-slate-400 text-sm">Try the magic, no commitment.</p>
            <div class="flex items-baseline gap-1 mt-2">
              <span class="text-slate-900 dark:text-white text-5xl font-black tracking-tight">$0</span>
            </div>
            <p class="text-slate-400 dark:text-slate-500 text-xs font-medium">One free book, yours to keep</p>
          </div>
          <RouterLink to="/signup" class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-900 dark:text-white text-sm font-bold transition-colors">
            Get Started Free
          </RouterLink>
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
          <button @click="openModal('Single Masterpiece')" class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-200 text-white dark:text-slate-900 text-sm font-bold transition-colors">
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
        <div class="relative flex flex-col gap-6 rounded-2xl border-2 border-primary bg-white dark:bg-slate-900 p-8 shadow-xl shadow-primary/10 lg:scale-105 z-10">
          <div class="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-lg">
            Most Popular
          </div>
          <div class="flex flex-col gap-2">
            <h3 class="text-primary text-xl font-bold leading-tight">Family Plan</h3>
            <p class="text-slate-500 dark:text-slate-400 text-sm">Perfect for siblings and busy families.</p>
            <div class="flex items-baseline gap-1 mt-2">
              <span class="text-slate-900 dark:text-white text-5xl font-black tracking-tight">$19.99</span>
              <span class="text-slate-500 dark:text-slate-400 text-base font-bold">/mo</span>
            </div>
          </div>
          <button @click="openModal('Family Plan')" class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-primary hover:bg-blue-600 text-white text-sm font-bold transition-colors shadow-lg shadow-primary/30">
            Start Family Plan
          </button>
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
        <div class="relative flex flex-col gap-6 rounded-2xl border-2 border-amber-500 bg-white dark:bg-slate-900 p-8 shadow-sm hover:shadow-md transition-shadow">
          <div class="absolute -top-4 left-1/2 -translate-x-1/2 bg-amber-500 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-lg">
            Classroom License Included
          </div>
          <div class="flex flex-col gap-2">
            <h3 class="text-amber-500 text-xl font-bold leading-tight">Teacher Edition</h3>
            <p class="text-slate-500 dark:text-slate-400 text-sm">One theme. Thirty students. Zero prep.</p>
            <div class="flex items-baseline gap-1 mt-2">
              <span class="text-slate-900 dark:text-white text-5xl font-black tracking-tight">$39.99</span>
              <span class="text-slate-500 dark:text-slate-400 text-base font-bold">/mo</span>
            </div>
          </div>
          <button @click="openModal('Teacher Edition')" class="w-full flex items-center justify-center rounded-full h-12 px-6 bg-amber-500 hover:bg-amber-600 text-white text-sm font-bold transition-colors shadow-lg shadow-amber-500/30">
            Get Teacher Plan
          </button>
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
            <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">We offer a 7-day money-back guarantee if you're not completely satisfied with your ColorMagic AI experience.</p>
          </div>
        </div>
      </div>
    </main>

    <AppFooter />

    <!-- Coming Soon Modal -->
    <ComingSoonModal :visible="showModal" :plan-name="selectedPlan" @close="showModal = false" />
  </div>
</template>
