# Claude Code prompt — Add Privacy Policy, Terms, and parental consent

> Copy everything below the line into Claude Code. Two files (`PRIVACY_POLICY.md`, `TERMS_OF_SERVICE.md`) are attached/available — place them at the repo root or paste their contents where indicated. Do all work on a branch; do **not** touch `main`.

---

**Context:** This is the TailorMade Coloring Book monorepo (`tailortrends/tailormade-coloring-book`). Frontend is Vue 3 + Vite + TypeScript + Tailwind + Pinia, deployed to Vercel, using Vue Router with views in `frontend/src/views/`. Backend is FastAPI on Railway. The app currently has **dead links** for Privacy Policy and Terms of Service that must be replaced with real, working pages.

**Branch:** Create and work on `feature/legal-pages`. Do not merge to `main` — stop after pushing the branch and give me a summary to review.

**Tasks:**

1. **Add two new routed views** in `frontend/src/views/`:
   - `PrivacyView.vue` at route `/privacy`
   - `TermsView.vue` at route `/terms`
   Register both routes in the Vue Router config. These are public, unauthenticated pages.

2. **Render the content** from the provided `PRIVACY_POLICY.md` and `TERMS_OF_SERVICE.md`. Choose the cleaner of:
   - importing the markdown and rendering it with a lightweight markdown renderer already compatible with the stack, or
   - converting the markdown to semantic HTML directly in the component.
   Style with existing Tailwind classes for readable long-form legal text (constrained max-width, prose spacing, working tables, anchor links for section navigation). Match the existing app theme and navbar/footer chrome. Keep the placeholder tokens (e.g., `[LEGAL ENTITY NAME]`, `[PRIVACY EMAIL]`, `[EFFECTIVE DATE]`) exactly as-is for now — I will fill them in; do not invent values.

3. **Replace every dead Privacy/Terms link** across the app with real links to `/privacy` and `/terms`. Search the codebase for existing placeholder or `#`/`javascript:void` links and any footer, signup, or checkout references. Ensure the footer links to both pages on every page.

4. **Add a parental-consent acknowledgment at signup.** On the sign-in/account-creation flow, add a required checkbox the user must check before proceeding: *"I am a parent or legal guardian, at least 18 years old, and I agree to the [Terms of Service] and [Privacy Policy]."* with both phrases linking to the respective pages. Block account creation until it is checked. Persist a timestamped record that consent was given (e.g., a `consentAcceptedAt` field on the user document in Firestore) so we have proof of consent.

5. **Add a short COPPA notice at child-profile creation.** Where a parent creates or edits a child profile, display a brief inline notice: *"We use your child's first name and age range only to personalize their coloring books. You can review or delete this at any time. See our Privacy Policy."* Link "Privacy Policy" to `/privacy`.

6. **Verify** the frontend builds and type-checks clean (`pnpm build` + `vue-tsc`/type-check). Do not modify backend generation, payment, or auth logic beyond persisting the consent timestamp.

**Do NOT** in this task: build the full account/child-data deletion flow (that's a separate, deliberate decision), change subscription logic, or edit `main`.

**When done:** Print a summary of files added/changed, the routes registered, every dead link you replaced (with file paths), and confirmation that build + type-check pass. Then stop for my review.
