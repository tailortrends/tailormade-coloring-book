<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'

const invoices = [
  { date: "Oct 15, 2023", plan: "Pro Plan - Monthly", period: "Oct 15 - Nov 15", amount: "$7.99" },
  { date: "Sep 15, 2023", plan: "Pro Plan - Monthly", period: "Sep 15 - Oct 15", amount: "$7.99" },
  { date: "Aug 15, 2023", plan: "Pro Plan - Monthly", period: "Aug 15 - Sep 15", amount: "$7.99" },
  { date: "Jul 15, 2023", plan: "Starter Plan", period: "One-time purchase", amount: "$4.99" },
]
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-1 w-full max-w-[1200px] mx-auto px-6 py-10 md:px-10 lg:py-12">
      <!-- Header -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 mb-10">
        <div class="flex flex-col gap-3 max-w-2xl">
          <h1 class="text-slate-900 dark:text-white text-3xl md:text-4xl font-extrabold tracking-tight">Billing &amp; Receipts</h1>
          <p class="text-slate-500 dark:text-slate-400 text-lg">Manage your subscription, update payment methods, and download your receipt history.</p>
        </div>
      </div>

      <!-- Cards Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
        <!-- Current Plan Card -->
        <div class="lg:col-span-2 bg-white dark:bg-slate-900 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col md:flex-row justify-between gap-8 relative overflow-hidden">
          <div class="absolute -right-10 -top-10 w-40 h-40 bg-primary/5 rounded-full blur-3xl"></div>
          <div class="flex flex-col justify-between gap-6 z-10">
            <div>
              <div class="flex items-center gap-3 mb-2">
                <span class="material-symbols-outlined text-primary">verified</span>
                <p class="text-slate-500 dark:text-slate-400 text-sm font-bold uppercase tracking-wider">Current Plan</p>
              </div>
              <h3 class="text-3xl font-bold mb-1">Pro Plan</h3>
              <p class="text-slate-500 dark:text-slate-400 text-lg">$7.99/mo</p>
            </div>
            <div>
              <p class="text-sm font-bold mb-1">Next Billing Date</p>
              <p class="text-slate-500 dark:text-slate-400 text-sm">Your next charge will be on <span class="text-slate-900 dark:text-white font-medium">November 15, 2023</span>.</p>
            </div>
          </div>
          <div class="flex flex-col justify-end items-start md:items-end gap-4 z-10">
            <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-bold uppercase tracking-wide">
              <span class="size-2 rounded-full bg-green-500"></span>
              Active
            </span>
            <div class="flex gap-3">
              <button class="h-10 px-5 rounded-full border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-bold text-sm hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                Change Plan
              </button>
              <button class="h-10 px-5 rounded-full bg-primary hover:bg-primary-dark text-white font-bold text-sm transition-colors shadow-lg shadow-primary/20">
                Manage Subscription
              </button>
            </div>
          </div>
        </div>

        <!-- Payment Method Card -->
        <div class="bg-white dark:bg-slate-900 rounded-xl p-8 shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col justify-between gap-6">
          <div>
            <div class="flex items-center gap-3 mb-6">
              <div class="size-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <span class="material-symbols-outlined">credit_card</span>
              </div>
              <p class="text-lg font-bold">Payment Method</p>
            </div>
            <div class="flex items-center gap-4 mb-2">
              <div class="w-12 h-8 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded flex items-center justify-center text-xs font-bold text-primary">
                VISA
              </div>
              <div>
                <p class="font-bold">Visa ending in 4242</p>
                <p class="text-slate-500 dark:text-slate-400 text-xs">Expires 12/2025</p>
              </div>
            </div>
          </div>
          <button class="w-full h-10 flex items-center justify-center gap-2 rounded-full bg-slate-100 dark:bg-slate-800 text-sm font-bold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
            <span class="material-symbols-outlined text-lg">edit</span>
            Update Payment Method
          </button>
        </div>
      </div>

      <!-- Billing History -->
      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
        <div class="p-6 border-b border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <h3 class="text-xl font-bold">Billing History</h3>
          <div class="relative">
            <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-lg">search</span>
            <input class="pl-10 pr-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 w-full sm:w-64" placeholder="Search invoices..." type="text" />
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-slate-50/50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
                <th class="py-4 px-6 text-xs font-bold text-slate-500 uppercase tracking-wider">Date</th>
                <th class="py-4 px-6 text-xs font-bold text-slate-500 uppercase tracking-wider">Plan Details</th>
                <th class="py-4 px-6 text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                <th class="py-4 px-6 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Amount</th>
                <th class="py-4 px-6 text-xs font-bold text-slate-500 uppercase tracking-wider text-center">Receipt</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
              <tr v-for="invoice in invoices" :key="invoice.date + invoice.plan" class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                <td class="py-4 px-6 text-sm font-medium">{{ invoice.date }}</td>
                <td class="py-4 px-6">
                  <div class="flex flex-col">
                    <span class="text-sm font-bold">{{ invoice.plan }}</span>
                    <span class="text-slate-500 dark:text-slate-400 text-xs">{{ invoice.period }}</span>
                  </div>
                </td>
                <td class="py-4 px-6">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400">
                    Paid
                  </span>
                </td>
                <td class="py-4 px-6 text-sm font-bold text-right">{{ invoice.amount }}</td>
                <td class="py-4 px-6 text-center">
                  <button class="text-slate-400 hover:text-primary transition-colors p-2 rounded-full hover:bg-primary/10">
                    <span class="material-symbols-outlined">download</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="px-6 py-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <p class="text-sm text-slate-500">Showing <span class="font-bold text-slate-900 dark:text-white">1-4</span> of <span class="font-bold text-slate-900 dark:text-white">12</span> transactions</p>
          <div class="flex gap-2">
            <button class="px-3 py-1 text-sm font-bold text-slate-400 cursor-not-allowed" disabled>Previous</button>
            <button class="px-3 py-1 text-sm font-bold text-primary hover:text-primary-dark">Next</button>
          </div>
        </div>
      </div>
    </main>

    <AppFooter />
  </div>
</template>
