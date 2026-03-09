<script setup lang="ts">
import { RouterLink } from 'vue-router'

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    books: '1 book total',
    features: ['6 pages per book', 'Basic themes', 'PDF download'],
    current: true,
    highlight: false,
  },
  {
    name: 'Family',
    price: '$9',
    period: '/month',
    books: '12 books/mo',
    features: ['Up to 15 pages', 'All themes', 'Priority generation', 'Child profiles'],
    current: false,
    highlight: true,
  },
  {
    name: 'Teacher',
    price: '$19',
    period: '/month',
    books: '25 books/mo',
    features: ['Up to 20 pages', 'All themes', 'Classroom sets', 'Bulk export', 'Priority support'],
    current: false,
    highlight: false,
  },
]
</script>

<template>
  <div class="bg-white dark:bg-slate-900 rounded-[2rem] p-6 md:p-10 shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-800 text-center">
    <div class="mb-8">
      <div class="inline-flex items-center justify-center size-16 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-600 mb-4">
        <span class="material-symbols-outlined text-3xl">auto_stories</span>
      </div>
      <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">You've used all your books!</h2>
      <p class="text-slate-500 dark:text-slate-400 max-w-md mx-auto">Upgrade your plan to keep creating magical coloring books for your kids.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div
        v-for="plan in plans"
        :key="plan.name"
        class="relative rounded-2xl border p-5 text-left transition-all"
        :class="plan.highlight
          ? 'border-primary bg-primary/5 shadow-lg shadow-primary/10 ring-1 ring-primary'
          : 'border-slate-200 dark:border-slate-700'"
      >
        <div v-if="plan.highlight" class="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-primary text-white text-xs font-bold">
          Most Popular
        </div>
        <h3 class="text-lg font-bold text-slate-900 dark:text-white mb-1">{{ plan.name }}</h3>
        <div class="flex items-baseline gap-1 mb-1">
          <span class="text-3xl font-black text-slate-900 dark:text-white">{{ plan.price }}</span>
          <span class="text-sm text-slate-500">{{ plan.period }}</span>
        </div>
        <p class="text-sm font-semibold text-primary mb-3">{{ plan.books }}</p>
        <ul class="space-y-1.5 text-sm text-slate-600 dark:text-slate-400">
          <li v-for="f in plan.features" :key="f" class="flex items-center gap-1.5">
            <span class="material-symbols-outlined text-sm text-green-500">check</span>
            {{ f }}
          </li>
        </ul>
        <div v-if="plan.current" class="mt-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Current Plan</div>
      </div>
    </div>

    <RouterLink
      to="/upgrade"
      class="inline-flex items-center justify-center gap-2 h-14 px-8 rounded-full bg-gradient-to-r from-primary to-accent-purple text-white text-lg font-bold shadow-xl shadow-primary/25 hover:from-primary-dark hover:to-primary transition-all"
    >
      <span class="material-symbols-outlined">rocket_launch</span>
      Upgrade Now
    </RouterLink>
  </div>
</template>
