import { api } from './client'
import type { LibraryIndex } from '@/types/book'

export function getIndex(): Promise<LibraryIndex> {
  return api.get<LibraryIndex>('/api/library/index')
}
