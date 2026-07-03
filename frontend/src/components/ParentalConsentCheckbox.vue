<script setup lang="ts">
import { RouterLink } from 'vue-router'

defineProps<{
  modelValue: boolean
  error?: string | null
}>()

defineEmits<{
  'update:modelValue': [value: boolean]
}>()
</script>

<template>
  <div>
    <label class="flex items-start gap-3 cursor-pointer select-none">
      <input
        :checked="modelValue"
        @change="$emit('update:modelValue', ($event.target as HTMLInputElement).checked)"
        type="checkbox"
        required
        class="mt-0.5 h-5 w-5 shrink-0 cursor-pointer rounded border-slate-300 dark:border-slate-500 text-primary focus:ring-primary/30"
      />
      <span class="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
        I am a parent or legal guardian, at least 18 years old, and I agree to the
        <RouterLink to="/terms" target="_blank" class="text-primary font-semibold hover:underline">Terms of Service</RouterLink>
        and
        <RouterLink to="/privacy" target="_blank" class="text-primary font-semibold hover:underline">Privacy Policy</RouterLink>.
      </span>
    </label>
    <p v-if="error" class="text-red-500 text-sm font-medium mt-3">{{ error }}</p>
  </div>
</template>
