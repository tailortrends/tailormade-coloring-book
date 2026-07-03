<script setup lang="ts">
import { computed } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import { renderLegalMarkdown } from '@/utils/markdown'

const props = defineProps<{ source: string }>()

const rendered = computed(() => renderLegalMarkdown(props.source))
</script>

<template>
  <div class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-1 w-full">
      <div class="mx-auto max-w-3xl px-4 py-10 md:py-16">
        <!-- On this page (section navigation) -->
        <nav
          v-if="rendered.toc.length"
          aria-label="On this page"
          class="mb-10 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6"
        >
          <p class="text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-3">
            On this page
          </p>
          <ul class="grid gap-x-6 gap-y-1.5 sm:grid-cols-2">
            <li v-for="entry in rendered.toc" :key="entry.id">
              <a
                :href="`#${entry.id}`"
                class="text-sm text-primary hover:underline"
              >{{ entry.text }}</a>
            </li>
          </ul>
        </nav>

        <!-- Rendered legal content (trusted, bundled markdown) -->
        <article class="legal-prose" v-html="rendered.html"></article>
      </div>
    </main>

    <AppFooter />
  </div>
</template>

<style scoped>
/* The content is injected via v-html, so it can't take Tailwind utility classes
   directly. Style the rendered elements here for readable long-form legal text
   in both light and dark themes. */
.legal-prose :deep(h1) {
  font-size: 2rem;
  line-height: 1.2;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 1.5rem;
}
.legal-prose :deep(h2) {
  font-size: 1.375rem;
  line-height: 1.3;
  font-weight: 700;
  margin-top: 2.5rem;
  margin-bottom: 0.75rem;
  scroll-margin-top: 5rem;
}
.legal-prose :deep(h3) {
  font-size: 1.1rem;
  font-weight: 700;
  margin-top: 1.75rem;
  margin-bottom: 0.5rem;
  scroll-margin-top: 5rem;
}
.legal-prose :deep(p) {
  margin-bottom: 1rem;
  line-height: 1.75;
  color: rgb(51 65 85); /* slate-700 */
}
:global(.dark) .legal-prose :deep(p) {
  color: rgb(203 213 225); /* slate-300 */
}
.legal-prose :deep(ul),
.legal-prose :deep(ol) {
  margin: 0 0 1rem 1.25rem;
  padding-left: 1rem;
  line-height: 1.75;
  color: rgb(51 65 85);
}
:global(.dark) .legal-prose :deep(ul),
:global(.dark) .legal-prose :deep(ol) {
  color: rgb(203 213 225);
}
.legal-prose :deep(ul) { list-style: disc; }
.legal-prose :deep(ol) { list-style: decimal; }
.legal-prose :deep(li) { margin-bottom: 0.375rem; }
.legal-prose :deep(strong) { font-weight: 700; color: inherit; }
.legal-prose :deep(a) { color: var(--tw-prose-links, #2B6CEE); text-decoration: underline; }
.legal-prose :deep(a:hover) { opacity: 0.8; }
.legal-prose :deep(hr) {
  border: 0;
  border-top: 1px solid rgb(226 232 240);
  margin: 2rem 0;
}
:global(.dark) .legal-prose :deep(hr) { border-top-color: rgb(30 41 59); }
.legal-prose :deep(blockquote) {
  border-left: 4px solid #2B6CEE;
  background: rgb(239 246 255);
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  margin: 1.25rem 0;
  color: rgb(30 58 138);
}
:global(.dark) .legal-prose :deep(blockquote) {
  background: rgba(30, 58, 138, 0.15);
  color: rgb(191 219 254);
}
/* Tables (retention schedule, sub-processors) — scrollable on small screens */
.legal-prose :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.25rem 0;
  font-size: 0.9rem;
  display: block;
  overflow-x: auto;
}
.legal-prose :deep(th),
.legal-prose :deep(td) {
  border: 1px solid rgb(226 232 240);
  padding: 0.6rem 0.85rem;
  text-align: left;
  vertical-align: top;
}
:global(.dark) .legal-prose :deep(th),
:global(.dark) .legal-prose :deep(td) {
  border-color: rgb(30 41 59);
}
.legal-prose :deep(th) {
  background: rgb(248 250 252);
  font-weight: 700;
}
:global(.dark) .legal-prose :deep(th) {
  background: rgb(15 23 42);
}
</style>
