<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import { RouterLink } from 'vue-router'

const creditsUsed = 7
const creditsTotal = 10
const creditsPercent = (creditsUsed / creditsTotal) * 100

const galleryImages = [
  'https://lh3.googleusercontent.com/aida-public/AB6AXuCEZClNyDYk_3j7BTlyfJ3oL2qBA4dCjou6lwudraOnGkQifXGnVO5-vI25QsGbUIZTjgdcELYKVDYAvaEONIpYni-9SJnhb5D5vyuBWO5gHXXtDtm4AHqjghNBdhbmZ6zrDMWE2ymOFHjSQ6fmohZMh1DsUtpuosiWljbjdonYisIdy4wM-PDT_g2ROoXjrgFsahTqf9WDCxmY7OeA0LtRQexNfHQ6PoPe2-2WYj16KAAOxQ7feBq2-7lNM6D40grwkO-8vuZSz-T',
  'https://lh3.googleusercontent.com/aida-public/AB6AXuBYi75jRgw757I4gf_6nQ7BmabR28Jd7vmhTEU9tqcwqu-5KSuWX56cKQc6DKXhV_mh3XRArRvxgWLYyMtD8zXH3mC7pvGAkDWGqLz6C5s5w85MZrqdYyGm4RaoWClY8xDYRFsQT_LqcfLjrYd84ohG6xzSewhRpV48BozbElxHXbjpDhym0n_TzFp-KHsyCMAqLuRENtOtX6BSi59KlHxbkbLpcjRn5rwfkios6wOSNGZSxl9F5iWDpWB5OFt_rasU29nQJxBiXeM_',
  'https://lh3.googleusercontent.com/aida-public/AB6AXuDtUZBG3LIWVV1yQYysHOQBqfsit6BtWkSIl5_qOic3kG8rsY7lUzGrymv9TslPGLw1WwhejshU9oL7dGRaQrDbYYkfEnN7VVEHLjISpkB37W5VX9IB2yrHtKRXygdmAeC6-RtfO3YII-x3fpR04ie-J9I_KpQkQ_MXA2qFkRtmz01W2_tuBoLUylDMf7nRvld7YYwVLJN8NRmgPJ1_eevD73jHfc81zj615SSxCUJwICVIgfKFOSG2-gsb5l9PNMzlSgWJnawSAyR9',
  'https://lh3.googleusercontent.com/aida-public/AB6AXuAx7tu_nAiZvpnIxzXg-3wMNGjPZWKKbCjXGGoNaelJ0Y4JJZe2ceoTPzW2w86w6L3VGMXoA37A41tuocO0vtDB-YflgAr24FwMVePwHKMDRxuCNrA1DAuLbz-DDUBfcRZ-eSuepHSgteLcDQgQ94h3wC0RB25Rr3S4pqOjB958381n2redACGp9lGUtqzap7h7obg97ly1nlYLbhnaOT6o3wbpXgSkNSGnxXbc9duUHapSQ2Rzu3QmBnZ6oRuujatrshmx2YceObpj',
]
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-1 flex flex-col items-center justify-start py-12 px-4 relative overflow-hidden">
      <!-- Decorative background shapes -->
      <div class="absolute top-0 left-1/4 size-64 bg-accent-purple/10 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute bottom-20 right-1/4 size-80 bg-accent-pink/10 rounded-full blur-3xl pointer-events-none"></div>

      <!-- Success Card -->
      <div class="relative z-10 w-full max-w-md">
        <div class="bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-100 dark:border-slate-800 p-8 text-center">
          <!-- Icon -->
          <div class="size-20 rounded-full bg-accent-purple/10 flex items-center justify-center mx-auto mb-5">
            <span class="material-symbols-outlined text-[40px] text-accent-purple">card_giftcard</span>
          </div>

          <!-- Headline -->
          <h1 class="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-2">Magic Unlocked!</h1>
          <p class="text-slate-500 dark:text-slate-400 text-base leading-relaxed mb-6">
            Your gift code was successful!
            <strong class="text-slate-900 dark:text-white">5 Extra Book Credits</strong>
            have been added to your account.
          </p>

          <!-- Credits display -->
          <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-5 mb-6 text-left">
            <div class="flex justify-between items-end mb-2">
              <span class="text-sm font-semibold text-slate-600 dark:text-slate-300">Available Credits</span>
              <span class="text-xl font-extrabold text-slate-900 dark:text-white">
                {{ creditsUsed }}
                <span class="text-slate-400 font-normal text-base">/ {{ creditsTotal }} Books</span>
              </span>
            </div>
            <!-- Progress bar -->
            <div class="h-3 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
              <div
                class="h-full rounded-full bg-gradient-to-r from-accent-purple to-accent-pink transition-all duration-700"
                :style="{ width: creditsPercent + '%' }"
              ></div>
            </div>
            <p class="text-xs text-slate-400 mt-2 text-right">{{ creditsPercent.toFixed(0) }}% Capacity</p>
          </div>

          <!-- CTAs -->
          <div class="flex flex-col gap-3">
            <RouterLink
              to="/create"
              class="w-full flex items-center justify-center gap-2 bg-accent-purple hover:opacity-90 text-white font-bold py-3.5 rounded-xl transition-all shadow-md"
            >
              <span class="material-symbols-outlined">add_circle</span>
              Create a New Book
            </RouterLink>
            <RouterLink
              to="/library"
              class="w-full flex items-center justify-center gap-2 border-2 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:border-accent-purple hover:text-accent-purple font-bold py-3.5 rounded-xl transition-all"
            >
              <span class="material-symbols-outlined">auto_stories</span>
              View My Library
            </RouterLink>
          </div>

          <p class="mt-5 text-xs text-slate-400">
            Need help?
            <a href="#" class="text-accent-purple hover:underline font-medium">Visit Support Center</a>
          </p>
        </div>

        <!-- Gallery teaser -->
        <div class="mt-8">
          <p class="text-xs font-bold uppercase tracking-wider text-slate-400 text-center mb-4">Ready to print your next adventure?</p>
          <div class="grid grid-cols-4 gap-3">
            <div
              v-for="(img, i) in galleryImages"
              :key="i"
              class="aspect-square rounded-xl overflow-hidden shadow-sm"
            >
              <img :src="img" :alt="`Sample ${i + 1}`" class="w-full h-full object-cover" />
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
