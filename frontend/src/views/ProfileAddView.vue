<script setup lang="ts">
import { ref, computed } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { useRouter } from 'vue-router'
import { useProfilesStore } from '@/stores/profiles'
import { useFormValidation } from '@/composables/useFormValidation'
import { profileSchema } from '@/validation/schemas'

const router = useRouter()
const profilesStore = useProfilesStore()
const { errors, validate, clearErrors } = useFormValidation(profileSchema)

const childName = ref('')
const age = ref(6)
const selectedThemes = ref<string[]>([])
const isSubmitting = ref(false)
const submitError = ref<string | null>(null)

const THEME_OPTIONS = [
  { value: 'animals',    label: 'Animals',    icon: 'pets',           color: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400' },
  { value: 'dinosaur',   label: 'Dinosaurs',  icon: 'forest',         color: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' },
  { value: 'space',      label: 'Space',      icon: 'rocket_launch',  color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' },
  { value: 'fantasy',    label: 'Fantasy',    icon: 'auto_fix',       color: 'bg-pink-100 text-pink-600 dark:bg-pink-900/30 dark:text-pink-400' },
  { value: 'ocean',      label: 'Ocean',      icon: 'water',          color: 'bg-cyan-100 text-cyan-600 dark:bg-cyan-900/30 dark:text-cyan-400' },
  { value: 'vehicles',   label: 'Vehicles',   icon: 'directions_car', color: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400' },
  { value: 'nature',     label: 'Nature',     icon: 'eco',            color: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400' },
  { value: 'farm',       label: 'Farm',       icon: 'agriculture',    color: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400' },
  { value: 'unicorns',   label: 'Unicorns',   icon: 'star',           color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400' },
  { value: 'princesses', label: 'Princesses', icon: 'castle',         color: 'bg-fuchsia-100 text-fuchsia-600 dark:bg-fuchsia-900/30 dark:text-fuchsia-400' },
]

function toggleTheme(value: string) {
  const idx = selectedThemes.value.indexOf(value)
  if (idx >= 0) {
    selectedThemes.value.splice(idx, 1)
  } else if (selectedThemes.value.length < 3) {
    selectedThemes.value.push(value)
  }
}

const formData = computed(() => ({
  name: childName.value.trim(),
  age: age.value,
  favorite_themes: selectedThemes.value,
}))

async function handleSave() {
  clearErrors()
  submitError.value = null

  if (!validate(formData.value)) return

  isSubmitting.value = true
  try {
    await profilesStore.createProfile(formData.value)
    router.push('/profiles')
  } catch (e: any) {
    submitError.value = e?.body?.detail || 'Failed to create profile. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}

function handleCancel() {
  router.push('/profiles')
}
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-1 flex items-start justify-center py-10 px-4">
      <div class="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-2xl flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20 rounded-t-2xl">
          <div class="flex items-center gap-3">
            <div class="size-10 bg-primary/10 rounded-full flex items-center justify-center text-primary">
              <span class="material-symbols-outlined">sentiment_very_satisfied</span>
            </div>
            <div>
              <h2 class="text-xl font-bold text-slate-900 dark:text-white">Add New Adventurer!</h2>
              <p class="text-sm text-slate-500 dark:text-slate-400">Create a profile for your little artist.</p>
            </div>
          </div>
          <button @click="handleCancel" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <!-- Body -->
        <div class="p-8 space-y-8">
          <!-- Name -->
          <label class="flex flex-col gap-2">
            <span class="text-sm font-semibold text-slate-700 dark:text-slate-300">Child's Name</span>
            <div class="relative group">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-primary transition-colors">
                <span class="material-symbols-outlined">face</span>
              </div>
              <input
                v-model="childName"
                type="text"
                placeholder="e.g. Leo"
                class="w-full rounded-xl border bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white h-14 pl-12 pr-4 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-slate-400"
                :class="errors.name ? 'border-red-400 dark:border-red-500' : 'border-slate-200 dark:border-slate-700'"
              />
            </div>
            <span v-if="errors.name" class="text-xs text-red-500">{{ errors.name }}</span>
          </label>

          <!-- Age Slider -->
          <div class="flex flex-col gap-3">
            <div class="flex items-center justify-between">
              <span class="text-sm font-semibold text-slate-700 dark:text-slate-300">Age</span>
              <span class="text-2xl font-bold text-primary">{{ age }}</span>
            </div>
            <input
              v-model.number="age"
              type="range"
              min="2"
              max="12"
              step="1"
              class="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <div class="flex justify-between text-xs text-slate-400 font-medium px-1">
              <span>2</span>
              <span>4</span>
              <span>6</span>
              <span>8</span>
              <span>10</span>
              <span>12</span>
            </div>
            <span v-if="errors.age" class="text-xs text-red-500">{{ errors.age }}</span>
          </div>

          <!-- Favorite Themes (pick up to 3) -->
          <div class="flex flex-col gap-3">
            <div class="flex items-center justify-between">
              <span class="text-sm font-semibold text-slate-700 dark:text-slate-300">Favorite Themes</span>
              <span class="text-xs font-medium text-slate-400">{{ selectedThemes.length }}/3 selected</span>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
              <button
                v-for="t in THEME_OPTIONS"
                :key="t.value"
                type="button"
                @click="toggleTheme(t.value)"
                class="flex flex-col items-center gap-2 p-3 rounded-xl border-2 transition-all hover:shadow-sm"
                :class="selectedThemes.includes(t.value)
                  ? 'border-primary bg-primary/5 ring-1 ring-primary/20'
                  : selectedThemes.length >= 3
                    ? 'border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 opacity-40 cursor-not-allowed'
                    : 'border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-primary/50'"
              >
                <div class="size-10 rounded-full flex items-center justify-center" :class="t.color">
                  <span class="material-symbols-outlined text-xl">{{ t.icon }}</span>
                </div>
                <span class="text-xs font-semibold text-slate-700 dark:text-slate-200">{{ t.label }}</span>
                <span
                  v-if="selectedThemes.includes(t.value)"
                  class="text-primary"
                >
                  <span class="material-symbols-outlined text-lg">check_circle</span>
                </span>
              </button>
            </div>
            <span v-if="errors.favorite_themes" class="text-xs text-red-500">{{ errors.favorite_themes }}</span>
          </div>

          <!-- Submit Error -->
          <div v-if="submitError" class="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 text-sm font-semibold flex items-center gap-2">
            <span class="material-symbols-outlined text-sm">warning</span>
            {{ submitError }}
          </div>
        </div>

        <!-- Footer -->
        <div class="p-6 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20 flex items-center justify-end gap-4 rounded-b-2xl">
          <button @click="handleCancel" class="px-6 py-3 rounded-xl text-slate-600 dark:text-slate-300 font-bold hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
            Cancel
          </button>
          <button
            @click="handleSave"
            :disabled="isSubmitting"
            class="px-8 py-3 rounded-xl bg-primary hover:bg-blue-600 text-white font-bold shadow-lg shadow-blue-500/30 transition-all transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <span v-if="isSubmitting" class="material-symbols-outlined text-lg animate-spin">progress_activity</span>
            <span>{{ isSubmitting ? 'Saving...' : 'Save Profile' }}</span>
          </button>
        </div>
      </div>
    </main>
  </div>
</template>
