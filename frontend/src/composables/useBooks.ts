import { useBooksStore } from '@/stores/books'
import * as booksApi from '@/api/books'

export function useBooks() {
  const store = useBooksStore()

  async function fetchAll() {
    store.setLoading(true)
    store.setError(null)
    try {
      const books = await booksApi.list()
      store.setBooks(books)
    } catch (err) {
      store.setError(err instanceof Error ? err.message : 'Failed to fetch books')
      throw err
    } finally {
      store.setLoading(false)
    }
  }

  async function deleteBook(bookId: string) {
    store.setError(null)
    try {
      await booksApi.deleteBook(bookId)
      store.removeBook(bookId)
    } catch (err) {
      store.setError(err instanceof Error ? err.message : 'Failed to delete book')
      throw err
    }
  }

  async function downloadPDF(bookId: string) {
    store.setError(null)
    try {
      const book = await booksApi.getById(bookId)
      if (!book.pdf_url) {
        throw new Error('PDF not available yet')
      }
      window.open(book.pdf_url, '_blank')
    } catch (err) {
      store.setError(err instanceof Error ? err.message : 'Failed to download PDF')
      throw err
    }
  }

  return {
    books: store.books,
    loading: store.loading,
    error: store.error,
    fetchAll,
    deleteBook,
    downloadPDF,
  }
}
