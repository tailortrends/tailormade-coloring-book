#!/usr/bin/env bash
#
# TailorMade — Quick Smoke Test (~60 seconds)
# Validates all critical systems are operational after deploy.
#
# Usage:
#   chmod +x tests/smoke_test.sh
#   ./tests/smoke_test.sh https://tailormade-coloring-book-production.up.railway.app
#
#   # With auth (optional):
#   TOKEN=your_firebase_token ./tests/smoke_test.sh https://YOUR.railway.app
#

set -euo pipefail

BASE_URL="${1:?Usage: $0 <base-url> [e.g. https://myapp.railway.app]}"
BASE_URL="${BASE_URL%/}"  # strip trailing slash
TOKEN="${TOKEN:-}"
PASS=0
FAIL=0
SKIP=0

green() { printf "\033[92m%s\033[0m" "$1"; }
red()   { printf "\033[91m%s\033[0m" "$1"; }
yellow(){ printf "\033[93m%s\033[0m" "$1"; }

check() {
    local label="$1" url="$2" method="${3:-GET}" expected="${4:-200}" auth="${5:-}" body="${6:-}"
    local curl_args=(-s -o /tmp/sm_body -w "%{http_code}" -X "$method" --max-time 15)

    if [ -n "$auth" ]; then
        curl_args+=(-H "Authorization: Bearer $auth")
    fi
    if [ -n "$body" ]; then
        curl_args+=(-H "Content-Type: application/json" -d "$body")
    fi

    local status
    status=$(curl "${curl_args[@]}" "$url" 2>/dev/null || echo "000")

    if [ "$status" = "$expected" ]; then
        printf "  [$(green PASS)] %s → %s\n" "$label" "$status"
        PASS=$((PASS + 1))
    else
        printf "  [$(red FAIL)] %s → %s (expected %s)\n" "$label" "$status" "$expected"
        # Show response body on failure for debugging
        if [ -f /tmp/sm_body ]; then
            printf "         %s\n" "$(head -c 200 /tmp/sm_body)"
        fi
        FAIL=$((FAIL + 1))
    fi
}

skip() {
    printf "  [$(yellow SKIP)] %s (%s)\n" "$1" "$2"
    SKIP=$((SKIP + 1))
}

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   TailorMade Smoke Test                  ║"
echo "  ╚══════════════════════════════════════════╝"
echo "  Target: $BASE_URL"
echo ""

# ── 1. Health ──
echo "--- Infrastructure ---"
check "Health endpoint" "$BASE_URL/health"

# Check sub-statuses
HEALTH_BODY=$(curl -s --max-time 10 "$BASE_URL/health" 2>/dev/null || echo "{}")
FB_STATUS=$(echo "$HEALTH_BODY" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('checks',{}).get('firebase','?'))" 2>/dev/null || echo "?")
R2_STATUS=$(echo "$HEALTH_BODY" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('checks',{}).get('r2','?'))" 2>/dev/null || echo "?")

if [ "$FB_STATUS" = "ok" ]; then
    printf "  [$(green PASS)] Firebase connected\n"; PASS=$((PASS+1))
else
    printf "  [$(red FAIL)] Firebase: %s\n" "$FB_STATUS"; FAIL=$((FAIL+1))
fi
if [ "$R2_STATUS" = "ok" ]; then
    printf "  [$(green PASS)] R2 storage connected\n"; PASS=$((PASS+1))
else
    printf "  [$(red FAIL)] R2 storage: %s\n" "$R2_STATUS"; FAIL=$((FAIL+1))
fi

# ── 2. CORS ──
echo ""
echo "--- CORS ---"
CORS_HEADER=$(curl -s -o /dev/null -w "%{http_code}" -X OPTIONS \
    -H "Origin: https://tailormade-coloring-book.vercel.app" \
    -H "Access-Control-Request-Method: GET" \
    --max-time 10 "$BASE_URL/health" 2>/dev/null || echo "000")
if [ "$CORS_HEADER" = "200" ] || [ "$CORS_HEADER" = "204" ]; then
    printf "  [$(green PASS)] CORS preflight → %s\n" "$CORS_HEADER"; PASS=$((PASS+1))
else
    printf "  [$(red FAIL)] CORS preflight → %s\n" "$CORS_HEADER"; FAIL=$((FAIL+1))
fi

# ── 3. Auth ──
echo ""
echo "--- Authentication ---"
check "No token → 401/403" "$BASE_URL/api/v1/auth/me" "GET" "401"
check "Bad token → 401" "$BASE_URL/api/v1/auth/me" "GET" "401" "bad-token"

if [ -n "$TOKEN" ]; then
    check "Valid token → 200" "$BASE_URL/api/v1/auth/me" "GET" "200" "$TOKEN"
else
    skip "Valid token → 200" "set TOKEN env var"
fi

# ── 4. Public endpoints ──
echo ""
echo "--- Public Endpoints ---"
check "Library index (no auth)" "$BASE_URL/api/library/index"
check "Library with pagination" "$BASE_URL/api/library/index?limit=5&offset=0"

# ── 5. Protected endpoints ──
echo ""
echo "--- Protected Endpoints ---"
check "Books list without auth → 401/403" "$BASE_URL/api/v1/books/" "GET" "401"
check "Admin stats without auth → 401/403" "$BASE_URL/api/v1/admin/stats" "GET" "401"

if [ -n "$TOKEN" ]; then
    check "Books list with auth → 200" "$BASE_URL/api/v1/books/" "GET" "200" "$TOKEN"
    check "Get nonexistent book → 404" "$BASE_URL/api/v1/books/fake-id-123" "GET" "404" "$TOKEN"
    check "Delete nonexistent book → 404" "$BASE_URL/api/v1/books/fake-id-123" "DELETE" "404" "$TOKEN"

    # Validation tests
    echo ""
    echo "--- Input Validation ---"
    check "Invalid age_range → 422" "$BASE_URL/api/v1/books/generate" "POST" "422" "$TOKEN" \
        '{"title":"Test","theme":"dinos","age_range":"bad","page_count":6}'
    check "page_count too low → 422" "$BASE_URL/api/v1/books/generate" "POST" "422" "$TOKEN" \
        '{"title":"Test","theme":"dinos","age_range":"4-6","page_count":1}'
    check "page_count too high → 422" "$BASE_URL/api/v1/books/generate" "POST" "422" "$TOKEN" \
        '{"title":"Test","theme":"dinos","age_range":"4-6","page_count":99}'
    check "Title too short → 422" "$BASE_URL/api/v1/books/generate" "POST" "422" "$TOKEN" \
        '{"title":"A","theme":"dinos","age_range":"4-6","page_count":6}'
    check "Missing fields → 422" "$BASE_URL/api/v1/books/generate" "POST" "422" "$TOKEN" \
        '{"title":"Test"}'

    # Admin guard
    echo ""
    echo "--- Admin Guard ---"
    check "Admin stats with regular user → 403" "$BASE_URL/api/v1/admin/stats" "GET" "403" "$TOKEN"
else
    skip "Authenticated endpoint tests" "set TOKEN env var"
fi

# ── Summary ──
echo ""
echo "  ══════════════════════════════════════════"
TOTAL=$((PASS + FAIL + SKIP))
if [ "$FAIL" -eq 0 ]; then
    echo "  $(green "ALL $PASS PASSED") ($SKIP skipped) / $TOTAL total"
else
    echo "  $(red "$FAIL FAILED") / $PASS passed / $SKIP skipped / $TOTAL total"
fi
echo "  ══════════════════════════════════════════"
echo ""

# Clean up
rm -f /tmp/sm_body

exit "$FAIL"
