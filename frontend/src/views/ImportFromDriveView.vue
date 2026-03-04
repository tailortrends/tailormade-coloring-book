<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const selectedFolder = ref('Birthday 2023')
const lineDetail = ref<'low' | 'medium' | 'high'>('medium')
const lineThickness = ref(50)
const aiCreativity = ref(true)
const simplifyBg = ref(true)
const funElements = ref(false)
const searchQuery = ref('')

const folders = [
  { name: 'Birthday 2023', count: 24, label: 'Modified', time: 'Yesterday' },
  { name: 'Zoo Trip', count: 16, label: 'Items', time: '3 weeks ago' },
  { name: 'Summer Vacat...', count: 158, label: 'Items', time: 'Last week' },
  { name: 'First School Day', count: 12, label: 'Items', time: 'Aug 24' },
  { name: 'Family Shared', count: 450, label: 'Items', time: 'Aug 10' },
]

const analyzedPhotos = [
  { label: 'High Potential', score: 92, color: 'text-green-600', bg: 'bg-green-100', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCEZClNyDYk_3j7BTlyfJ3oL2qBA4dCjou6lwudraOnGkQifXGnVO5-vI25QsGbUIZTjgdcELYKVDYAvaEONIpYni-9SJnhb5D5vyuBWO5gHXXtDtm4AHqjghNBdhbmZ6zrDMWE2ymOFHjSQ6fmohZMh1DsUtpuosiWljbjdonYisIdy4wM-PDT_g2ROoXjrgFsahTqf9WDCxmY7OeA0LtRQexNfHQ6PoPe2-2WYj16KAAOxQ7feBq2-7lNM6D40grwkO-8vuZSz-T' },
  { label: 'High Potential', score: 88, color: 'text-green-600', bg: 'bg-green-100', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBYi75jRgw757I4gf_6nQ7BmabR28Jd7vmhTEU9tqcwqu-5KSuWX56cKQc6DKXhV_mh3XRArRvxgWLYyMtD8zXH3mC7pvGAkDWGqLz6C5s5w85MZrqdYyGm4RaoWClY8xDYRFsQT_LqcfLjrYd84ohG6xzSewhRpV48BozbElxHXbjpDhym0n_TzFp-KHsyCMAqLuRENtOtX6BSi59KlHxbkbLpcjRn5rwfkios6wOSNGZSxl9F5iWDpWB5OFt_rasU29nQJxBiXeM_' },
  { label: 'Medium Potential', score: 61, color: 'text-yellow-600', bg: 'bg-yellow-100', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDtUZBG3LIWVV1yQYysHOQBqfsit6BtWkSIl5_qOic3kG8rsY7lUzGrymv9TslPGLw1WwhejshU9oL7dGRaQrDbYYkfEnN7VVEHLjISpkB37W5VX9IB2yrHtKRXygdmAeC6-RtfO3YII-x3fpR04ie-J9I_KpQkQ_MXA2qFkRtmz01W2_tuBoLUylDMf7nRvld7YYwVLJN8NRmgPJ1_eevD73jHfc81zj615SSxCUJwICVIgfKFOSG2-gsb5l9PNMzlSgWJnawSAyR9' },
  { label: 'Low Potential', score: 32, color: 'text-red-500', bg: 'bg-red-100', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAx7tu_nAiZvpnIxzXg-3wMNGjPZWKKbCjXGGoNaelJ0Y4JJZe2ceoTPzW2w86w6L3VGMXoA37A41tuocO0vtDB-YflgAr24FwMVePwHKMDRxuCNrA1DAuLbz-DDUBfcRZ-eSuepHSgteLcDQgQ94h3wC0RB25Rr3S4pqOjB958381n2redACGp9lGUtqzap7h7obg97ly1nlYLbhnaOT6o3wbpXgSkNSGnxXbc9duUHapSQ2Rzu3QmBnZ6oRuujatrshmx2YceObpj' },
]

const selectedCount = ref(12)
const totalCount = 24
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col overflow-hidden">
    <AppHeader />

    <!-- Breadcrumb -->
    <div class="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-6 py-2.5 text-xs text-slate-500 flex items-center gap-1.5">
      <RouterLink to="/dashboard" class="hover:text-primary transition-colors">Home</RouterLink>
      <span class="material-symbols-outlined text-sm text-slate-300">chevron_right</span>
      <span>Import</span>
      <span class="material-symbols-outlined text-sm text-slate-300">chevron_right</span>
      <span class="text-slate-700 dark:text-slate-300 font-medium">Google Drive</span>
    </div>

    <div class="flex flex-1 overflow-hidden h-[calc(100vh-110px)]">
      <!-- Main Content -->
      <main class="flex-1 flex flex-col overflow-y-auto">
        <!-- Connected Account Banner -->
        <div class="mx-6 mt-5 flex items-center gap-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl px-5 py-3.5">
          <div class="size-8 rounded-full bg-green-500 flex items-center justify-center shrink-0">
            <span class="material-symbols-outlined text-white text-base">check</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-green-800 dark:text-green-200">Connected to jane.doe@gmail.com</p>
            <p class="text-xs text-green-600 dark:text-green-400">Your Google Drive is linked. Ready to start generating coloring pages.</p>
          </div>
          <button class="text-xs font-semibold text-green-700 dark:text-green-300 hover:underline shrink-0">Change Account</button>
        </div>

        <!-- Folder Selector -->
        <div class="px-6 mt-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-bold text-slate-900 dark:text-white">Select an Event Folder</h2>
            <div class="relative">
              <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-base">search</span>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search folders..."
                class="pl-9 pr-4 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:border-primary w-52"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
            <button
              v-for="folder in folders"
              :key="folder.name"
              class="flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all text-center"
              :class="selectedFolder === folder.name
                ? 'border-primary bg-primary/5 dark:bg-primary/10'
                : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-primary/40'"
              @click="selectedFolder = folder.name"
            >
              <span class="material-symbols-outlined text-4xl" :class="selectedFolder === folder.name ? 'text-primary' : 'text-amber-400'">folder</span>
              <div>
                <p class="text-xs font-bold text-slate-800 dark:text-slate-200 truncate w-full">{{ folder.name }}</p>
                <p class="text-[10px] text-slate-400 mt-0.5">{{ folder.count }} items · {{ folder.time }}</p>
              </div>
            </button>
          </div>
        </div>

        <!-- AI Analysis -->
        <div class="px-6 mt-8 pb-28">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-bold text-slate-900 dark:text-white">
              Analysing
              <span class="text-primary">'{{ selectedFolder }}'</span>
            </h3>
            <div class="flex items-center gap-1.5 text-xs text-primary font-medium">
              <span class="material-symbols-outlined text-base animate-spin">refresh</span>
              AI Processing Coloring Potential
            </div>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div
              v-for="(photo, i) in analyzedPhotos"
              :key="i"
              class="rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm"
            >
              <div class="aspect-square overflow-hidden relative">
                <img :src="photo.img" :alt="`Photo ${i + 1}`" class="w-full h-full object-cover" />
                <div class="absolute top-2 right-2">
                  <span class="text-[10px] font-bold px-2 py-0.5 rounded-full" :class="[photo.color, photo.bg]">
                    {{ photo.score }}%
                  </span>
                </div>
              </div>
              <div class="px-3 py-2">
                <p class="text-[11px] font-semibold" :class="photo.color">{{ photo.label }}</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- Right Panel: Transformation Settings -->
      <aside class="w-72 bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 flex flex-col shrink-0 overflow-y-auto">
        <div class="p-5 border-b border-slate-100 dark:border-slate-800">
          <h2 class="text-base font-bold">Transformation Settings</h2>
          <p class="text-xs text-slate-500 mt-0.5">Configure how AI converts your photos.</p>
        </div>

        <div class="p-5 space-y-6 flex-1">
          <!-- Line Detail Level -->
          <section>
            <label class="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">Line Detail Level</label>
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="level in ['low', 'medium', 'high'] as const"
                :key="level"
                class="py-1.5 rounded-lg text-xs font-semibold capitalize border transition-all"
                :class="lineDetail === level
                  ? 'bg-primary border-primary text-white'
                  : 'bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-primary/40'"
                @click="lineDetail = level"
              >
                {{ level }}
              </button>
            </div>
            <p class="text-[10px] text-slate-400 mt-2">Medium provides the best quality-to-file size ratio.</p>
          </section>

          <!-- Line Thickness -->
          <section>
            <div class="flex justify-between mb-1">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Line Thickness</label>
              <span class="text-xs text-slate-400">{{ lineThickness }}</span>
            </div>
            <input
              v-model="lineThickness"
              type="range"
              min="10"
              max="100"
              class="w-full h-1.5 rounded-full appearance-none bg-slate-200 dark:bg-slate-700 accent-primary cursor-pointer"
            />
            <div class="flex justify-between text-[10px] text-slate-400 mt-1">
              <span>Thin</span>
              <span>Thick</span>
            </div>
          </section>

          <div class="h-px bg-slate-100 dark:bg-slate-800"></div>

          <!-- Toggles -->
          <section class="space-y-4">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm font-semibold text-slate-800 dark:text-slate-200">AI Creativity</p>
                <p class="text-xs text-slate-400">Removes clutter to focus on subjects.</p>
              </div>
              <button
                class="shrink-0 relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
                :class="aiCreativity ? 'bg-primary' : 'bg-slate-200 dark:bg-slate-700'"
                @click="aiCreativity = !aiCreativity"
              >
                <span
                  class="inline-block size-4 transform rounded-full bg-white shadow transition-transform"
                  :class="aiCreativity ? 'translate-x-4' : 'translate-x-0.5'"
                ></span>
              </button>
            </div>
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm font-semibold text-slate-800 dark:text-slate-200">Simplify Backgrounds</p>
                <p class="text-xs text-slate-400">Removes clutter to focus on subjects.</p>
              </div>
              <button
                class="shrink-0 relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
                :class="simplifyBg ? 'bg-primary' : 'bg-slate-200 dark:bg-slate-700'"
                @click="simplifyBg = !simplifyBg"
              >
                <span
                  class="inline-block size-4 transform rounded-full bg-white shadow transition-transform"
                  :class="simplifyBg ? 'translate-x-4' : 'translate-x-0.5'"
                ></span>
              </button>
            </div>
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm font-semibold text-slate-800 dark:text-slate-200">Add Fun Elements</p>
                <p class="text-xs text-slate-400">Adds stars, balloons, or clouds.</p>
              </div>
              <button
                class="shrink-0 relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
                :class="funElements ? 'bg-primary' : 'bg-slate-200 dark:bg-slate-700'"
                @click="funElements = !funElements"
              >
                <span
                  class="inline-block size-4 transform rounded-full bg-white shadow transition-transform"
                  :class="funElements ? 'translate-x-4' : 'translate-x-0.5'"
                ></span>
              </button>
            </div>
          </section>
        </div>

        <!-- Sticky CTA -->
        <div class="p-5 border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 sticky bottom-0">
          <div class="flex items-center justify-between text-xs text-slate-500 mb-3">
            <span>Selected images</span>
            <span class="font-bold text-slate-700 dark:text-slate-200">{{ selectedCount }} / {{ totalCount }}</span>
          </div>
          <RouterLink
            to="/generating"
            class="w-full flex items-center justify-center gap-2 bg-teal-500 hover:bg-teal-400 text-white font-bold py-3.5 rounded-xl transition-colors shadow-lg"
          >
            <span class="material-symbols-outlined">auto_awesome</span>
            Convert to Coloring Book
          </RouterLink>
        </div>
      </aside>
    </div>
  </div>
</template>
