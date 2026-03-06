import { initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider } from 'firebase/auth'

const firebaseConfig = {
  apiKey: 'AIzaSyA13wwkVymQrqkAtiuQ52QSlb_BPTatjeI',
  authDomain: 'tailormade-coloring-book.firebaseapp.com',
  projectId: 'tailormade-coloring-book',
  storageBucket: 'tailormade-coloring-book.firebasestorage.app',
  messagingSenderId: '472850519072',
  appId: '1:472850519072:web:bb0782216626e8f65f1845',
}

const app = initializeApp(firebaseConfig)
export const auth = getAuth(app)
export const googleProvider = new GoogleAuthProvider()
