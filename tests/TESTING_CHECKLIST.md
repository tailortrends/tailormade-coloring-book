# TailorMade Coloring Book — Pre-Launch Testing Checklist

> Print this out or open it in a browser and check items off as you go.
> Target: verify everything works before payment integration.

---

## 1. Infrastructure Verification

### Environment Variables (Railway Dashboard)
- [ ] `APP_ENV` = `production`
- [ ] `ANTHROPIC_API_KEY` — set and not empty
- [ ] `FAL_KEY` — set and not empty
- [ ] `FIREBASE_SERVICE_ACCOUNT_JSON` — set (full JSON string)
- [ ] `FIREBASE_PROJECT_ID` — set
- [ ] `R2_ACCOUNT_ID` — set
- [ ] `R2_ACCESS_KEY_ID` — set
- [ ] `R2_SECRET_ACCESS_KEY` — set
- [ ] `R2_BUCKET_NAME` — set
- [ ] `R2_PUBLIC_URL` — set
- [ ] `ADMIN_UIDS` — set to your Firebase UID

### Health Check
- [ ] `GET /health` returns 200
- [ ] Response shows `firebase: "ok"`
- [ ] Response shows `r2: "ok"`
- [ ] Response shows `status: "ok"` (not "degraded")

### CORS
- [ ] Vercel frontend can call backend without CORS errors (check browser console)
- [ ] No `Access-Control-Allow-Origin: *` (should be specific domains only)

---

## 2. Authentication Flow

### Google Sign-In
- [ ] Visit https://tailormade-coloring-book.vercel.app
- [ ] Click "Sign Up Free" → signup page loads
- [ ] Click "Sign in with Google" → Google popup appears
- [ ] Select account → redirects to /dashboard
- [ ] Dashboard displays user name/email
- [ ] Refresh page → stays logged in (Firebase persists auth)
- [ ] Log out (if button exists) → session cleared

### Route Guards
- [ ] Visit /dashboard while logged out → redirected to /login
- [ ] Visit /create while logged out → redirected to /login
- [ ] Visit /profiles while logged out → redirected to /login
- [ ] Login from redirected page → returns to original destination (check URL ?redirect param)
- [ ] Visit / (home) while logged out → works fine (public)
- [ ] Visit /library while logged out → works fine (public)
- [ ] Visit /pricing while logged out → works fine (public)

### Auth API
- [ ] `GET /api/v1/auth/me` with valid token → returns `{uid, email, tier}`
- [ ] `GET /api/v1/auth/me` without token → returns 401
- [ ] `GET /api/v1/auth/me` with expired/bad token → returns 401

---

## 3. Book Creation Flow

### Form Validation (Frontend)
- [ ] Navigate to /create
- [ ] Submit empty form → Zod validation errors appear under each field
- [ ] Title < 2 chars → "Title must be at least 2 characters"
- [ ] Title > 80 chars → "Title must be at most 80 characters"
- [ ] No age range selected → "Please select an age range"
- [ ] Page count = 3 (below min) → validation error
- [ ] Page count = 16 (above max) → validation error
- [ ] Story prompt > 300 chars → validation error
- [ ] Fix all errors → errors clear, form submits

### Backend Validation
- [ ] Invalid age_range value → 422
- [ ] Missing required fields → 422
- [ ] page_count outside 4-15 → 422
- [ ] All validation errors return clear detail messages

### Generation (LIVE TEST — costs ~$0.50)
- [ ] Fill form: title="My Dino Book", theme="dinosaurs", age_range="6-9", pages=4
- [ ] Click Generate → loading state appears
- [ ] Cancel button visible during generation
- [ ] Wait for completion (~3-5 minutes)
- [ ] Redirects to book-ready page on success
- [ ] Book-ready page shows title, theme, page count
- [ ] PDF download link works → downloads valid PDF
- [ ] PDF has cover page with hero image
- [ ] PDF has correct number of interior coloring pages
- [ ] Page images are clean line art (not photos)
- [ ] Print button opens browser print dialog

### Cancellation
- [ ] Start generating → click Cancel → returns to create form
- [ ] Start generating → navigate away → no error toast (silent cancel)
- [ ] After cancel, can start a new generation

---

## 4. Library / My Books

### List Books
- [ ] Navigate to library/dashboard
- [ ] Previously generated books appear
- [ ] Each book shows: title, theme, thumbnail, date
- [ ] Click a book → shows detail/preview

### Download
- [ ] Click download on an existing book → PDF downloads
- [ ] PDF filename is reasonable (not just `undefined.pdf`)

### Delete Book
- [ ] Click delete on a book → confirmation prompt appears
- [ ] Confirm delete → book removed from list
- [ ] Refresh page → deleted book stays gone
- [ ] Verify in Firestore: document deleted
- [ ] Verify in R2: assets cleaned up (best-effort)

### Empty State
- [ ] New user with no books → friendly empty state message
- [ ] "Create New Book" CTA visible and links to /create

---

## 5. Public Gallery (Library Index)

- [ ] Visit /library or /community (unauthenticated)
- [ ] Page loads without requiring sign-in
- [ ] Gallery images display (if any exist in library_images collection)
- [ ] Filter by theme works
- [ ] Filter by age range works
- [ ] Pagination works (if > 50 images)
- [ ] Empty gallery shows friendly message

---

## 6. Rate Limiting & Quotas

