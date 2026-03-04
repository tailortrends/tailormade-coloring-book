<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { RouterLink } from 'vue-router'

const profiles = [
  {
    name: "Leo",
    age: 4,
    bgColor: "bg-blue-50 dark:bg-slate-800/50",
    borderColor: "border-blue-100 dark:border-slate-700/50",
    tagBg: "bg-blue-100 dark:bg-blue-900/30",
    tagText: "text-blue-600 dark:text-blue-300",
    interestBorder: "border-blue-100/50 dark:border-slate-700",
    interests: ["Dinosaurs", "Volcanoes"],
    avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuAPxYiP_W5n206zxLPKHcW3s8sHEANIirwlCE1NvlNv2TNFspOL2qBqhKVAw832bq5gktYkXqOaxd5UgkXuYiiiZBiRu4xsSqffbmalThvtRpDv9JX4ELH591nVBznp7kiBF_IBh77GnfF9gwTiLjpdrzNqUnuwMqs_gw9b2gxoCMnkmWU59OiDashfyqvC8GxKg23Zv9Gqpf4FXIDYei04Zu31Fu3MaZ6jGZ0jhRv3CHryRCwe6VhceLRRNqu7qS1df3VGOIdKRiPq",
  },
  {
    name: "Mia",
    age: 6,
    bgColor: "bg-pink-50 dark:bg-slate-800/50",
    borderColor: "border-pink-100 dark:border-slate-700/50",
    tagBg: "bg-pink-100 dark:bg-pink-900/30",
    tagText: "text-pink-600 dark:text-pink-300",
    interestBorder: "border-pink-100/50 dark:border-slate-700",
    interests: ["Princesses", "Fairies"],
    avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuBKfP7kHRk9-3ORnR_TZbe4P-Q4My4orPfyVIg7PD4tLSto7jf5QqEGqg1WOvWqRUuLDbFrK4v_lcbSWsshshY-kxugIjJsHQGkbCMo6g_BQRcBhdgxnQ4vYwh0MCYMPiNmrHOM4cYtO6oXi1gSB4b8GBCVfErApDUbevyH2QTKI7e_FdKvk0jTc_fkZfbkqzo-usU1KLp_U1BD8PPJmnU9tr0Xd3g79hvqVhQNkGEsyGH0CUfJvittuLUu4cCPmUlfB52kLvSBU5Vh",
  },
  {
    name: "Noah",
    age: 5,
    bgColor: "bg-indigo-50 dark:bg-slate-800/50",
    borderColor: "border-indigo-100 dark:border-slate-700/50",
    tagBg: "bg-indigo-100 dark:bg-indigo-900/30",
    tagText: "text-indigo-600 dark:text-indigo-300",
    interestBorder: "border-indigo-100/50 dark:border-slate-700",
    interests: ["Space", "Rockets"],
    avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuB8sFJu1gdsJmBOxmWeONWOKw0412QqOzXQoayXAAgSmiMKFP3hVaXrkoqTWRbquoVTWU4_FmWT_zVsZ-qY4AEP3tAYsZLNbqk-okf425owXojEXIf0scUka1gvVlWbktKVgPJnOoCmMVALaFmo0CoCC56a0aXLvgPl7rnj74PyCxxWV2YGRhzzN_OxOtpitED-XNjyyonOD1XOn7JpFWfgKKT9R1CKcRvtT6hKBS77j-fbmaIBYmIB78DoukoBXHA-B996MhMjke8v",
  },
]
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-1 flex justify-center py-10 px-6 sm:px-10">
      <div class="w-full max-w-[1024px] flex flex-col gap-8">
        <!-- Header -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div class="flex flex-col gap-2 max-w-2xl">
            <h1 class="text-slate-900 dark:text-white text-4xl md:text-5xl font-extrabold leading-tight tracking-tight">Manage Child Profiles</h1>
            <p class="text-slate-600 dark:text-slate-400 text-lg font-normal leading-relaxed">
              Create profiles for your little artists to make generating personalized coloring books even faster.
            </p>
          </div>
          <RouterLink to="/profiles/add" class="group flex items-center justify-center gap-3 h-14 px-8 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-full font-bold text-base shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300">
            <span class="material-symbols-outlined group-hover:rotate-90 transition-transform duration-300">add</span>
            <span>Add New Child</span>
          </RouterLink>
        </div>

        <!-- Profiles Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-4">
          <div
            v-for="profile in profiles"
            :key="profile.name"
            class="rounded-xl p-6 flex flex-col items-center gap-4 text-center hover:shadow-lg transition-all duration-300 group relative overflow-hidden"
            :class="[profile.bgColor, profile.borderColor, 'border']"
          >
            <div class="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
              <button class="text-slate-400 hover:text-red-500 transition-colors">
                <span class="material-symbols-outlined text-[20px]">delete</span>
              </button>
            </div>
            <div class="relative">
              <img :src="profile.avatar" :alt="profile.name" class="w-24 h-24 rounded-full border-4 border-white dark:border-slate-700 shadow-md object-cover" />
              <button class="absolute bottom-0 right-0 bg-white dark:bg-slate-700 text-primary p-1.5 rounded-full shadow-sm hover:scale-110 transition-transform border border-slate-100 dark:border-slate-600">
                <span class="material-symbols-outlined text-[18px]">edit</span>
              </button>
            </div>
            <div class="flex flex-col gap-1 w-full">
              <h3 class="text-slate-900 dark:text-white text-xl font-bold">{{ profile.name }}</h3>
              <div class="flex items-center justify-center gap-2 text-sm text-slate-500 dark:text-slate-400 font-medium">
                <span class="bg-white/60 dark:bg-slate-900/40 px-2 py-0.5 rounded-md">{{ profile.age }} years old</span>
              </div>
              <div class="mt-3 bg-white dark:bg-slate-900 p-3 rounded-lg border" :class="profile.interestBorder">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">Likes</span>
                <div class="flex flex-wrap gap-1.5 justify-center">
                  <span
                    v-for="interest in profile.interests"
                    :key="interest"
                    class="text-xs font-semibold px-2 py-1 rounded-md"
                    :class="[profile.tagBg, profile.tagText]"
                  >{{ interest }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Add New Placeholder Card -->
          <RouterLink to="/profiles/add" class="flex flex-col items-center justify-center gap-4 rounded-xl p-6 border-2 border-dashed border-slate-300 dark:border-slate-700 text-slate-400 hover:text-primary hover:border-primary dark:hover:border-primary hover:bg-white dark:hover:bg-slate-800/50 transition-all duration-300 min-h-[340px]">
            <div class="size-16 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
              <span class="material-symbols-outlined text-4xl">add</span>
            </div>
            <span class="font-bold text-lg">Add New Child</span>
          </RouterLink>
        </div>
      </div>
    </main>

    <AppFooter />
  </div>
</template>
