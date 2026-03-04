<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col overflow-hidden">
    <AppHeader />

    <main class="flex flex-1 w-full h-[calc(100vh-65px)] overflow-hidden">
      <!-- Left Sidebar: Settings -->
      <aside class="w-80 flex flex-col border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-y-auto shrink-0 z-10">
        <div class="p-6 pb-2">
          <h1 class="text-xl font-bold mb-1">Layout Settings</h1>
          <p class="text-sm text-slate-500">Customize your PDF export</p>
        </div>
        <div class="px-6 py-4 space-y-8">
          <!-- Layout Mode -->
          <section>
            <h3 class="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
              <span class="material-symbols-outlined text-base">grid_view</span> Page Layout
            </h3>
            <div class="flex flex-col gap-3">
              <label class="cursor-pointer">
                <input checked class="peer sr-only" name="layout_mode" type="radio" />
                <div class="flex items-center p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50 peer-checked:border-primary peer-checked:bg-primary/5 transition-all">
                  <div class="w-10 h-12 bg-slate-200 dark:bg-slate-600 rounded flex items-center justify-center mr-3 text-slate-400">
                    <span class="material-symbols-outlined text-xl">crop_portrait</span>
                  </div>
                  <div class="flex-1">
                    <div class="text-sm font-medium">Single Image</div>
                    <div class="text-xs text-slate-500">Best for detailed coloring</div>
                  </div>
                </div>
              </label>
              <label class="cursor-pointer">
                <input class="peer sr-only" name="layout_mode" type="radio" />
                <div class="flex items-center p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50 peer-checked:border-primary peer-checked:bg-primary/5 transition-all">
                  <div class="w-10 h-12 bg-slate-200 dark:bg-slate-600 rounded flex items-center justify-center mr-3 text-slate-400">
                    <span class="material-symbols-outlined text-xl">view_agenda</span>
                  </div>
                  <div class="flex-1">
                    <div class="text-sm font-medium">Two Images</div>
                    <div class="text-xs text-slate-500">Economical printing</div>
                  </div>
                </div>
              </label>
              <label class="cursor-pointer">
                <input class="peer sr-only" name="layout_mode" type="radio" />
                <div class="flex items-center p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50 peer-checked:border-primary peer-checked:bg-primary/5 transition-all">
                  <div class="w-10 h-12 bg-slate-200 dark:bg-slate-600 rounded flex items-center justify-center mr-3 text-slate-400">
                    <span class="material-symbols-outlined text-xl">grid_view</span>
                  </div>
                  <div class="flex-1">
                    <div class="text-sm font-medium">Collage Mode</div>
                    <div class="text-xs text-slate-500">Fun mix of sizes</div>
                  </div>
                </div>
              </label>
            </div>
          </section>

          <div class="h-px bg-slate-100 dark:bg-slate-800 w-full"></div>

          <!-- Paper Size -->
          <section>
            <h3 class="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
              <span class="material-symbols-outlined text-base">description</span> Paper Size
            </h3>
            <div class="grid grid-cols-2 gap-3">
              <label class="cursor-pointer">
                <input checked class="peer sr-only" name="paper_size" type="radio" />
                <div class="flex flex-col items-center justify-center p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 peer-checked:border-primary peer-checked:bg-primary/5 transition-all h-20 text-center">
                  <span class="text-sm font-medium">Letter</span>
                  <span class="text-[10px] text-slate-500">8.5 x 11 in</span>
                </div>
              </label>
              <label class="cursor-pointer">
                <input class="peer sr-only" name="paper_size" type="radio" />
                <div class="flex flex-col items-center justify-center p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 peer-checked:border-primary peer-checked:bg-primary/5 transition-all h-20 text-center">
                  <span class="text-sm font-medium">A4</span>
                  <span class="text-[10px] text-slate-500">210 x 297 mm</span>
                </div>
              </label>
            </div>
          </section>

          <!-- Margins -->
          <section>
            <h3 class="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
              <span class="material-symbols-outlined text-base">format_align_center</span> Margins
            </h3>
            <div class="flex rounded-lg bg-slate-100 dark:bg-slate-800 p-1">
              <label class="flex-1 cursor-pointer">
                <input class="peer sr-only" name="margins" type="radio" />
                <div class="text-center py-1.5 px-2 rounded-md text-xs font-medium text-slate-500 peer-checked:bg-white dark:peer-checked:bg-slate-700 peer-checked:text-primary peer-checked:shadow-sm transition-all">Narrow</div>
              </label>
              <label class="flex-1 cursor-pointer">
                <input checked class="peer sr-only" name="margins" type="radio" />
                <div class="text-center py-1.5 px-2 rounded-md text-xs font-medium text-slate-500 peer-checked:bg-white dark:peer-checked:bg-slate-700 peer-checked:text-primary peer-checked:shadow-sm transition-all">Standard</div>
              </label>
              <label class="flex-1 cursor-pointer">
                <input class="peer sr-only" name="margins" type="radio" />
                <div class="text-center py-1.5 px-2 rounded-md text-xs font-medium text-slate-500 peer-checked:bg-white dark:peer-checked:bg-slate-700 peer-checked:text-primary peer-checked:shadow-sm transition-all">Wide</div>
              </label>
            </div>
          </section>

          <div class="h-px bg-slate-100 dark:bg-slate-800 w-full"></div>

          <!-- Page Elements -->
          <section>
            <h3 class="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
              <span class="material-symbols-outlined text-base">tune</span> Page Elements
            </h3>
            <div class="space-y-2">
              <label class="text-sm text-slate-700 dark:text-slate-200 block">Footer Title</label>
              <input class="w-full text-sm rounded-lg border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 focus:border-primary focus:ring-primary px-3 py-2" placeholder="Enter book title..." type="text" value="My Awesome Adventure" />
            </div>
          </section>
        </div>
      </aside>

      <!-- Main Content: Preview -->
      <section class="flex-1 flex flex-col bg-slate-100 dark:bg-slate-950 relative">
        <!-- Toolbar -->
        <div class="h-14 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6 shrink-0 z-10">
          <div class="flex items-center gap-2">
            <button class="p-2 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition-colors">
              <span class="material-symbols-outlined text-xl">zoom_out</span>
            </button>
            <span class="text-sm font-medium text-slate-600 dark:text-slate-300 w-12 text-center">45%</span>
            <button class="p-2 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition-colors">
              <span class="material-symbols-outlined text-xl">zoom_in</span>
            </button>
          </div>
          <div class="flex items-center gap-2">
            <button class="p-2 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition-colors">
              <span class="material-symbols-outlined text-xl">chevron_left</span>
            </button>
            <span class="text-sm font-medium text-slate-600 dark:text-slate-300">Page 1 of 12</span>
            <button class="p-2 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition-colors">
              <span class="material-symbols-outlined text-xl">chevron_right</span>
            </button>
          </div>
          <div class="w-[100px]"></div>
        </div>

        <!-- Preview Area -->
        <div class="flex-1 overflow-auto flex justify-center p-10">
          <div class="bg-white shadow-xl w-[500px] h-[647px] relative shrink-0 flex flex-col">
            <div class="flex-1 p-12 flex flex-col items-center">
              <div class="w-full h-full border-2 border-dashed border-slate-200 rounded-lg flex items-center justify-center bg-slate-50 relative overflow-hidden">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuABd69BFB0qb-Ge6nwixGunYFGI0y9PmpbaEl9xii3CczZQJv2LrnbLk4SzueNol5xg-PhdKUyDyKhMyhM1HM6-h9JnYvVPp85u5F6_luIS1-BD9t4pHbsnhEoC04HdgjX3VsSk99v4P5hQJmbK2yC88zthf694S8Ek17is_y3nzO3ASDN_2Y8k0y2MdA2UuM-YoZWlbGSxyUpOttAaEyvWb-dBsi4K81el6GPJoHp9ZnyQYRMWuJqAxWBP3aj9pxokASO2tzoRl80l" alt="Coloring page preview" class="w-full h-full object-contain opacity-80" />
              </div>
            </div>
            <div class="h-16 px-12 flex items-center justify-between border-t border-transparent text-slate-400 text-sm">
              <span>My Awesome Adventure</span>
              <span>1</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Right Sidebar: Summary -->
      <aside class="w-80 bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 flex flex-col shrink-0 z-10">
        <div class="p-6 border-b border-slate-100 dark:border-slate-800">
          <h2 class="text-lg font-bold mb-4">Book Summary</h2>
          <div class="space-y-4">
            <div class="flex items-center gap-3">
              <div class="size-10 rounded bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center text-primary">
                <span class="material-symbols-outlined">auto_stories</span>
              </div>
              <div>
                <p class="text-sm font-medium">12 Pages</p>
                <p class="text-xs text-slate-500">Total length</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div class="size-10 rounded bg-green-50 dark:bg-green-900/20 flex items-center justify-center text-green-600 dark:text-green-400">
                <span class="material-symbols-outlined">save</span>
              </div>
              <div>
                <p class="text-sm font-medium">~4.2 MB</p>
                <p class="text-xs text-slate-500">Estimated file size</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div class="size-10 rounded bg-purple-50 dark:bg-purple-900/20 flex items-center justify-center text-purple-600 dark:text-purple-400">
                <span class="material-symbols-outlined">print</span>
              </div>
              <div>
                <p class="text-sm font-medium">High Quality</p>
                <p class="text-xs text-slate-500">300 DPI Optimization</p>
              </div>
            </div>
          </div>
        </div>
        <div class="flex-1 p-6">
          <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 border border-slate-100 dark:border-slate-700 mb-6">
            <h4 class="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">Export Checklist</h4>
            <ul class="space-y-2">
              <li class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
                <span class="material-symbols-outlined text-green-500 text-lg">check_circle</span>
                Margins checked
              </li>
              <li class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
                <span class="material-symbols-outlined text-green-500 text-lg">check_circle</span>
                Images optimized
              </li>
              <li class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
                <span class="material-symbols-outlined text-green-500 text-lg">check_circle</span>
                Pagination ready
              </li>
            </ul>
          </div>
        </div>
        <div class="p-6 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900">
          <button class="w-full bg-primary hover:bg-blue-600 text-white font-semibold py-3.5 px-4 rounded-xl shadow-lg shadow-blue-200 dark:shadow-blue-900/20 transition-all flex items-center justify-center gap-2 group">
            <span class="material-symbols-outlined group-hover:animate-bounce">download</span>
            Download PDF
          </button>
          <p class="text-center text-xs text-slate-400 mt-3">Ready for home printing</p>
        </div>
      </aside>
    </main>
  </div>
</template>
