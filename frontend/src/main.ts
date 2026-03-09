import './assets/style.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from './firebase'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

const authStore = useAuthStore()

// Resolves once Firebase has determined the initial auth state
let authReady: Promise<void>
let resolveAuth: () => void
authReady = new Promise((resolve) => {
  resolveAuth = resolve
})

let isFirstCheck = true
onAuthStateChanged(auth, (user) => {
  if (user) {
    authStore.setUser({
      uid: user.uid,
      email: user.email,
      displayName: user.displayName,
    })
  } else {
    authStore.clearUser()
  }
  if (isFirstCheck) {
    isFirstCheck = false
    resolveAuth()
  }
})

// Route guard: redirect unauthenticated users to /login for protected routes
router.beforeEach(async (to) => {
  await authReady
  if (!to.meta.public && !authStore.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})

app.mount('#app')
