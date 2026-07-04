import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getMe } from '@/api/auth'
import { computeQuota } from '@/utils/quota'
import { useBooksStore } from '@/stores/books'
import * as charactersApi from '@/api/characters'
import type { Character } from '@/api/characters'
import { getLibraryStats } from '@/api/library'

export interface BookRecord {
  id: string
  title: string
  theme: string
  page_count: number
  pdf_url: string
  cover_url: string
  created_at: unknown
  status: string
}

export interface DashboardData {
  // Quota
  booksGeneratedTotal: number
  booksGeneratedThisMonth: number
  subscriptionTier: string
  subscriptionActive: boolean
  oneTimeCredits: number
  monthlyLimit: number
  
  // Derived
  booksRemaining: number
  tierLabel: string
  isAtLimit: boolean
  nextResetDate: string
  
  // Activity
  recentBooks: BookRecord[]
  topTheme: string | null
  topThemeCount: number
  
  // Custom Characters
  customCharacters: Character[]

  // Library stats
  libraryStats: {
    totalImages: number
    hitRate: number
    estimatedSavings: number
  } | null

  // Loading state
  loading: boolean
  error: string | null
}

export function useDashboard() {
  const authStore = useAuthStore()
  const booksStore = useBooksStore()

  const data = ref<DashboardData>({
    booksGeneratedTotal: 0,
    booksGeneratedThisMonth: 0,
    subscriptionTier: 'free',
    subscriptionActive: false,
    oneTimeCredits: 0,
    monthlyLimit: 1,
    booksRemaining: 1,
    tierLabel: 'Free',
    isAtLimit: false,
    nextResetDate: '',
    recentBooks: [],
    topTheme: null,
    topThemeCount: 0,
    customCharacters: [],
    libraryStats: null,
    loading: true,
    error: null
  })

  async function fetchDashboard() {
    if (!authStore.uid) return
    
    try {
      data.value.loading = true
      data.value.error = null
      
      // 1. Fetch quota from the backend (source of truth) instead of a direct
      //    client-side Firestore read. A failure here throws to the catch below
      //    and surfaces as an error state — no fail-to-zero fallback.
      const q = computeQuota(await getMe())

      // Next reset date (1st of next month)
      const now = new Date()
      const nextReset = new Date(now.getFullYear(), now.getMonth() + 1, 1)
      const resetStr = nextReset.toLocaleDateString(
        'en-US', { month: 'long', day: 'numeric', year: 'numeric' }
      )

      data.value.booksGeneratedTotal = q.total
      data.value.booksGeneratedThisMonth = q.thisMonth
      data.value.subscriptionTier = q.tier
      data.value.subscriptionActive = q.active
      data.value.oneTimeCredits = q.oneTimeCredits
      data.value.monthlyLimit = q.limit
      data.value.booksRemaining = q.remaining
      data.value.tierLabel = q.tierLabel
      data.value.isAtLimit = q.isAtLimit
      data.value.nextResetDate = resetStr

      // 2. Fetch recent books via API (to bypass restricted Firestore client rules)
      if (booksStore.books.length === 0) {
        await booksStore.fetchBooks()
      }
      data.value.recentBooks = booksStore.books.slice(0, 6).map(b => ({
        id: b.book_id,
        title: b.title,
        theme: b.theme,
        page_count: b.page_count,
        pdf_url: b.pdf_url ?? '',
        cover_url: b.page_urls?.[0] || '', // the backend provides first page as cover visually
        created_at: b.created_at,
        status: b.status
      }))
      
      // 3. Calculate top theme from recent books
      if (data.value.recentBooks.length > 0) {
        const themeCounts: Record<string, number> = {}
        data.value.recentBooks.forEach(b => {
          themeCounts[b.theme] = (themeCounts[b.theme] ?? 0) + 1
        })
        const topEntry = Object.entries(themeCounts)
          .sort((a, b) => b[1] - a[1])[0]
        if (topEntry) {
          data.value.topTheme = topEntry[0]
          data.value.topThemeCount = topEntry[1]
        }
      }

      // 4. Fetch custom characters
      try {
        const chars = await charactersApi.listCharacters()
        data.value.customCharacters = chars || []
      } catch (e) {
        console.error('Failed to load custom characters', e)
        data.value.customCharacters = []
      }

      // 5. Fetch library stats
      try {
        const stats = await getLibraryStats()
        data.value.libraryStats = {
          totalImages: stats.cache.total_images,
          hitRate: stats.aggregate.hit_rate_percent,
          estimatedSavings: stats.aggregate.estimated_total_savings,
        }
      } catch (e) {
        console.error('Failed to load library stats', e)
        data.value.libraryStats = null
      }
      
    } catch (err: unknown) {
      console.error('Dashboard fetch error:', err)
      data.value.error = 'Could not load dashboard data.'
    } finally {
      data.value.loading = false
    }
  }
  
  onMounted(() => {
    if (authStore.isAuthenticated) fetchDashboard()
  })
  
  return { data, fetchDashboard }
}
