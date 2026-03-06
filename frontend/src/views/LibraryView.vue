<script setup lang="ts">
import { onMounted } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { RouterLink } from 'vue-router'
import { useBooksStore } from '@/stores/books'

const store = useBooksStore()

const THEME_ICONS: Record<string, string> = {
  animals: 'pets',
  dinosaur: 'forest',
  fantasy: 'star',
  space: 'rocket_launch',
  ocean: 'water_drop',
  nature: 'eco',
  vehicles: 'directions_car',
}

const THEME_COLORS: Record<string, string> = {
  animals: 'text-orange-600',
  dinosaur: 'text-green-600',
  fantasy: 'text-purple-500',
  space: 'text-primary',
  ocean: 'text-blue-500',
  nature: 'text-emerald-500',
  vehicles: 'text-amber-600',
}

function themeIcon(theme: string): string {
  return THEME_ICONS[theme] ?? 'auto_stories'
}

function themeColor(theme: string): string {
  return THEME_COLORS[theme] ?? 'text-slate-500'
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return dateStr
  }
}

onMounted(() => {
  store.fetchBooks()
})
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

      <!-- Loading State -->
      <div v-if="store.loading" class="flex flex-col items-center justify-center py-24 gap-4">
        <div class="w-12 h-12 rounded-full border-4 border-slate-200 dark:border-slate-700 border-t-primary animate-spin"></div>
        <p class="text-slate-500 dark:text-slate-400 font-medium">Loading your books...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="store.error" class="flex flex-col items-center justify-center py-24 gap-4 text-center">
        <div class="w-14 h-14 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
          <span class="material-symbols-outlined text-red-500 text-2xl">error</span>
        </div>
        <p class="text-slate-700 dark:text-slate-300 font-semibold">{{ store.error }}</p>
        <button @click="store.fetchBooks()" class="px-6 py-2.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-full text-sm font-bold text-slate-700 dark:text-slate-300 transition-colors">
          Try Again
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="store.books.length === 0" class="flex flex-col items-center justify-center py-24 gap-6 text-center">
        <div class="w-20 h-20 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
          <span class="material-symbols-outlined text-4xl text-slate-400">menu_book</span>
        </div>
        <div>
          <h3 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">No books yet</h3>
          <p class="text-slate-500 dark:text-slate-400 text-lg">Create your first one!</p>
        </div>
        <RouterLink to="/create" class="px-8 py-3.5 bg-gradient-to-r from-primary to-accent-purple hover:from-primary-dark hover:to-primary rounded-full text-white font-bold shadow-lg shadow-primary/20 transition-all active:scale-95 flex items-center gap-2">
          <span class="material-symbols-outlined">add</span>
          Create Your First Book
        </RouterLink>
      </div>

      <!-- Books Grid -->
      <template v-else>
        <!-- Search & Filters -->
        <div class="flex flex-col md:flex-row gap-4 mb-8 items-center bg-white dark:bg-slate-900 p-2 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
          <div class="relative flex-grow w-full md:w-auto">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
              <span class="material-symbols-outlined">search</span>
            </div>
            <input
              class="w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-slate-800/50 border-transparent focus:border-primary focus:ring-0 rounded-xl text-slate-900 dark:text-slate-100 placeholder-slate-400 font-medium transition-all"
              placeholder="Search by book title"
              type="text"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <!-- Book Cards -->
          <div
            v-for="book in store.books"
            :key="book.book_id"
            class="group relative bg-white dark:bg-slate-900 rounded-2xl p-4 shadow-sm hover:shadow-xl hover:shadow-primary/10 border border-slate-100 dark:border-slate-800 transition-all duration-300 flex flex-col"
          >
            <div class="relative w-full aspect-[3/4] rounded-xl overflow-hidden mb-4 bg-slate-100 dark:bg-slate-800">
              <img
                v-if="book.page_urls.length"
                :alt="book.title"
                :src="book.page_urls[0]"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <span class="material-symbols-outlined text-5xl text-slate-300 dark:text-slate-600">auto_stories</span>
              </div>
              <div class="absolute top-3 right-3 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm p-1.5 rounded-lg shadow-sm" :class="themeColor(book.theme)">
                <span class="material-symbols-outlined text-[20px]">{{ themeIcon(book.theme) }}</span>
              </div>
            </div>
            <div class="flex-grow">
              <h3 class="text-lg font-bold text-slate-900 dark:text-white line-clamp-1 group-hover:text-primary transition-colors">{{ book.title }}</h3>
              <div class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-4 flex-wrap">
                <span class="capitalize">{{ book.theme }}</span>
                <span class="w-1 h-1 rounded-full bg-slate-300"></span>
                <span>{{ book.age_range }} yrs</span>
                <span class="w-1 h-1 rounded-full bg-slate-300"></span>
                <span>{{ formatDate(book.created_at) }}</span>
              </div>
            </div>
            <div class="flex gap-2 mt-auto pt-4 border-t border-slate-100 dark:border-slate-800/50">
              <a
                v-if="book.pdf_url"
                :href="book.pdf_url"
                target="_blank"
                rel="noopener"
                class="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-primary/10 hover:bg-primary/20 text-primary text-sm font-bold transition-colors"
              >
                <span class="material-symbols-outlined text-[18px]">download</span>
                Download
              </a>
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
      </template>
    </main>

    <AppFooter />
  </div>
</template>
