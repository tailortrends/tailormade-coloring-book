<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { RouterLink } from 'vue-router'

const storyPrompt = ref('')

function appendChip(text: string) {
  const base = storyPrompt.value.trimEnd()
  const joined = base ? `${base} ${text}` : text
  storyPrompt.value = joined.slice(0, 300)
}
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 font-display min-h-screen flex flex-col relative">
    <AppHeader />

    <main class="flex-grow flex justify-center py-10 px-4 md:px-10">
      <div class="flex flex-col max-w-[1024px] w-full gap-8">
        <!-- Header & Quota -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 mb-4">
          <div class="flex flex-col gap-3 max-w-2xl">
            <h1 class="text-slate-900 dark:text-white text-4xl md:text-5xl font-black leading-tight tracking-[-0.033em]">
              Create Your <span class="text-transparent bg-clip-text bg-gradient-to-r from-accent-purple to-primary">Magic Book</span>
            </h1>
            <p class="text-slate-500 dark:text-slate-400 text-lg font-medium leading-normal max-w-lg">
              Turn your child's imagination into a printable coloring adventure in seconds.
            </p>
          </div>

          <div class="w-full md:w-auto bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-900 p-6 rounded-2xl shadow-lg shadow-primary/5 border border-primary/20 min-w-[300px] relative overflow-hidden group">
            <div class="absolute top-0 right-0 w-20 h-20 bg-primary/10 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
            <div class="flex gap-6 justify-between mb-4 relative z-10">
              <div class="flex items-center gap-2">
                <div class="bg-primary/10 p-1.5 rounded-lg text-primary">
                  <span class="material-symbols-outlined text-xl">auto_stories</span>
                </div>
                <p class="text-slate-900 dark:text-white text-sm font-bold">Monthly Quota</p>
              </div>
              <p class="text-primary font-black text-lg">1<span class="text-slate-400 text-sm font-medium">/2</span></p>
            </div>
            
            <div class="relative z-10">
              <div class="flex justify-between text-xs mb-1.5 font-semibold">
                <span class="text-slate-700 dark:text-slate-300">50% Used</span>
                <span class="text-slate-400">Refreshes in 12 days</span>
              </div>
              <div class="rounded-full bg-slate-200 dark:bg-slate-700 h-4 w-full overflow-hidden border border-slate-100 dark:border-slate-600">
                <div class="h-full rounded-full bg-gradient-to-r from-primary to-accent-purple transition-all duration-500 shadow-[0_0_10px_rgba(139,92,246,0.5)]" style="width: 50%;"></div>
              </div>
            </div>
            
            <div class="mt-4 flex justify-end relative z-10">
              <RouterLink to="/pricing" class="text-primary text-xs font-bold hover:text-primary-dark transition-colors flex items-center gap-1 group/link">
                Upgrade Plan
                <span class="material-symbols-outlined text-sm group-hover/link:translate-x-0.5 transition-transform">arrow_forward</span>
              </RouterLink>
            </div>
          </div>
        </div>

        <!-- Form Container -->
        <div class="bg-white dark:bg-slate-900 rounded-[2rem] p-6 md:p-10 shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-800 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-primary via-purple-400 to-accent-pink"></div>
          
          <!-- Child Name & Age -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
            <div class="flex flex-col gap-4">
              <label class="flex flex-col">
                <span class="text-slate-900 dark:text-white text-base font-bold pb-2 ml-1">Child's Name</span>
                <div class="relative group">
                  <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-primary transition-colors">
                    <span class="material-symbols-outlined">face</span>
                  </div>
                  <input type="text" placeholder="e.g. Leo" class="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white h-14 pl-12 pr-4 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-slate-400" />
                </div>
              </label>
            </div>

            <div class="group/age flex flex-col gap-4">
              <span class="text-slate-900 dark:text-white text-base font-bold ml-1">Age Range</span>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <label class="cursor-pointer">
                  <input type="radio" name="age" value="2-4" class="peer sr-only age-toddler" />
                  <div class="h-16 flex flex-col items-center justify-center rounded-xl border-2 border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 peer-checked:border-primary peer-checked:text-primary peer-checked:bg-primary/5 hover:border-primary/50 transition-all">
                    <span class="font-bold text-sm leading-tight">2-4</span>
                    <span class="text-[11px] font-medium opacity-70">Toddler</span>
                  </div>
                </label>
                <label class="cursor-pointer">
                  <input type="radio" name="age" value="4-6" class="peer sr-only age-beginner" />
                  <div class="h-16 flex flex-col items-center justify-center rounded-xl border-2 border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 peer-checked:border-primary peer-checked:text-primary peer-checked:bg-primary/5 hover:border-primary/50 transition-all">
                    <span class="font-bold text-sm leading-tight">4-6</span>
                    <span class="text-[11px] font-medium opacity-70">Beginner</span>
                  </div>
                </label>
                <label class="cursor-pointer">
                  <input type="radio" name="age" value="6-9" class="peer sr-only age-kids" checked />
                  <div class="h-16 flex flex-col items-center justify-center rounded-xl border-2 border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 peer-checked:border-primary peer-checked:text-primary peer-checked:bg-primary/5 hover:border-primary/50 transition-all">
                    <span class="font-bold text-sm leading-tight">6-9</span>
                    <span class="text-[11px] font-medium opacity-70">Kids</span>
                  </div>
                </label>
                <label class="cursor-pointer">
                  <input type="radio" name="age" value="9-12" class="peer sr-only age-tweens" />
                  <div class="h-16 flex flex-col items-center justify-center rounded-xl border-2 border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 peer-checked:border-primary peer-checked:text-primary peer-checked:bg-primary/5 hover:border-primary/50 transition-all">
                    <span class="font-bold text-sm leading-tight">9-12</span>
                    <span class="text-[11px] font-medium opacity-70">Tweens</span>
                  </div>
                </label>
              </div>

              <!-- Complexity indicator -->
              <div class="hidden group-has-[.age-toddler:checked]/age:flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-900 border border-primary/15 text-sm">
                <span class="text-base shrink-0">🎨</span>
                <span class="font-semibold text-primary shrink-0">Simple</span>
                <span class="text-slate-500 dark:text-slate-400">— Extra thick outlines, big shapes, perfect for little hands</span>
              </div>
              <div class="hidden group-has-[.age-beginner:checked]/age:flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-900 border border-primary/15 text-sm">
                <span class="text-base shrink-0">✏️</span>
                <span class="font-semibold text-primary shrink-0">Beginner</span>
                <span class="text-slate-500 dark:text-slate-400">— Bold lines with light backgrounds, easy to color</span>
              </div>
              <div class="hidden group-has-[.age-kids:checked]/age:flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-900 border border-primary/15 text-sm">
                <span class="text-base shrink-0">🖌️</span>
                <span class="font-semibold text-primary shrink-0">Medium</span>
                <span class="text-slate-500 dark:text-slate-400">— Standard detail with fun scenes</span>
              </div>
              <div class="hidden group-has-[.age-tweens:checked]/age:flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-900 border border-primary/15 text-sm">
                <span class="text-base shrink-0">🎭</span>
                <span class="font-semibold text-primary shrink-0">Advanced</span>
                <span class="text-slate-500 dark:text-slate-400">— Fine detail, rich scenes, satisfying to complete</span>
              </div>
            </div>
          </div>

          <!-- Themes -->
          <div class="mb-10">
            <div class="flex justify-between items-end mb-4 px-1">
              <h3 class="text-slate-900 dark:text-white text-xl font-bold">Choose a Magical Theme</h3>
            </div>
            
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              <label class="cursor-pointer group relative">
                <input type="radio" name="theme" class="peer sr-only" checked />
                <div class="flex flex-col items-center p-4 rounded-2xl border-2 border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-primary/50 peer-checked:border-primary peer-checked:bg-primary/5 transition-all h-full">
                  <div class="size-12 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                    <span class="material-symbols-outlined">pets</span>
                  </div>
                  <span class="font-bold text-slate-700 dark:text-slate-200 text-sm">Animals</span>
                </div>
                <div class="absolute top-2 right-2 opacity-0 peer-checked:opacity-100 text-primary transition-opacity">
                  <span class="material-symbols-outlined text-xl">check_circle</span>
                </div>
              </label>

              <label class="cursor-pointer group relative">
                <input type="radio" name="theme" class="peer sr-only" />
                <div class="flex flex-col items-center p-4 rounded-2xl border-2 border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-primary/50 peer-checked:border-primary peer-checked:bg-primary/5 transition-all h-full">
                  <div class="size-12 rounded-full bg-green-100 text-green-600 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                    <span class="material-symbols-outlined">forest</span>
                  </div>
                  <span class="font-bold text-slate-700 dark:text-slate-200 text-sm">Dinosaurs</span>
                </div>
                <div class="absolute top-2 right-2 opacity-0 peer-checked:opacity-100 text-primary transition-opacity">
                  <span class="material-symbols-outlined text-xl">check_circle</span>
                </div>
              </label>

              <label class="cursor-pointer group relative">
                <input type="radio" name="theme" class="peer sr-only" />
                <div class="flex flex-col items-center p-4 rounded-2xl border-2 border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-primary/50 peer-checked:border-primary peer-checked:bg-primary/5 transition-all h-full">
                  <div class="size-12 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                    <span class="material-symbols-outlined">star</span>
                  </div>
                  <span class="font-bold text-slate-700 dark:text-slate-200 text-sm">Unicorns</span>
                </div>
                <div class="absolute top-2 right-2 opacity-0 peer-checked:opacity-100 text-primary transition-opacity">
                  <span class="material-symbols-outlined text-xl">check_circle</span>
                </div>
              </label>

              <label class="cursor-pointer group relative">
                <input type="radio" name="theme" class="peer sr-only" />
                <div class="flex flex-col items-center p-4 rounded-2xl border-2 border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-primary/50 peer-checked:border-primary peer-checked:bg-primary/5 transition-all h-full">
                  <div class="size-12 rounded-full bg-primary/10 text-primary flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                    <span class="material-symbols-outlined">rocket_launch</span>
                  </div>
                  <span class="font-bold text-slate-700 dark:text-slate-200 text-sm">Space</span>
                </div>
                <div class="absolute top-2 right-2 opacity-0 peer-checked:opacity-100 text-primary transition-opacity">
                  <span class="material-symbols-outlined text-xl">check_circle</span>
                </div>
              </label>

              <label class="cursor-pointer group relative">
                <input type="radio" name="theme" class="peer sr-only" />
                <div class="flex flex-col items-center p-4 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-800/50 hover:border-primary/50 peer-checked:border-primary peer-checked:bg-primary/5 transition-all h-full">
                  <div class="size-12 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-500 dark:text-slate-400 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                    <span class="material-symbols-outlined">add</span>
                  </div>
                  <span class="font-bold text-slate-700 dark:text-slate-200 text-sm">Custom</span>
                </div>
                <div class="absolute top-2 right-2 opacity-0 peer-checked:opacity-100 text-primary transition-opacity">
                  <span class="material-symbols-outlined text-xl">check_circle</span>
                </div>
              </label>
            </div>
            
            <div class="mt-4">
              <label class="cursor-pointer group relative block">
                <input type="radio" name="theme" class="peer sr-only" />
                <div class="flex items-center gap-4 p-4 rounded-2xl border-2 border-slate-100 dark:border-slate-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-900 hover:border-primary/50 peer-checked:border-primary peer-checked:ring-1 peer-checked:ring-primary/20 transition-all">
                  <div class="size-14 rounded-xl bg-white dark:bg-slate-700 text-primary shadow-sm flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-3xl">add_a_photo</span>
                  </div>
                  <div class="flex flex-col flex-1">
                    <div class="flex items-center gap-2">
                       <span class="font-bold text-slate-900 dark:text-white text-base">Import from Photo</span>
                       <span class="px-2 py-0.5 rounded-full bg-primary text-white text-[10px] font-bold uppercase tracking-wider">New</span>
                    </div>
                    <span class="text-sm text-slate-500 dark:text-slate-400">Create a coloring book from your own photos or drawings</span>
                  </div>
                  <div class="shrink-0 size-8 rounded-full border-2 border-slate-300 dark:border-slate-600 peer-checked:border-primary peer-checked:bg-primary text-white flex items-center justify-center transition-colors">
                    <span class="material-symbols-outlined text-lg opacity-0 peer-checked:opacity-100">check</span>
                  </div>
                </div>
              </label>
            </div>
          </div>

          <!-- Page Count -->
          <div class="mb-12">
            <h3 class="text-slate-900 dark:text-white text-xl font-bold mb-4 ml-1">Number of Pages</h3>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <label class="cursor-pointer">
                <input type="radio" name="pages" class="peer sr-only" checked />
                <div class="p-4 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 hover:bg-white dark:hover:bg-slate-700 peer-checked:border-primary peer-checked:ring-1 peer-checked:ring-primary peer-checked:bg-white dark:peer-checked:bg-slate-800 transition-all flex items-center gap-3">
                  <div class="size-10 rounded-full bg-white dark:bg-slate-900 shadow-sm flex items-center justify-center font-bold text-slate-900 dark:text-white border border-slate-100 dark:border-slate-600 peer-checked:text-primary peer-checked:border-primary">6</div>
                  <div class="flex flex-col">
                    <span class="text-sm font-bold text-slate-900 dark:text-white peer-checked:text-primary">Short Story</span>
                    <span class="text-xs text-slate-500">Perfect for quick fun</span>
                  </div>
                </div>
              </label>
              
              <label class="cursor-pointer">
                <input type="radio" name="pages" class="peer sr-only" />
                <div class="p-4 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 hover:bg-white dark:hover:bg-slate-700 peer-checked:border-primary peer-checked:ring-1 peer-checked:ring-primary peer-checked:bg-white dark:peer-checked:bg-slate-800 transition-all flex items-center gap-3">
                  <div class="size-10 rounded-full bg-white dark:bg-slate-900 shadow-sm flex items-center justify-center font-bold text-slate-900 dark:text-white border border-slate-100 dark:border-slate-600 peer-checked:text-primary peer-checked:border-primary">10</div>
                  <div class="flex flex-col">
                    <span class="text-sm font-bold text-slate-900 dark:text-white peer-checked:text-primary">Standard</span>
                    <span class="text-xs text-slate-500">Most popular choice</span>
                  </div>
                </div>
              </label>
              
              <label class="cursor-pointer">
                <input type="radio" name="pages" class="peer sr-only" />
                <div class="p-4 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 hover:bg-white dark:hover:bg-slate-700 peer-checked:border-primary peer-checked:ring-1 peer-checked:ring-primary peer-checked:bg-white dark:peer-checked:bg-slate-800 transition-all flex items-center gap-3">
                  <div class="size-10 rounded-full bg-white dark:bg-slate-900 shadow-sm flex items-center justify-center font-bold text-slate-900 dark:text-white border border-slate-100 dark:border-slate-600 peer-checked:text-primary peer-checked:border-primary">15</div>
                  <div class="flex flex-col">
                    <span class="text-sm font-bold text-slate-900 dark:text-white peer-checked:text-primary">Epic Journey</span>
                    <span class="text-xs text-slate-500">For avid colorists</span>
                  </div>
                </div>
              </label>
            </div>
          </div>

          <!-- Story Prompt -->
          <div class="mb-10">
            <h3 class="text-slate-900 dark:text-white text-xl font-bold mb-4 ml-1">Personalize the Story</h3>
            <label class="flex flex-col gap-1 mb-3 ml-1" for="story-prompt">
              <span class="text-slate-900 dark:text-white text-base font-bold">Tell us about your child</span>
              <span class="text-slate-400 dark:text-slate-500 text-xs font-medium">Optional — the more you share, the more personal the story</span>
            </label>
            <div class="relative">
              <textarea
                id="story-prompt"
                v-model="storyPrompt"
                maxlength="300"
                rows="3"
                placeholder="e.g. Emma loves horses, her best friend is Sofia, and she wants to be a vet someday..."
                class="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white p-4 pb-7 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-slate-400 resize-y text-sm leading-relaxed"
                style="max-height: 160px;"
              ></textarea>
              <span class="absolute bottom-2 right-3 text-[11px] text-slate-400 pointer-events-none tabular-nums">{{ storyPrompt.length }}/300</span>
            </div>
            <div class="flex flex-wrap gap-2 mt-3">
              <button type="button" @click="appendChip('Loves animals')" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-xs font-medium hover:bg-primary/10 hover:text-primary transition-colors">
                <span class="material-symbols-outlined text-sm">add</span>
                Loves animals
              </button>
              <button type="button" @click="appendChip('Has a best friend')" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-xs font-medium hover:bg-primary/10 hover:text-primary transition-colors">
                <span class="material-symbols-outlined text-sm">add</span>
                Has a best friend
              </button>
              <button type="button" @click="appendChip('Wants to be a')" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-xs font-medium hover:bg-primary/10 hover:text-primary transition-colors">
                <span class="material-symbols-outlined text-sm">add</span>
                Wants to be a...
              </button>
              <button type="button" @click="appendChip('Favorite color is')" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-xs font-medium hover:bg-primary/10 hover:text-primary transition-colors">
                <span class="material-symbols-outlined text-sm">add</span>
                Favorite color
              </button>
              <button type="button" @click="appendChip('Has a pet')" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-xs font-medium hover:bg-primary/10 hover:text-primary transition-colors">
                <span class="material-symbols-outlined text-sm">add</span>
                Has a pet
              </button>
              <button type="button" @click="appendChip('Goes on adventures')" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-xs font-medium hover:bg-primary/10 hover:text-primary transition-colors">
                <span class="material-symbols-outlined text-sm">add</span>
                Goes on adventures
              </button>
            </div>
          </div>

          <!-- Submit -->
          <div class="flex flex-col md:flex-row items-center justify-between gap-6 pt-6 border-t border-slate-100 dark:border-slate-800">
            <div class="text-sm text-slate-500 dark:text-slate-400 flex items-center gap-2">
              <span class="material-symbols-outlined text-lg text-primary">info</span>
              This will use 1 book credit from your quota.
            </div>
            
            <RouterLink to="/generating" class="w-full md:w-auto min-w-[240px] h-16 bg-gradient-to-r from-primary to-accent-purple hover:from-primary-dark hover:to-primary active:scale-95 transition-all rounded-full text-white text-lg font-bold flex items-center justify-center gap-3 shadow-xl shadow-primary/30">
              <span class="material-symbols-outlined">magic_button</span>
              <span>Generate Book</span>
            </RouterLink>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
