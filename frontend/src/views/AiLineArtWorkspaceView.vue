<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const lineThickness = ref(40)
const detailLevel = ref('high')
const contrast = ref(100)
const activeTool = ref<'eraser' | 'smooth'>('eraser')
const eraserSize = ref(24)
const selectedThumb = ref(0)

const thumbs = [
  'https://lh3.googleusercontent.com/aida-public/AB6AXuCEZClNyDYk_3j7BTlyfJ3oL2qBA4dCjou6lwudraOnGkQifXGnVO5-vI25QsGbUIZTjgdcELYKVDYAvaEONIpYni-9SJnhb5D5vyuBWO5gHXXtDtm4AHqjghNBdhbmZ6zrDMWE2ymOFHjSQ6fmohZMh1DsUtpuosiWljbjdonYisIdy4wM-PDT_g2ROoXjrgFsahTqf9wWDCxmY7OeA0LtRQexNfHQ6PoPe2-2WYj16KAAOxQ7feBq2-7lNM6D40grwkO-8vuZSz-T',
  'https://lh3.googleusercontent.com/aida-public/AB6AXuBYi75jRgw757I4gf_6nQ7BmabR28Jd7vmhTEU9tqcwqu-5KSuWX56cKQc6DKXhV_mh3XRArRvxgWLYyMtD8zXH3mC7pvGAkDWGqLz6C5s5w85MZrqdYyGm4RaoWClY8xDYRFsQT_LqcfLjrYd84ohG6xzSewhRpV48BozbElxHXbjpDhym0n_TzFp-KHsyCMAqLuRENtOtX6BSi59KlHxbkbLpcjRn5rwfkios6wOSNGZSxl9F5iWDpWB5OFt_rasU29nQJxBiXeM_',
  'https://lh3.googleusercontent.com/aida-public/AB6AXuDtUZBG3LIWVV1yQYysHOQBqfsit6BtWkSIl5_qOic3kG8rsY7lUzGrymv9TslPGLw1WwhejshU9oL7dGRaQrDbYYkfEnN7VVEHLjISpkB37W5VX9IB2yrHtKRXygdmAeC6-RtfO3YII-x3fpR04ie-J9I_KpQkQ_MXA2qFkRtmz01W2_tuBoLUylDMf7nRvld7YYwVLJN8NRmgPJ1_eevD73jHfc81zj615SSxCUJwICVIgfKFOSG2-gsb5l9PNMzlSgWJnawSAyR9',
  'https://lh3.googleusercontent.com/aida-public/AB6AXuAx7tu_nAiZvpnIxzXg-3wMNGjPZWKKbCjXGGoNaelJ0Y4JJZe2ceoTPzW2w86w6L3VGMXoA37A41tuocO0vtDB-YflgAr24FwMVePwHKMDRxuCNrA1DAuLbz-DDUBfcRZ-eSuepHSgteLcDQgQ94h3wC0RB25Rr3S4pqOjB958381n2redACGp9lGUtqzap7h7obg97ly1nlYLbhnaOT6o3wbpXgSkNSGnxXbc9duUHapSQ2Rzu3QmBnZ6oRuujatrshmx2YceObpj',
]
</script>

