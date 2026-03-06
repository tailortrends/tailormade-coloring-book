import { ref } from 'vue'
import { useBooksStore } from '@/stores/books'
import type { BookGenerateRequest } from '@/types/book'

export function useBookGeneration() {
  const booksStore = useBooksStore()

  const loading = ref(false)
  const error = ref<string | null>(null)

  async function generate(params: BookGenerateRequest) {
    loading.value = true
    error.value = null

    try {
      const book = await booksStore.generateBook(params)
      return book
    } catch (err) {
      error.value = booksStore.error
      throw err
    } finally {
      loading.value = false
    }
  }

  function cancel() {
    booksStore.resetGeneration()
  }

  return {
    loading,
    error,
    generate,
    cancel,
  }
}
