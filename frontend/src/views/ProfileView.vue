<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { useAuthStore } from '@/stores/auth'
import { useBookQuota } from '@/composables/useBookQuota'
import { signOut } from 'firebase/auth'
import { auth } from '@/firebase'
import { useRouter } from 'vue-router'
import { api } from '@/api/client'

const authStore = useAuthStore()
const router = useRouter()
const { booksUsed, booksLimit, booksRemaining, percentUsed } = useBookQuota()

const showDeleteConfirm = ref(false)
const deleteLoading = ref(false)
const signOutLoading = ref(false)
const actionError = ref('')
const copySuccess = ref(false)

async function handleSignOut() {
  actionError.value = ''
  signOutLoading.value = true
  try {
    await signOut(auth)
    authStore.clearUser()
    router.push('/')
  } catch {
    actionError.value = 'Could not sign out. Please try again.'
  } finally {
    signOutLoading.value = false
  }
}

async function handleDeleteAccount() {
  actionError.value = ''
  deleteLoading.value = true
  try {
    // Server-side cascade: deletes every book, child profile, character, and
    // their R2 files, then the user document, and only then the Auth record.
    // (The old client-side deleteUser() removed only the login and orphaned
    // everything else.)
    await api.delete('/api/v1/account')
    // The Auth record is already gone server-side; clear the local session too.
    try {
      await signOut(auth)
    } catch {
      /* token already invalid after deletion — ignore */
    }
    authStore.clearUser()
    router.push('/')
  } catch {
    actionError.value =
      'Could not delete your account. Nothing was changed — please try again, or contact support if this keeps happening.'
  } finally {
    deleteLoading.value = false
  }
}

function copyReferralLink() {
  const link = `${window.location.origin}/?ref=${authStore.uid}`
  navigator.clipboard.writeText(link)
  copySuccess.value = true
  setTimeout(() => { copySuccess.value = false }, 2000)
}
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 min-h-screen font-display">
    <AppHeader />

    <main class="max-w-2xl mx-auto px-4 py-10 space-y-6">
      <h1 class="text-3xl font-bold tracking-tight">My Account</h1>

      <div v-if="actionError" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-300" role="alert">
        {{ actionError }}
      </div>

      <!-- Section 1: User Info -->
      <section class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 p-6 shadow-sm">
        <h2 class="text-lg font-bold mb-4">Profile</h2>
        <div class="flex items-center gap-4">
          <div class="size-16 rounded-full bg-primary/10 flex items-center justify-center overflow-hidden border-2 border-primary/20">
            <img v-if="authStore.photoURL" :src="authStore.photoURL" alt="Avatar" class="w-full h-full object-cover" />
            <span v-else class="text-primary font-bold text-2xl">{{ authStore.displayName.charAt(0).toUpperCase() }}</span>
          </div>
          <div>
            <p class="text-lg font-bold text-slate-900 dark:text-white">{{ authStore.displayName }}</p>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ authStore.email }}</p>
          </div>
        </div>
      </section>

      <!-- Section 2: Subscription & Billing -->
      <section class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 p-6 shadow-sm">
        <h2 class="text-lg font-bold mb-4">Subscription</h2>
        <div class="flex items-center justify-between mb-4">
          <div>
            <p class="text-sm font-semibold text-slate-700 dark:text-slate-200 capitalize">{{ authStore.tier }} Plan</p>
            <p class="text-xs text-slate-500 dark:text-slate-400">{{ booksUsed }}/{{ booksLimit }} books used this period</p>
          </div>
          <RouterLink to="/upgrade" class="px-4 py-2 rounded-full bg-primary text-white text-sm font-bold hover:bg-primary-dark transition-colors">
            Upgrade
          </RouterLink>
        </div>
        <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3 overflow-hidden">
          <div
            class="h-full rounded-full bg-gradient-to-r from-primary to-accent-purple transition-all duration-500"
            :style="{ width: percentUsed + '%' }"
          ></div>
        </div>
        <p class="text-xs text-slate-400 mt-2">{{ booksRemaining }} book{{ booksRemaining === 1 ? '' : 's' }} remaining</p>
      </section>

      <!-- Section 3: Referral -->
      <section class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 p-6 shadow-sm">
        <h2 class="text-lg font-bold mb-2">Refer a Friend</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">Share your link and earn free books when friends sign up.</p>
        <div class="flex gap-2">
          <input
            type="text"
            readonly
            :value="`${$router.options.history.base || ''}/?ref=${authStore.uid}`"
            class="flex-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm text-slate-600 dark:text-slate-300 truncate"
          />
          <button
            @click="copyReferralLink"
            class="px-4 py-2 rounded-lg bg-primary/10 text-primary text-sm font-bold hover:bg-primary/20 transition-colors flex items-center gap-1"
          >
            <span class="material-symbols-outlined text-sm">{{ copySuccess ? 'check' : 'content_copy' }}</span>
            {{ copySuccess ? 'Copied!' : 'Copy' }}
          </button>
        </div>
      </section>

      <!-- Section 4: Leave a Review -->
      <section class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 p-6 shadow-sm">
        <h2 class="text-lg font-bold mb-2">Enjoying TailorMade?</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">We'd love your feedback! Leave a review to help other parents find us.</p>
        <button class="px-5 py-2.5 rounded-full bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 text-sm font-bold hover:bg-amber-200 dark:hover:bg-amber-900/50 transition-colors flex items-center gap-2">
          <span class="material-symbols-outlined text-lg">star</span>
          Leave a Review
        </button>
      </section>

      <!-- Section 5: Danger Zone -->
      <section class="bg-white dark:bg-slate-900 rounded-2xl border border-red-200 dark:border-red-900/50 p-6 shadow-sm">
        <h2 class="text-lg font-bold text-red-600 dark:text-red-400 mb-2">Danger Zone</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">Sign out of your account or permanently delete it. This action cannot be undone.</p>
        <div class="flex flex-wrap gap-3">
          <button
            @click="handleSignOut"
            :disabled="signOutLoading"
            class="px-5 py-2.5 rounded-full border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-sm font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ signOutLoading ? 'Signing out...' : 'Sign Out' }}
          </button>
          <button
            v-if="!showDeleteConfirm"
            @click="showDeleteConfirm = true"
            class="px-5 py-2.5 rounded-full bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 text-sm font-bold hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors"
          >
            Delete Account
          </button>
          <div v-else class="w-full space-y-3">
            <div class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 dark:border-red-900/50 dark:bg-red-900/20">
              <p class="text-sm font-bold text-red-700 dark:text-red-300">This is permanent and cannot be undone.</p>
              <p class="mt-1 text-sm text-red-600 dark:text-red-400">
                Deleting your account permanently removes all of your child profiles, saved books,
                book inputs, and generated coloring pages and PDFs. There is no way to recover them,
                and you will not be able to sign back in.
              </p>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="handleDeleteAccount"
                :disabled="deleteLoading"
                class="px-4 py-2 rounded-full bg-red-600 text-white text-sm font-bold hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {{ deleteLoading ? 'Deleting...' : 'Yes, permanently delete everything' }}
              </button>
              <button
                @click="showDeleteConfirm = false"
                :disabled="deleteLoading"
                class="px-4 py-2 rounded-full border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 text-sm font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
