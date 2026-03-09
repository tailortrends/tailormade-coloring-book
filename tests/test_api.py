#!/usr/bin/env python3
"""
TailorMade Coloring Book — Comprehensive Backend API Test Suite

Usage:
  # Quick smoke test (no generation, ~30 seconds)
  python tests/test_api.py --base-url https://tailormade-coloring-book-production.up.railway.app

  # Full suite including book generation (~5 minutes)
  python tests/test_api.py --base-url https://tailormade-coloring-book-production.up.railway.app --token YOUR_FIREBASE_TOKEN --full

  # With admin tests
  python tests/test_api.py --base-url https://YOUR.railway.app --token YOUR_TOKEN --admin-token ADMIN_TOKEN --full

How to get a Firebase token:
  1. Open browser console on your deployed frontend while logged in
  2. Run: await firebase.auth().currentUser.getIdToken()
  3. Copy the token string
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# ─── Helpers ──────────────────────────────────────────────────────────────────

@dataclass
class TestResult:
    name: str
    passed: bool
    status: int = 0
    detail: str = ""
    duration_ms: float = 0


@dataclass
class TestSuite:
    results: list[TestResult] = field(default_factory=list)

    def add(self, result: TestResult):
        self.results.append(result)
        icon = "\033[92mPASS\033[0m" if result.passed else "\033[91mFAIL\033[0m"
        time_str = f"{result.duration_ms:.0f}ms"
        print(f"  [{icon}] {result.name} ({time_str})")
        if not result.passed and result.detail:
            print(f"         {result.detail}")

    def summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        print(f"\n{'='*60}")
        if failed == 0:
            print(f"\033[92m  ALL {total} TESTS PASSED\033[0m")
        else:
            print(f"\033[91m  {failed} FAILED\033[0m / {passed} passed / {total} total")
            print(f"\n  Failed tests:")
            for r in self.results:
                if not r.passed:
                    print(f"    - {r.name}: {r.detail}")
        print(f"{'='*60}\n")
        return failed == 0


def api_call(base_url: str, path: str, method: str = "GET",
             body: dict | None = None, token: str | None = None,
             expect_status: int | None = None) -> tuple[int, dict | str | None]:
    """Make an HTTP request. Returns (status_code, response_body)."""
    url = f"{base_url}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)

    try:
        resp = urlopen(req, timeout=30)
        status = resp.status
        raw = resp.read().decode()
        try:
            body_out = json.loads(raw)
        except json.JSONDecodeError:
            body_out = raw
        return status, body_out
    except HTTPError as e:
        raw = e.read().decode()
        try:
            body_out = json.loads(raw)
        except json.JSONDecodeError:
            body_out = raw
        return e.code, body_out
    except URLError as e:
        return 0, str(e)
    except Exception as e:
        return 0, str(e)


def timed_test(name: str, fn) -> TestResult:
    """Run a test function and measure duration."""
    start = time.time()
    try:
        passed, detail = fn()
        duration = (time.time() - start) * 1000
        return TestResult(name=name, passed=passed, detail=detail, duration_ms=duration)
    except Exception as e:
        duration = (time.time() - start) * 1000
        return TestResult(name=name, passed=False, detail=str(e), duration_ms=duration)


# ─── Test Groups ──────────────────────────────────────────────────────────────

def test_health(suite: TestSuite, base_url: str):
    print("\n--- Health & Connectivity ---")

    def t_health_200():
        status, body = api_call(base_url, "/health")
        if status == 200:
            checks = body.get("checks", {}) if isinstance(body, dict) else {}
            return True, f"status={body.get('status','?')}, firebase={checks.get('firebase','?')}, r2={checks.get('r2','?')}"
        return False, f"Expected 200, got {status}: {body}"

    def t_health_firebase_ok():
        status, body = api_call(base_url, "/health")
        if status != 200 and status != 503:
            return False, f"Health returned {status}"
        checks = body.get("checks", {}) if isinstance(body, dict) else {}
        fb = checks.get("firebase", "missing")
        return fb == "ok", f"firebase={fb}"

    def t_health_r2_ok():
        status, body = api_call(base_url, "/health")
        if status != 200 and status != 503:
            return False, f"Health returned {status}"
        checks = body.get("checks", {}) if isinstance(body, dict) else {}
        r2 = checks.get("r2", "missing")
        return r2 == "ok", f"r2={r2}"

    def t_cors_headers():
        """Verify CORS allows Vercel origin."""
        url = f"{base_url}/health"
        req = Request(url, method="OPTIONS")
        req.add_header("Origin", "https://tailormade-coloring-book.vercel.app")
        req.add_header("Access-Control-Request-Method", "GET")
        try:
            resp = urlopen(req, timeout=10)
            allow = resp.getheader("access-control-allow-origin") or ""
            if "tailormade-coloring-book.vercel.app" in allow or allow == "*":
                return True, f"CORS origin: {allow}"
            return False, f"CORS origin missing, got: {allow}"
        except HTTPError as e:
            allow = e.headers.get("access-control-allow-origin", "")
            if "tailormade-coloring-book.vercel.app" in allow:
                return True, f"CORS origin present (status {e.code}): {allow}"
            return False, f"CORS preflight returned {e.code}, allow-origin: {allow}"
        except Exception as e:
            return False, str(e)

    suite.add(timed_test("Health endpoint returns 200", t_health_200))
    suite.add(timed_test("Firebase connection healthy", t_health_firebase_ok))
    suite.add(timed_test("R2 storage connection healthy", t_health_r2_ok))
    suite.add(timed_test("CORS allows Vercel origin", t_cors_headers))


def test_auth(suite: TestSuite, base_url: str, token: str | None):
    print("\n--- Authentication ---")

    def t_no_token_401():
        status, _ = api_call(base_url, "/api/v1/auth/me")
        return status == 401 or status == 403, f"Expected 401/403, got {status}"

    def t_bad_token_401():
        status, _ = api_call(base_url, "/api/v1/auth/me", token="invalid-garbage-token")
        return status == 401, f"Expected 401, got {status}"

    suite.add(timed_test("No token → 401/403", t_no_token_401))
    suite.add(timed_test("Bad token → 401", t_bad_token_401))

    if token:
        def t_valid_token():
            status, body = api_call(base_url, "/api/v1/auth/me", token=token)
            if status == 200 and isinstance(body, dict):
                uid = body.get("uid", "")
                email = body.get("email", "")
                return True, f"uid={uid}, email={email}"
            return False, f"Expected 200 with user, got {status}: {body}"

        suite.add(timed_test("Valid token → user object", t_valid_token))
    else:
        print("  [SKIP] Valid token test (no --token provided)")


def test_books_list(suite: TestSuite, base_url: str, token: str | None):
    print("\n--- Books: List ---")

    def t_list_no_auth():
        status, _ = api_call(base_url, "/api/v1/books/")
        return status == 401 or status == 403, f"Expected 401/403, got {status}"

    suite.add(timed_test("List books without auth → 401", t_list_no_auth))

    if token:
        def t_list_books():
            status, body = api_call(base_url, "/api/v1/books/", token=token)
            if status == 200 and isinstance(body, list):
                return True, f"Found {len(body)} books"
            return False, f"Expected 200 with array, got {status}: {body}"

        suite.add(timed_test("List books with auth → array", t_list_books))


def test_books_get(suite: TestSuite, base_url: str, token: str | None):
    print("\n--- Books: Get by ID ---")

    if not token:
        print("  [SKIP] Get book tests (no --token provided)")
        return

    def t_get_nonexistent():
        status, body = api_call(base_url, "/api/v1/books/nonexistent-id-12345", token=token)
        return status == 404, f"Expected 404, got {status}"

    suite.add(timed_test("Get nonexistent book → 404", t_get_nonexistent))

    # Try to get a real book ID from the list
    _, books = api_call(base_url, "/api/v1/books/", token=token)
    if isinstance(books, list) and len(books) > 0:
        book_id = books[0].get("book_id", "")

        def t_get_own_book():
            status, body = api_call(base_url, f"/api/v1/books/{book_id}", token=token)
            if status == 200 and isinstance(body, dict):
                return True, f"book_id={body.get('book_id')}, title={body.get('title')}"
            return False, f"Expected 200, got {status}"

        suite.add(timed_test(f"Get own book {book_id[:8]}... → 200", t_get_own_book))


def test_books_validation(suite: TestSuite, base_url: str, token: str | None):
    print("\n--- Books: Validation ---")

    if not token:
        print("  [SKIP] Validation tests (no --token provided)")
        return

    def t_generate_no_auth():
        status, _ = api_call(base_url, "/api/v1/books/generate", method="POST",
                             body={"title": "Test", "theme": "animals", "age_range": "4-6", "page_count": 6})
        return status == 401 or status == 403, f"Expected 401/403, got {status}"

    def t_invalid_age_range():
        status, body = api_call(base_url, "/api/v1/books/generate", method="POST", token=token,
                                body={"title": "Test Book", "theme": "animals", "age_range": "invalid", "page_count": 6})
        return status == 422, f"Expected 422, got {status}"

    def t_page_count_too_low():
        status, _ = api_call(base_url, "/api/v1/books/generate", method="POST", token=token,
                             body={"title": "Test Book", "theme": "animals", "age_range": "4-6", "page_count": 1})
        return status == 422, f"Expected 422, got {status}"

    def t_page_count_too_high():
        status, _ = api_call(base_url, "/api/v1/books/generate", method="POST", token=token,
                             body={"title": "Test Book", "theme": "animals", "age_range": "4-6", "page_count": 50})
        return status == 422, f"Expected 422, got {status}"

    def t_title_too_short():
        status, _ = api_call(base_url, "/api/v1/books/generate", method="POST", token=token,
                             body={"title": "A", "theme": "animals", "age_range": "4-6", "page_count": 6})
        return status == 422, f"Expected 422, got {status}"

    def t_title_too_long():
        status, _ = api_call(base_url, "/api/v1/books/generate", method="POST", token=token,
                             body={"title": "X" * 100, "theme": "animals", "age_range": "4-6", "page_count": 6})
        return status == 422, f"Expected 422, got {status}"

    def t_missing_required_fields():
        status, _ = api_call(base_url, "/api/v1/books/generate", method="POST", token=token,
                             body={"title": "Test Book"})
        return status == 422, f"Expected 422, got {status}"

    suite.add(timed_test("Generate without auth → 401", t_generate_no_auth))
    suite.add(timed_test("Invalid age_range → 422", t_invalid_age_range))
    suite.add(timed_test("page_count < 4 → 422", t_page_count_too_low))
    suite.add(timed_test("page_count > 15 → 422", t_page_count_too_high))
    suite.add(timed_test("Title too short → 422", t_title_too_short))
    suite.add(timed_test("Title too long → 422", t_title_too_long))
    suite.add(timed_test("Missing required fields → 422", t_missing_required_fields))


def test_books_generate(suite: TestSuite, base_url: str, token: str | None):
    """Actually generate a book. Only runs with --full flag."""
    print("\n--- Books: Generation (LIVE — costs money!) ---")

    if not token:
        print("  [SKIP] Generation tests (no --token provided)")
        return

    def t_generate_book():
        status, body = api_call(base_url, "/api/v1/books/generate", method="POST", token=token,
                                body={
                                    "title": "Test Dinosaurs",
                                    "theme": "dinosaurs",
                                    "age_range": "6-9",
                                    "page_count": 4,
                                    "story_prompt": "A friendly T-Rex goes on an adventure",
                                })
        # Generation may take minutes; urllib has a 30s timeout — extend it
        # For a proper test, use the requests library or increase timeout
        if status == 200:
            bid = body.get("book_id", "?") if isinstance(body, dict) else "?"
            pdf = body.get("pdf_url", "") if isinstance(body, dict) else ""
            has_pdf = bool(pdf)
            pages = body.get("page_count", 0) if isinstance(body, dict) else 0
            return True, f"book_id={bid}, pages={pages}, has_pdf={has_pdf}"
        if status == 429:
            detail = body.get("detail", {}) if isinstance(body, dict) else body
            return True, f"Rate limited (expected for free tier): {detail}"
        return False, f"Expected 200 or 429, got {status}: {body}"

    # Generation takes 3-5 minutes — we need a much longer timeout
    start = time.time()
    try:
        import urllib.request
        url = f"{base_url}/api/v1/books/generate"
        req_body = json.dumps({
            "title": "Test Dinosaurs",
            "theme": "dinosaurs",
            "age_range": "6-9",
            "page_count": 4,
            "story_prompt": "A friendly T-Rex goes on an adventure",
        }).encode()
        req = Request(url, data=req_body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {token}")
        try:
            resp = urlopen(req, timeout=360)  # 6 minute timeout
            raw = json.loads(resp.read().decode())
            duration = (time.time() - start) * 1000
            bid = raw.get("book_id", "?")
            pages = raw.get("page_count", 0)
            has_pdf = bool(raw.get("pdf_url"))
            suite.add(TestResult(
                name="Generate book (4 pages, dinosaurs)",
                passed=True,
                detail=f"book_id={bid}, pages={pages}, has_pdf={has_pdf}",
                duration_ms=duration,
            ))
        except HTTPError as e:
            raw = json.loads(e.read().decode())
            duration = (time.time() - start) * 1000
            if e.code == 429:
                suite.add(TestResult(
                    name="Generate book (rate limited — expected for free tier)",
                    passed=True,
                    detail=f"429: {raw.get('detail', raw)}",
                    duration_ms=duration,
                ))
            else:
                suite.add(TestResult(
                    name="Generate book (4 pages, dinosaurs)",
                    passed=False,
                    detail=f"HTTP {e.code}: {raw}",
                    duration_ms=duration,
                ))
    except Exception as e:
        duration = (time.time() - start) * 1000
        suite.add(TestResult(
            name="Generate book (4 pages, dinosaurs)",
            passed=False,
            detail=str(e),
            duration_ms=duration,
        ))


def test_books_delete(suite: TestSuite, base_url: str, token: str | None):
    print("\n--- Books: Delete ---")

    if not token:
        print("  [SKIP] Delete tests (no --token provided)")
        return

    def t_delete_no_auth():
        status, _ = api_call(base_url, "/api/v1/books/some-id", method="DELETE")
        return status == 401 or status == 403, f"Expected 401/403, got {status}"

    def t_delete_nonexistent():
        status, _ = api_call(base_url, "/api/v1/books/nonexistent-id-99999", method="DELETE", token=token)
        return status == 404, f"Expected 404, got {status}"

    suite.add(timed_test("Delete without auth → 401", t_delete_no_auth))
    suite.add(timed_test("Delete nonexistent → 404", t_delete_nonexistent))


def test_library(suite: TestSuite, base_url: str):
    print("\n--- Library (Public) ---")

    def t_library_index():
        status, body = api_call(base_url, "/api/library/index")
        if status == 200 and isinstance(body, dict):
            themes = body.get("themes", [])
            images = body.get("images", [])
            return True, f"themes={len(themes)}, images={len(images)}"
        return False, f"Expected 200 with themes+images, got {status}: {body}"

    def t_library_no_auth_required():
        """Library should work without a token."""
        status, _ = api_call(base_url, "/api/library/index")
        return status == 200, f"Expected 200, got {status}"

    def t_library_pagination():
        status, body = api_call(base_url, "/api/library/index?limit=5&offset=0")
        if status == 200 and isinstance(body, dict):
            images = body.get("images", [])
            return len(images) <= 5, f"Got {len(images)} images (limit=5)"
        return False, f"Expected 200, got {status}"

    def t_library_filter():
        status, body = api_call(base_url, "/api/library/index?age_range=4-6")
        if status == 200 and isinstance(body, dict):
            return True, f"Filtered response OK"
        return False, f"Expected 200, got {status}"

    suite.add(timed_test("Library index → themes + images", t_library_index))
    suite.add(timed_test("Library requires no auth", t_library_no_auth_required))
    suite.add(timed_test("Library pagination (limit=5)", t_library_pagination))
    suite.add(timed_test("Library filter (age_range=4-6)", t_library_filter))


def test_admin(suite: TestSuite, base_url: str, token: str | None, admin_token: str | None):
    print("\n--- Admin ---")

    def t_admin_no_auth():
        status, _ = api_call(base_url, "/api/v1/admin/stats")
        return status == 401 or status == 403, f"Expected 401/403, got {status}"

    suite.add(timed_test("Admin stats without auth → 401", t_admin_no_auth))

    if token:
        def t_admin_non_admin():
            status, _ = api_call(base_url, "/api/v1/admin/stats", token=token)
            return status == 403, f"Expected 403, got {status}"

        suite.add(timed_test("Admin stats with regular user → 403", t_admin_non_admin))

    if admin_token:
        def t_admin_stats():
            status, body = api_call(base_url, "/api/v1/admin/stats", token=admin_token)
            if status == 200 and isinstance(body, dict):
                return True, f"total_books={body.get('total_books')}, total_spend={body.get('total_spend')}"
            return False, f"Expected 200, got {status}: {body}"

        suite.add(timed_test("Admin stats with admin token → 200", t_admin_stats))
    else:
        print("  [SKIP] Admin token test (no --admin-token provided)")


def test_response_times(suite: TestSuite, base_url: str, token: str | None):
    print("\n--- Performance ---")

    def t_health_fast():
        start = time.time()
        api_call(base_url, "/health")
        ms = (time.time() - start) * 1000
        return ms < 2000, f"{ms:.0f}ms (threshold: 2000ms)"

    def t_library_fast():
        start = time.time()
        api_call(base_url, "/api/library/index?limit=10")
        ms = (time.time() - start) * 1000
        return ms < 3000, f"{ms:.0f}ms (threshold: 3000ms)"

    suite.add(timed_test("Health response < 2s", t_health_fast))
    suite.add(timed_test("Library response < 3s", t_library_fast))

    if token:
        def t_list_books_fast():
            start = time.time()
            api_call(base_url, "/api/v1/books/", token=token)
            ms = (time.time() - start) * 1000
            return ms < 3000, f"{ms:.0f}ms (threshold: 3000ms)"

        suite.add(timed_test("List books response < 3s", t_list_books_fast))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="TailorMade API Test Suite")
    parser.add_argument("--base-url", required=True, help="Backend base URL (e.g. https://myapp.railway.app)")
    parser.add_argument("--token", help="Firebase ID token for authenticated tests")
    parser.add_argument("--admin-token", help="Firebase ID token for an admin user")
    parser.add_argument("--full", action="store_true", help="Run full suite including live generation (costs money!)")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    print(f"\n  TailorMade API Test Suite")
    print(f"  Target: {base}")
    print(f"  Auth token: {'provided' if args.token else 'not provided (some tests will be skipped)'}")
    print(f"  Admin token: {'provided' if args.admin_token else 'not provided'}")
    print(f"  Full mode: {'YES (will generate a book!)' if args.full else 'no (validation only)'}")

    suite = TestSuite()

    test_health(suite, base)
    test_auth(suite, base, args.token)
    test_books_list(suite, base, args.token)
    test_books_get(suite, base, args.token)
    test_books_validation(suite, base, args.token)
    test_books_delete(suite, base, args.token)
    test_library(suite, base)
    test_admin(suite, base, args.token, args.admin_token)
    test_response_times(suite, base, args.token)

    if args.full:
        test_books_generate(suite, base, args.token)

    all_passed = suite.summary()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
