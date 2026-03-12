import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from 'firebase/auth'

export type UserTier = 'free' | 'single' | 'family' | 'teacher'

const ADMIN_UIDS = ((import.meta.env.VITE_ADMIN_UIDS as string) || '')
  .split(',')
  .map(u => u.trim())
  .filter(Boolean)

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isReady = ref(false)
  const tier = ref<UserTier>('free')
  const subscriptionActive = ref(false)
  const creditsRemaining = ref(0)
  const booksGeneratedThisMonth = ref(0)
  const booksGeneratedTotal = ref(0)

  const isAuthenticated = computed(() => !!user.value)
  const isSubscribed = computed(() => subscriptionActive.value && (tier.value === 'family' || tier.value === 'teacher'))
  const isPro = computed(() => isSubscribed.value)
  const isAdmin = computed(() => !!user.value && ADMIN_UIDS.includes(user.value.uid))
  const displayName = computed(() => user.value?.displayName || user.value?.email || 'User')
  const photoURL = computed(() => user.value?.photoURL || null)
  const email = computed(() => user.value?.email || null)
  const uid = computed(() => user.value?.uid || null)

  function setUser(newUser: User) {
    user.value = newUser
    isReady.value = true
  }

  function clearUser() {
    user.value = null
    isReady.value = true
    tier.value = 'free'
    subscriptionActive.value = false
    creditsRemaining.value = 0
    booksGeneratedThisMonth.value = 0
    booksGeneratedTotal.value = 0
  }

  function setTier(newTier: UserTier) {
    tier.value = newTier
  }

  function setSubscriptionActive(active: boolean) {
    subscriptionActive.value = active
  }

  function setCredits(credits: number) {
    creditsRemaining.value = credits
  }

  function setBooksGenerated(thisMonth: number, total: number) {
    booksGeneratedThisMonth.value = thisMonth
    booksGeneratedTotal.value = total
  }

  function decrementCredits() {
    if (creditsRemaining.value > 0) {
      creditsRemaining.value--
    }
  }

  /**
   * Sync all subscription fields from /api/v1/auth/me response.
   */
  function syncFromMe(data: {
    subscription_tier?: string
    subscription_active?: boolean
    one_time_credits?: number
    books_generated_this_month?: number
    books_generated_total?: number
  }) {
    const t = data.subscription_tier as UserTier | undefined
    if (t) tier.value = t
    subscriptionActive.value = data.subscription_active ?? false
    creditsRemaining.value = data.one_time_credits ?? 0
    booksGeneratedThisMonth.value = data.books_generated_this_month ?? 0
    booksGeneratedTotal.value = data.books_generated_total ?? 0
  }

  return {
    user,
    isReady,
    uid,
    email,
    displayName,
    photoURL,
    tier,
    subscriptionActive,
    creditsRemaining,
    booksGeneratedThisMonth,
    booksGeneratedTotal,
    isAuthenticated,
    isSubscribed,
    isPro,
    isAdmin,
    setUser,
    clearUser,
    setTier,
    setSubscriptionActive,
    setCredits,
    setBooksGenerated,
    decrementCredits,
    syncFromMe,
  }
})
