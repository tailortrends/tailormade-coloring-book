import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export type UserTier = 'free' | 'pro' | 'premium'

export const useAuthStore = defineStore('auth', () => {
  const uid = ref<string | null>(null)
  const email = ref<string | null>(null)
  const displayName = ref<string | null>(null)
  const tier = ref<UserTier>('free')
  const creditsRemaining = ref(0)

  const isAuthenticated = computed(() => uid.value !== null)
  const isPro = computed(() => tier.value === 'pro' || tier.value === 'premium')

  function setUser(user: { uid: string; email: string | null; displayName: string | null }) {
    uid.value = user.uid
    email.value = user.email
    displayName.value = user.displayName
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

  function clearUser() {
    uid.value = null
    email.value = null
    displayName.value = null
    tier.value = 'free'
    creditsRemaining.value = 0
  }

  return {
    uid,
    email,
    displayName,
    tier,
    creditsRemaining,
    isAuthenticated,
    isPro,
    setUser,
    setTier,
    setCredits,
    decrementCredits,
    clearUser,
  }
})
