import { ref, computed, watch, effectScope } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getMe } from '@/api/auth'
import { computeQuota } from '@/utils/quota'

export type QuotaStatus = 'idle' | 'loading' | 'ready' | 'error'

// Shared singleton state — the quota widget appears in several places (header,
// create page, profile) and should present one consistent value.
const status = ref<QuotaStatus>('idle')
const errorMessage = ref<string | null>(null)
const booksLimitRef = ref(0)
const booksRemainingRef = ref(0)
const isAtLimitRef = ref(false)

let inFlight = false
let watcherStarted = false
// Detached scope so the driving watcher survives individual component unmounts.
const scope = effectScope(true)

export function useBookQuota() {
  const authStore = useAuthStore()

  const isLoading = computed(() => status.value === 'loading')
  const isError = computed(() => status.value === 'error')
  const isReady = computed(() => status.value === 'ready')
  // Backward-compatible alias for existing consumers that destructured `loading`.
  const loading = isLoading

  const booksRemaining = computed(() => booksRemainingRef.value)
  const isAtLimit = computed(() => isAtLimitRef.value)
  const booksLimit = computed(() => booksLimitRef.value)
  const booksUsed = computed(() => Math.max(0, booksLimitRef.value - booksRemainingRef.value))
  const percentUsed = computed(() =>
    booksLimitRef.value > 0 ? Math.round((booksUsed.value / booksLimitRef.value) * 100) : 0,
  )

  async function fetchQuota() {
    if (!authStore.uid || inFlight) return
    inFlight = true
    status.value = 'loading'
    errorMessage.value = null
    try {
      const q = computeQuota(await getMe())
      booksLimitRef.value = q.limit
      booksRemainingRef.value = q.remaining
      isAtLimitRef.value = q.isAtLimit
      status.value = 'ready'
    } catch (err) {
      // NO fail-to-zero fallback. On failure we surface an explicit error state
      // and deliberately do NOT write numbers that would render as a valid-
      // looking "0 used" — consumers must show the error/loading state instead.
      console.error('Failed to fetch quota', err)
      errorMessage.value = 'Unable to load usage'
      status.value = 'error'
    } finally {
      inFlight = false
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

  // Register exactly one driving watcher. Fetch once a user is present and
  // re-fetch whenever the signed-in user changes (login after mount, account
  // switch, logout→login) — replacing the old one-shot onMounted that only ran
  // if the user happened to already be authenticated at mount time.
  if (!watcherStarted) {
    watcherStarted = true
    scope.run(() => {
      watch(
        () => authStore.uid,
        (uid) => {
          if (uid) {
            fetchQuota()
          } else {
            // Signed out — reset to idle, don't leave stale numbers around.
            status.value = 'idle'
            errorMessage.value = null
            booksLimitRef.value = 0
            booksRemainingRef.value = 0
            isAtLimitRef.value = false
          }
        },
        { immediate: true },
      )
    })
  }

  return {
    // status
    status,
    isLoading,
    loading,
    isError,
    isReady,
    errorMessage,
    // values (only meaningful when isReady)
    booksUsed,
    booksRemaining,
    isAtLimit,
    booksLimit,
    percentUsed,
    // actions
    fetchQuota,
    refresh: fetchQuota,
    decrementRemaining,
  }
}
