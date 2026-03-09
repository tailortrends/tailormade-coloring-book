import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Book, BookGenerateRequest } from '@/types/book'
import * as booksApi from '@/api/books'
import { ApiError } from '@/api/client'

export type GenerationPhase = 'idle' | 'planning' | 'generating' | 'ready'

export interface QuotaInfo {
  used: number
  limit: number
  remaining: number
  reset_date: string | null
  tier: string
  is_subscription_active: boolean
}

export const useBooksStore = defineStore('books', () => {
  const books = ref<Book[]>([])
  const activeBook = ref<Book | null>(null)
  const generationStatus = ref<GenerationPhase>('idle')
  const generationProgress = ref(0)

  const loading = ref(false)
  const error = ref<string | null>(null)
  const quota = ref<QuotaInfo | null>(null)
  let generationAbort: AbortController | null = null

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

  /** Fetch all books for the current user */
  async function fetchBooks() {
    loading.value = true
    error.value = null
    try {
      const result = await booksApi.list()
      books.value = result
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch books'
    } finally {
      loading.value = false
    }
  }

  /** Cancel an in-progress generation request */
  function cancelGeneration() {
    if (generationAbort) {
      generationAbort.abort()
      generationAbort = null
    }
    resetGeneration()
    loading.value = false
    error.value = null
  }

  /** Generate a new book via POST /api/v1/books/generate */
  async function generateBook(params: BookGenerateRequest) {
    // Cancel any previous in-flight request
    if (generationAbort) generationAbort.abort()
    generationAbort = new AbortController()

    loading.value = true
    error.value = null
    generationStatus.value = 'generating'
    generationProgress.value = 0

    try {
      const book = await booksApi.generate(params, generationAbort.signal)
      activeBook.value = book
      books.value.unshift(book)
      generationStatus.value = 'ready'
      return book
    } catch (err) {
      generationStatus.value = 'idle'
      // Silently swallow user-initiated cancellations
      if (err instanceof ApiError && err.statusText === 'Request Cancelled') {
        return undefined
      }
      if (err instanceof ApiError) {
        if (err.status === 429) {
          const body = err.body as { detail?: { message?: string; quota?: QuotaInfo } }
          const quotaData = body?.detail?.quota
          if (quotaData) {
            quota.value = quotaData
            const resetPart = quotaData.reset_date
              ? ` Resets ${new Date(quotaData.reset_date).toLocaleDateString()}.`
              : ''
            error.value = `You've used ${quotaData.used} of ${quotaData.limit} books on the ${quotaData.tier} plan.${resetPart} Upgrade to keep creating!`
          } else {
            error.value = "You've used your free book! Upgrade to keep creating personalized books for your little artist."
          }
        } else if (err.status === 400 || err.status === 422) {
          const detail = (err.body as { detail?: string })?.detail
          if (detail && detail.toLowerCase().startsWith('content not allowed')) {
            error.value = `Our safety filter flagged your request: ${detail.replace(/^content not allowed:\s*/i, '')}. Please try a different prompt.`
          } else if (detail) {
            error.value = detail
          } else {
            error.value = 'Your request was not accepted. Try a different story prompt.'
          }
        } else if (err.status === 0) {
          // Timeout or network error from our AbortController handling
          const detail = (err.body as { detail?: string })?.detail
          error.value = detail || 'Unable to reach the server. Please try again.'
        } else {
          error.value = 'Something went wrong. Please try again.'
        }
      } else {
        error.value = err instanceof Error ? err.message : 'Something went wrong. Please try again.'
      }
      throw err
    } finally {
      generationAbort = null
      loading.value = false
    }
  }

  return {
    books,
    activeBook,
    generationStatus,
    generationProgress,
    loading,
    error,
    quota,
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
    fetchBooks,
    generateBook,
    cancelGeneration,
  }
})
