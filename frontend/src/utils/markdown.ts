import { marked } from 'marked'

export interface TocEntry {
  id: string
  text: string
}

function slugify(text: string): string {
  return (
    text
      .toLowerCase()
      .trim()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-') || 'section'
  )
}

/**
 * Render a trusted, bundled legal markdown document to HTML.
 *
 * The input is our own static content (imported at build time), not user input,
 * so rendering it via v-html is safe. Adds stable `id` slugs to h2/h3 headings
 * for deep-linking and returns a table of contents built from the h2 sections.
 */
export function renderLegalMarkdown(raw: string): { html: string; toc: TocEntry[] } {
  const rawHtml = marked.parse(raw, { gfm: true, async: false }) as string

  const doc = new DOMParser().parseFromString(rawHtml, 'text/html')
  const toc: TocEntry[] = []
  const seen = new Set<string>()

  doc.querySelectorAll('h2, h3').forEach((el) => {
    const text = el.textContent ?? ''
    let id = slugify(text)
    let n = 1
    while (seen.has(id)) id = `${slugify(text)}-${n++}`
    seen.add(id)
    el.id = id
    if (el.tagName === 'H2') toc.push({ id, text })
  })

  return { html: doc.body.innerHTML, toc }
}
