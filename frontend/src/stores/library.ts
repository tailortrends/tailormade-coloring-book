import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { LibraryImage } from '@/types/book'

const STALE_MS = 5 * 60 * 1000 // 5 minutes

export const useLibraryStore = defineStore('library', () => {
  const libraryImages = ref<LibraryImage[]>([])
  const themes = ref<string[]>([])
  const lastFetched = ref<number | null>(null)

  const loading = ref(false)
  const error = ref<string | null>(null)

  const isStale = computed(() => {
    if (lastFetched.value === null) return true
    return Date.now() - lastFetched.value > STALE_MS
  })

  function setIndex(newThemes: string[], images: LibraryImage[]) {
    themes.value = newThemes
    libraryImages.value = images
    lastFetched.value = Date.now()
  }

  function setLoading(state: boolean) {
    loading.value = state
  }

  function setError(msg: string | null) {
    error.value = msg
  }

  return {
    libraryImages,
    themes,
    lastFetched,
    loading,
    error,
    isStale,
    setIndex,
    setLoading,
    setError,
  }
})
