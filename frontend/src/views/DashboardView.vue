<script setup lang="ts">
import BottomNav from '@/components/BottomNav.vue'
import AppHeader from '@/components/AppHeader.vue'
import { RouterLink } from 'vue-router'

const recentBooks = [
  {
    title: 'Dragon Adventures',
    pages: 12,
    age: '2h ago',
    img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCEZClNyDYk_3j7BTlyfJ3oL2qBA4dCjou6lwudraOnGkQifXGnVO5-vI25QsGbUIZTjgdcELYKVDYAvaEONIpYni-9SJnhb5D5vyuBWO5gHXXtDtm4AHqjghNBdhbmZ6zrDMWE2ymOFHjSQ6fmohZMh1DsUtpuosiWljbjdonYisIdy4wM-PDT_g2ROoXjrgFsahTqf9WDCxmY7OeA0LtRQexNfHQ6PoPe2-2WYj16KAAOxQ7feBq2-7lNM6D40grwkO-8vuZSz-T',
  },
  {
    title: 'Space Explorers',
    pages: 8,
    age: 'Yesterday',
    img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBYi75jRgw757I4gf_6nQ7BmabR28Jd7vmhTEU9tqcwqu-5KSuWX56cKQc6DKXhV_mh3XRArRvxgWLYyMtD8zXH3mC7pvGAkDWGqLz6C5s5w85MZrqdYyGm4RaoWClY8xDYRFsQT_LqcfLjrYd84ohG6xzSewhRpV48BozbElxHXbjpDhym0n_TzFp-KHsyCMAqLuRENtOtX6BSi59KlHxbkbLpcjRn5rwfkios6wOSNGZSxl9F5iWDpWB5OFt_rasU29nQJxBiXeM_',
  },
  {
    title: 'Deep Sea Pals',
    pages: 15,
    age: '3 days ago',
    img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDtUZBG3LIWVV1yQYysHOQBqfsit6BtWkSIl5_qOic3kG8rsY7lUzGrymv9TslPGLw1WwhejshU9oL7dGRaQrDbYYkfEnN7VVEHLjISpkB37W5VX9IB2yrHtKRXygdmAeC6-RtfO3YII-x3fpR04ie-J9I_KpQkQ_MXA2qFkRtmz01W2_tuBoLUylDMf7nRvld7YYwVLJN8NRmgPJ1_eevD73jHfc81zj615SSxCUJwICVIgfKFOSG2-gsb5l9PNMzlSgWJnawSAyR9',
  },
]

