<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex items-center justify-center relative overflow-hidden">
    <!-- Decorative Background -->
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
      <div class="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] bg-primary/10 rounded-full blur-[100px]"></div>
      <div class="absolute top-[30%] -right-[10%] w-[40%] h-[40%] bg-primary/10 rounded-full blur-[100px]"></div>
    </div>

    <div class="relative w-full max-w-5xl mx-auto p-4 md:p-8">
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-100 dark:border-slate-800 overflow-hidden flex flex-col md:flex-row">
        <!-- Left Side: Visual -->
        <div class="w-full md:w-5/12 bg-primary/5 dark:bg-primary/10 p-8 flex flex-col items-center justify-center text-center relative overflow-hidden">
          <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuC5eqRSQzKTnpGien1HvlCEONd_tIPg0flkzGgGV1oR-nm0zLzhewzKzUzPFRY3eJVuQLanN612eSv7Qk8mt6nUhGHsu9hOTPHnVxjN3mA-avIJPWIHn2RFR893juj3dw8qs2CiJKDE5Wwktf5hRH4cjX9-0XssPYEC5M8v1btDvsuTHYbuK9ZUhq7406fabN9Df2aQkx5rwIyrlmCfqcp-fB90jow04h6r8frv57wacfqBE7Aq_ntu3fi3fm9EwXwWEh-D_K0bHb0P" alt="Art supplies" class="w-full max-w-[280px] aspect-[4/3] rounded-xl object-cover mb-6 shadow-sm border border-white/50" />
          <h2 class="text-2xl font-bold mb-2">Unlock Imagination</h2>
          <p class="text-sm text-slate-600 dark:text-slate-400 mb-8 max-w-xs mx-auto">
            Create unlimited magical stories with your personalized characters. Upgrade now and never stop dreaming!
          </p>
          <div class="w-full bg-white dark:bg-slate-800 p-5 rounded-lg border border-slate-100 dark:border-slate-700 shadow-sm">
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm font-semibold text-slate-700 dark:text-slate-200">Free Limit Reached</span>
              <span class="text-xs font-medium text-red-500 bg-red-50 dark:bg-red-900/20 px-2 py-1 rounded-full">100% Full</span>
            </div>
            <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3 mb-2">
              <div class="bg-gradient-to-r from-red-400 to-red-500 h-3 rounded-full w-full"></div>
            </div>
            <p class="text-xs text-slate-500 text-left">2 of 2 books created this month</p>
          </div>
        </div>

        <!-- Right Side: Pricing -->
        <div class="w-full md:w-7/12 p-6 md:p-10 flex flex-col overflow-y-auto">
          <div class="text-center md:text-left mb-8">
            <h1 class="text-3xl font-bold mb-2">Continue your journey</h1>
            <p class="text-slate-500 dark:text-slate-400">Choose a plan to create more personalized books.</p>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
            <!-- Pro Plan -->
            <div class="relative flex flex-col rounded-xl border-2 border-primary bg-primary/5 dark:bg-primary/10 p-5 transition-transform hover:scale-[1.02] duration-200">
              <div class="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide shadow-md">
                Most Popular
              </div>
              <div class="mb-4 pt-2">
                <h3 class="text-lg font-bold text-primary">Pro</h3>
                <div class="flex items-baseline gap-1 mt-1">
                  <span class="text-3xl font-extrabold">$7.99</span>
                  <span class="text-sm font-medium text-slate-500">/mo</span>
                </div>
              </div>
              <ul class="flex-1 space-y-3 mb-6">
                <li class="flex items-start gap-3 text-sm">
                  <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
                  10 books per month
                </li>
                <li class="flex items-start gap-3 text-sm">
                  <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
                  High resolution PDF
                </li>
                <li class="flex items-start gap-3 text-sm">
                  <span class="material-symbols-outlined text-primary text-[20px]">check_circle</span>
                  No watermarks
                </li>
              </ul>
              <button class="w-full py-3 px-4 rounded-full bg-primary hover:bg-primary/90 text-white font-bold text-sm shadow-lg shadow-primary/30 transition-all flex items-center justify-center gap-2 group">
                Upgrade to Pro
                <span class="material-symbols-outlined text-[18px] group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </button>
            </div>

            <!-- Premium Plan -->
            <div class="flex flex-col rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 hover:border-slate-300 dark:hover:border-slate-600 transition-colors">
              <div class="mb-4 pt-2">
                <h3 class="text-lg font-bold">Premium</h3>
                <div class="flex items-baseline gap-1 mt-1">
                  <span class="text-3xl font-extrabold">$14.99</span>
                  <span class="text-sm font-medium text-slate-500">/mo</span>
                </div>
              </div>
              <ul class="flex-1 space-y-3 mb-6">
                <li class="flex items-start gap-3 text-sm">
                  <span class="material-symbols-outlined text-slate-400 text-[20px]">check</span>
                  <strong>Unlimited</strong> books
                </li>
                <li class="flex items-start gap-3 text-sm">
                  <span class="material-symbols-outlined text-slate-400 text-[20px]">check</span>
                  Priority generation
                </li>
                <li class="flex items-start gap-3 text-sm">
                  <span class="material-symbols-outlined text-slate-400 text-[20px]">check</span>
                  Early access features
                </li>
                <li class="flex items-start gap-3 text-sm">
                  <span class="material-symbols-outlined text-slate-400 text-[20px]">check</span>
                  Commercial license
                </li>
              </ul>
              <button class="w-full py-3 px-4 rounded-full bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 font-bold text-sm transition-colors">
                Select Premium
              </button>
            </div>
          </div>
          <div class="mt-8 text-center">
            <p class="text-xs text-slate-400">Cancel anytime. Secure payment processing.</p>
            <RouterLink to="/dashboard" class="mt-2 inline-block text-sm text-slate-500 hover:text-slate-800 dark:hover:text-slate-300 font-medium underline decoration-slate-300 underline-offset-4">
              Maybe later
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
