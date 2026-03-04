import { ref } from 'vue'
import { useBooksStore } from '@/stores/books'
import { useLibrary } from './useLibrary'
import * as booksApi from '@/api/books'
import type { Book, CreateBookParams } from '@/types/book'

const POLL_INTERVAL_MS = 2000

export function useBookGeneration() {
  const booksStore = useBooksStore()
  const { fetchIfStale, findMatches } = useLibrary()

  const loading = ref(false)
  const error = ref<string | null>(null)

  let pollTimer: ReturnType<typeof setInterval> | null = null

  function stopPolling() {
    if (pollTimer !== null) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  async function pollStatus(bookId: string): Promise<Book> {
    return new Promise((resolve, reject) => {
      pollTimer = setInterval(async () => {
        try {
          const status = await booksApi.getStatus(bookId)
          booksStore.setGenerationProgress(status.progress)

          if (status.done) {
            stopPolling()
            const book = await booksApi.getById(bookId)
            resolve(book)
          }
        } catch (err) {
          stopPolling()
          reject(err)
        }
      }, POLL_INTERVAL_MS)
    })
  }

  async function generate(params: CreateBookParams): Promise<Book> {
    loading.value = true
    error.value = null
    booksStore.setError(null)
    booksStore.setGenerationProgress(0)

    try {
      // Phase 1: Check library for pre-existing matches
      booksStore.setGenerationStatus('planning')
      await fetchIfStale()

      const matches = findMatches(params.theme, params.age_range, params.page_count)

      let book: Book

      if (matches.length >= params.page_count) {
        // Full match — assemble from library
        booksStore.setGenerationProgress(50)
        book = await booksApi.createFromLibrary({
          theme: params.theme,
          age_range: params.age_range,
          page_count: params.page_count,
          image_ids: matches.map((m) => m.image_id),
        })
        booksStore.setGenerationProgress(100)
      } else {
        // Miss — generate fresh then poll
        booksStore.setGenerationStatus('generating')
        const created = await booksApi.create(params)
        booksStore.setGenerationProgress(10)

        book = await pollStatus(created.book_id)
      }

      booksStore.setGenerationStatus('ready')
      booksStore.setActiveBook(book)
      booksStore.addBook(book)

      return book
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Generation failed'
      error.value = message
      booksStore.setError(message)
      booksStore.resetGeneration()
      throw err
    } finally {
      loading.value = false
      stopPolling()
    }
  }

  function cancel() {
    stopPolling()
    booksStore.resetGeneration()
  }

  return {
    loading,
    error,
    generate,
    cancel,
  }
}
