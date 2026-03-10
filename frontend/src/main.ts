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
const unsub = onAuthStateChanged(auth, async (user) => {
  unsub()
  if (user) {
    authStore.setUser(user)
    // Set Sentry user context
    if (sentryDsn) {
      Sentry.setUser({ id: user.uid, email: user.email ?? undefined })
    }
    // Load child profiles after auth is ready
    const profilesStore = useProfilesStore()
    profilesStore.fetchProfiles()  // fire-and-forget — don't block mount
  } else {
    authStore.clearUser()
    if (sentryDsn) {
      Sentry.setUser(null)
    }
  }
  app.mount('#app')
})
