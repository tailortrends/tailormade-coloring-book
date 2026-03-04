<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Dummy redirect to book-ready after 5 seconds
onMounted(() => {
  setTimeout(() => {
    router.push('/book-ready')
  }, 5000)
})
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-text-main dark:text-slate-100 min-h-screen flex flex-col overflow-x-hidden">
    <AppHeader />

    <main class="flex-grow flex flex-col items-center justify-center py-12 px-6 relative w-full max-w-[1200px] mx-auto">
      <!-- Decorative Background Elements -->
      <div class="absolute top-20 left-10 text-primary/10 animate-pulse hidden lg:block">
        <span class="material-symbols-outlined text-[120px]">brush</span>
      </div>
      <div class="absolute bottom-20 right-10 text-accent-purple/10 animate-pulse hidden lg:block">
        <span class="material-symbols-outlined text-[120px]">palette</span>
      </div>
      <div class="absolute top-40 right-40 size-4 rounded-full bg-yellow-400/40"></div>
      <div class="absolute bottom-60 left-40 size-6 rounded-full bg-purple-400/40"></div>
      <div class="absolute top-1/4 left-1/4 size-3 rounded-full bg-primary/30"></div>

      <!-- Central Status Area -->
      <div class="w-full max-w-2xl text-center z-10 mb-16">
        <div class="inline-flex items-center justify-center p-3 mb-6 bg-primary/10 rounded-full text-primary animate-bounce">
          <span class="material-symbols-outlined text-3xl">magic_button</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-extrabold text-slate-900 dark:text-white mb-4 tracking-tight">
          Magic in Progress
        </h1>
        <p class="text-lg text-slate-600 dark:text-slate-300 mb-10">
          Your book is being crafted with magic! Our AI elves are drawing the lines.
        </p>

        <!-- Progress Bar Card -->
        <div class="bg-white dark:bg-slate-900 rounded-xl shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-800 p-8 w-full">
          <div class="flex justify-between items-end mb-4">
            <div class="text-left">
              <p class="text-sm font-bold text-primary uppercase tracking-wider mb-1">Status</p>
              <p class="text-lg font-medium text-slate-900 dark:text-white flex items-center gap-2">
                Generating page 4 of 10...
                <span class="flex h-2 w-2 relative">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                </span>
              </p>
            </div>
            <div class="text-right">
              <span class="text-3xl font-bold text-slate-900 dark:text-white">40%</span>
            </div>
          </div>
          
          <div class="h-4 w-full bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-primary to-accent-purple rounded-full transition-all duration-1000 ease-out relative overflow-hidden" style="width: 40%">
              <div class="absolute inset-0 bg-white/20 w-full h-full animate-shimmer skew-x-12 translate-x-[-100%]"></div>
            </div>
          </div>
          
          <div class="mt-6 flex items-center justify-center gap-2 text-sm text-slate-400 dark:text-slate-500">
            <span class="material-symbols-outlined text-base">timer</span>
            Estimated time remaining: ~5 seconds (Dummy)
          </div>
        </div>
      </div>

      <!-- Horizontal Scroll Preview -->
      <div class="w-full z-10">
        <div class="flex items-center justify-between mb-6 px-4">
          <h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">visibility</span>
            Finished Pages Preview
          </h2>
          <div class="flex gap-2">
            <button class="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-colors">
              <span class="material-symbols-outlined">arrow_back</span>
            </button>
            <button class="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-colors">
              <span class="material-symbols-outlined">arrow_forward</span>
            </button>
          </div>
        </div>

        <!-- Scroll Container -->
        <div class="overflow-x-auto no-scrollbar pb-8 -mx-6 px-6 md:mx-0 md:px-0">
          <div class="flex gap-6 w-max">
            <!-- Finished Page 1 -->
            <div class="group relative w-48 aspect-[3/4] bg-white dark:bg-slate-900 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden hover:-translate-y-1 transition-transform duration-300">
              <div class="absolute top-3 right-3 z-10 bg-green-500 text-white text-[10px] font-bold px-2 py-1 rounded-full flex items-center gap-1 shadow-sm">
                <span class="material-symbols-outlined text-[12px]">check</span> DONE
              </div>
              <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuACfTmTGyBua0Xwx0LF8ZLyBcAmx6PpuYc49h7I84ip7NHPMtXApplzJL4eVIz6P34_4407SfJqUNduT1fCIuht6DjP0AsyEGKhHoKY8_-Xz-7g96knbLrfL1cnnqG4QbJwWeJMB4cOFKsgruvEgMhngVTodqrMal27Tr2tJdcBqgW32oClU7Fzh3GjWzHhDhn8eymwvhyL8qpCR4Wh22zkLMGJGlth2R7rQYJ1j7ErScFs4GNHJxcB-Po3pnuTD9YybsVUSIom46Yd" alt="Page 1" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity grayscale contrast-125" />
              <div class="absolute bottom-0 left-0 w-full p-3 bg-gradient-to-t from-black/60 to-transparent">
                <p class="text-white text-xs font-medium">Page 1: Dragon</p>
              </div>
            </div>

            <!-- Finished Page 2 -->
            <div class="group relative w-48 aspect-[3/4] bg-white dark:bg-slate-900 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden hover:-translate-y-1 transition-transform duration-300">
              <div class="absolute top-3 right-3 z-10 bg-green-500 text-white text-[10px] font-bold px-2 py-1 rounded-full flex items-center gap-1 shadow-sm">
                <span class="material-symbols-outlined text-[12px]">check</span> DONE
              </div>
              <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuAq7xGHT-GgRBLopQUSoKjkQn4TgIa-eb4CXFsMKls_e7TXId6u76etQbwDJaosGuqn0durrARUWvmcY4icVSP32jWL97wTsrujqVwTuM_LJaZhH1nj8XyATrlPgWkOrrKEPobnYKByg8kQJHod2bdNZSiyKd-SBSw-G4BlJEyW4wztr2yJ3d91xPyVK2XDk6psBjpghH94eFHA6NLEXFVRmOSNRaHpv2VXN4IYTo09Md9em3aPaneSpWQJFfJ8poYWc6rjReXZrZT4" alt="Page 2" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity grayscale contrast-125" />
              <div class="absolute bottom-0 left-0 w-full p-3 bg-gradient-to-t from-black/60 to-transparent">
                <p class="text-white text-xs font-medium">Page 2: Puppy</p>
              </div>
            </div>

            <!-- Finished Page 3 -->
            <div class="group relative w-48 aspect-[3/4] bg-white dark:bg-slate-900 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden hover:-translate-y-1 transition-transform duration-300">
              <div class="absolute top-3 right-3 z-10 bg-green-500 text-white text-[10px] font-bold px-2 py-1 rounded-full flex items-center gap-1 shadow-sm">
                <span class="material-symbols-outlined text-[12px]">check</span> DONE
              </div>
              <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCqSgy7EkdElnQDpFXk4HfkoQf3gFwfESQ23VPUy9VTOAHfYi3VMkmyWrlYes9AHzrJD_G5iCEdnvpt47ohK9JSpzhH9fi4y5t6KH6D4uwbDZWDfwZVNzE-FrEzvk5Wfbx-7g2vQxlcNsP29gvCkXONQuuJDhBmtiZb8mHXW9-YJ5JQsBBhz47XKDxyNAx8sgSlox8K0hj70AtSeL4BtXFGnpAq-bbuJ1_IPhcnKoSHHnl7X3y8Yez_qNRLosj5ADyjCWb3FxZnhrBQ" alt="Page 3" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity grayscale contrast-125" />
              <div class="absolute bottom-0 left-0 w-full p-3 bg-gradient-to-t from-black/60 to-transparent">
                <p class="text-white text-xs font-medium">Page 3: Space</p>
              </div>
            </div>

            <!-- Current Generating Page (Placeholder) -->
            <div class="relative w-48 aspect-[3/4] bg-slate-100 dark:bg-slate-800 rounded-xl border-2 border-dashed border-primary/40 flex flex-col items-center justify-center p-4">
              <div class="size-12 rounded-full bg-primary/10 flex items-center justify-center mb-3 animate-spin text-primary">
                <span class="material-symbols-outlined opacity-100 hover:opacity-100">refresh</span>
              </div>
              <p class="text-sm font-semibold text-slate-700 dark:text-slate-200 text-center">Drawing...</p>
              <p class="text-xs text-slate-500 dark:text-slate-400 text-center mt-1">Page 4: Castle</p>
            </div>

            <!-- Future Page (Locked) -->
            <div class="relative w-48 aspect-[3/4] bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-800 flex flex-col items-center justify-center p-4 opacity-60">
              <div class="size-10 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center mb-3 text-slate-400">
                <span class="material-symbols-outlined opacity-100 hover:opacity-100">lock</span>
              </div>
              <p class="text-xs font-semibold text-slate-400 dark:text-slate-500 text-center">Page 5</p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <AppFooter />
  </div>
</template>
