<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'

const referrals = [
  { name: "Emma Johnson", initials: "EJ", color: "bg-orange-100 text-orange-600", date: "Oct 24, 2023", status: "Signed Up", reward: "+1 Credit" },
  { name: "Michael P.", initials: "MP", color: "bg-blue-100 text-blue-600", date: "Oct 22, 2023", status: "Pending", reward: "-" },
  { name: "Sarah Lee", initials: "SL", color: "bg-pink-100 text-pink-600", date: "Oct 20, 2023", status: "Signed Up", reward: "+1 Credit" },
]
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-grow">
      <div class="px-4 md:px-10 lg:px-40 flex flex-1 justify-center py-10 w-full">
        <div class="flex flex-col max-w-[1100px] flex-1 w-full gap-12">
          <!-- Hero Section -->
          <div class="flex flex-col md:flex-row gap-12 items-center">
            <div class="flex-1">
              <div class="flex flex-col gap-6 text-left">
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 w-fit">
                  <span class="material-symbols-outlined text-primary text-sm">stars</span>
                  <span class="text-primary text-xs font-bold uppercase tracking-wide">Referral Program</span>
                </div>
                <h1 class="text-4xl md:text-5xl font-extrabold leading-[1.1] tracking-tight">
                  Share the Magic, <br class="hidden sm:block" />
                  <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent-purple">Get Free Books!</span>
                </h1>
                <p class="text-slate-500 dark:text-slate-400 text-lg font-normal leading-relaxed max-w-lg">
                  For every friend who signs up using your link, you get <strong class="text-slate-900 dark:text-white">1 extra book credit</strong> this month! Spread the joy of personalized coloring books.
                </p>

                <!-- Referral Link Card -->
                <div class="mt-4 p-1 rounded-[24px] bg-gradient-to-r from-primary/40 to-accent-purple/40 w-full max-w-xl">
                  <div class="bg-white dark:bg-slate-900 rounded-[20px] p-6 shadow-lg">
                    <h3 class="text-sm font-bold uppercase tracking-wider mb-3 ml-1">Your Unique Referral Link</h3>
                    <div class="flex flex-col sm:flex-row items-center gap-3">
                      <div class="flex-1 w-full bg-background-light dark:bg-background-dark border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 font-medium truncate">
                        colormagic.ai/ref/sarah-j-123
                      </div>
                      <button class="w-full sm:w-auto flex items-center justify-center gap-2 rounded-xl h-12 px-6 bg-slate-900 dark:bg-white text-white dark:text-slate-900 text-sm font-bold hover:opacity-90 transition-opacity">
                        <span class="material-symbols-outlined text-lg">content_copy</span>
                        <span>Copy Link</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex-1 flex justify-center">
              <div class="relative w-full aspect-square max-w-[400px]">
                <div class="absolute inset-0 bg-primary/20 rounded-full blur-3xl transform translate-x-4 translate-y-4"></div>
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuAoTsY6H4f5hWDVPrAEK8EXz3HTwgpQLWq2GhmeKKXUcZEGn0QZFotJ31FerYLSXK5R4MD5BKimJmprU8bA0HB8V8fS98vXhczjaQ4bYEqC30mHpuiLaeq8Lv5xyBGRsx8_O61FQCW9KeR9gmJv4-7VNgRc7p9Pi1UTGqkKSd6vZK-s7JigJdJBIc6mOeCq5rD_CSckwqnxUFeS9wCz5yrwVUWJXiNBy9sf5FK7sPBIJ7EJuhWj4dxoAdLdE9R830yx59ipWGw2m1lg" alt="Children coloring" class="relative w-full h-full rounded-3xl shadow-2xl object-cover" />
              </div>
            </div>
          </div>

          <!-- How it Works -->
          <div class="py-10">
            <h3 class="text-2xl font-bold text-center mb-12">How It Works</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div class="flex flex-col items-center text-center gap-4 p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 shadow-sm hover:shadow-md transition-shadow">
                <div class="size-16 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400 mb-2">
                  <span class="material-symbols-outlined text-3xl">share</span>
                </div>
                <h4 class="text-lg font-bold">1. Invite Friends</h4>
                <p class="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">Send your unique link to friends via WhatsApp, Email, or Social Media.</p>
              </div>
              <div class="flex flex-col items-center text-center gap-4 p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 shadow-sm hover:shadow-md transition-shadow">
                <div class="size-16 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 mb-2">
                  <span class="material-symbols-outlined text-3xl">person_add</span>
                </div>
                <h4 class="text-lg font-bold">2. They Sign Up</h4>
                <p class="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">Your friend creates a free account to start making their own coloring books.</p>
              </div>
              <div class="flex flex-col items-center text-center gap-4 p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 shadow-sm hover:shadow-md transition-shadow">
                <div class="size-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 dark:text-green-400 mb-2">
                  <span class="material-symbols-outlined text-3xl">card_giftcard</span>
                </div>
                <h4 class="text-lg font-bold">3. You Get Credits</h4>
                <p class="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">Earn 1 book credit instantly for every successful referral. No limits!</p>
              </div>
            </div>
          </div>

          <!-- Referral Status -->
          <div class="bg-white dark:bg-slate-900 rounded-2xl p-8 shadow-sm border border-slate-100 dark:border-slate-800">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
              <div>
                <h3 class="text-xl font-bold">Referral Status</h3>
                <p class="text-slate-500 dark:text-slate-400 text-sm mt-1">Track your invites and earnings</p>
              </div>
              <div class="flex gap-4">
                <div class="bg-background-light dark:bg-background-dark px-6 py-3 rounded-2xl flex flex-col items-center min-w-[120px]">
                  <span class="text-xs uppercase font-bold text-slate-500 tracking-wider">Invited</span>
                  <span class="text-2xl font-extrabold">12</span>
                </div>
                <div class="bg-background-light dark:bg-background-dark px-6 py-3 rounded-2xl flex flex-col items-center min-w-[120px] ring-2 ring-primary/20">
                  <span class="text-xs uppercase font-bold text-primary tracking-wider">Earned</span>
                  <span class="text-2xl font-extrabold text-primary">5</span>
                </div>
              </div>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full min-w-[600px]">
                <thead>
                  <tr class="border-b border-slate-100 dark:border-slate-700">
                    <th class="text-left pb-4 text-xs font-bold text-slate-500 uppercase tracking-wider pl-4">Friend</th>
                    <th class="text-left pb-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Date Invited</th>
                    <th class="text-left pb-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                    <th class="text-right pb-4 text-xs font-bold text-slate-500 uppercase tracking-wider pr-4">Reward</th>
                  </tr>
                </thead>
                <tbody class="text-sm">
                  <tr v-for="ref in referrals" :key="ref.name" class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors border-t border-slate-50 dark:border-slate-800">
                    <td class="py-4 pl-4 font-medium flex items-center gap-3">
                      <div class="size-8 rounded-full flex items-center justify-center font-bold text-xs" :class="ref.color">{{ ref.initials }}</div>
                      {{ ref.name }}
                    </td>
                    <td class="py-4 text-slate-500">{{ ref.date }}</td>
                    <td class="py-4">
                      <span
                        class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold"
                        :class="ref.status === 'Signed Up' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'"
                      >
                        <span class="size-1.5 rounded-full" :class="ref.status === 'Signed Up' ? 'bg-green-500' : 'bg-slate-400'"></span>
                        {{ ref.status }}
                      </span>
                    </td>
                    <td class="py-4 pr-4 text-right font-bold" :class="ref.reward !== '-' ? 'text-primary' : 'text-slate-500'">{{ ref.reward }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </main>

    <AppFooter />
  </div>
</template>
