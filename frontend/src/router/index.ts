import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
    { path: '/signup', name: 'signup', component: () => import('@/views/SignUpView.vue') },
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
    { path: '/dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
    { path: '/create', name: 'create', component: () => import('@/views/CreateView.vue') },
    { path: '/generating', name: 'generating', component: () => import('@/views/GeneratingView.vue') },
    { path: '/book-ready', name: 'book-ready', component: () => import('@/views/BookReadyView.vue') },
    { path: '/library', name: 'library', component: () => import('@/views/LibraryView.vue') },
    { path: '/pricing', name: 'pricing', component: () => import('@/views/PricingView.vue') },
    { path: '/community', name: 'community', component: () => import('@/views/CommunityView.vue') },
    { path: '/profiles', name: 'profiles', component: () => import('@/views/ProfilesView.vue') },
    { path: '/profiles/add', name: 'profiles-add', component: () => import('@/views/ProfileAddView.vue') },
    { path: '/share', name: 'share', component: () => import('@/views/ShareView.vue') },
    { path: '/referral', name: 'referral', component: () => import('@/views/ReferralView.vue') },
    { path: '/billing', name: 'billing', component: () => import('@/views/BillingView.vue') },
    { path: '/export', name: 'export', component: () => import('@/views/ExportView.vue') },
    { path: '/upgrade', name: 'upgrade', component: () => import('@/views/UpgradeView.vue') },
    { path: '/workspace', name: 'workspace', component: () => import('@/views/AiLineArtWorkspaceView.vue') },
    { path: '/gift-redeemed', name: 'gift-redeemed', component: () => import('@/views/GiftRedeemedView.vue') },
    { path: '/import', name: 'import', component: () => import('@/views/ImportFromDriveView.vue') },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

export default router
