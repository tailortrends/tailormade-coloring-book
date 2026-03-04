<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="relative flex h-auto min-h-screen w-full flex-col bg-background-light dark:bg-background-dark font-display overflow-x-hidden text-slate-900 dark:text-slate-100 selection:bg-primary/20">
    <AppHeader />
    
    <main class="flex-1">
      <section class="relative px-4 py-16 lg:py-24 overflow-hidden">
        <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-7xl pointer-events-none">
          <div class="absolute top-20 -left-20 w-96 h-96 bg-accent-purple/20 rounded-full blur-3xl opacity-60 mix-blend-multiply dark:mix-blend-screen"></div>
          <div class="absolute bottom-20 -right-20 w-96 h-96 bg-primary/20 rounded-full blur-3xl opacity-60 mix-blend-multiply dark:mix-blend-screen"></div>
          <div class="absolute top-40 right-20 w-72 h-72 bg-accent-pink/20 rounded-full blur-3xl opacity-40 mix-blend-multiply dark:mix-blend-screen"></div>
        </div>

        <div class="mx-auto max-w-7xl">
          <div class="flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
            <!-- Left Text Content -->
            <div class="flex-1 flex flex-col gap-6 text-center lg:text-left z-10">
              <div class="inline-flex items-center gap-2 self-center lg:self-start px-4 py-1.5 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-md transition-shadow cursor-default">
                <span class="relative flex h-2 w-2">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-pink opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2 w-2 bg-accent-pink"></span>
                </span>
                <span class="text-xs font-semibold text-slate-600 dark:text-slate-300">New Feature: Turn Photos into Coloring Pages!</span>
              </div>
              
              <h1 class="text-5xl lg:text-7xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.1]">
                Turn Imagination & Photos into <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary via-accent-purple to-accent-pink">Coloring Magic</span>
              </h1>
              
              <p class="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto lg:mx-0 leading-relaxed">
                Create personalized, printable coloring books instantly. Describe a scene or upload a photo, and our AI crafts the perfect outline for your child to color.
              </p>
              
              <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start pt-4">
                <RouterLink to="/signup" class="flex items-center justify-center gap-2 rounded-full bg-primary hover:bg-primary-dark transition-all px-8 py-4 text-white text-base font-bold shadow-xl shadow-primary/30 hover:scale-105 active:scale-95 group">
                  <span class="material-symbols-outlined group-hover:animate-pulse">auto_awesome</span>
                  <span>Create Your First Book Free</span>
                </RouterLink>
                <RouterLink to="/create" class="flex items-center justify-center gap-2 rounded-full bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 transition-all px-8 py-4 text-slate-900 dark:text-white text-base font-bold border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-md">
                  <span class="material-symbols-outlined text-accent-purple">add_a_photo</span>
                  <span>Try Photo to Sketch</span>
                </RouterLink>
              </div>
            </div>

            <!-- Right Image Content -->
            <div class="flex-1 w-full max-w-[600px] lg:max-w-none perspective-1000">
              <div class="relative transform rotate-y-6 lg:rotate-y-12 transition-transform hover:rotate-y-0 duration-700 ease-out group">
                <div class="absolute -inset-4 bg-gradient-to-r from-primary via-accent-purple to-accent-pink rounded-[2.5rem] opacity-30 blur-2xl group-hover:opacity-40 transition-opacity"></div>
                <div class="relative rounded-[2rem] overflow-hidden shadow-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 aspect-[4/3]">
                  <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuBWcwbtu57U-1J6CTlADAR0iXLvsct014tFUyxYHBTScWONEiMXHn7zNGBcV2VWqNcUURNy52lAo7FR8DwFPqiNi2o5BgSDlSucTZL_Z4Uk9y0dDqeZfF31taXaZzTKiYspCqb1wrthlFMP4zqtmVh9DzC4BxkiRPVef0kPjdW-zMV2NyijQTm8mHI2LdW-8EICAQFq2-WtkhEk8MAu_H0heChMKit0qOzbGcLR59mOQFsGzzjZre1ckDNKATF78CMervbCUVY9BDHd" alt="Child coloring" class="w-full h-full object-cover transform scale-105 group-hover:scale-100 transition-transform duration-700" />
                  <div class="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent pointer-events-none"></div>
                  
                  <div class="absolute bottom-6 left-6 right-6 p-4 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md rounded-2xl border border-slate-200 dark:border-slate-700 shadow-xl flex items-center gap-4">
                    <div class="size-12 rounded-xl bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center text-white shadow-lg shadow-primary/20">
                      <span class="material-symbols-outlined">print</span>
                    </div>
                    <div>
                      <p class="font-bold text-slate-900 dark:text-white text-sm">Print Ready PDF</p>
                      <div class="flex items-center gap-2 mt-0.5">
                        <span class="inline-block size-2 rounded-full bg-green-500 animate-pulse"></span>
                        <p class="text-xs text-slate-500">Processing complete</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- How it works section -->
      <section id="how-it-works" class="py-20 bg-white dark:bg-slate-900 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-20 bg-gradient-to-b from-background-light dark:from-background-dark to-transparent"></div>
        <div class="mx-auto max-w-7xl px-4 relative z-10">
          <div class="text-center mb-16">
            <span class="inline-block px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold tracking-wider uppercase mb-3">Simple Process</span>
            <h2 class="text-3xl lg:text-4xl font-bold text-slate-900 dark:text-white">How the Magic Happens</h2>
            <p class="mt-4 text-slate-600 dark:text-slate-300 max-w-2xl mx-auto text-lg">Creating a unique coloring book is as easy as 1-2-3.</p>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            <div class="hidden md:block absolute top-12 left-16 right-16 h-0.5 bg-gradient-to-r from-primary/20 via-accent-purple/20 to-primary/20 z-0 border-t-2 border-dashed border-slate-200 dark:border-slate-700"></div>
            
            <div class="relative z-10 bg-white dark:bg-slate-800 p-8 rounded-[2rem] border border-slate-100 dark:border-slate-700 shadow-xl shadow-slate-200/50 dark:shadow-none flex flex-col items-center text-center group hover:-translate-y-2 transition-all duration-300">
              <div class="mb-6 size-24 rounded-2xl bg-gradient-to-br from-primary/10 to-blue-50 dark:from-primary/20 dark:to-slate-700 flex items-center justify-center text-primary group-hover:scale-110 transition-transform duration-300 shadow-inner">
                <span class="material-symbols-outlined text-5xl">perm_media</span>
              </div>
              <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-3">1. Describe or Upload</h3>
              <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">Type a prompt like "A cute dinosaur" OR upload a photo.</p>
            </div>
            
            <div class="relative z-10 bg-white dark:bg-slate-800 p-8 rounded-[2rem] border border-slate-100 dark:border-slate-700 shadow-xl shadow-slate-200/50 dark:shadow-none flex flex-col items-center text-center group hover:-translate-y-2 transition-all duration-300">
              <div class="mb-6 size-24 rounded-2xl bg-gradient-to-br from-accent-purple/10 to-purple-50 dark:from-accent-purple/20 dark:to-slate-700 flex items-center justify-center text-accent-purple group-hover:scale-110 transition-transform duration-300 shadow-inner">
                <span class="material-symbols-outlined text-5xl">auto_fix</span>
              </div>
              <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-3">2. AI Magic Generation</h3>
              <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">Our AI engine transforms your text or photo into black & white outlines.</p>
            </div>
            
            <div class="relative z-10 bg-white dark:bg-slate-800 p-8 rounded-[2rem] border border-slate-100 dark:border-slate-700 shadow-xl shadow-slate-200/50 dark:shadow-none flex flex-col items-center text-center group hover:-translate-y-2 transition-all duration-300">
              <div class="mb-6 size-24 rounded-2xl bg-gradient-to-br from-accent-pink/10 to-pink-50 dark:from-accent-pink/20 dark:to-slate-700 flex items-center justify-center text-accent-pink group-hover:scale-110 transition-transform duration-300 shadow-inner">
                <span class="material-symbols-outlined text-5xl">print_connect</span>
              </div>
              <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-3">3. Print & Color</h3>
              <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">Download the PDF instantly. Print it on your home printer!</p>
            </div>
          </div>
        </div>
      </section>
    </main>

    <AppFooter />
  </div>
</template>
