<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-1 flex flex-col items-center justify-start py-10 px-4 relative">
      <!-- Confetti Background -->
      <div
        class="absolute inset-0 z-0 pointer-events-none opacity-40 bg-cover bg-center"
        style="background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuAZi3BwxD8sY_ZzVJJfdywRWpVEvmUp4sRL0imA7g5Ie9iV244j6FCqkYd9q7OepwPQyq1SgTdwu1fYEZyo7gwG5rB3OR1LbKSuJMKS_ZqYj3xnrfPrSK-ADiswJou-g7g8FvE0vNvCAaRYfaiwWXKL8OgqFBJUscFs9HwUlAILa5q1gL26IILZ1CiuhyzEWmHDSdDNHCxvJYDAlkQB7h_8C-Dxzv7tpLXw0-NMnyxHJO1AJibvs_PdBkLnzqXQQJ_AWqSe8m8goiAJ');"
      ></div>

      <!-- Content Container -->
      <div class="relative z-10 w-full max-w-5xl flex flex-col items-center gap-8">
        <!-- Success Message -->
        <div class="text-center space-y-4 max-w-2xl mx-auto bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-8 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
          <div class="size-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto text-green-600 dark:text-green-400 mb-4">
            <span class="material-symbols-outlined text-[32px]">check_circle</span>
          </div>
          <h1 class="text-slate-900 dark:text-white tracking-tight text-4xl md:text-5xl font-bold leading-tight">Your book is ready!</h1>
          <p class="text-slate-600 dark:text-slate-400 text-lg font-normal leading-relaxed">
            Congratulations! <strong class="text-slate-900 dark:text-white">"Emma's Dinosaur Adventure"</strong> has been generated successfully. It's ready for coloring!
          </p>
        </div>

        <!-- Book Mockup & Actions Layout -->
        <div class="w-full grid grid-cols-1 lg:grid-cols-2 gap-8 items-center mt-4">
          <!-- Left: Book Mockup -->
          <div class="flex justify-center lg:justify-end">
            <div class="relative group cursor-pointer transition-transform duration-500 hover:scale-[1.02]">
              <!-- Glow effect -->
              <div class="absolute -inset-1 bg-gradient-to-r from-primary to-purple-500 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-500"></div>
              <!-- Book Cover -->
              <div class="relative w-[320px] h-[460px] bg-white dark:bg-slate-800 rounded-r-lg rounded-l-sm shadow-2xl overflow-hidden flex flex-col border-l-[12px] border-slate-200 dark:border-slate-700">
                <div
                  class="h-full w-full bg-cover bg-center"
                  style="background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuBg-ruGhD_i-_gC05wjNACTyuH6Q6uv7LEShOCtA8batfDqfTKiO4LK250fDcIr_16LUrOGuvBeXiI56XY8Xcw8KgvVXhD6NQmRh41n2WzgSGx7Rajbi0pUeUvmm7rNOsowhN-B_17BGc4Ri7ORAg2IYaYo3Ma5ek5wd-gAw4e8tVwLQifW5s0j-JWYsZD3FKegbdjBrH0uvsF3o_96bsn0NMiAtJkxutDUiB5ci364w-s3oub_rpEJ6hLj4aP_gMcrAtL8Z0hxFNwR');"
                >
                  <div class="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/70"></div>
                  <div class="absolute bottom-0 left-0 w-full p-6 text-white">
                    <div class="uppercase tracking-widest text-xs font-bold mb-1 opacity-80">Coloring Book</div>
                    <h3 class="text-2xl font-bold leading-tight">Emma's Dinosaur Adventure</h3>
                    <div class="mt-2 text-sm opacity-90 flex items-center gap-1">
                      <span class="material-symbols-outlined text-sm">print</span>
                      <span>Printable PDF &bull; 12 Pages</span>
                    </div>
                  </div>
                </div>
              </div>
              <!-- Page shadow effect -->
              <div class="absolute top-0 bottom-0 left-0 w-4 bg-gradient-to-r from-black/20 to-transparent pointer-events-none rounded-l-sm z-20"></div>
            </div>
          </div>

          <!-- Right: Actions -->
          <div class="flex flex-col gap-6 lg:items-start items-center max-w-md mx-auto lg:mx-0">
            <!-- Primary Actions Card -->
            <div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-lg border border-slate-100 dark:border-slate-800 w-full space-y-4">
              <button class="w-full flex items-center justify-center gap-3 bg-primary hover:bg-primary-dark text-white h-14 rounded-full font-bold text-lg transition-all shadow-md hover:shadow-lg active:scale-95">
                <span class="material-symbols-outlined">download</span>
                Download PDF
              </button>
              <button class="w-full flex items-center justify-center gap-3 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-900 dark:text-slate-100 h-14 rounded-full font-bold text-lg transition-all">
                <span class="material-symbols-outlined">print</span>
                Print Now
              </button>
            </div>

            <!-- Secondary Actions -->
            <div class="grid grid-cols-2 gap-4 w-full">
              <RouterLink to="/create" class="flex flex-col items-center justify-center gap-2 p-4 rounded-xl bg-white/50 dark:bg-slate-900/50 hover:bg-white dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 transition-all text-slate-700 dark:text-slate-300 hover:text-primary hover:border-primary/30">
                <div class="size-10 rounded-full bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center text-primary">
                  <span class="material-symbols-outlined">add_circle</span>
                </div>
                <span class="font-semibold text-sm">Create Another</span>
              </RouterLink>
              <button class="flex flex-col items-center justify-center gap-2 p-4 rounded-xl bg-white/50 dark:bg-slate-900/50 hover:bg-white dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 transition-all text-slate-700 dark:text-slate-300 hover:text-pink-500 hover:border-pink-500/30">
                <div class="size-10 rounded-full bg-pink-50 dark:bg-pink-900/20 flex items-center justify-center text-pink-500">
                  <span class="material-symbols-outlined">share</span>
                </div>
                <span class="font-semibold text-sm">Share with Friends</span>
              </button>
            </div>

            <!-- Preview Thumbs -->
            <div class="w-full pt-4">
              <p class="text-sm font-medium text-slate-500 dark:text-slate-400 mb-3 px-1">Sneak Peek</p>
              <div class="flex gap-3 overflow-x-auto pb-2 no-scrollbar">
                <div class="shrink-0 w-20 h-28 bg-white dark:bg-slate-800 rounded shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
                  <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuAx7tu_nAiZvpnIxzXg-3wMNGjPZWKKbCjXGGoNaelJ0Y4JJZe2ceoTPzW2w86w6L3VGMXoA37A41tuocO0vtDB-YflgAr24FwMVePwHKMDRxuCNrA1DAuLbz-DDUBfcRZ-eSuepHSgteLcDQgQ94h3wC0RB25Rr3S4pqOjB958381n2redACGp9lGUtqzap7h7obg97ly1nlYLbhnaOT6o3wbpXgSkNSGnxXbc9duUHapSQ2Rzu3QmBnZ6oRuujatrshmx2YceObpj" alt="Page 1" class="w-full h-full object-cover" />
                </div>
                <div class="shrink-0 w-20 h-28 bg-white dark:bg-slate-800 rounded shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
                  <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuChzSA6xzlvI6U7WdJzurpm0nF_MQLXU-RXr0aAGxXvNO5Katb9cu0pKo6pgLkpRlvta2UyWoXdW9iuCT9A93Mh5AT1JPQJetLisi6h4-9ghvSySomQX54K1ClrWfrVjwStvmRwrg_Q9mD5Wlbp91Rhb7P9_9mkeSlEjks4lUFbjjS6t3dYkWywRDxhGMp4BcRR16-jRNj6jZA10i5rwoeGzjQ5jcWHWKxbLPpoIUjy_EB1a1CSWc-X3RuAkijuATarPS5ws2IAm6CD" alt="Page 2" class="w-full h-full object-cover" />
                </div>
                <div class="shrink-0 w-20 h-28 bg-white dark:bg-slate-800 rounded shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
                  <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuAnChdw1ljEHO8fN6Mc49MNY_Jf-DuU9RpTNQMMENEA0LyCRq8WVlthpGi0DlNMv510kj2IVmCgoUjE1GkQEU1XmJkGC8TMWKsSYfN1dV9AN3OoDQ9S84s2c7ioYzOMwlgc64XzDlwTAFs1zXSRyTiIBhmzfP9B8OQF5y2K4JlXVXRWk7KlgeZx23uIyjIX_MT19FemnSUrjSTcF0F8ixQX7QEfbYR3ZKPrAYmjgZX8sFl4FZUXaZVuGdJAbfysRQJlaRx3BH7hOmHr" alt="Page 3" class="w-full h-full object-cover" />
                </div>
                <div class="shrink-0 w-20 h-28 bg-slate-100 dark:bg-slate-800 rounded border border-dashed border-slate-300 dark:border-slate-600 flex items-center justify-center text-slate-400">
                  <span class="text-xs font-medium">+9 more</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <AppFooter />
  </div>
</template>
