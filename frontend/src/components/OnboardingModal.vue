<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const emit = defineEmits<{ close: [] }>()
const router = useRouter()
const selected = ref<string | null>(null)

const themes = [
  { id: 'animals', label: 'Animals', icon: 'pets', color: 'bg-orange-100 text-orange-600' },
  { id: 'dinosaurs', label: 'Dinosaurs', icon: 'forest', color: 'bg-green-100 text-green-600' },
  { id: 'unicorns', label: 'Unicorns', icon: 'star', color: 'bg-purple-100 text-purple-600' },
  { id: 'space', label: 'Space', icon: 'rocket_launch', color: 'bg-blue-100 text-blue-600' },
  { id: 'ocean', label: 'Ocean', icon: 'water', color: 'bg-cyan-100 text-cyan-600' },
  { id: 'nature', label: 'Nature', icon: 'eco', color: 'bg-emerald-100 text-emerald-600' },
  { id: 'vehicles', label: 'Vehicles', icon: 'directions_car', color: 'bg-red-100 text-red-600' },
]

function handleSelect(themeId: string) {
  selected.value = themeId
}

function handleContinue() {
  localStorage.setItem('tm_onboarding_done', '1')
  if (selected.value) {
    router.push({ path: '/create', query: { theme: selected.value } })
  }
  emit('close')
}

function handleSkip() {
  localStorage.setItem('tm_onboarding_done', '1')
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="handleSkip"></div>

      <!-- Modal -->
      <div class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
        <!-- Header gradient -->
        <div class="h-2 w-full bg-gradient-to-r from-primary via-blue-400 to-accent-purple"></div>

        <div class="p-6 md:p-8">
          <!-- Logo + Welcome -->
          <div class="text-center mb-6">
            <img src="/logo3.png" alt="TailorMade" class="h-12 w-auto mx-auto mb-4 dark:hidden" />
            <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">Welcome to TailorMade!</h2>
            <p class="text-slate-500 dark:text-slate-400 text-sm">Pick a theme to get started with your first coloring book.</p>
          </div>

          <!-- Theme grid -->
          <div class="grid grid-cols-3 sm:grid-cols-4 gap-3 mb-6">
            <button
              v-for="t in themes"
              :key="t.id"
              @click="handleSelect(t.id)"
              class="flex flex-col items-center gap-2 p-3 rounded-xl border-2 transition-all hover:scale-105"
              :class="selected === t.id ? 'border-primary bg-primary/5 shadow-md' : 'border-slate-100 dark:border-slate-700 hover:border-primary/40'"
            >
              <div class="size-10 rounded-full flex items-center justify-center" :class="t.color">
                <span class="material-symbols-outlined text-xl">{{ t.icon }}</span>
              </div>
              <span class="text-xs font-bold text-slate-700 dark:text-slate-200">{{ t.label }}</span>
            </button>
          </div>

          <!-- Actions -->
          <div class="flex flex-col gap-3">
            <button
              @click="handleContinue"
              :disabled="!selected"
              class="w-full h-12 rounded-full bg-primary text-white font-bold text-sm shadow-lg shadow-primary/25 hover:bg-primary-dark transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <span class="material-symbols-outlined text-lg">auto_fix_high</span>
              Create My First Book
            </button>
            <button
              @click="handleSkip"
              class="w-full py-2 text-sm font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
            >
              Skip for now
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
