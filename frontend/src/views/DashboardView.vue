<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProfilesStore } from '@/stores/profiles'
import { useDashboard } from '@/composables/useDashboard'

import AppHeader from '@/components/AppHeader.vue'

const router = useRouter()
const authStore = useAuthStore()
const profilesStore = useProfilesStore()

// We get our reactive data payload and the fetch function from the composable
const { data: dashboard, fetchDashboard } = useDashboard()

// Hardcoded updates to show as part of notifications
const updates = [
  { text: "📸 Photo-to-book mode coming soon!", subtext: "Turn event photos into coloring books" },
  { text: "🎨 New complexity tiers available", subtext: "Books now adapt to your child's age" },
  { text: "⚡ Faster generation", subtext: "Books now generate 40% faster" }
]

// Determine which Pro Tip to show based on day of month
const proTips = [
  "Add your child's name and age for a more personalized story and characters.",
  "The more specific your theme, the better the results. Try 'underwater adventure with a clownfish' instead of just 'ocean'.",
  "Books with 6-8 pages generate fastest. Longer books take 3-5 minutes.",
  "Ages 4-6 get simpler line art. Ages 8+ get more detailed scenes.",
  "Try themes your child is currently obsessed with — dinosaurs, unicorns, superheroes, space."
]
const tipIndex = new Date().getDate() % proTips.length
const currentProTip = proTips[tipIndex]

const firstName = computed(() => {
  if (!authStore.displayName) return 'Friend'
  return authStore.displayName.split(' ')[0]
})

function navigateToCreate() {
  if (dashboard.value.isAtLimit) {
    router.push('/pricing')
  } else {
    router.push('/create')
  }
}

