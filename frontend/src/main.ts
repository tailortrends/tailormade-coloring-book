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

// Wait for Firebase to resolve auth state before mounting.
const unsub = onAuthStateChanged(auth, (user) => {
  unsub()
  if (user) {
    authStore.setUser(user)
  } else {
    authStore.clearUser()
  }
  app.mount('#app')
})
