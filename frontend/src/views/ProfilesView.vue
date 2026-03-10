<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import { useProfilesStore } from '@/stores/profiles'
import { RouterLink } from 'vue-router'

const router = useRouter()
const profilesStore = useProfilesStore()
const deletingId = ref<string | null>(null)
const deleteError = ref<string | null>(null)

function selectProfile(profileId: string) {
  profilesStore.setActiveProfile(profileId)
  profilesStore.setDefault(profileId)
  router.push('/dashboard')
}

async function handleDelete(profileId: string) {
  deleteError.value = null
  deletingId.value = profileId
  try {
    await profilesStore.deleteProfile(profileId)
  } catch (e: any) {
    deleteError.value = e?.body?.detail || 'Failed to delete profile'
  } finally {
    deletingId.value = null
  }
}

function getInitial(name: string) {
  return name.charAt(0).toUpperCase()
}
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-1 flex justify-center py-10 px-6 sm:px-10">
      <div class="w-full max-w-[1024px] flex flex-col gap-8">
        <!-- Header -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div class="flex flex-col gap-2 max-w-2xl">
            <h1 class="text-slate-900 dark:text-white text-4xl md:text-5xl font-extrabold leading-tight tracking-tight">
              Child Profiles
            </h1>
            <p class="text-slate-600 dark:text-slate-400 text-lg font-normal leading-relaxed">
              Create profiles for your little artists. Tap a profile to set it as active.
            </p>
          </div>
          <RouterLink
            v-if="profilesStore.profiles.length < 5"
            to="/profiles/add"
            class="group flex items-center justify-center gap-3 h-14 px-8 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-full font-bold text-base shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300"
          >
            <span class="material-symbols-outlined group-hover:rotate-90 transition-transform duration-300">add</span>
            <span>Add Child</span>
          </RouterLink>
        </div>

        <!-- Error -->
        <div v-if="deleteError" class="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 text-sm font-semibold flex items-center gap-2">
          <span class="material-symbols-outlined text-sm">warning</span>
          {{ deleteError }}
        </div>

        <!-- Loading -->
        <div v-if="profilesStore.isLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-4">
          <div v-for="i in 3" :key="i" class="rounded-2xl p-8 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 animate-pulse">
            <div class="flex flex-col items-center gap-4">
              <div class="w-20 h-20 rounded-full bg-slate-200 dark:bg-slate-700"></div>
              <div class="h-5 w-24 bg-slate-200 dark:bg-slate-700 rounded"></div>
              <div class="h-4 w-16 bg-slate-200 dark:bg-slate-700 rounded"></div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="profilesStore.profiles.length === 0" class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-10 flex flex-col items-center justify-center text-center">
          <span class="material-symbols-outlined text-6xl text-slate-300 dark:text-slate-600 mb-4">family_restroom</span>
          <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-2">No profiles yet</h3>
          <p class="text-slate-500 dark:text-slate-400 mb-6 max-w-sm">
            Add your first child profile to personalize their coloring books.
          </p>
          <RouterLink
            to="/profiles/add"
            class="h-12 px-8 rounded-full bg-primary text-white font-bold transition-transform hover:scale-105 shadow-md hover:shadow-lg flex items-center gap-2"
          >
            <span class="material-symbols-outlined">add</span>
            Add Your First Child
          </RouterLink>
        </div>

        <!-- Profiles Grid -->
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-4">
          <button
            v-for="profile in profilesStore.profiles"
            :key="profile.profile_id"
            @click="selectProfile(profile.profile_id)"
            class="rounded-2xl p-8 flex flex-col items-center gap-4 text-center hover:shadow-lg transition-all duration-300 group relative overflow-hidden border-2 bg-white dark:bg-slate-800"
            :class="profilesStore.activeProfileId === profile.profile_id
              ? 'border-primary ring-2 ring-primary/20 shadow-md'
              : 'border-slate-200 dark:border-slate-700'"
          >
            <!-- Active checkmark -->
            <div
              v-if="profilesStore.activeProfileId === profile.profile_id"
              class="absolute top-3 left-3 flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold"
            >
              <span class="material-symbols-outlined text-sm">check_circle</span>
              Active
            </div>

            <!-- Delete button -->
            <div class="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                @click.stop="handleDelete(profile.profile_id)"
                :disabled="deletingId === profile.profile_id"
                class="text-slate-400 hover:text-red-500 transition-colors p-1.5 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                <span v-if="deletingId === profile.profile_id" class="material-symbols-outlined text-lg animate-spin">progress_activity</span>
                <span v-else class="material-symbols-outlined text-lg">delete</span>
              </button>
            </div>

            <!-- Avatar -->
            <div
              class="w-20 h-20 rounded-full flex items-center justify-center text-white text-3xl font-bold shadow-md group-hover:scale-110 transition-transform"
              :style="{ backgroundColor: profile.avatar_color }"
            >
              {{ getInitial(profile.name) }}
            </div>

            <!-- Info -->
            <div class="flex flex-col gap-1.5 w-full">
              <h3 class="text-slate-900 dark:text-white text-xl font-bold">{{ profile.name }}</h3>
              <span class="text-sm text-slate-500 dark:text-slate-400 font-medium">
                {{ profile.age }} years old
              </span>
            </div>

            <!-- Favorite themes -->
            <div v-if="profile.favorite_themes.length > 0" class="flex flex-wrap gap-1.5 justify-center mt-1">
              <span
                v-for="theme in profile.favorite_themes"
                :key="theme"
                class="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 capitalize"
              >
                {{ theme }}
              </span>
            </div>
          </button>

          <!-- Add New Placeholder Card -->
          <RouterLink
            v-if="profilesStore.profiles.length < 5"
            to="/profiles/add"
            class="flex flex-col items-center justify-center gap-4 rounded-2xl p-8 border-2 border-dashed border-slate-300 dark:border-slate-700 text-slate-400 hover:text-primary hover:border-primary dark:hover:border-primary hover:bg-white dark:hover:bg-slate-800/50 transition-all duration-300 min-h-[280px]"
          >
            <div class="size-16 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
              <span class="material-symbols-outlined text-4xl">add</span>
            </div>
            <span class="font-bold text-lg">Add Child</span>
          </RouterLink>
        </div>
      </div>
    </main>
  </div>
</template>