### Free Tier (1 book lifetime)
- [ ] Generate first book → succeeds
- [ ] Attempt second book → 429 with quota info
- [ ] Error message: "You've used 1 of 1 books on the free plan"
- [ ] Frontend shows friendly upgrade prompt
- [ ] "Upgrade" link → goes to /pricing or /upgrade

### Quota Response Structure
- [ ] 429 body contains `detail.quota.used`
- [ ] 429 body contains `detail.quota.limit`
- [ ] 429 body contains `detail.quota.remaining`
- [ ] 429 body contains `detail.quota.tier`
- [ ] 429 body contains `detail.quota.is_subscription_active`

---

## 7. Admin Endpoint

- [ ] `GET /api/v1/admin/stats` without token → 401
- [ ] `GET /api/v1/admin/stats` with regular user token → 403
- [ ] `GET /api/v1/admin/stats` with admin token → 200 with stats
- [ ] Stats include: total_books, avg_cost_per_book, total_spend
- [ ] Stats include: most_expensive_book object
- [ ] Your UID is in `ADMIN_UIDS` env var on Railway

---

## 8. Error Handling

### Network Errors
- [ ] Kill backend (or use wrong URL) → "Unable to reach the server" message
- [ ] Frontend doesn't crash on network error

### Timeout
- [ ] If generation exceeds 5 minutes → timeout error with friendly message
- [ ] User can retry after timeout

### Content Filter
- [ ] Submit prompt with inappropriate content
- [ ] Backend returns 422 with "Content not allowed: [reason]"
- [ ] Frontend shows: "Our safety filter flagged your request: [reason]"

### 500 Errors
- [ ] If backend returns 500 → "Something went wrong. Please try again."
- [ ] No stack traces or internal details exposed to user

---

## 9. Performance

| Endpoint | Target | Actual | Pass? |
|----------|--------|--------|-------|
| `GET /health` | < 1s | ___ms | [ ] |
| `GET /api/v1/books/` | < 2s | ___ms | [ ] |
| `GET /api/library/index` | < 2s | ___ms | [ ] |
| `GET /api/v1/auth/me` | < 1s | ___ms | [ ] |
| `POST /api/v1/books/generate` (4 pages) | < 5 min | ___s | [ ] |

### Measure with:
```bash
time curl -s -o /dev/null -w "%{time_total}s" https://YOUR.railway.app/health
```

---

## 10. Security Checklist

- [ ] `.env` file is NOT committed to git (check with `git log --all -- .env`)
- [ ] Firebase service account JSON is NOT in the repository
- [ ] API responses don't leak internal paths or stack traces
- [ ] Admin endpoint returns 403 for non-admin users
- [ ] Dev auth bypass (`dev-test-token`) is disabled in production (`APP_ENV=production`)
- [ ] CORS only allows known frontend origins
- [ ] All user inputs are sanitized (bleach) on the backend
- [ ] Rate limiting prevents unlimited generation
- [ ] Book ownership is enforced (can't read/delete other users' books)

---

## 11. End-to-End Scenarios

### Scenario 1: New User Journey
```
1. [ ] Open https://tailormade-coloring-book.vercel.app in incognito
2. [ ] Homepage loads with CTA
3. [ ] Sign up with Google
4. [ ] Land on dashboard (empty state)
5. [ ] Click "Create New Book"
6. [ ] Fill: title="Space Adventure", theme="space", age=6-9, pages=4
7. [ ] Submit → generation starts
8. [ ] Wait for completion
9. [ ] Download PDF → valid, looks good
10. [ ] Go to library → book appears
11. [ ] Log out
```

### Scenario 2: Returning User
```
1. [ ] Log back in
2. [ ] Dashboard shows previous book
3. [ ] Download previously generated PDF
4. [ ] Try to create another book → should hit free tier limit (429)
5. [ ] Upgrade prompt appears
```

### Scenario 3: Content Filter
```
1. [ ] Try to create book with theme "violence and weapons"
2. [ ] Content filter blocks with specific reason
3. [ ] Change to "friendly animals"
4. [ ] Succeeds (or hits rate limit)
```

### Scenario 4: Edge Cases
```
1. [ ] Open /create in two tabs, submit both → only one succeeds, other rate-limited
2. [ ] Refresh during generation → generation continues (or clean error)
3. [ ] Submit form with emoji in title → sanitized, doesn't crash
4. [ ] Submit with HTML in story_prompt → bleach strips it
```

---

## 12. Railway-Specific Checks

- [ ] Railway deployment succeeded (check deploy logs)
- [ ] Custom domain configured (if applicable)
- [ ] Railway health check passing (check service dashboard)
- [ ] Logs are structured JSON (check Railway logs)
- [ ] No "firebase_disabled_dev_mode" warnings in prod logs
- [ ] Memory usage reasonable (check Railway metrics)
- [ ] No restart loops (check Railway deployment history)

---

## Sign-Off

| Area | Status | Notes |
|------|--------|-------|
| Infrastructure | [ ] Pass / [ ] Fail | |
| Authentication | [ ] Pass / [ ] Fail | |
| Book Generation | [ ] Pass / [ ] Fail | |
| Library/Gallery | [ ] Pass / [ ] Fail | |
| Rate Limiting | [ ] Pass / [ ] Fail | |
| Admin | [ ] Pass / [ ] Fail | |
| Error Handling | [ ] Pass / [ ] Fail | |
| Performance | [ ] Pass / [ ] Fail | |
| Security | [ ] Pass / [ ] Fail | |

**Ready for payment integration?** [ ] YES / [ ] NO — blockers: _______________

**Tested by:** _______________ **Date:** _______________
