<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <nav class="fixed bottom-0 left-0 right-0 max-w-md mx-auto bg-white/80 dark:bg-slate-900/80 backdrop-blur-lg border-t border-slate-100 dark:border-slate-800 px-6 py-4 flex justify-between items-center z-40">
    <RouterLink to="/dashboard" class="flex flex-col items-center gap-1" :class="$route.name === 'dashboard' ? 'text-primary' : 'text-slate-400 dark:text-slate-500 hover:text-primary transition-colors'">
      <span class="material-symbols-outlined" :class="{ 'filled': $route.name === 'dashboard' }">home</span>
      <span class="text-[10px] font-bold">Home</span>
    </RouterLink>

    <RouterLink to="/library" class="flex flex-col items-center gap-1" :class="$route.name === 'library' ? 'text-primary' : 'text-slate-400 dark:text-slate-500 hover:text-primary transition-colors'">
      <span class="material-symbols-outlined" :class="{ 'filled': $route.name === 'library' }">auto_stories</span>
      <span class="text-[10px] font-bold">Library</span>
    </RouterLink>

    <div class="w-12"></div> <!-- Spacer for FAB -->

    <RouterLink to="/gallery" class="flex flex-col items-center gap-1" :class="$route.name === 'gallery' ? 'text-primary' : 'text-slate-400 dark:text-slate-500 hover:text-primary transition-colors'">
      <span class="material-symbols-outlined" :class="{ 'filled': $route.name === 'gallery' }">auto_awesome</span>
      <span class="text-[10px] font-bold">Gallery</span>
    </RouterLink>

    <RouterLink to="/settings" class="flex flex-col items-center gap-1" :class="$route.name === 'settings' ? 'text-primary' : 'text-slate-400 dark:text-slate-500 hover:text-primary transition-colors'">
      <span class="material-symbols-outlined" :class="{ 'filled': $route.name === 'settings' }">settings</span>
      <span class="text-[10px] font-bold">Settings</span>
    </RouterLink>
  </nav>
</template>
