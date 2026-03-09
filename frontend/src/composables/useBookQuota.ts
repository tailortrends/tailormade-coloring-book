import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getFirestore, doc, getDoc } from 'firebase/firestore'

const booksRemainingRef = ref(0)
const isAtLimitRef = ref(false)
const booksLimitRef = ref(1)
const loading = ref(false)
const error = ref<string | null>(null)

export function useBookQuota() {
  const authStore = useAuthStore()
  const db = getFirestore()

  const booksRemaining = computed(() => booksRemainingRef.value)
  const isAtLimit = computed(() => isAtLimitRef.value)
  const booksLimit = computed(() => booksLimitRef.value)
  const booksUsed = computed(() => Math.max(0, booksLimitRef.value - booksRemainingRef.value))
  const percentUsed = computed(() => booksLimitRef.value > 0 ? Math.round((booksUsed.value / booksLimitRef.value) * 100) : 100)

  async function fetchQuota() {
    if (!authStore.uid) return
    loading.value = true
    error.value = null
    try {
      const userSnap = await getDoc(doc(db, 'users', authStore.uid))
      if (userSnap.exists()) {
        const u = userSnap.data()
        
        const tier = u.subscription_tier ?? 'free'
        const active = u.subscription_active ?? false
        const otc = u.one_time_credits ?? 0
        const total = u.books_generated_total ?? 0
        const thisMonth = u.books_generated_this_month ?? 0
        
        let limit = 1
        let remaining = Math.max(0, 1 - total)
        
        if (tier === 'teacher' && active) {
          limit = 25
          remaining = Math.max(0, 25 - thisMonth)
        } else if (tier === 'family' && active) {
          limit = 12
          remaining = Math.max(0, 12 - thisMonth)
        } else if (otc > 0) {
          limit = otc
          remaining = otc
        }

        booksLimitRef.value = limit
        booksRemainingRef.value = remaining
        isAtLimitRef.value = remaining <= 0
      } else {
        // Fallback for missing user doc
        booksLimitRef.value = 1
        booksRemainingRef.value = 1
        isAtLimitRef.value = false
      }
    } catch (err) {
      console.error('Failed to fetch quota', err)
      error.value = 'Could not load quota'
      booksLimitRef.value = 1
      booksRemainingRef.value = 1
      isAtLimitRef.value = false
    } finally {
      loading.value = false
    }
  }

  function decrementRemaining() {
    if (booksRemainingRef.value > 0) {
      booksRemainingRef.value--
      if (booksRemainingRef.value <= 0) {
        isAtLimitRef.value = true
      }
    }
  }

  onMounted(() => {
    if (authStore.isAuthenticated) {
      fetchQuota()
    }
  })

  return {
    loading,
    error,
    booksUsed,
    booksRemaining,
    isAtLimit,
    booksLimit,
    percentUsed,
    fetchQuota,
    decrementRemaining
  }
}