function getInitials(title: string) {
  return title.slice(0, 2).toUpperCase()
}
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 min-h-screen font-display flex flex-col">
    <AppHeader />
    
    <div class="flex-1 max-w-[1280px] mx-auto w-full px-4 py-8 lg:px-10 flex flex-col lg:flex-row gap-8">
      
      <!-- LEFT COLUMN (grows) -->
      <div class="flex-1 flex flex-col gap-8">
        
        <!-- A) Hero greeting -->
        <header>
          <h1 class="text-3xl lg:text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-2">
            Hello, {{ firstName }}! 👋
          </h1>
          <p class="text-slate-600 dark:text-slate-400 text-lg sm:text-xl font-medium">
            {{ dashboard.tierLabel }} Plan · {{ dashboard.booksRemaining }} {{ dashboard.booksRemaining === 1 ? 'book' : 'books' }} remaining
          </p>
        </header>

        <!-- Active Child Profile -->
        <div v-if="profilesStore.activeProfile" class="flex items-center gap-3 px-5 py-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm">
          <div
            class="size-9 rounded-full flex items-center justify-center text-white text-sm font-bold shrink-0"
            :style="{ backgroundColor: profilesStore.activeProfile.avatar_color }"
          >
            {{ profilesStore.activeProfile.name.charAt(0).toUpperCase() }}
          </div>
          <div class="flex flex-col">
            <span class="text-sm font-bold text-slate-900 dark:text-white">{{ profilesStore.activeProfile.name }}</span>
            <span class="text-xs text-slate-500 dark:text-slate-400">{{ profilesStore.activeProfile.age }} years old</span>
          </div>
          <RouterLink to="/profiles" class="ml-auto flex items-center gap-1 text-xs font-bold text-primary hover:underline">
            <span class="material-symbols-outlined text-sm">swap_horiz</span>
            Switch Child
          </RouterLink>
        </div>
        <RouterLink v-else-if="!profilesStore.isLoading && profilesStore.profiles.length === 0" to="/profiles/add" class="flex items-center gap-3 px-5 py-3 rounded-xl border-2 border-dashed border-primary/30 hover:border-primary/60 bg-primary/5 transition-colors">
          <span class="material-symbols-outlined text-primary">person_add</span>
          <span class="text-sm font-semibold text-primary">Add a child profile to personalize books</span>
        </RouterLink>

        <!-- B) Three stat cards (3-col grid) -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <!-- Card 1: Books Used -->
          <div class="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col justify-center">
            <p class="text-sm font-semibold text-slate-500 mb-1 uppercase tracking-wider">Books Used</p>
            <p class="text-3xl font-bold text-slate-900 dark:text-white mb-1">
              <span v-if="dashboard.subscriptionTier === 'free'">{{ dashboard.booksGeneratedTotal }} / 1</span>
              <span v-else>{{ dashboard.booksGeneratedThisMonth }} / {{ dashboard.monthlyLimit }}</span>
            </p>
            <p class="text-xs font-semibold text-slate-400">
              <span v-if="dashboard.subscriptionTier === 'free'">(lifetime)</span>
              <span v-else>this month</span>
            </p>
          </div>

          <!-- Card 2: Recent Activity -->
          <div class="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col justify-center">
            <p class="text-sm font-semibold text-slate-500 mb-1 uppercase tracking-wider">Recent Activity</p>
            <p v-if="dashboard.booksGeneratedTotal > 0" class="text-3xl font-bold text-slate-900 dark:text-white mb-1">
              {{ dashboard.booksGeneratedTotal }}
            </p>
            <p v-if="dashboard.booksGeneratedTotal > 0" class="text-xs font-semibold text-slate-400">
              books created
            </p>
            <p v-else class="text-slate-600 dark:text-slate-400 text-sm font-medium mt-1">
              No books yet — create your first!
            </p>
          </div>

          <!-- Card 3: Favorite Theme -->
          <div class="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col justify-center">
            <p class="text-sm font-semibold text-slate-500 mb-1 uppercase tracking-wider">Favorite Theme</p>
            <p class="text-2xl font-bold text-slate-900 dark:text-white mb-1 truncate capitalize">
              {{ dashboard.topTheme || "—" }}
            </p>
            <p class="text-xs font-semibold text-slate-400">
              <span v-if="dashboard.topThemeCount > 0">Used {{ dashboard.topThemeCount }} time(s)</span>
              <span v-else>Create a book to see</span>
            </p>
          </div>
        </div>

        <!-- C) Recent Creations section -->
        <section class="mt-4">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Your Books</h2>
          </div>
          
          <div v-if="dashboard.loading" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
            <!-- Skeleton cards -->
            <div v-for="i in 3" :key="i" class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-4">
              <div class="aspect-[4/3] bg-slate-200 dark:bg-slate-700 rounded-xl mb-4 animate-pulse"></div>
              <div class="h-6 w-3/4 bg-slate-200 dark:bg-slate-700 rounded mb-2 animate-pulse"></div>
              <div class="h-4 w-1/2 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
            </div>
          </div>
          
          <div v-else-if="dashboard.recentBooks.length === 0" class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-10 flex flex-col items-center justify-center text-center">
            <span class="text-4xl mb-4">✨</span>
            <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-2">No books yet</h3>
            <p class="text-slate-500 dark:text-slate-400 mb-6 max-w-sm">
              Your personalized coloring books will appear here once you create one.
            </p>
            <button @click="navigateToCreate()" class="h-12 px-6 rounded-full bg-primary text-white font-bold transition-transform hover:scale-105 shadow-md hover:shadow-lg">
              Create Your First Book →
            </button>
          </div>
          
          <div v-else class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
            <!-- Book cards -->
            <div v-for="book in dashboard.recentBooks" :key="book.id" class="flex flex-col bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
              
              <div class="aspect-[4/3] relative bg-slate-100 dark:bg-slate-900 overflow-hidden flex items-center justify-center">
                <!-- Cover Image or Fallback -->
                <img v-if="book.cover_url" :src="book.cover_url" :alt="book.title" class="w-full h-full object-cover" />
                <div v-else class="text-6xl flex items-center justify-center">
                  📚
                </div>
                <!-- Theme Badge -->
                <div class="absolute top-3 right-3 px-2 py-1 bg-white/90 backdrop-blur text-xs font-bold text-slate-700 rounded-md capitalize shadow-sm">
                  {{ book.theme }}
                </div>
              </div>
              
              <div class="p-5 flex-1 flex flex-col">
                <h3 class="text-lg font-bold text-slate-900 dark:text-white mb-1 line-clamp-1" :title="book.title">{{ book.title }}</h3>
                <div class="flex items-center text-xs text-slate-500 dark:text-slate-400 font-medium mb-4 gap-1.5">
                  <span class="material-symbols-outlined text-[14px]">description</span>
                  <span>{{ book.page_count }} pages</span>
                  <span>•</span>
                  <span>{{ new Date(book.created_at.seconds * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}</span>
                </div>
                
                <div class="mt-auto grid grid-cols-2 gap-3">
                  <a v-if="book.pdf_url" :href="book.pdf_url" target="_blank" rel="noopener noreferrer" class="flex items-center justify-center gap-1.5 h-10 rounded-xl bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 text-sm font-bold hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors">
                    <span class="material-symbols-outlined text-[18px]">download</span>
                    PDF
                  </a>
                  <button v-else disabled class="flex items-center justify-center gap-1.5 h-10 rounded-xl bg-slate-50 dark:bg-slate-800 text-slate-400 dark:text-slate-500 text-sm font-bold cursor-not-allowed group relative" title="PDF not available">
                    <span class="material-symbols-outlined text-[18px]">download</span>
                    PDF
                  </button>
                  <RouterLink :to="'/library'" class="flex items-center justify-center h-10 rounded-xl border border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-200 text-sm font-bold hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                    Details
                  </RouterLink>
                </div>
              </div>
            </div>
          </div>
        </section>
        
      </div>


      <!-- RIGHT COLUMN (fixed width on desktop) -->
      <div class="w-full lg:w-80 flex-shrink-0 flex flex-col gap-6">
        
        <!-- D) Quick Stats Card -->
        <div class="bg-sky-600 rounded-2xl p-6 text-white shadow-lg overflow-hidden relative">
          <!-- Decorative shapes -->
          <div class="absolute -top-10 -right-10 w-32 h-32 bg-sky-400 rounded-full opacity-30 blur-2xl"></div>
          <div class="absolute -bottom-10 -left-10 w-32 h-32 bg-sky-800 rounded-full opacity-30 blur-2xl"></div>
          
          <div class="relative z-10">
            <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
              <span>📚</span> Your Plan
            </h3>
            
            <div class="flex items-end justify-between mb-4">
              <div>
                <p class="text-sky-100 text-sm uppercase tracking-wider font-semibold mb-1">Tier</p>
                <p class="text-2xl font-bold">{{ dashboard.tierLabel }}</p>
              </div>
              <div class="text-right">
                <p class="text-sky-100 text-sm uppercase tracking-wider font-semibold mb-1">Remaining</p>
                <p class="text-2xl font-bold">{{ dashboard.booksRemaining }}</p>
              </div>
            </div>
            
            <div class="mb-6">
              <p v-if="dashboard.subscriptionTier !== 'free' && dashboard.subscriptionActive" class="text-sky-100 text-sm font-medium">
                Resets {{ dashboard.nextResetDate }}
              </p>
              <p v-else-if="dashboard.subscriptionTier === 'free' && !dashboard.isAtLimit" class="text-sky-100 text-sm font-medium">
                1 free book available<br/>No credit card needed
              </p>
              
              <div v-if="dashboard.isAtLimit" class="mt-3 bg-red-500/20 border border-red-500/30 rounded-xl py-2 px-3 text-red-100 text-sm font-bold flex items-center gap-2">
                <span class="material-symbols-outlined text-[16px]">info</span>
                You've used your quota!
              </div>
            </div>
            
            <div class="flex flex-col gap-3">
              <button @click="navigateToCreate()" class="w-full h-12 flex items-center justify-center rounded-xl font-bold transition-colors" :class="dashboard.isAtLimit ? 'bg-white/20 text-white cursor-not-allowed' : 'bg-white text-sky-700 hover:bg-sky-50'">
                {{ dashboard.isAtLimit ? 'Upgrade to create more' : 'Create New Book →' }}
              </button>
              
              <button v-if="dashboard.isAtLimit" @click="router.push('/pricing')" class="w-full h-12 flex items-center justify-center rounded-xl bg-white text-sky-700 font-bold hover:bg-sky-50 transition-colors">
                Upgrade Plan
              </button>
            </div>
          </div>
        </div>

        <!-- E) Pro Tip Card -->
        <div class="bg-white dark:bg-slate-800 border border-amber-100 dark:border-amber-900/30 rounded-2xl p-6 shadow-sm">
          <div class="flex items-center gap-2 mb-3 text-amber-500">
            <span class="material-symbols-outlined bg-amber-100 dark:bg-amber-900/40 p-1.5 rounded-lg text-[20px]">lightbulb</span>
            <h3 class="font-bold text-slate-900 dark:text-white">Pro Tip</h3>
          </div>
          <p class="text-sm text-slate-600 dark:text-slate-400 font-medium leading-relaxed">
            {{ currentProTip }}
          </p>
        </div>

        <!-- F) Custom Characters card -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col">
          <div class="flex items-center justify-between mb-5">
            <h3 class="font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <span class="material-symbols-outlined text-primary">face</span>
              Your Characters
            </h3>
            <RouterLink to="/characters/add" class="text-xs font-bold text-primary hover:text-primary-dark hover:underline flex items-center">
              Add New
              <span class="material-symbols-outlined text-[14px]">add</span>
            </RouterLink>
          </div>
          
          <div v-if="dashboard.customCharacters.length === 0" class="text-center py-6 text-slate-500 text-sm">
            <p>No characters yet.</p>
            <p>Add some to feature them in your books!</p>
          </div>
          
          <div v-else class="grid grid-cols-2 gap-3">
            <div v-for="char in dashboard.customCharacters.slice(0, 4)" :key="char.character_id" class="flex flex-col gap-1.5 items-center">
              <div class="w-16 h-16 rounded-full overflow-hidden border-2 border-slate-100 dark:border-slate-700">
                <img :src="char.sketch_url || char.original_url" class="w-full h-full object-cover" />
              </div>
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 truncate w-full text-center" :title="char.name">{{ char.name }}</span>
              <span v-if="char.relationship" class="text-[10px] font-medium text-slate-400 capitalize">{{ char.relationship }}</span>
            </div>
          </div>
        </div>

        <!-- G) Library Stats card -->
        <div v-if="dashboard.libraryStats" class="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col">
          <h3 class="font-bold text-slate-900 dark:text-white flex items-center gap-2 mb-4">
            <span class="material-symbols-outlined text-green-500">library_books</span>
            Image Library
          </h3>
          <div class="flex flex-col gap-3">
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500 font-medium">Available Images</span>
              <span class="text-sm font-bold text-slate-900 dark:text-white">{{ dashboard.libraryStats.totalImages.toLocaleString() }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500 font-medium">Cache Hit Rate</span>
              <span class="text-sm font-bold" :class="dashboard.libraryStats.hitRate > 50 ? 'text-green-600' : 'text-slate-900 dark:text-white'">{{ dashboard.libraryStats.hitRate }}%</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500 font-medium">Est. Savings</span>
              <span class="text-sm font-bold text-green-600">${{ dashboard.libraryStats.estimatedSavings.toFixed(2) }}</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  </div>
</template>
