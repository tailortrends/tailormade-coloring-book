import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { 
  getFirestore, 
  doc, 
  getDoc, 
  collection, 
  query, 
  where, 
  orderBy, 
  limit, 
  getDocs 
} from 'firebase/firestore'

export interface BookRecord {
  id: string
  title: string
  theme: string
  page_count: number
  pdf_url: string
  cover_url: string
  created_at: any
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
  
  // Loading state
  loading: boolean
  error: string | null
}

export function useDashboard() {
  const authStore = useAuthStore()
  const db = getFirestore()
  
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
    loading: true,
    error: null
  })

  async function fetchDashboard() {
    if (!authStore.uid) return
    
    try {
      data.value.loading = true
      data.value.error = null
      
      // 1. Fetch user document
      const userSnap = await getDoc(
        doc(db, 'users', authStore.uid)
      )
      
      if (userSnap.exists()) {
        const u = userSnap.data()
        
        const tier = u.subscription_tier ?? 'free'
        const active = u.subscription_active ?? false
        const otc = u.one_time_credits ?? 0
        const total = u.books_generated_total ?? 0
        const thisMonth = u.books_generated_this_month ?? 0
        
        // Calculate monthly limit
        let limit = 1 // free lifetime
        let remaining = Math.max(0, 1 - total)
        let tierLabel = 'Free'
        
        if (tier === 'teacher' && active) {
          limit = 25
          remaining = Math.max(0, 25 - thisMonth)
          tierLabel = 'Teacher'
        } else if (tier === 'family' && active) {
          limit = 12
          remaining = Math.max(0, 12 - thisMonth)
          tierLabel = 'Family'
        } else if (otc > 0) {
          limit = otc
          remaining = otc
          tierLabel = 'Single Book'
        }
        
        // Next reset date (1st of next month)
        const now = new Date()
        const nextReset = new Date(
          now.getFullYear(), 
          now.getMonth() + 1, 
          1
        )
        const resetStr = nextReset.toLocaleDateString(
          'en-US', { month: 'long', day: 'numeric', year: 'numeric' }
        )
        
        data.value.booksGeneratedTotal = total
        data.value.booksGeneratedThisMonth = thisMonth
        data.value.subscriptionTier = tier
        data.value.subscriptionActive = active
        data.value.oneTimeCredits = otc
        data.value.monthlyLimit = limit
        data.value.booksRemaining = remaining
        data.value.tierLabel = tierLabel
        data.value.isAtLimit = remaining <= 0
        data.value.nextResetDate = resetStr
      }
      
      // 2. Fetch recent books
      const booksQuery = query(
        collection(db, 'books'),
        where('uid', '==', authStore.uid),
        orderBy('created_at', 'desc'),
        limit(6)
      )
      
      const booksSnap = await getDocs(booksQuery)
      data.value.recentBooks = booksSnap.docs.map(d => ({
        id: d.id,
        title: d.data().title ?? 'Untitled Book',
        theme: d.data().theme ?? 'general',
        page_count: d.data().page_count ?? 0,
        pdf_url: d.data().pdf_url ?? '',
        cover_url: d.data().cover_url ?? '',
        created_at: d.data().created_at,
        status: d.data().status ?? 'complete'
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
      
    } catch (err: any) {
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
