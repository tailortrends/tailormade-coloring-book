<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  visible: boolean
  planName: string
}>()

const emit = defineEmits<{
  close: []
}>()

const email = ref('')
const submitted = ref(false)
const emailError = ref('')

function handleSubmit() {
  emailError.value = ''
  const trimmed = email.value.trim()
  if (!trimmed) {
    emailError.value = 'Please enter your email address.'
    return
  }

  const existing = JSON.parse(localStorage.getItem('tm_waitlist') || '[]')
  existing.push({ email: trimmed, planName: props.planName, timestamp: Date.now() })
  localStorage.setItem('tm_waitlist', JSON.stringify(existing))

  submitted.value = true
}

function handleClose() {
  submitted.value = false
  email.value = ''
  emailError.value = ''
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center px-4" @click.self="handleClose">
      <div class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
      <div class="relative bg-white dark:bg-slate-900 rounded-2xl max-w-md w-full p-8 shadow-2xl border border-slate-200 dark:border-slate-700">
        <!-- Close button -->
        <button @click="handleClose" class="absolute top-4 right-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors">
          <span class="material-symbols-outlined text-xl">close</span>
        </button>

        <template v-if="!submitted">
          <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-3 pr-8">{{ planName }} — Coming Soon!</h2>
          <p class="text-slate-500 dark:text-slate-400 text-sm leading-relaxed mb-6">
            We're putting the finishing touches on payments. Drop your email below and we'll notify you the moment it's live — plus get 1 bonus book on us when we launch.
          </p>
          <div class="flex flex-col gap-3">
            <input
              v-model="email"
              type="email"
              placeholder="your@email.com"
              class="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white h-12 px-4 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-slate-400"
              @keyup.enter="handleSubmit"
            />
            <p v-if="emailError" class="text-red-500 text-xs font-medium">{{ emailError }}</p>
            <button
              @click="handleSubmit"
              class="w-full h-12 bg-gradient-to-r from-primary to-accent-purple hover:from-primary-dark hover:to-primary text-white font-bold rounded-xl transition-all shadow-lg shadow-primary/20"
            >
              Notify Me!
            </button>
          </div>
        </template>

        <template v-else>
          <div class="text-center py-4">
            <div class="text-4xl mb-4">🎉</div>
            <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-3">You're on the list!</h2>
            <p class="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">
              We'll email you at <strong class="text-slate-700 dark:text-slate-200">{{ email }}</strong> when {{ planName }} is ready.
            </p>
          </div>
        </template>
      </div>
    </div>
  </Teleport>
</template>
