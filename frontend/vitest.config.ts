import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    // The quota composable is pure reactivity (no DOM), so the node env is enough.
    environment: 'node',
    include: ['src/**/*.spec.ts'],
  },
})
