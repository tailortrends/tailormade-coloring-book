<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-grow flex flex-col items-center w-full px-6 py-8">
      <div class="w-full max-w-[1080px] flex flex-col gap-8">
        <!-- Breadcrumbs -->
        <div class="flex flex-wrap items-center gap-2">
          <RouterLink to="/dashboard" class="text-slate-500 hover:text-primary transition-colors text-base font-medium">Home</RouterLink>
          <span class="text-slate-400 text-base font-medium">/</span>
          <RouterLink to="/library" class="text-slate-500 hover:text-primary transition-colors text-base font-medium">My Library</RouterLink>
          <span class="text-slate-400 text-base font-medium">/</span>
          <span class="text-slate-900 dark:text-white text-base font-medium">Share Creation</span>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <!-- Left: Mockup Preview -->
          <div class="lg:col-span-7 flex flex-col gap-6">
            <div class="relative bg-white dark:bg-slate-900 rounded-xl overflow-hidden shadow-sm border border-slate-200 dark:border-slate-800 p-8 min-h-[480px] flex items-center justify-center group">
              <div class="absolute inset-0 bg-gradient-to-br from-accent-purple/5 via-transparent to-primary/5 dark:from-accent-purple/10 dark:to-primary/10"></div>
              <span class="material-symbols-outlined absolute top-10 left-10 text-accent-purple/20 text-4xl animate-pulse">star</span>
              <span class="material-symbols-outlined absolute bottom-12 right-12 text-primary/20 text-3xl">auto_awesome</span>

              <div class="relative z-10 w-full max-w-md">
                <div class="aspect-[3/4] w-full rounded-r-lg shadow-2xl overflow-hidden">
                  <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuBk_Ol0TmtbK2qDBgpQH8ScUMc2fqt0U_fyq2Pm5DM3rdgnNeIbNGywuWH2qxctssByzQt2Bay2QbRvBp--nhfPCy0JoatXQvKog37GDUXieQxCnI1qVc0x37Gh5AN79N2RUZxUFGCyk8EgTIzb0Nb3wnXHLBI6hm3IbMKMPapdZS-vTVdXwq0-bZSgm3cIv95wIGOo0siePuZOwNVc_V_fJODqYx7rt47FwhjKKUSTmL6kLtsa45bf-KJx-2CQ-kJsPE3nYbrmLIxI" alt="Coloring book cover" class="w-full h-full object-cover" />
                </div>
                <div class="absolute bottom-6 left-0 right-0 text-center">
                  <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm text-xs font-semibold text-primary border border-primary/20">
                    <span class="material-symbols-outlined text-sm">check_circle</span>
                    Ready to Print
                  </span>
                </div>
              </div>
            </div>
            <div class="flex justify-between items-center">
              <RouterLink to="/library" class="flex items-center gap-2 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors font-medium">
                <span class="material-symbols-outlined">arrow_back</span>
                Back to Library
              </RouterLink>
              <button class="flex items-center gap-2 text-primary hover:text-primary-dark transition-colors font-bold">
                <span class="material-symbols-outlined">download</span>
                Download PDF
              </button>
            </div>
          </div>

          <!-- Right: Sharing Actions -->
          <div class="lg:col-span-5 flex flex-col justify-center gap-8">
            <div class="space-y-2 text-center lg:text-left">
              <h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white leading-tight">Your Masterpiece is Ready!</h1>
              <p class="text-slate-600 dark:text-slate-400 text-lg">Show off your custom coloring book to friends and family.</p>
            </div>

            <!-- Social Share Buttons -->
            <div class="flex flex-col gap-3">
              <button class="flex items-center justify-center gap-3 w-full h-12 rounded-lg bg-[#1877F2] hover:bg-[#166fe5] text-white font-bold transition-all hover:-translate-y-0.5 shadow-md hover:shadow-lg">
                <span class="material-symbols-outlined">public</span>
                Share on Facebook
              </button>
              <button class="flex items-center justify-center gap-3 w-full h-12 rounded-lg bg-[#E60023] hover:bg-[#d50021] text-white font-bold transition-all hover:-translate-y-0.5 shadow-md hover:shadow-lg">
                <span class="material-symbols-outlined">push_pin</span>
                Pin to Board
              </button>
              <button class="flex items-center justify-center gap-3 w-full h-12 rounded-lg bg-[#25D366] hover:bg-[#20bd5a] text-white font-bold transition-all hover:-translate-y-0.5 shadow-md hover:shadow-lg">
                <span class="material-symbols-outlined">chat</span>
                WhatsApp
              </button>
            </div>

            <!-- Secret Link Card -->
            <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700 shadow-sm">
              <div class="flex items-center gap-3 mb-3">
                <span class="material-symbols-outlined text-primary">lock</span>
                <h3 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">Secret Link</h3>
              </div>
              <p class="text-xs text-slate-500 mb-3">Only people with this link can view this page.</p>
              <div class="flex items-center gap-2 p-2 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
                <input class="flex-1 bg-transparent border-none text-slate-600 dark:text-slate-300 text-sm focus:ring-0 px-2 truncate" readonly type="text" value="colormagic.ai/s/8f2k9l1m" />
                <button class="flex-shrink-0 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-primary border border-slate-200 dark:border-slate-700 rounded-md px-3 py-1.5 text-xs font-bold transition-colors">
                  Copy
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <AppFooter />
  </div>
</template>
