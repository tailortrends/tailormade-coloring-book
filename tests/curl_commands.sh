#!/usr/bin/env bash
#
# TailorMade — Quick CURL Commands Reference
#
# Replace these variables before running:
BASE="https://tailormade-coloring-book-production.up.railway.app"
TOKEN="PASTE_YOUR_FIREBASE_TOKEN_HERE"
ADMIN_TOKEN="PASTE_ADMIN_TOKEN_HERE"

echo "=== Copy/paste individual commands below ==="
echo ""

# ┌─────────────────────────────────────────────┐
# │  HEALTH & INFRASTRUCTURE                    │
# └─────────────────────────────────────────────┘

echo "--- Health Check ---"
echo 'curl -s $BASE/health | python3 -m json.tool'
echo ""
curl -s "$BASE/health" | python3 -m json.tool
echo ""

# ┌─────────────────────────────────────────────┐
# │  CORS CHECK                                 │
# └─────────────────────────────────────────────┘

echo "--- CORS Preflight ---"
echo 'curl -v -X OPTIONS -H "Origin: https://tailormade-coloring-book.vercel.app" -H "Access-Control-Request-Method: GET" $BASE/health 2>&1 | grep -i "access-control"'
echo ""

# ┌─────────────────────────────────────────────┐
# │  AUTH                                       │
# └─────────────────────────────────────────────┘

echo "--- Auth: Get current user ---"
echo 'curl -s -H "Authorization: Bearer $TOKEN" $BASE/api/v1/auth/me | python3 -m json.tool'
echo ""

echo "--- Auth: No token (expect 401) ---"
echo 'curl -s -w "\nHTTP %{http_code}\n" $BASE/api/v1/auth/me'
echo ""

echo "--- Auth: Bad token (expect 401) ---"
echo 'curl -s -w "\nHTTP %{http_code}\n" -H "Authorization: Bearer garbage" $BASE/api/v1/auth/me'
echo ""

# ┌─────────────────────────────────────────────┐
# │  BOOKS                                      │
# └─────────────────────────────────────────────┘

echo "--- Books: List ---"
echo 'curl -s -H "Authorization: Bearer $TOKEN" $BASE/api/v1/books/ | python3 -m json.tool'
echo ""

echo "--- Books: Get by ID ---"
echo 'curl -s -w "\nHTTP %{http_code}\n" -H "Authorization: Bearer $TOKEN" $BASE/api/v1/books/YOUR_BOOK_ID'
echo ""

echo "--- Books: Get nonexistent (expect 404) ---"
echo 'curl -s -w "\nHTTP %{http_code}\n" -H "Authorization: Bearer $TOKEN" $BASE/api/v1/books/nonexistent-id'
echo ""

echo "--- Books: Delete (expect 204) ---"
echo 'curl -s -w "\nHTTP %{http_code}\n" -X DELETE -H "Authorization: Bearer $TOKEN" $BASE/api/v1/books/YOUR_BOOK_ID'
echo ""

echo "--- Books: Generate (WARNING: costs money, takes 3-5 min) ---"
cat << 'CURL_CMD'
curl -s -w "\nHTTP %{http_code}\n" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Dinosaur Adventures",
    "theme": "dinosaurs",
    "age_range": "6-9",
    "page_count": 4,
    "story_prompt": "A friendly T-Rex explores a magical forest"
  }' \
  "$BASE/api/v1/books/generate" | python3 -m json.tool
CURL_CMD
echo ""

# ┌─────────────────────────────────────────────┐
# │  VALIDATION (expect 422s)                   │
# └─────────────────────────────────────────────┘

echo "--- Validation: Invalid age range (expect 422) ---"
cat << 'CURL_CMD'
curl -s -w "\nHTTP %{http_code}\n" \
  -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Test","theme":"dinos","age_range":"invalid","page_count":6}' \
  "$BASE/api/v1/books/generate"
CURL_CMD
echo ""

echo "--- Validation: Page count too low (expect 422) ---"
cat << 'CURL_CMD'
curl -s -w "\nHTTP %{http_code}\n" \
  -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Test","theme":"dinos","age_range":"4-6","page_count":1}' \
  "$BASE/api/v1/books/generate"
CURL_CMD
echo ""

echo "--- Validation: Title too short (expect 422) ---"
cat << 'CURL_CMD'
curl -s -w "\nHTTP %{http_code}\n" \
  -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"A","theme":"dinos","age_range":"4-6","page_count":6}' \
  "$BASE/api/v1/books/generate"
CURL_CMD
echo ""

# ┌─────────────────────────────────────────────┐
# │  LIBRARY (public — no auth needed)          │
# └─────────────────────────────────────────────┘

echo "--- Library: Index ---"
echo 'curl -s "$BASE/api/library/index" | python3 -m json.tool'
echo ""

echo "--- Library: Filtered ---"
echo 'curl -s "$BASE/api/library/index?age_range=4-6&limit=5" | python3 -m json.tool'
echo ""

# ┌─────────────────────────────────────────────┐
# │  ADMIN                                      │
# └─────────────────────────────────────────────┘

echo "--- Admin: Stats (expect 403 with normal user) ---"
echo 'curl -s -w "\nHTTP %{http_code}\n" -H "Authorization: Bearer $TOKEN" $BASE/api/v1/admin/stats'
echo ""

echo "--- Admin: Stats (with admin token) ---"
echo 'curl -s -H "Authorization: Bearer $ADMIN_TOKEN" $BASE/api/v1/admin/stats | python3 -m json.tool'
echo ""

# ┌─────────────────────────────────────────────┐
# │  GET A TOKEN (run in browser console)       │
# └─────────────────────────────────────────────┘

echo "=== HOW TO GET A FIREBASE TOKEN ==="
echo "Open browser DevTools on your deployed app while logged in, then run:"
echo ""
echo '  const { getAuth } = await import("firebase/auth")'
echo '  const token = await getAuth().currentUser.getIdToken()'
echo '  console.log(token)'
echo ""
echo "Or simpler — paste this one-liner in the console:"
echo ""
echo '  await (await import("firebase/auth")).getAuth().currentUser.getIdToken().then(t => { console.log(t); navigator.clipboard.writeText(t) })'
echo ""
echo "(This copies the token to your clipboard automatically)"
