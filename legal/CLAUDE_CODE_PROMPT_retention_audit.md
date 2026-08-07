# Claude Code prompt — Audit actual data retention (read-only)

> This is a read-only audit. Do not delete data, do not change infrastructure, do not modify retention settings. Just report the truth so I can either fix the gaps or correct the Privacy Policy's numbers to match reality.

**Context:** TailorMade Coloring Book privacy policy commits to a 30-day deletion window for account info, child profiles, and generated books/PDFs after account closure or a deletion request. I need to know whether the codebase and infrastructure actually enforce that, or whether it's currently just a policy statement with no automated mechanism behind it.

**Check and report on each of the following:**

1. **Firestore.** Search the codebase (`backend/app/`) for any of: a `deleteAt`, `expiresAt`, `ttl`, or similar timestamp field on `users`, `children`/`profiles`, or `books` documents; any scheduled job, Cloud Function, or cron task that purges old documents; any code path triggered by account deletion that removes Firestore documents. Report what exists today, file and line references, and whether it actually runs on a schedule or only fires synchronously when a user clicks delete (which is different from a genuine 30-day *retention limit* — a limit implies data is removed even if the user never asks).

2. **Cloudflare R2.** Check whether the `tailormadecoloringbook` bucket has any Lifecycle Rules configured (list via API/CLI if credentials are available in the environment, otherwise tell me exactly how to check in the dashboard: R2 → bucket → Settings → Object Lifecycle Rules). Report whether generated images and PDFs are deleted automatically on any schedule, or only if application code explicitly issues a delete call — and if the latter, whether that code exists and where.

3. **Sentry.** Report the configured data-retention window for the project (check `sentry.io` project settings if accessible, otherwise tell me exactly where to look: Settings → Data & Privacy). Note this is usually plan-tier dependent and may not be independently configurable.

4. **Account-deletion flow.** Confirm whether an actual "delete my account" action exists anywhere in the app today (frontend button, backend endpoint). If it doesn't exist yet, say so plainly — this matters because the Privacy Policy currently promises deletion "within 30 days of an account-deletion request," which requires a request mechanism to exist.

**Output:** A short table — one row per data type (account info, child profiles, book inputs, generated books/PDFs, technical logs) — with columns: *Where it lives*, *Automated deletion mechanism exists? (yes/no)*, *If yes, what triggers it and after how long*, *File/config reference*. Then a one-paragraph plain-English verdict: is "30 days" currently true, false, or partially true, and what's the smallest change needed to make it true everywhere.
