<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import CharacterForm from '@/components/CharacterForm.vue'
import AppHeader from '@/components/AppHeader.vue'

const createdCharacter = ref<any>(null)

function handleCharacterCreated(data: any) {
  createdCharacter.value = data
}

function resetForm() {
  createdCharacter.value = null
}
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 min-h-screen font-display flex flex-col">
    <AppHeader />

    <main class="flex-grow flex justify-center py-10 px-4 md:px-10">
      <div class="flex flex-col max-w-[800px] w-full gap-8">

        <!-- Header -->
        <div class="flex flex-col gap-3">
          <div class="flex items-center gap-3 mb-1">
            <RouterLink to="/dashboard" class="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-500 hover:text-primary hover:bg-primary/10 transition-colors">
              <span class="material-symbols-outlined">arrow_back</span>
            </RouterLink>
            <h1 class="text-slate-900 dark:text-white text-3xl md:text-4xl font-black leading-tight tracking-[-0.033em]">
              Add a <span class="text-transparent bg-clip-text bg-gradient-to-r from-accent-purple to-primary">Character</span>
            </h1>
          </div>
          <p class="text-slate-500 dark:text-slate-400 text-lg font-medium leading-normal max-w-lg ml-[52px]">
            Build your family tree of characters to feature in your coloring books.
          </p>
        </div>

        <!-- Success State -->
        <div v-if="createdCharacter" class="bg-white dark:bg-slate-900 rounded-[2rem] p-10 md:p-16 shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-800 flex flex-col items-center gap-8">
          <div class="flex flex-col items-center gap-4 text-center">
            <div class="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <span class="material-symbols-outlined text-green-600 text-3xl">check_circle</span>
            </div>
            <h2 class="text-3xl font-bold text-slate-900 dark:text-white">Character Created!</h2>
            <p class="text-slate-500 dark:text-slate-400 text-lg">{{ createdCharacter.name }} has been added to your library.</p>
          </div>

          <!-- Preview: original vs sketch side-by-side -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full max-w-md">
            <div class="flex flex-col items-center gap-2">
              <p class="text-xs font-bold text-slate-500 uppercase tracking-wider">Original</p>
              <div class="w-40 h-40 rounded-2xl overflow-hidden border-2 border-slate-200 dark:border-slate-700 shadow-md">
                <img :src="createdCharacter.original_url" alt="Original" class="w-full h-full object-cover" />
              </div>
            </div>
            <div class="flex flex-col items-center gap-2">
              <p class="text-xs font-bold text-slate-500 uppercase tracking-wider">Sketch</p>
              <div class="w-40 h-40 rounded-2xl overflow-hidden border-2 border-primary/30 shadow-md">
                <img :src="createdCharacter.sketch_url" alt="Sketch" class="w-full h-full object-cover" />
              </div>
            </div>
          </div>

          <div class="flex flex-col sm:flex-row items-center gap-4">
            <button
              @click="resetForm"
              class="px-6 py-3 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors text-sm"
            >
              Add Another Character
            </button>
            <RouterLink
              to="/dashboard"
              class="px-6 py-3 rounded-full bg-gradient-to-r from-primary to-accent-purple hover:from-primary-dark hover:to-primary text-white font-bold transition-all shadow-lg shadow-primary/20 text-sm"
            >
              Back to Dashboard
            </RouterLink>
          </div>
        </div>

        <!-- Form Container -->
        <div v-else class="bg-white dark:bg-slate-900 rounded-[2rem] p-6 md:p-10 shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-800 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-primary via-purple-400 to-accent-pink"></div>
          <CharacterForm @character-created="handleCharacterCreated" />
        </div>

      </div>
    </main>
  </div>
</template>
