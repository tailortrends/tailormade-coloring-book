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
})

app.mount('#app')
