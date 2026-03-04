import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useLibraryStore } from '@/stores/library'
import * as libraryApi from '@/api/library'
import type { LibraryImage } from '@/types/book'

export function useLibrary() {
  const store = useLibraryStore()
  const { themes, loading, error } = storeToRefs(store)

  async function fetchIfStale() {
    if (!store.isStale) return

    store.setLoading(true)
    store.setError(null)
    try {
      const index = await libraryApi.getIndex()
      store.setIndex(index.themes, index.images)
    } catch (err) {
      store.setError(err instanceof Error ? err.message : 'Failed to fetch library')
      throw err
    } finally {
      store.setLoading(false)
    }
  }

  function findMatches(theme: string, ageRange: string, count: number): LibraryImage[] {
    return store.libraryImages
      .filter((img) => img.theme === theme && img.age_range === ageRange)
      .slice(0, count)
  }

  const hasImages = computed(() => store.libraryImages.length > 0)

  return {
    themes,
    loading,
    error,
    hasImages,
    fetchIfStale,
    findMatches,
  }
}
