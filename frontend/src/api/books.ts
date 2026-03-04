import { api } from './client'
import type { Book, CreateBookParams, GenerationStatus } from '@/types/book'

export function create(params: CreateBookParams): Promise<Book> {
  return api.post<Book>('/api/books', params)
}

export function createFromLibrary(params: {
  theme: string
  age_range: string
  page_count: number
  image_ids: string[]
}): Promise<Book> {
  return api.post<Book>('/api/books/from-library', params)
}

export function getById(bookId: string): Promise<Book> {
  return api.get<Book>(`/api/books/${bookId}`)
}

export function getStatus(bookId: string): Promise<GenerationStatus> {
  return api.get<GenerationStatus>(`/api/books/${bookId}/status`)
}

export function list(): Promise<Book[]> {
  return api.get<Book[]>('/api/books')
}

export function deleteBook(bookId: string): Promise<void> {
  return api.delete<void>(`/api/books/${bookId}`)
}

export function getPDFUrl(bookId: string): Promise<{ url: string }> {
  return api.get<{ url: string }>(`/api/books/${bookId}`)
}
