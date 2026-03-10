import { api } from './client'
import type { LibraryIndex } from '@/types/book'

export function getIndex(): Promise<LibraryIndex> {
  return api.get<LibraryIndex>('/api/library/index')
}

export interface LibraryStats {
  cache: {
    loaded: boolean
    entries: number
    total_images: number
    themes: string[]
  }
  aggregate: {
    total_hits: number
    total_misses: number
    hit_rate_percent: number
    books_with_library_data: number
    estimated_total_savings: number
  }
}

export function getLibraryStats(): Promise<LibraryStats> {
  return api.get<LibraryStats>('/api/library/stats')
}
