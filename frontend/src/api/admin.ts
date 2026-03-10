import { api } from './client'

export interface AdminStats {
  total_books: number
  books_this_month: number
  avg_cost_per_book: number
  total_spend: number
  total_image_spend: number
  total_planning_spend: number
  total_retries: number
  library_hit_rate: number
  top_themes: { theme: string; count: number }[]
  books_by_tier: Record<string, number>
  most_expensive_book: {
    book_id: string
    title: string
    total_cost: number
    retry_count: number
    theme: string
    uid: string
  } | null
}

export interface DailyAnalytics {
  date: string
  books_generated?: number
  pages_generated?: number
  library_hits?: number
  library_misses?: number
  total_cost?: number
  failures?: number
  themes?: Record<string, number>
  tiers?: Record<string, number>
}

export interface FailedBook {
  book_id: string
  uid: string
  title: string
  theme: string
  error: string
  created_at: string
  page_count: number
}

export interface CostEntry {
  book_id: string
  uid: string
  theme: string
  title: string
  total_cost: number
  image_cost: number
  planning_cost: number
  library_hits: number
  library_misses: number
  retry_count: number
  timestamp: string
}

export function getAdminStats(): Promise<AdminStats> {
  return api.get<AdminStats>('/api/v1/admin/stats')
}

export function getDailyAnalytics(days = 30): Promise<DailyAnalytics[]> {
  return api.get<DailyAnalytics[]>(`/api/v1/admin/daily?days=${days}`)
}

export function getFailures(limit = 20): Promise<FailedBook[]> {
  return api.get<FailedBook[]>(`/api/v1/admin/failures?limit=${limit}`)
}

export function getCosts(limit = 50): Promise<CostEntry[]> {
  return api.get<CostEntry[]>(`/api/v1/admin/costs?limit=${limit}`)
}
