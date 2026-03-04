<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <header class="sticky top-0 z-50 w-full bg-white/80 dark:bg-background-dark/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 py-3 lg:px-10 transition-all duration-300">
    <div class="mx-auto flex max-w-7xl items-center justify-between">
      <RouterLink to="/" class="flex items-center gap-3 text-slate-900 dark:text-white group cursor-pointer">
        <div class="flex size-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-accent-purple text-white shadow-lg shadow-primary/30 group-hover:shadow-primary/50 transition-all group-hover:rotate-6">
          <span class="material-symbols-outlined text-2xl">palette</span>
        </div>
        <h2 class="text-xl font-bold tracking-tight">ColorMagic AI</h2>
      </RouterLink>

      <nav class="hidden md:flex items-center gap-8">
        <RouterLink to="/community" class="text-slate-600 dark:text-slate-300 text-sm font-semibold hover:text-primary transition-colors">Gallery</RouterLink>
        <a href="/#how-it-works" class="text-slate-600 dark:text-slate-300 text-sm font-semibold hover:text-primary transition-colors">How it works</a>
        <RouterLink to="/pricing" class="text-slate-600 dark:text-slate-300 text-sm font-semibold hover:text-primary transition-colors">Pricing</RouterLink>
      </nav>

      <div class="flex items-center gap-4">
        <RouterLink to="/login" class="hidden sm:block text-slate-900 dark:text-white text-sm font-semibold hover:text-primary transition-colors">
          Log in
        </RouterLink>
        <RouterLink to="/signup" class="flex items-center justify-center rounded-full bg-slate-900 dark:bg-white hover:bg-slate-800 dark:hover:bg-slate-200 transition-all px-6 py-2.5 text-white dark:text-slate-900 text-sm font-bold shadow-lg shadow-slate-900/20">
          <span class="truncate">Sign Up Free</span>
        </RouterLink>
      </div>
    </div>
  </header>
</template>
