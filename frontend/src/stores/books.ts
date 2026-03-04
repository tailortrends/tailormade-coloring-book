import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Book } from '@/types/book'

export type GenerationPhase = 'idle' | 'planning' | 'generating' | 'ready'

export const useBooksStore = defineStore('books', () => {
  const books = ref<Book[]>([])
  const activeBook = ref<Book | null>(null)
  const generationStatus = ref<GenerationPhase>('idle')
  const generationProgress = ref(0)

  const loading = ref(false)
  const error = ref<string | null>(null)

  const isGenerating = computed(
    () => generationStatus.value === 'planning' || generationStatus.value === 'generating',
  )

  function setBooks(newBooks: Book[]) {
    books.value = newBooks
  }

  function addBook(book: Book) {
    books.value.unshift(book)
  }

  function removeBook(bookId: string) {
    books.value = books.value.filter((b) => b.book_id !== bookId)
    if (activeBook.value?.book_id === bookId) {
      activeBook.value = null
    }
  }

  function setActiveBook(book: Book | null) {
    activeBook.value = book
  }

  function setGenerationStatus(status: GenerationPhase) {
    generationStatus.value = status
  }

  function setGenerationProgress(progress: number) {
    generationProgress.value = Math.min(100, Math.max(0, progress))
  }

  function resetGeneration() {
    generationStatus.value = 'idle'
    generationProgress.value = 0
  }

  function setLoading(state: boolean) {
    loading.value = state
  }

  function setError(msg: string | null) {
    error.value = msg
  }

  return {
    books,
    activeBook,
    generationStatus,
    generationProgress,
    loading,
    error,
    isGenerating,
    setBooks,
    addBook,
    removeBook,
    setActiveBook,
    setGenerationStatus,
    setGenerationProgress,
    resetGeneration,
    setLoading,
    setError,
  }
})
