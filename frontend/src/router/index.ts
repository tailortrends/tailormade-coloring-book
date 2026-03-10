import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue'), meta: { public: true } },
    { path: '/signup', name: 'signup', component: () => import('@/views/SignUpView.vue'), meta: { public: true } },
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
    { path: '/dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
    { path: '/create', name: 'create', component: () => import('@/views/CreateView.vue') },
    { path: '/generating', name: 'generating', component: () => import('@/views/GeneratingView.vue') },
    { path: '/book-ready', name: 'book-ready', component: () => import('@/views/BookReadyView.vue') },
    { path: '/library', name: 'library', component: () => import('@/views/LibraryView.vue'), meta: { public: true } },
    { path: '/pricing', name: 'pricing', component: () => import('@/views/PricingView.vue'), meta: { public: true } },
    { path: '/community', name: 'community', component: () => import('@/views/CommunityView.vue'), meta: { public: true } },
    { path: '/profile', name: 'profile', component: () => import('@/views/ProfileView.vue') },
    { path: '/profiles', name: 'profiles', component: () => import('@/views/ProfilesView.vue') },
    { path: '/profiles/add', name: 'profiles-add', component: () => import('@/views/ProfileAddView.vue') },
    { path: '/share', name: 'share', component: () => import('@/views/ShareView.vue') },
    { path: '/referral', name: 'referral', component: () => import('@/views/ReferralView.vue') },
    { path: '/billing', name: 'billing', component: () => import('@/views/BillingView.vue') },
    { path: '/export', name: 'export', component: () => import('@/views/ExportView.vue') },
    { path: '/upgrade', name: 'upgrade', component: () => import('@/views/UpgradeView.vue'), meta: { public: true } },
    { path: '/workspace', name: 'workspace', component: () => import('@/views/AiLineArtWorkspaceView.vue') },
    { path: '/gift-redeemed', name: 'gift-redeemed', component: () => import('@/views/GiftRedeemedView.vue') },
    { path: '/import', name: 'import', component: () => import('@/views/ImportFromDriveView.vue') },
    { path: '/characters/add', name: 'create-character', component: () => import('@/views/CreateCharacterView.vue') },
    { path: '/admin', name: 'admin', component: () => import('@/views/AdminView.vue'), meta: { admin: true } },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  // Wait for auth to initialize on hard refresh
  if (!authStore.isReady) {
    await new Promise<void>((resolve) => {
      const unwatch = authStore.$subscribe((mutation, state) => {
        if (state.isReady) {
          unwatch()
          resolve()
        }
      })
    })
  }

  // Protected route + not logged in → redirect to login
  if (!to.meta.public && !authStore.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // Admin route — must be authenticated AND admin
  if (to.meta.admin && !authStore.isAdmin) {
    return { name: 'dashboard' }
  }

  // Already logged in + visiting login/signup → redirect to dashboard
  if ((to.name === 'login' || to.name === 'signup') && authStore.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

export default router
