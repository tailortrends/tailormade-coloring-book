import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from 'firebase/auth'

export type UserTier = 'free' | 'pro' | 'premium'

const ADMIN_UIDS = ((import.meta.env.VITE_ADMIN_UIDS as string) || '')
  .split(',')
  .map(u => u.trim())
  .filter(Boolean)

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isReady = ref(false)
  const tier = ref<UserTier>('free')
  const creditsRemaining = ref(0)

  const isAuthenticated = computed(() => !!user.value)
  const isPro = computed(() => tier.value === 'pro' || tier.value === 'premium')
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
    creditsRemaining.value = 0
  }

  function setTier(newTier: UserTier) {
    tier.value = newTier
  }

  function setCredits(credits: number) {
    creditsRemaining.value = credits
  }

  function decrementCredits() {
    if (creditsRemaining.value > 0) {
      creditsRemaining.value--
    }
  }

  return {
    user,
    isReady,
    uid,
    email,
    displayName,
    photoURL,
    tier,
    creditsRemaining,
    isAuthenticated,
    isPro,
    isAdmin,
    setUser,
    clearUser,
    setTier,
    setCredits,
    decrementCredits,
  }
})
