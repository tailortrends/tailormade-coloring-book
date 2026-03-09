# TailorMade — Troubleshooting Guide

Quick fixes for common deployment and testing failures.

---

## CORS Errors

**Symptom:** Browser console shows `Access-Control-Allow-Origin` errors.

**Fix:**
1. Check `backend/app/main.py` → `allow_origins` list includes your Vercel URL
2. Make sure the URL matches exactly (no trailing slash, correct subdomain)
3. Current allowed origins:
   ```
   http://localhost:5173
   https://tailormade-coloring-book.vercel.app
   https://tailormadecoloringbook.vercel.app
   ```
4. After changing, redeploy the backend on Railway
5. Verify with:
   ```bash
   curl -v -X OPTIONS \
     -H "Origin: https://tailormade-coloring-book.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     https://YOUR.railway.app/health 2>&1 | grep -i access-control
   ```

---

## Health Check Returns "degraded" (503)

**Symptom:** `/health` returns 503 with `status: "degraded"`.

**Check `firebase` status:**
- `"error: ..."` → Firebase credentials problem
  - Verify `FIREBASE_SERVICE_ACCOUNT_JSON` is set in Railway env vars
  - Make sure it's the raw JSON string, not a file path
  - Check for escaped quotes or truncation

**Check `r2` status:**
- `"error: ..."` → R2 connection problem
  - Verify all R2 env vars are set: `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`
  - Verify the bucket actually exists in your Cloudflare dashboard
  - Check that the API token has the correct permissions

---

## 401 Unauthorized on All Authenticated Requests

**Symptom:** Every API call with a token returns 401.

**Possible causes:**

1. **Token expired** — Firebase tokens expire after 1 hour
   - Get a fresh token from the browser console:
     ```js
     await (await import("firebase/auth")).getAuth().currentUser.getIdToken(true).then(t => console.log(t))
     ```
   - Note: `getIdToken(true)` forces a refresh

2. **Firebase not initialized** — Check Railway logs for `firebase_disabled_dev_mode`
   - This means Firebase Admin SDK failed to initialize
   - Check `FIREBASE_SERVICE_ACCOUNT_JSON` env var

3. **Wrong Firebase project** — Token was issued by a different project
   - Verify `FIREBASE_PROJECT_ID` matches your frontend's `firebaseConfig.projectId`

4. **Dev bypass active** — If `APP_ENV` is not `production`, the dev bypass accepts `dev-test-token`
   - Set `APP_ENV=production` in Railway to disable this

---

## 403 Forbidden on Admin Endpoint

**Symptom:** `GET /api/v1/admin/stats` returns 403 even with valid token.

**Fix:**
1. Get your Firebase UID:
   ```js
   // In browser console while logged in
   (await import("firebase/auth")).getAuth().currentUser.uid
   ```
2. Set it in Railway env vars:
   ```
   ADMIN_UIDS=your-uid-here
   ```
3. Multiple admins? Comma-separate: `ADMIN_UIDS=uid1,uid2,uid3`
4. Redeploy after changing env vars

---

## 422 on Valid Book Generation Request

**Symptom:** Generate request returns 422 with validation error.

**Common causes:**

1. **age_range format** — Must be exactly one of: `2-4`, `4-6`, `6-9`, `9-12`
   - Check: no spaces, no other formats like `4_6` or `4 to 6`

2. **page_count range** — Must be integer between 4 and 15 inclusive

3. **title length** — Must be 2-80 characters after sanitization
   - bleach strips HTML tags, so `<b>Title</b>` becomes `Title` (5 chars, OK)

4. **Content filter** — Returns 422 with `"Content not allowed: [reason]"`
   - This is the content safety check, not a validation error
   - Change the prompt to something child-appropriate

---

## 429 Rate Limited

**Symptom:** Generate returns 429 when trying to create a book.

**This is expected behavior!** Free tier = 1 book lifetime.

**To reset for testing:**
1. Go to Firestore Console → `users` collection → find your user doc
2. Set `books_generated_total` to 0
3. Or set `subscription_tier` to `teacher` and `subscription_active` to `true` for unlimited testing

**To verify quota info in response:**
```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Test","theme":"dinos","age_range":"4-6","page_count":4}' \
  https://YOUR.railway.app/api/v1/books/generate | python3 -m json.tool
```
Should return:
```json
{
  "detail": {
    "message": "You've used your free book!...",
    "quota": {
      "used": 1,
      "limit": 1,
      "remaining": 0,
      "tier": "free",
      "is_subscription_active": false
    }
  }
}
```