<template>
  <div class="bg-slate-900 text-slate-100 min-h-screen flex flex-col font-display overflow-hidden">
    <!-- Top Nav -->
    <header class="h-14 bg-slate-900 border-b border-slate-700 flex items-center justify-between px-6 shrink-0 z-20">
      <div class="flex items-center gap-6">
        <RouterLink to="/dashboard" class="flex items-center gap-2 text-white font-bold text-lg">
          <span class="material-symbols-outlined text-teal-400">brush</span>
          Ai Line Art Workspace
        </RouterLink>
        <nav class="hidden md:flex items-center gap-4 text-sm text-slate-400">
          <RouterLink to="/library" class="hover:text-white transition-colors">My Projects</RouterLink>
          <a href="#" class="hover:text-white transition-colors">Templates</a>
          <a href="#" class="hover:text-white transition-colors">Help</a>
        </nav>
      </div>
      <RouterLink
        to="/export"
        class="flex items-center gap-2 bg-teal-500 hover:bg-teal-400 text-white font-semibold px-5 py-2 rounded-lg text-sm transition-colors"
      >
        <span class="material-symbols-outlined text-base">picture_as_pdf</span>
        Confirm &amp; Generate PDF
      </RouterLink>
    </header>

    <div class="flex flex-1 overflow-hidden">
      <!-- Main Canvas Area -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Zoom Toolbar -->
        <div class="h-10 bg-slate-800 border-b border-slate-700 flex items-center gap-3 px-4 shrink-0">
          <button class="p-1 rounded hover:bg-slate-700 text-slate-400 transition-colors">
            <span class="material-symbols-outlined text-lg">undo</span>
          </button>
          <button class="p-1 rounded hover:bg-slate-700 text-slate-400 transition-colors">
            <span class="material-symbols-outlined text-lg">redo</span>
          </button>
          <div class="h-4 w-px bg-slate-600 mx-1"></div>
          <button class="p-1 rounded hover:bg-slate-700 text-slate-400 transition-colors">
            <span class="material-symbols-outlined text-lg">zoom_out</span>
          </button>
          <span class="text-xs text-slate-400 font-medium w-10 text-center">100%</span>
          <button class="p-1 rounded hover:bg-slate-700 text-slate-400 transition-colors">
            <span class="material-symbols-outlined text-lg">zoom_in</span>
          </button>
          <div class="h-4 w-px bg-slate-600 mx-1"></div>
          <span class="text-xs text-slate-500">Use scroll to zoom · Drag to pan</span>
        </div>

        <!-- Split Canvas -->
        <div class="flex-1 relative overflow-hidden bg-slate-950 flex items-center justify-center">
          <div class="relative w-full max-w-4xl h-full max-h-[600px] mx-8 rounded-lg overflow-hidden shadow-2xl flex">
            <!-- Left: Original Photo -->
            <div class="relative w-1/2 overflow-hidden">
              <div class="absolute top-3 left-3 z-10 bg-black/60 text-white text-xs font-bold px-2 py-1 rounded backdrop-blur-sm">LINE ART</div>
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuCEZClNyDYk_3j7BTlyfJ3oL2qBA4dCjou6lwudraOnGkQifXGnVO5-vI25QsGbUIZTjgdcELYKVDYAvaEONIpYni-9SJnhb5D5vyuBWO5gHXXtDtm4AHqjghNBdhbmZ6zrDMWE2ymOFHjSQ6fmohZMh1DsUtpuosiWljbjdonYisIdy4wM-PDT_g2ROoXjrgFsahTqf9wWDCxmY7OeA0LtRQexNfHQ6PoPe2-2WYj16KAAOxQ7feBq2-7lNM6D40grwkO-8vuZSz-T"
                alt="Line art result"
                class="w-full h-full object-cover filter grayscale contrast-125"
              />
            </div>
            <!-- Divider -->
            <div class="absolute inset-y-0 left-1/2 -translate-x-1/2 w-1 bg-white z-10 flex items-center justify-center">
              <div class="size-7 rounded-full bg-white shadow-lg flex items-center justify-center text-slate-700">
                <span class="material-symbols-outlined text-base">drag_indicator</span>
              </div>
            </div>
            <!-- Right: Original -->
            <div class="relative w-1/2 overflow-hidden">
              <div class="absolute top-3 right-3 z-10 bg-black/60 text-white text-xs font-bold px-2 py-1 rounded backdrop-blur-sm">ORIGINAL</div>
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuCEZClNyDYk_3j7BTlyfJ3oL2qBA4dCjou6lwudraOnGkQifXGnVO5-vI25QsGbUIZTjgdcELYKVDYAvaEONIpYni-9SJnhb5D5vyuBWO5gHXXtDtm4AHqjghNBdhbmZ6zrDMWE2ymOFHjSQ6fmohZMh1DsUtpuosiWljbjdonYisIdy4wM-PDT_g2ROoXjrgFsahTqf9xWDCxmY7OeA0LtRQexNfHQ6PoPe2-2WYj16KAAOxQ7feBq2-7lNM6D40grwkO-8vuZSz-T"
                alt="Original photo"
                class="w-full h-full object-cover"
              />
            </div>
          </div>
        </div>

        <!-- Bottom Thumbnail Strip -->
        <div class="h-28 bg-slate-800 border-t border-slate-700 flex items-center gap-3 px-6 shrink-0">
          <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider mr-2 shrink-0">Imported from Google Drive</span>
          <div class="flex gap-3 overflow-x-auto no-scrollbar flex-1">
            <div
              v-for="(thumb, i) in thumbs"
              :key="i"
              class="shrink-0 size-16 rounded-lg overflow-hidden border-2 cursor-pointer transition-all"
              :class="selectedThumb === i ? 'border-teal-400 ring-2 ring-teal-400/40' : 'border-slate-600 hover:border-slate-400'"
              @click="selectedThumb = i"
            >
              <img :src="thumb" :alt="`Photo ${i + 1}`" class="w-full h-full object-cover" />
            </div>
            <div class="shrink-0 size-16 rounded-lg border-2 border-dashed border-slate-600 flex items-center justify-center text-slate-500 hover:border-slate-400 cursor-pointer transition-colors">
              <span class="material-symbols-outlined text-xl">add_photo_alternate</span>
            </div>
          </div>
          <button class="shrink-0 text-xs text-teal-400 font-semibold hover:text-teal-300 transition-colors">Select All</button>
        </div>
      </div>

      <!-- Right Panel: Controls -->
      <aside class="w-72 bg-slate-800 border-l border-slate-700 flex flex-col shrink-0 overflow-y-auto">
        <div class="p-5 border-b border-slate-700">
          <h2 class="text-base font-bold text-white">Line Art Controls</h2>
          <p class="text-xs text-slate-400 mt-0.5">Fine-tune your coloring page.</p>
        </div>

        <div class="p-5 space-y-6 flex-1">
          <!-- Line Thickness -->
          <section>
            <div class="flex justify-between items-center mb-2">
              <label class="text-xs font-semibold text-slate-300 uppercase tracking-wider">Line Thickness</label>
              <span class="text-xs text-slate-400">{{ lineThickness }}</span>
            </div>
            <input
              v-model="lineThickness"
              type="range"
              min="10"
              max="100"
              class="w-full h-1.5 rounded-full appearance-none bg-slate-600 accent-teal-400 cursor-pointer"
            />
            <div class="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>Fine</span>
              <span>Bold</span>
            </div>
          </section>

          <!-- Detail Level -->
          <section>
            <label class="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">Detail Level</label>
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="level in ['low', 'high', 'sample']"
                :key="level"
                class="py-1.5 rounded-lg text-xs font-semibold capitalize border transition-all"
                :class="detailLevel === level
                  ? 'bg-teal-500 border-teal-500 text-white'
                  : 'bg-slate-700 border-slate-600 text-slate-300 hover:border-slate-400'"
                @click="detailLevel = level"
              >
                {{ level }}
              </button>
            </div>
          </section>

          <!-- Contrast -->
          <section>
            <div class="flex justify-between items-center mb-2">
              <label class="text-xs font-semibold text-slate-300 uppercase tracking-wider">Contrast</label>
              <span class="text-xs text-slate-400">±{{ contrast }}</span>
            </div>
            <input
              v-model="contrast"
              type="range"
              min="0"
              max="200"
              class="w-full h-1.5 rounded-full appearance-none bg-slate-600 accent-teal-400 cursor-pointer"
            />
          </section>

          <div class="h-px bg-slate-700"></div>

          <!-- Manual Touch-up -->
          <section>
            <label class="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-3">Manual Touch-up</label>
            <div class="grid grid-cols-2 gap-2 mb-4">
              <button
                class="flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold border transition-all"
                :class="activeTool === 'eraser'
                  ? 'bg-teal-500 border-teal-500 text-white'
                  : 'bg-slate-700 border-slate-600 text-slate-300 hover:border-slate-400'"
                @click="activeTool = 'eraser'"
              >
                <span class="material-symbols-outlined text-base">auto_fix_high</span>
                Magic Eraser
              </button>
              <button
                class="flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold border transition-all"
                :class="activeTool === 'smooth'
                  ? 'bg-teal-500 border-teal-500 text-white'
                  : 'bg-slate-700 border-slate-600 text-slate-300 hover:border-slate-400'"
                @click="activeTool = 'smooth'"
              >
                <span class="material-symbols-outlined text-base">blur_on</span>
                Smooth Lines
              </button>
            </div>
            <div class="flex justify-between items-center mb-2">
              <label class="text-xs text-slate-400">Eraser Size</label>
              <span class="text-xs text-slate-400">{{ eraserSize }}px</span>
            </div>
            <input
              v-model="eraserSize"
              type="range"
              min="4"
              max="80"
              class="w-full h-1.5 rounded-full appearance-none bg-slate-600 accent-teal-400 cursor-pointer"
            />
          </section>
        </div>

        <!-- Tip -->
        <div class="p-4 border-t border-slate-700 bg-slate-900/50">
          <div class="flex gap-2">
            <span class="material-symbols-outlined text-teal-400 text-base shrink-0 mt-0.5">lightbulb</span>
            <p class="text-[11px] text-slate-400 leading-relaxed">
              Use <span class="text-teal-400 font-semibold">Magic Eraser</span> to remove smudges and add clean fill areas for easier coloring.
            </p>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>