const notifications = [
  { text: 'Photo-to-color mode is live!', icon: 'photo_camera', color: 'text-primary', time: '1h ago' },
  { text: "New 'Superheroes' pack available", icon: 'local_fire_department', color: 'text-accent-orange', time: '3h ago' },
  { text: "Your 'Fairy Garden' book is ready", icon: 'check_circle', color: 'text-green-500', time: 'Yesterday' },
]
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 min-h-screen font-display">

    <!-- ===================== MOBILE LAYOUT (< lg) ===================== -->
    <div class="lg:hidden">
      <div class="max-w-md mx-auto bg-white dark:bg-slate-900 min-h-screen shadow-2xl relative flex flex-col pb-24">
        <!-- Header -->
        <header class="flex items-center justify-between px-6 pt-8 pb-4">
          <div class="flex flex-col">
            <h1 class="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">Hello, Sarah! 👋</h1>
            <p class="text-slate-500 dark:text-slate-400 text-sm font-medium">Ready for some magic?</p>
          </div>
          <div class="relative">
            <div class="size-12 rounded-full bg-primary/10 flex items-center justify-center border-2 border-primary/20 overflow-hidden">
              <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCJcV3Bn8ZSqnME-yTuun0QTCv70iXiaT4CPxc0I64VIYBoz117tNxSFnkGXidqaAfGS-Qroha6xZU3uaYpZpSzANMCG_jtTF6bEr26dXLyTHABP49MKmhqUETGHsALNEXDFQ3D9abiD4Tv4WS2T5AqS85nsQtXkSn9SwstbZw1dZfKpfQr9ibsyiCUGM04YWNRYF0-PyfP0BDaw1XLmEcVPD6cbWQey6CGtwJW3RzgeiuCq7tQYkhIZlRqNk9nm9CgnpX1Ebe0__0E" alt="Avatar" class="w-full h-full object-cover" />
            </div>
            <div class="absolute -top-1 -right-1 size-4 bg-primary rounded-full border-2 border-white dark:border-slate-900"></div>
          </div>
        </header>

        <!-- Stats Horizontal Scroll -->
        <div class="px-6 py-4">
          <h3 class="text-sm font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-4">Monthly Quotas</h3>
          <div class="flex gap-4 overflow-x-auto no-scrollbar">
            <div class="flex-shrink-0 w-32 h-40 bg-primary/5 dark:bg-primary/10 rounded-xl p-4 flex flex-col items-center justify-between border border-primary/10">
              <div class="relative size-16">
                <svg viewBox="0 0 36 36" class="size-full">
                  <circle cx="18" cy="18" r="16" fill="none" class="stroke-slate-200 dark:stroke-slate-700" stroke-width="3"></circle>
                  <circle cx="18" cy="18" r="16" fill="none" class="stroke-primary" stroke-width="3" stroke-dasharray="75, 100" stroke-linecap="round"></circle>
                </svg>
                <div class="absolute inset-0 flex items-center justify-center">
                  <span class="text-xs font-bold text-primary">12/20</span>
                </div>
              </div>
              <p class="text-xs font-bold text-slate-600 dark:text-slate-300 text-center">PDFs Remaining</p>
            </div>
            <div class="flex-shrink-0 w-32 h-40 bg-primary/5 dark:bg-primary/10 rounded-xl p-4 flex flex-col items-center justify-between border border-primary/10">
              <div class="relative size-16">
                <svg viewBox="0 0 36 36" class="size-full">
                  <circle cx="18" cy="18" r="16" fill="none" class="stroke-slate-200 dark:stroke-slate-700" stroke-width="3"></circle>
                  <circle cx="18" cy="18" r="16" fill="none" class="stroke-primary" stroke-width="3" stroke-dasharray="45, 100" stroke-linecap="round"></circle>
                </svg>
                <div class="absolute inset-0 flex items-center justify-center">
                  <span class="text-xs font-bold text-primary">85</span>
                </div>
              </div>
              <p class="text-xs font-bold text-slate-600 dark:text-slate-300 text-center">Total Pages</p>
            </div>
            <div class="flex-shrink-0 w-32 h-40 bg-primary/5 dark:bg-primary/10 rounded-xl p-4 flex flex-col items-center justify-between border border-primary/10">
              <div class="relative size-16">
                <svg viewBox="0 0 36 36" class="size-full">
                  <circle cx="18" cy="18" r="16" fill="none" class="stroke-slate-200 dark:stroke-slate-700" stroke-width="3"></circle>
                  <circle cx="18" cy="18" r="16" fill="none" class="stroke-primary" stroke-width="3" stroke-dasharray="90, 100" stroke-linecap="round"></circle>
                </svg>
                <div class="absolute inset-0 flex items-center justify-center">
                  <span class="text-xs font-bold text-primary">5</span>
                </div>
              </div>
              <p class="text-xs font-bold text-slate-600 dark:text-slate-300 text-center">Bonus Credits</p>
            </div>
          </div>
        </div>

        <!-- Usage Chart -->
        <div class="px-6 py-4">
          <div class="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-5 border border-slate-100 dark:border-slate-800">
            <div class="flex justify-between items-end mb-4">
              <div>
                <h3 class="text-sm font-bold text-slate-900 dark:text-white">Creation Activity</h3>
                <p class="text-xs text-slate-500">Last 7 days</p>
              </div>
              <span class="text-primary font-bold text-lg">+12%</span>
            </div>
            <div class="h-16 flex items-end gap-1 justify-between px-2">
              <div class="w-full bg-primary/20 rounded-t-sm h-8"></div>
              <div class="w-full bg-primary/20 rounded-t-sm h-12"></div>
              <div class="w-full bg-primary/40 rounded-t-sm h-10"></div>
              <div class="w-full bg-primary/20 rounded-t-sm h-6"></div>
              <div class="w-full bg-primary rounded-t-sm h-14"></div>
              <div class="w-full bg-primary/30 rounded-t-sm h-9"></div>
              <div class="w-full bg-primary/60 rounded-t-sm h-11"></div>
            </div>
          </div>
        </div>

        <!-- Recent Creations -->
        <div class="px-6 py-4 flex-grow">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">Recent Creations</h3>
            <RouterLink to="/library" class="text-primary text-sm font-bold">See All</RouterLink>
          </div>
          <div class="space-y-4">
            <div v-for="book in recentBooks" :key="book.title" class="flex items-center gap-4 p-3 bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700 shadow-sm">
              <div class="size-20 rounded-lg bg-slate-100 dark:bg-slate-700 overflow-hidden flex-shrink-0">
                <img :src="book.img" :alt="book.title" class="w-full h-full object-cover" />
              </div>
              <div class="flex-grow">
                <h4 class="font-bold text-slate-900 dark:text-white text-base">{{ book.title }}</h4>
                <p class="text-xs text-slate-500">{{ book.pages }} Pages • Created {{ book.age }}</p>
              </div>
              <button class="size-10 rounded-full bg-primary/10 text-primary flex items-center justify-center">
                <span class="material-symbols-outlined text-xl">download</span>
              </button>
            </div>
          </div>
        </div>

        <!-- FAB -->
        <RouterLink to="/create" class="fixed bottom-28 right-6 size-16 rounded-full bg-primary text-white shadow-xl flex items-center justify-center z-50 ring-4 ring-white dark:ring-slate-900">
          <span class="material-symbols-outlined text-3xl font-bold">add</span>
        </RouterLink>

        <BottomNav />
      </div>
    </div>

    <!-- ===================== DESKTOP LAYOUT (>= lg) ===================== -->
    <div class="hidden lg:flex lg:flex-col lg:min-h-screen">
      <AppHeader />

      <div class="flex-1 max-w-[1280px] mx-auto w-full px-8 py-8 lg:px-10">
        <!-- Greeting Row -->
        <div class="flex items-center justify-between gap-6 mb-10">
          <div>
            <h1 class="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-2">Hello, Sarah! 👋</h1>
            <p class="text-slate-500 dark:text-slate-400 text-lg">Ready to spark some creativity today?</p>
          </div>
          <div class="flex items-center gap-3">
            <RouterLink to="/community" class="h-12 px-6 flex items-center justify-center rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 font-semibold hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-sm">
              View Gallery
            </RouterLink>
            <RouterLink to="/create" class="h-12 px-6 flex items-center justify-center rounded-xl bg-primary text-white font-bold shadow-lg shadow-primary/25 hover:bg-primary-dark hover:scale-[1.02] transition-all">
              <span class="material-symbols-outlined mr-2 text-[20px]">auto_fix_high</span>
              Create New Book
            </RouterLink>
          </div>
        </div>

        <!-- Main Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Left: Metrics + Chart + Recent Creations (2/3 width) -->
          <div class="lg:col-span-2 flex flex-col gap-8">
            <!-- Stats Row (3 columns) -->
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              <!-- Monthly Limit -->
              <div class="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm flex flex-col items-center justify-center relative overflow-hidden group hover:shadow-md transition-shadow">
                <div class="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                  <span class="material-symbols-outlined text-6xl text-primary">menu_book</span>
                </div>
                <h3 class="text-sm font-semibold text-slate-500 dark:text-slate-400 mb-4 w-full text-center">Monthly Limit</h3>
                <div class="relative size-24">
                  <svg viewBox="0 0 36 36" class="size-full text-primary">
                    <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" class="stroke-slate-100 dark:stroke-slate-800" stroke-width="3.8"></path>
                    <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-width="2.8" stroke-dasharray="80, 100" stroke-linecap="round"></path>
                    <text x="18" y="20.35" text-anchor="middle" class="fill-slate-900 dark:fill-white text-[0.5em] font-bold" style="font-family: 'Plus Jakarta Sans', sans-serif">8/10</text>
                  </svg>
                </div>
                <p class="mt-2 text-xs font-medium text-slate-400">2 books remaining</p>
              </div>

              <!-- Pages Printed -->
              <div class="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-4">
                  <h3 class="text-sm font-semibold text-slate-500 dark:text-slate-400">Pages Printed</h3>
                  <div class="p-2 bg-green-50 dark:bg-green-900/20 rounded-lg text-green-600">
                    <span class="material-symbols-outlined text-xl">print</span>
                  </div>
                </div>
                <div>
                  <span class="text-4xl font-bold text-slate-900 dark:text-white">142</span>
                  <span class="text-xs font-medium text-green-600 ml-2 bg-green-100 dark:bg-green-900/30 px-2 py-0.5 rounded-full">+12 this week</span>
                </div>
                <p class="text-xs text-slate-400 mt-2">Total lifetime prints</p>
              </div>

              <!-- Top Theme -->
              <div class="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow bg-gradient-to-br from-white to-purple-50/50 dark:from-slate-900 dark:to-purple-950/20">
                <div class="flex justify-between items-start mb-4">
                  <h3 class="text-sm font-semibold text-slate-500 dark:text-slate-400">Top Theme</h3>
                  <div class="p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg text-purple-600">
                    <span class="material-symbols-outlined text-xl">star</span>
                  </div>
                </div>
                <div>
                  <span class="text-2xl font-bold text-slate-900 dark:text-white break-words">Dinosaurs</span>
                  <div class="flex mt-2">
                    <span class="text-xs font-medium text-purple-600 bg-purple-100 dark:bg-purple-900/30 px-2 py-0.5 rounded-full">Used 5 times</span>
                  </div>
                </div>
                <p class="text-xs text-slate-400 mt-2">Most generated category</p>
              </div>
            </div>

            <!-- Activity History Chart -->
            <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm p-6">
              <div class="flex justify-between items-center mb-6">
                <div>
                  <h3 class="text-lg font-bold text-slate-900 dark:text-white">Activity History</h3>
                  <p class="text-sm text-slate-500">Books generated over the last 30 days</p>
                </div>
                <div class="flex items-center gap-2">
                  <span class="flex h-3 w-3 rounded-full bg-primary"></span>
                  <span class="text-xs font-medium text-slate-600 dark:text-slate-400">Generations</span>
                </div>
              </div>
              <div class="h-64 w-full relative">
                <!-- Chart grid lines -->
                <div class="absolute inset-0 flex flex-col justify-between text-xs text-slate-300">
                  <div class="border-b border-slate-50 dark:border-slate-800 w-full h-full"></div>
                  <div class="border-b border-slate-50 dark:border-slate-800 w-full h-full"></div>
                  <div class="border-b border-slate-50 dark:border-slate-800 w-full h-full"></div>
                  <div class="border-b border-slate-50 dark:border-slate-800 w-full h-full"></div>
                </div>
                <!-- SVG Chart with bezier curve -->
                <svg class="absolute inset-0 h-full w-full overflow-visible" viewBox="0 0 100 50" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="#2b6cee" stop-opacity="0.2"></stop>
                      <stop offset="100%" stop-color="#2b6cee" stop-opacity="0"></stop>
                    </linearGradient>
                  </defs>
                  <path d="M0,45 Q10,35 20,40 T40,20 T60,25 T80,10 T100,15 V50 H0 Z" fill="url(#chartGradient)"></path>
                  <path d="M0,45 Q10,35 20,40 T40,20 T60,25 T80,10 T100,15" fill="none" stroke="#2b6cee" stroke-width="0.8" stroke-linecap="round" stroke-linejoin="round"></path>
                  <circle cx="20" cy="40" r="1" class="fill-white stroke-primary stroke-[0.5]"></circle>
                  <circle cx="40" cy="20" r="1" class="fill-white stroke-primary stroke-[0.5]"></circle>
                  <circle cx="60" cy="25" r="1" class="fill-white stroke-primary stroke-[0.5]"></circle>
                  <circle cx="80" cy="10" r="1" class="fill-white stroke-primary stroke-[0.5]"></circle>
                  <circle cx="100" cy="15" r="1" class="fill-white stroke-primary stroke-[0.5]"></circle>
                </svg>
              </div>
              <div class="flex justify-between text-xs text-slate-400 mt-4 px-2">
                <span>Jul 1</span>
                <span>Jul 8</span>
                <span>Jul 15</span>
                <span>Jul 22</span>
                <span>Jul 29</span>
              </div>
            </div>

            <!-- Recent Creations -->
            <div class="flex flex-col gap-4">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-bold text-slate-900 dark:text-white">Recent Creations</h3>
                <RouterLink to="/library" class="text-sm font-semibold text-primary hover:text-primary-dark">View all</RouterLink>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                <div v-for="book in recentBooks" :key="book.title" class="group bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 overflow-hidden hover:shadow-lg transition-all duration-300">
                  <div class="aspect-[4/3] bg-slate-100 dark:bg-slate-800 relative overflow-hidden">
                    <img :src="book.img" :alt="book.title" class="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
                    <div class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors"></div>
                    <button class="absolute bottom-3 right-3 size-10 rounded-full bg-white text-primary shadow-lg translate-y-12 group-hover:translate-y-0 transition-transform duration-300 flex items-center justify-center hover:bg-primary hover:text-white">
                      <span class="material-symbols-outlined text-xl">download</span>
                    </button>
                  </div>
                  <div class="p-4">
                    <h4 class="font-bold text-slate-900 dark:text-white mb-1">{{ book.title }}</h4>
                    <p class="text-xs text-slate-500">Created {{ book.age }} · {{ book.pages }} Pages</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Sidebar (1/3 width) -->
          <div class="lg:col-span-1 space-y-6">
            <!-- Quick Stats -->
            <div class="bg-primary text-white p-6 rounded-2xl shadow-lg relative overflow-hidden">
              <div class="absolute top-[-50%] right-[-50%] w-full h-full rounded-full bg-white/10 blur-3xl"></div>
              <h3 class="text-lg font-bold mb-6 relative z-10">Quick Stats</h3>
              <div class="space-y-6 relative z-10">
                <div class="flex items-start gap-4">
                  <div class="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                    <span class="material-symbols-outlined text-xl">token</span>
                  </div>
                  <div>
                    <p class="text-white/80 text-xs font-medium uppercase tracking-wider">Credits</p>
                    <p class="text-3xl font-bold">450</p>
                    <p class="text-white/60 text-xs">Tokens remaining</p>
                  </div>
                </div>
                <div class="h-px w-full bg-white/20"></div>
                <div class="flex items-start gap-4">
                  <div class="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                    <span class="material-symbols-outlined text-xl">update</span>
                  </div>
                  <div>
                    <p class="text-white/80 text-xs font-medium uppercase tracking-wider">Next Reset</p>
                    <p class="text-xl font-bold">Aug 1, 2024</p>
                    <p class="text-white/60 text-xs">Plan renews automatically</p>
                  </div>
                </div>
              </div>
              <RouterLink to="/billing" class="mt-8 block w-full py-3 bg-white text-primary rounded-xl font-bold text-sm text-center hover:bg-slate-50 transition-colors">
                Manage Subscription
              </RouterLink>
            </div>

            <!-- Pro Tip -->
            <div class="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm">
              <div class="flex items-center gap-2 mb-4">
                <span class="material-symbols-outlined text-amber-500">lightbulb</span>
                <h3 class="font-bold text-slate-900 dark:text-white">Pro Tip</h3>
              </div>
              <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed mb-4">
                Did you know? Detailed prompts yield better results. Try adding "simple outline" or "thick lines" for younger kids!
              </p>
              <a href="#" class="text-primary text-sm font-semibold hover:underline">Read Prompt Guide →</a>
            </div>

            <!-- Notifications -->
            <div class="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm">
              <h3 class="font-bold text-slate-900 dark:text-white mb-4">Notifications</h3>
              <div class="space-y-4">
                <div v-for="notif in notifications" :key="notif.text" class="flex gap-3">
                  <div class="mt-1 min-w-[8px] h-2 w-2 rounded-full" :class="notif.text.includes('ready') ? 'bg-slate-200 dark:bg-slate-600' : 'bg-red-500'"></div>
                  <div>
                    <p class="text-sm font-medium text-slate-800 dark:text-slate-200">{{ notif.text }}</p>
                    <p class="text-xs text-slate-500 mt-1">{{ notif.time }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
