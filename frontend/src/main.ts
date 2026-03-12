import './assets/style.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from './firebase'
import * as Sentry from '@sentry/vue'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { useProfilesStore } from './stores/profiles'
import { api } from './api/client'

const app = createApp(App)
const pinia = createPinia()

// Sentry init (silently skip if no DSN configured)
const sentryDsn = import.meta.env.VITE_SENTRY_DSN as string | undefined
if (sentryDsn) {
  Sentry.init({
    app,
    dsn: sentryDsn,
    integrations: [Sentry.browserTracingIntegration({ router })],
    tracesSampleRate: 0.2,
  })
}

app.use(pinia)
app.use(router)

const authStore = useAuthStore()

// Wait for Firebase to resolve auth state before mounting.
// Keep the listener alive so login/logout events update the store.
let mounted = false
onAuthStateChanged(auth, async (user) => {
  if (user) {
    authStore.setUser(user)
    // Set Sentry user context
    if (sentryDsn) {
      Sentry.setUser({ id: user.uid, email: user.email ?? undefined })
    }
    // Sync subscription data from backend
    api.get<Record<string, unknown>>('/api/v1/auth/me')
      .then((data) => authStore.syncFromMe(data))
      .catch(() => {})  // non-blocking — worst case we stay on free tier
    // Load child profiles after auth is ready
    const profilesStore = useProfilesStore()
    profilesStore.fetchProfiles()  // fire-and-forget — don't block mount
  } else {
    authStore.clearUser()
    if (sentryDsn) {
      Sentry.setUser(null)
    }
  }
  if (!mounted) {
    mounted = true
    app.mount('#app')
  }
})
