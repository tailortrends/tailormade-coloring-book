<script setup lang="ts">
import { onMounted } from 'vue'
import LegalDocument from '@/components/LegalDocument.vue'
import privacySource from '@/content/privacy-policy.md?raw'

onMounted(() => {
  document.title = 'Privacy Policy — TailorMade Coloring Book'
})
</script>

<template>
  <LegalDocument :source="privacySource" />
</template>
