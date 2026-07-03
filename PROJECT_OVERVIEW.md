# TailorMade Coloring Book — Project Overview

> Reconciled to the code as of 2026-07-02 (branch `audit/full-sweep`). Where this
> document and the code ever disagree, **the code is the source of truth** —
> update this file, never the working code, to match.

Personalized, printable coloring books for children (ages 2–12), sold on a paid
subscription. Because the audience is children and money changes hands, the two
highest-stakes domains are **child safety** and **payment/quota integrity**.

## Stack (as built)

| Layer | Technology | Deploy |
|-------|-----------|--------|
| Frontend | Vue 3 + Vite + TypeScript + Tailwind + Pinia | Vercel |
| Backend | FastAPI + Python 3.12 | Railway (Docker) |
| Auth / DB | Firebase Auth + Firestore (Blaze) | — |
| Storage | Cloudflare R2 (bucket `tailormadecoloringbook`), private, signed URLs | — |
| Image gen | fal.ai **FLUX.1 Kontext [pro]** — `fal-ai/flux-pro/kontext` (+ `/text-to-image`) | — |
| Scene planning / safety | Anthropic **Claude Haiku** (`claude-haiku-4-5-20251001`) | — |
| PDF | **ReportLab** (pure Python; no system libs) | — |
| Payments | Stripe (dual mode via `STRIPE_MODE` + Firestore `settings/stripe`) | — |
| Email | Resend (transactional, best-effort) | — |
| Monitoring | Sentry (frontend + backend) | — |

> Historical note: earlier docs referenced WeasyPrint (now ReportLab) and
> `fal-ai/flux/dev` (now `fal-ai/flux-pro/kontext`). Those are resolved; the
> table above is current.

## Backend endpoint inventory

All under `/api/v1/*` except the library router (`/api/library`). Every endpoint
requires a valid Firebase token via `get_current_user` **except** where noted.

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| GET | `/health` | none | Liveness (always 200); body reports Firebase/R2/fal-model-URL/Anthropic status |
| GET | `/api/v1/auth/me` | user | Profile + subscription snapshot |
| POST | `/api/v1/books/generate` | user | Full pipeline; reserves quota, fails closed on safety |
| POST | `/api/v1/books/download-zip` | user (paid) | Bulk PDF zip; owner-checked |
| GET | `/api/v1/books/` | user | List own books |
| GET | `/api/v1/books/{book_id}` | user | Owner-checked |
| GET | `/api/v1/books/{book_id}/download` | user | Owner-checked signed PDF URL |
| DELETE | `/api/v1/books/{book_id}` | user | Owner-checked |
| POST | `/api/v1/characters/` | user | Paid Kontext sketch; daily-ceiling gated, 5/user cap |
| GET | `/api/v1/characters/` | user | List own characters |
| DELETE | `/api/v1/characters/{character_id}` | user | Owner-checked |
| POST/GET/PUT/DELETE | `/api/v1/profiles/...` | user | Child profiles, owner-checked, 5/user cap |
| GET | `/api/v1/stripe/config` | none | Publishable key + mode |
| POST | `/api/v1/stripe/checkout` (+ `/create-checkout-session`) | user | price_id allowlisted |
| POST | `/api/v1/stripe/create-portal-session` | user | Billing portal |
| POST | `/api/v1/stripe/webhook` | Stripe signature | Signature-verified + idempotent (event.id dedup) |
| GET | `/api/library/index`, `/api/library/stats` | none | Pre-generated library metadata |
| GET | `/api/v1/admin/stats`,`/daily`,`/failures`,`/costs`,`/stripe-mode` | **admin** | Gated by `ADMIN_UIDS` |
| POST | `/api/v1/admin/stripe-mode` | **admin** | Toggle test/live |

## Generation pipeline (`POST /api/v1/books/generate`)

1. **Quota reserve** — atomic Firestore transaction (`check_rate_limit`): tier
   precedence teacher → family → single-credit → free (1 lifetime). Enforces a
   hard per-user/day ceiling (`DAILY_GENERATION_CEILING`) shared with character
   gen. Reserved now, finalized only on success, rolled back on failure.
2. **Content safety (two layers)** — keyword pre-filter (word-boundary) then
   Anthropic semantic check. **Layer 2 fails CLOSED**: if Anthropic errors, the
   request is blocked (422) and Sentry is alerted.
3. **Scene planning** — Claude Haiku returns structured JSON scenes; untrusted
   user text is delimiter-guarded against prompt injection.
4. **Image gen** — fal Kontext per page (library cache checked first); output
   validated for line-art/NSFW.
5. **PDF** — ReportLab; **free tier is watermarked** and its clean page images
   are never exposed (only the watermarked PDF).
6. **Persist** — images + PDF to R2 (private, signed URLs), metadata to Firestore.
7. **Finalize** — increment usage; best-effort cost/analytics/email.

## Payments & quota integrity

- Webhook **signature-verified** and **idempotent** via `stripe_events/{event.id}`
  create-if-absent claim (released on processing failure so retries still work).
- Handles `checkout.session.completed`, `customer.subscription.updated`,
  `customer.subscription.deleted`, `invoice.payment_failed`.
- `price_id` allowlist on both checkout creation and webhook consumption.
- Quota transactions are atomic with reserve → finalize/rollback; a failed
  generation never burns a credit or the daily ceiling.

## Environment variables

Backend required (server refuses to start if missing — see
`Settings.validate_launch_environment`): `FAL_KEY`, `ANTHROPIC_API_KEY`,
`FIREBASE_PROJECT_ID`, `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`,
`R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_PUBLIC_URL`,
`STRIPE_WEBHOOK_SECRET`, `STRIPE_{FAMILY,TEACHER,SINGLE}_PRICE_ID`, and the
Stripe key pair for the active `STRIPE_MODE`. Firebase credentials via
`FIREBASE_SERVICE_ACCOUNT_JSON` (prod) or `FIREBASE_SERVICE_ACCOUNT_PATH` (dev).

Key optional: `APP_ENV` (`production`/`development`), `DEBUG`, `ADMIN_UIDS`,
`SENTRY_DSN`, `RESEND_API_KEY`, `DAILY_GENERATION_CEILING` (default 50), tier
limit overrides. **`APP_ENV` must be `production` in prod** — the `dev-test-token`
auth bypass is gated on `DEBUG && APP_ENV != production` and is inert otherwise.

Frontend (`VITE_*`): `VITE_API_URL` (falls back to the Railway prod URL when
`PROD`), the Firebase web config, Stripe price IDs, `VITE_SENTRY_DSN`,
`VITE_ADMIN_UIDS`. See `frontend/.env.example`.

## Tests

Canonical suite: `backend/tests/` (run `.venv/bin/python -m pytest tests/`).
Covers Stripe webhook (signature reject, idempotency/replay, one-time credit,
lifecycle), content-safety fail-closed, quota/daily-ceiling concurrency,
character-cap gating, watermark gate, deep health check, dev-bypass hardening,
admin gating, and profile validation. All external calls are stubbed.

## Repository layout

- `backend/app/routers/` — FastAPI routers (one per domain).
- `backend/app/services/` — content filter, scene planner, image gen, PDF,
  storage, library cache, firebase, email.
- `backend/app/middleware/` — auth (Firebase token + admin), rate_limit (quota +
  daily ceiling).
- `frontend/src/` — Vue app (`views/`, `components/`, `stores/`, `api/`).
- `firestore.rules` — default-deny; clients cannot mutate billing/quota fields.
- `AUDIT.md` — full security audit and remediation record.
