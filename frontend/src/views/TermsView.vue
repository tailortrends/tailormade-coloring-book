<script setup lang="ts">
import { onMounted } from 'vue'
import LegalDocument from '@/components/LegalDocument.vue'
import termsSource from '@/content/terms-of-service.md?raw'

onMounted(() => {
  document.title = 'Terms of Service — TailorMade Coloring Book'
})
</script>

<template>
  <LegalDocument :source="termsSource" />
</template>
