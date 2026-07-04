import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import type { User } from 'firebase/auth'

// Flush pending microtasks + the awaited fetch.
const tick = () => new Promise((r) => setTimeout(r, 0))

const getMe = vi.fn()
vi.mock('@/api/auth', () => ({ getMe: (...args: unknown[]) => getMe(...args) }))

async function freshModules() {
  // The composable holds module-level singleton state (shared widget); reset it
  // between tests so each starts from a clean slate.
  vi.resetModules()
  setActivePinia(createPinia())
  const { useBookQuota } = await import('@/composables/useBookQuota')
  const { useAuthStore } = await import('@/stores/auth')
  return { useBookQuota, useAuthStore }
}

function signIn(store: ReturnType<Awaited<ReturnType<typeof freshModules>>['useAuthStore']>, uid: string) {
  store.setUser({ uid } as User)
}

beforeEach(() => {
  getMe.mockReset()
})

describe('useBookQuota', () => {
  it('displays quota from the backend on success (no direct Firestore read)', async () => {
    getMe.mockResolvedValue({ subscription_tier: 'free', books_generated_total: 1 })
    const { useBookQuota, useAuthStore } = await freshModules()
    const store = useAuthStore()
    signIn(store, 'user-a') // sign in BEFORE using the composable

    const q = useBookQuota() // immediate watcher fires fetch since uid is present
    await tick()

    expect(getMe).toHaveBeenCalledTimes(1)
    expect(q.status.value).toBe('ready')
    expect(q.isReady.value).toBe(true)
    // free tier, 1 generated → 1/1 used, at limit
    expect(q.booksLimit.value).toBe(1)
    expect(q.booksUsed.value).toBe(1)
    expect(q.isAtLimit.value).toBe(true)
  })

  it('surfaces an error state and does NOT fall back to zero on fetch failure', async () => {
    getMe.mockRejectedValue(new Error('client is offline'))
    const { useBookQuota, useAuthStore } = await freshModules()
    const store = useAuthStore()
    signIn(store, 'user-b')

    const q = useBookQuota()
    await tick()

    expect(q.status.value).toBe('error')
    expect(q.isError.value).toBe(true)
    expect(q.isReady.value).toBe(false) // consumers must NOT render numbers
    expect(q.errorMessage.value).toBe('Unable to load usage')
    // The old bug set booksRemaining=1/booksLimit=1 (→ "0 used") on error. Assert
    // we never present a valid-looking "0 used": either it's not ready, or if a
    // number were read it must not read as a fresh 0/1.
    expect(q.isReady.value).toBe(false)
  })

  it('re-fetches when the signed-in user changes after mount', async () => {
    getMe.mockResolvedValue({ subscription_tier: 'free', books_generated_total: 0 })
    const { useBookQuota, useAuthStore } = await freshModules()
    const store = useAuthStore()

    const q = useBookQuota() // no user yet → stays idle, no fetch
    await tick()
    expect(getMe).toHaveBeenCalledTimes(0)
    expect(q.status.value).toBe('idle')

    signIn(store, 'user-c') // sign in AFTER mount → watcher triggers fetch
    await tick()
    expect(getMe).toHaveBeenCalledTimes(1)
    expect(q.status.value).toBe('ready')

    signIn(store, 'user-d') // switch account → re-fetch
    await tick()
    expect(getMe).toHaveBeenCalledTimes(2)
  })

  it('resets to idle on sign-out (no stale numbers)', async () => {
    getMe.mockResolvedValue({ subscription_tier: 'family', subscription_active: true, books_generated_this_month: 2 })
    const { useBookQuota, useAuthStore } = await freshModules()
    const store = useAuthStore()
    signIn(store, 'user-e')
    const q = useBookQuota()
    await tick()
    expect(q.status.value).toBe('ready')

    store.clearUser() // sign out
    await tick()
    expect(q.status.value).toBe('idle')
    expect(q.booksLimit.value).toBe(0)
  })
})
