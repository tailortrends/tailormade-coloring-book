<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { RouterLink } from 'vue-router'

const books = [
  {
    title: "Leo's Space Adventure",
    child: "Leo",
    date: "Oct 12, 2023",
    type: "Theme",
    typeIcon: "palette",
    themeIcon: "rocket_launch",
    themeColor: "text-primary",
    image: "https://lh3.googleusercontent.com/aida-public/AB6AXuDnuhhiXgHjQ1aPeqPbooc_wzKlxSBDd9_0qV4GCAhSCntgK4oF2s0CrXzLjVajFsKu-tU4xo6nx76sJDWMKdPKsqX9jZIQNms_xdFwds6r-Bsek6UntCMjhv7bL47ccHs66n4A3EjtXqjdkhuxrgg3ChJKz7c7zRuVePjVgtqejy5Pd_lX8NesP4pGafp-g_37DPWVBgLgfdm8PqTaSJlI3xBVZw5wp1OnClBWhe_MEhB9G9uU21kK_n9eKBj5uTo0Vq4g32RCjLq8",
  },
  {
    title: "Mia's Jungle Party",
    child: "Mia",
    date: "Sep 28, 2023",
    type: "Theme",
    typeIcon: "palette",
    themeIcon: "forest",
    themeColor: "text-green-600",
    image: "https://lh3.googleusercontent.com/aida-public/AB6AXuDZSq5FPNqyQ2ohirG79RzNRlWxXxutCCb3FKRK43XRoYMikg5MFF-47fOmEkAa2csCZJFsUXFydSrZpsUk_zwKxH4Dq-nStTbruPLbDAnHAbRk9_GA8rKEKY7rbFa_DwtODNJ60qezQ55iYVlV6BWtrVHer5exuPD3Hm30ml3fAbBhqzAOwUERAOsVYbxtJl3BaBUL4S2ovOb3GIK8Xii-wsvl24M8p268hjk_Q-WR_Uvf8DA6pzW1cVd273Oxo0DM8cusv0E_EFyR",
  },
  {
    title: "Noah's Ocean Quest",
    child: "Noah",
    date: "Sep 15, 2023",
    type: "Photo",
    typeIcon: "photo_camera",
    themeIcon: "water_drop",
    themeColor: "text-blue-500",
    image: "https://lh3.googleusercontent.com/aida-public/AB6AXuAX1i4OFGA11JjDO8tibWX5hBLln5PDB43WbpgrlsZdQAXIdfIFzVJuiqgVZyI5aLdDA3Urgweo0Oao795txPn2JaFC4Um-d0oDNWz63vyhcUk-bnhTq2UV3xaWPrABni0cLBrWFIQr8tk0BmT9oORZO7tpfjFQFYZ--q2sKAK89SCROmrf-4UQIjC7gjz06WxFufhnlc4PQOCiWYK3w2nKGqz5m09J2fNLvMckY9Q-DMpVdorcp_mDcsW2Qa8v47fFsTL5ApwGQmFJ",
  },
  {
    title: "Ava's Fairy Tale",
    child: "Ava",
    date: "Aug 05, 2023",
    type: "Theme",
    typeIcon: "palette",
    themeIcon: "auto_fix_high",
    themeColor: "text-purple-500",
    image: "https://lh3.googleusercontent.com/aida-public/AB6AXuCVAKV6eVos4yTXDDSmYwDUNEtc2nphfs1c4QW6yATXGK9oS9OOuVuhZCEVgYMVen9_gJCqOhZH6m1hsU3fZgeJSQ8M7Y_1hPYdDcNH74uZHbKXwoNpVIFu-1iN1hm0tXxD99cf5OdTBRJ6pufXQhhspe2r-eKL1YOvacbwuD8woMmoyCGMK3PyA9zY6XHUyDVTaz1t1nooi4vqPZR_gAXq1_kvo_tjLR9i5lKVkkZk8m923jFnCelNCoMUANosLS19e4edw4gGgEe-",
  },
  {
    title: "Rex's Dino World",
    child: "Rex",
    date: "Jul 21, 2023",
    type: "Photo",
    typeIcon: "photo_camera",
    themeIcon: "pets",
    themeColor: "text-amber-600",
    image: "https://lh3.googleusercontent.com/aida-public/AB6AXuB3qVxAOYqcAhfIxTSrWsVJWjH0JwPVdkYfHTRZOGLEI4ZMpriKNZRaQ1IozexNQScySlimT9x3yzME5MhmFjrF0J5Df63T1-4tc9G_flh1lgkv04NsugPchwKPD_HXTWh006-oeKo2jQoHskP8W1Lcy_Na7aG5GzCNcYb1mMtLi4JDW-zXgCC7UG9m-MRVMHngb8QESfCF8L_znHcGIhARP_J0YH4tsgyVG-LAxqQpwrSHvT44nkRWdIs1rDkmPnb4GLFXpB2bAYUm",
  },
  {
    title: "Sam's Super Day",
    child: "Sam",
    date: "Jun 14, 2023",
    type: "Theme",
    typeIcon: "palette",
    themeIcon: "bolt",
    themeColor: "text-red-600",
    image: "https://lh3.googleusercontent.com/aida-public/AB6AXuCB1dSHDPsqiG0xOMziySvOGZ8B33VkdQsH6Z-wEAc8tKtwoUB8B8W0fzKUydmnVDIZKQQPxUy3rQtwkh1SF-6t5lOtpbNEVk1d7OKZkfvOxUEia3Qt99YXitpmnuCGGrWEsiiFpfRKMHponeyhfJa4v8XCkCqW1aJ0untEYEQfnnCvXnmO7b6ckoydNjSKfjMSVWzCIZ_fsf5yKvmyuxBmLJhZ8Vf0v4nhqP1psyop0VemdBU7LD6YSo84zrndq2d3n945LL2K4dt8",
  },
]
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-grow w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 py-8">
      <!-- Page Title -->
      <div class="mb-10 space-y-2">
        <h2 class="text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">My Coloring Library</h2>
        <p class="text-slate-500 dark:text-slate-400 text-lg">Access and reprint your personalized coloring adventures.</p>
      </div>

      <!-- Search & Filters -->
      <div class="flex flex-col md:flex-row gap-4 mb-8 items-center bg-white dark:bg-slate-900 p-2 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
        <div class="relative flex-grow w-full md:w-auto">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
            <span class="material-symbols-outlined">search</span>
          </div>
          <input
            class="w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-slate-800/50 border-transparent focus:border-primary focus:ring-0 rounded-xl text-slate-900 dark:text-slate-100 placeholder-slate-400 font-medium transition-all"
            placeholder="Search by book title or child's name"
            type="text"
          />
        </div>
        <div class="flex gap-2 w-full md:w-auto overflow-x-auto pb-2 md:pb-0 no-scrollbar">
          <button class="flex items-center gap-2 px-4 py-2.5 bg-slate-100 dark:bg-slate-800 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors whitespace-nowrap group">
            <span class="text-sm font-semibold text-slate-700 dark:text-slate-300">Book Type</span>
            <span class="material-symbols-outlined text-[18px] text-slate-500 group-hover:text-primary transition-colors">keyboard_arrow_down</span>
          </button>
          <button class="flex items-center gap-2 px-4 py-2.5 bg-slate-100 dark:bg-slate-800 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors whitespace-nowrap group">
            <span class="text-sm font-semibold text-slate-700 dark:text-slate-300">All Themes</span>
            <span class="material-symbols-outlined text-[18px] text-slate-500 group-hover:text-primary transition-colors">keyboard_arrow_down</span>
          </button>
          <button class="flex items-center gap-2 px-4 py-2.5 bg-slate-100 dark:bg-slate-800 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors whitespace-nowrap group">
            <span class="text-sm font-semibold text-slate-700 dark:text-slate-300">Date Created</span>
            <span class="material-symbols-outlined text-[18px] text-slate-500 group-hover:text-primary transition-colors">keyboard_arrow_down</span>
          </button>
        </div>
        <div class="hidden md:block w-px h-8 bg-slate-200 dark:bg-slate-700 mx-2"></div>
        <div class="flex items-center gap-2 ml-auto">
          <button class="p-2 text-primary" title="Grid View">
            <span class="material-symbols-outlined">grid_view</span>
          </button>
          <button class="p-2 text-slate-400 hover:text-primary transition-colors" title="List View">
            <span class="material-symbols-outlined">view_list</span>
          </button>
        </div>
      </div>

      <!-- Books Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <!-- Book Cards -->
        <div
          v-for="book in books"
          :key="book.title"
          class="group relative bg-white dark:bg-slate-900 rounded-2xl p-4 shadow-sm hover:shadow-xl hover:shadow-primary/10 border border-slate-100 dark:border-slate-800 transition-all duration-300 flex flex-col"
        >
          <div class="relative w-full aspect-[3/4] rounded-xl overflow-hidden mb-4 bg-slate-100">
            <img :alt="book.title" :src="book.image" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
            <div class="absolute top-3 left-3 flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-white text-[10px] font-bold uppercase tracking-wide" :class="book.type === 'Photo' ? 'bg-blue-600/90 backdrop-blur-sm' : 'bg-slate-900/80 backdrop-blur-sm'">
              <span class="material-symbols-outlined text-[14px]">{{ book.typeIcon }}</span>
              {{ book.type }}
            </div>
            <div class="absolute top-3 right-3 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm p-1.5 rounded-lg shadow-sm" :class="book.themeColor">
              <span class="material-symbols-outlined text-[20px]">{{ book.themeIcon }}</span>
            </div>
            <button class="absolute bottom-3 right-3 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm p-2 rounded-full shadow-sm text-slate-600 hover:text-primary hover:scale-110 transition-all opacity-0 group-hover:opacity-100">
              <span class="material-symbols-outlined text-[18px]">share</span>
            </button>
          </div>
          <div class="flex-grow">
            <h3 class="text-lg font-bold text-slate-900 dark:text-white line-clamp-1 group-hover:text-primary transition-colors">{{ book.title }}</h3>
            <div class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-4">
              <span class="material-symbols-outlined text-[16px]">child_care</span>
              <span>For {{ book.child }}</span>
              <span class="w-1 h-1 rounded-full bg-slate-300"></span>
              <span>{{ book.date }}</span>
            </div>
          </div>
          <div class="flex gap-2 mt-auto pt-4 border-t border-slate-100 dark:border-slate-800/50">
            <button class="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-primary/10 hover:bg-primary/20 text-primary text-sm font-bold transition-colors">
              <span class="material-symbols-outlined text-[18px]">visibility</span>
              View
            </button>
            <button class="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-sm font-bold transition-colors">
              <span class="material-symbols-outlined text-[18px]">download</span>
              PDF
            </button>
          </div>
        </div>

        <!-- Create New Book Card -->
        <RouterLink to="/create" class="group relative rounded-2xl border-2 border-dashed border-slate-200 dark:border-slate-700 hover:border-primary dark:hover:border-primary/60 bg-transparent flex flex-col items-center justify-center p-8 transition-colors cursor-pointer min-h-[350px]">
          <div class="w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4 group-hover:bg-primary/10 transition-colors">
            <span class="material-symbols-outlined text-3xl text-slate-400 group-hover:text-primary transition-colors">add</span>
          </div>
          <h3 class="text-lg font-bold text-slate-900 dark:text-white mb-2">Create New Book</h3>
          <p class="text-sm text-slate-500 text-center max-w-[200px]">Start a new magical adventure for your child today!</p>
        </RouterLink>
      </div>
    </main>

    <AppFooter />
  </div>
</template>
