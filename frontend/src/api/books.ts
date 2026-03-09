import { api } from './client'
import type { Book, BookGenerateRequest } from '@/types/book'

export function generate(params: BookGenerateRequest, signal?: AbortSignal): Promise<Book> {
  return api.post<Book>('/api/v1/books/generate', params, { timeout: 5 * 60_000, signal })
}

export function getById(bookId: string): Promise<Book> {
  return api.get<Book>(`/api/v1/books/${bookId}`)
}

export function list(): Promise<Book[]> {
  return api.get<Book[]>('/api/v1/books/')
}

export function deleteBook(bookId: string): Promise<void> {
  return api.delete<void>(`/api/v1/books/${bookId}`)
}