---

## Generation Timeout

**Symptom:** Book generation fails after ~30 seconds or 5 minutes.

**30-second timeout** → Default API client timeout (non-generation requests)
- The frontend uses a 5-minute timeout specifically for `/generate`
- If you're testing with curl, add `--max-time 360`

**5-minute timeout** → Generation is genuinely too slow
- Check Railway logs for the specific failure step
- Common bottleneck: fal.ai image generation
- Check fal.ai dashboard for queue times or errors
- Try reducing page_count to 4 for testing

---

## Images Not Loading / Broken Thumbnails

**Symptom:** Book pages show broken images.

**Check R2:**
1. Verify `R2_PUBLIC_URL` is set and accessible:
   ```bash
   curl -I https://your-r2-public-url.com/books/some-book-id/page_1.png
   ```
2. Verify the R2 bucket has public access enabled
3. Check that the domain/custom domain for R2 is correct

**Check image URLs in book response:**
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  https://YOUR.railway.app/api/v1/books/BOOK_ID | python3 -c "
import sys, json
book = json.load(sys.stdin)
print('PDF:', book.get('pdf_url'))
for i, url in enumerate(book.get('page_urls', [])):
    print(f'Page {i+1}:', url)
"
```

---

## Frontend Route Guard Redirect Loop

**Symptom:** Visiting a protected page causes infinite redirect to /login.

**Cause:** Firebase auth hasn't resolved yet when the guard runs.

**This should be fixed** — `main.ts` has an `authReady` promise that the guard awaits.

**If it still happens:**
1. Check browser console for errors
2. Verify `firebase.ts` config matches your Firebase project
3. Clear browser cookies/localStorage and try again
4. Check if Firebase Auth is enabled in your Firebase Console

---

## Railway Deploy Fails

**Common causes:**

1. **Dockerfile build failure** — Usually a missing system dependency
   - Check Railway build logs
   - WeasyPrint needs: `libcairo2`, `libpango-1.0-0`, `libpangocairo-1.0-0`, `libgdk-pixbuf2.0-0`
   - These are in the Dockerfile already

2. **requirements.txt issues** — Pip install fails
   - Run locally: `pip install -r requirements.txt` to check for errors
   - If a package needs a specific Python version, verify Railway uses 3.12

3. **Port mismatch** — Railway injects `PORT` env var
   - Dockerfile uses `${PORT}`, which Railway sets automatically
   - Don't hardcode a port number

4. **Memory limit** — Railway free tier has limited memory
   - WeasyPrint + PIL can be memory-hungry
   - Check Railway metrics dashboard
   - If OOM: reduce `max_concurrent_fal_calls` in config

---

## Firebase Token — How to Get One

For testing API endpoints directly, you need a Firebase ID token.

### Method 1: Browser Console (easiest)
1. Open https://tailormade-coloring-book.vercel.app and log in
2. Open DevTools (F12) → Console
3. Paste:
   ```js
   const { getAuth } = await import("https://www.gstatic.com/firebasejs/11.0.0/firebase-auth.js")
   // If the above doesn't work, try this in your app's console:
   const token = await getAuth().currentUser.getIdToken()
   copy(token)  // copies to clipboard
   console.log(token)
   ```

### Method 2: Network Tab
1. Open DevTools → Network tab
2. Perform any action (load dashboard, etc.)
3. Find a request to your Railway backend
4. Copy the `Authorization: Bearer xxx` header value

### Token Expiry
- Tokens expire after **1 hour**
- For long test sessions, re-fetch the token periodically
- Firebase auto-refreshes in the browser, but copied tokens don't auto-refresh

---

## Quick Diagnostic Commands

```bash
# Full health check
curl -s https://YOUR.railway.app/health | python3 -m json.tool

# Check if backend is reachable at all
curl -s -o /dev/null -w "HTTP %{http_code} in %{time_total}s\n" https://YOUR.railway.app/health

# Check CORS headers
curl -s -D - -o /dev/null -X OPTIONS \
  -H "Origin: https://tailormade-coloring-book.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  https://YOUR.railway.app/api/v1/books/generate 2>&1 | grep -i "access-control"

# Railway logs (if you have the CLI)
railway logs --tail
```
