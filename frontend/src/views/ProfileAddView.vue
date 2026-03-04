<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

function handleSave() {
  router.push('/profiles')
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
        <!-- Modal Header -->
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

        <!-- Modal Body -->
        <div class="p-8 space-y-8">
          <!-- Name & Age -->
          <div class="flex flex-col md:flex-row gap-6">
            <label class="flex flex-col flex-1 gap-2">
              <span class="text-sm font-semibold text-slate-700 dark:text-slate-300">Child's Name</span>
              <input class="w-full rounded-xl border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-4 py-3 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:border-primary focus:ring-primary focus:ring-1 transition-all" placeholder="e.g. Charlie" type="text" />
            </label>
            <label class="flex flex-col w-full md:w-1/3 gap-2">
              <span class="text-sm font-semibold text-slate-700 dark:text-slate-300">Age</span>
              <select class="w-full rounded-xl border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-4 py-3 text-slate-900 dark:text-slate-100 focus:border-primary focus:ring-primary focus:ring-1 transition-all">
                <option disabled selected value="">Select Age</option>
                <option value="2">2 years old</option>
                <option value="3">3 years old</option>
                <option value="4">4 years old</option>
                <option value="5">5 years old</option>
                <option value="6">6 years old</option>
                <option value="7">7 years old</option>
                <option value="8+">8+ years old</option>
              </select>
            </label>
          </div>

          <!-- Favorite Theme -->
          <div class="flex flex-col gap-3">
            <span class="text-sm font-semibold text-slate-700 dark:text-slate-300">Favorite Theme</span>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <label class="cursor-pointer">
                <input class="peer sr-only" name="theme" type="radio" value="dinos" />
                <div class="flex flex-col items-center justify-center gap-3 p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 peer-checked:border-primary peer-checked:bg-primary/5 peer-checked:ring-1 peer-checked:ring-primary transition-all hover:bg-slate-50 dark:hover:bg-slate-700">
                  <div class="size-12 rounded-full bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 flex items-center justify-center">
                    <span class="material-symbols-outlined text-2xl">pest_control</span>
                  </div>
                  <span class="font-medium text-slate-700 dark:text-slate-200">Dinosaurs</span>
                </div>
              </label>
              <label class="cursor-pointer">
                <input checked class="peer sr-only" name="theme" type="radio" value="space" />
                <div class="flex flex-col items-center justify-center gap-3 p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 peer-checked:border-primary peer-checked:bg-primary/5 peer-checked:ring-1 peer-checked:ring-primary transition-all hover:bg-slate-50 dark:hover:bg-slate-700">
                  <div class="size-12 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center">
                    <span class="material-symbols-outlined text-2xl">rocket_launch</span>
                  </div>
                  <span class="font-medium text-slate-700 dark:text-slate-200">Space</span>
                </div>
              </label>
              <label class="cursor-pointer">
                <input class="peer sr-only" name="theme" type="radio" value="unicorns" />
                <div class="flex flex-col items-center justify-center gap-3 p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 peer-checked:border-primary peer-checked:bg-primary/5 peer-checked:ring-1 peer-checked:ring-primary transition-all hover:bg-slate-50 dark:hover:bg-slate-700">
                  <div class="size-12 rounded-full bg-pink-100 dark:bg-pink-900/30 text-pink-600 dark:text-pink-400 flex items-center justify-center">
                    <span class="material-symbols-outlined text-2xl">auto_fix</span>
                  </div>
                  <span class="font-medium text-slate-700 dark:text-slate-200">Fantasy</span>
                </div>
              </label>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="p-6 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20 flex items-center justify-end gap-4 rounded-b-2xl">
          <button @click="handleCancel" class="px-6 py-3 rounded-xl text-slate-600 dark:text-slate-300 font-bold hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
            Cancel
          </button>
          <button @click="handleSave" class="px-8 py-3 rounded-xl bg-primary hover:bg-blue-600 text-white font-bold shadow-lg shadow-blue-500/30 transition-all transform hover:-translate-y-0.5 active:translate-y-0">
            Save Profile
          </button>
        </div>
      </div>
    </main>
  </div>
</template>
