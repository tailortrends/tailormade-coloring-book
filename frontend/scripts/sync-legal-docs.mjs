#!/usr/bin/env node
/**
 * Single source of truth for legal documents.
 *
 * The canonical, human-edited Privacy Policy and Terms of Service live at the
 * repo root under legal/. This script copies them into frontend/src/content/
 * (which is gitignored and NEVER hand-edited) so Vite can bundle them via the
 * `?raw` imports rendered on /privacy and /terms. It runs automatically before
 * `vite dev` and `vite build` (see the predev/prebuild npm scripts), so the
 * live site can never silently drift from legal/*.md.
 *
 * Fails LOUDLY if the canonical source is missing — a broken build is far better
 * than the silent-staleness failure mode this exists to prevent.
 */
import { copyFileSync, existsSync, mkdirSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url)) // frontend/scripts
const frontendRoot = resolve(here, '..') // frontend
const repoRoot = resolve(frontendRoot, '..') // repo root
const legalDir = resolve(repoRoot, 'legal')
const contentDir = resolve(frontendRoot, 'src', 'content')

// [canonical source in legal/, generated destination in src/content/]
const FILES = [
  ['PRIVACY_POLICY.md', 'privacy-policy.md'],
  ['TERMS_OF_SERVICE.md', 'terms-of-service.md'],
]

if (!existsSync(contentDir)) mkdirSync(contentDir, { recursive: true })

let synced = 0
for (const [srcName, destName] of FILES) {
  const from = resolve(legalDir, srcName)
  const to = resolve(contentDir, destName)

  if (!existsSync(from)) {
    console.error(`\n[sync-legal-docs] ERROR: canonical source not found:\n  ${from}\n`)
    console.error('[sync-legal-docs] The build reads legal docs from the repo-root legal/ directory.')
    console.error('[sync-legal-docs] On Vercel (Root Directory = frontend), the build must be able to')
    console.error('[sync-legal-docs] read files OUTSIDE the root: enable Project Settings →')
    console.error('[sync-legal-docs] "Include source files outside of the Root Directory in the Build Step".\n')
    process.exit(1)
  }

  copyFileSync(from, to)
  synced++
  console.log(`[sync-legal-docs] legal/${srcName} -> src/content/${destName}`)
}

console.log(`[sync-legal-docs] synced ${synced} legal document(s) from legal/.`)
