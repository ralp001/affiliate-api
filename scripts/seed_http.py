"""
HTTP seed script — calls uvicorn directly on localhost:5003, bypassing nginx.
Run this ON the VM where the affiliate-api service is running.

Usage (on VM):
    python3 scripts/seed_http.py

Usage (override host for external testing):
    python3 scripts/seed_http.py https://abraham-emutare.duckdns.org/affiliate

What gets seeded
────────────────
  SupportAdmin  username=admin   email=admin@emutare.io   password=Admin123!
  Affiliate     username=alice   email=alice@emutare.io   password=Alice123!
  Affiliate     username=bob     email=bob@emutare.io     password=Bob123!
  3 Products · 5 Marketing Resources · 4 Referral Links · 5 Conversions
"""

import sys, json, uuid, urllib.request, urllib.error

# ── Host ──────────────────────────────────────────────────────────────────────
# Default: uvicorn directly on port 5003 (bypasses nginx — use on the VM)
# Pass an arg to target a different host.
#   e.g.  python3 scripts/seed_http.py https://abraham-emutare.duckdns.org/affiliate
HOST = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:5003"

# All routers register with prefix /api/v1/...
# When calling uvicorn directly that full path is required.
# When calling via nginx (which strips /affiliate/) use a host that already
# includes /affiliate so nginx strips it correctly.
# Default (localhost:5003) → keep the /affiliate prefix in the paths.
# If the user passes the nginx URL ending in /affiliate we strip the suffix and
# prepend it to every path, so the same path constants work either way.
if HOST.endswith("/affiliate"):
    # nginx mode: nginx strips /affiliate before forwarding → uvicorn sees /api/v1/...
    # BUT our routers expect /api/v1/... so we must include /affiliate in path.
    # nginx URL + /api/v1/... = nginx strips /affiliate → /api/v1/...
    # That still wouldn't work.  Actually safest: always call localhost directly.
    print("⚠  Detected nginx URL. For reliable seeding, run on the VM and use the default localhost target.")
    print("   Continuing with provided URL — routes may 404 depending on nginx config.\n")

# ── SSL context (needed for https) ────────────────────────────────────────────
import ssl
_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode    = ssl.CERT_NONE

# ── Helpers ───────────────────────────────────────────────────────────────────

def _req(method, path, body=None, token=None):
    url  = HOST + path
    data = json.dumps(body).encode() if body else None
    hdrs = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        kw = {"timeout": 15}
        if url.startswith("https"):
            kw["context"] = _ctx
        with urllib.request.urlopen(req, **kw) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"  ✗  HTTP {e.code}  {method} {url}  — {e.read().decode(errors='ignore')[:250]}")
        return {}
    except Exception as ex:
        print(f"  ✗  {ex}  {method} {url}")
        return {}

def post(path, body, token=None): return _req("POST", path, body, token)
def get(path, token=None):        return _req("GET",  path, token=token)

def ok(label, resp):
    if resp:
        print(f"  ✓  {label}")
        return True
    print(f"  ✗  {label}  (empty — already exists or schema error)")
    return False

# ── 1. Register users ─────────────────────────────────────────────────────────
print(f"\n── 1. Registering users  [target: {HOST}] ───────────────────────────")

ok("Register admin (SupportAdmin)", post("/api/v1/users/register", {
    "username": "admin", "email": "admin@emutare.io",
    "password": "Admin123!", "role": "SupportAdmin",
    "home_country": "NG", "terms_accepted": False,
}))
ok("Register alice (Affiliate)", post("/api/v1/users/register", {
    "username": "alice", "email": "alice@emutare.io",
    "password": "Alice123!", "role": "Affiliate",
    "home_country": "NG", "terms_accepted": True,
}))
ok("Register bob (Affiliate)", post("/api/v1/users/register", {
    "username": "bob", "email": "bob@emutare.io",
    "password": "Bob123!", "role": "Affiliate",
    "home_country": "US", "terms_accepted": True,
}))

# ── 2. Login ──────────────────────────────────────────────────────────────────
print("\n── 2. Logging in ────────────────────────────────────────────────────")

admin_resp = post("/api/v1/users/login", {"username": "admin", "password": "Admin123!"})
alice_resp = post("/api/v1/users/login", {"username": "alice", "password": "Alice123!"})
bob_resp   = post("/api/v1/users/login", {"username": "bob",   "password": "Bob123!"})

admin_token = admin_resp.get("access_token", "")
alice_token = alice_resp.get("access_token", "")
bob_token   = bob_resp.get("access_token", "")

print(f"  {'✓' if admin_token else '✗'}  admin  {'token: ' + admin_token[:40] + '...' if admin_token else 'LOGIN FAILED'}")
print(f"  {'✓' if alice_token else '✗'}  alice  {'token: ' + alice_token[:40] + '...' if alice_token else 'LOGIN FAILED'}")
print(f"  {'✓' if bob_token   else '✗'}  bob    {'token: ' + bob_token[:40]   + '...' if bob_token   else 'LOGIN FAILED'}")

alice_profile_id = alice_resp.get("affiliate_profile_id", "")
bob_profile_id   = bob_resp.get("affiliate_profile_id",   "")
print(f"\n  alice affiliate_profile_id: {alice_profile_id}")
print(f"  bob   affiliate_profile_id: {bob_profile_id}")

# ── 3. Products (admin) ───────────────────────────────────────────────────────
print("\n── 3. Creating products ─────────────────────────────────────────────")

starter_id = standard_id = biz_id = ""

if not admin_token:
    print("  ✗  Skipping — no admin token")
else:
    p1 = post("/api/v1/admin/products", {
        "name": "Idex Individual Starter",
        "description": "Entry-level plan for individuals — great for freelancers and students.",
        "product_type": "Individual", "subscription_plan": "Starter",
        "commission_type": "Percentage", "commission_value": 10.0,
        "base_price": 4.99, "currency": "USD",
    }, admin_token)
    ok("Idex Individual Starter  ($4.99, 10%)", p1)
    starter_id = p1.get("id", "")

    p2 = post("/api/v1/admin/products", {
        "name": "Idex Individual Standard",
        "description": "Standard plan with premium features for power users.",
        "product_type": "Individual", "subscription_plan": "Standard",
        "commission_type": "Percentage", "commission_value": 15.0,
        "base_price": 9.99, "currency": "USD",
    }, admin_token)
    ok("Idex Individual Standard ($9.99, 15%)", p2)
    standard_id = p2.get("id", "")

    p3 = post("/api/v1/admin/products", {
        "name": "Idex Business Pro",
        "description": "Full-featured business plan with team management and advanced analytics.",
        "product_type": "Business", "subscription_plan": "Pro",
        "commission_type": "Fixed", "commission_value": 25.0,
        "base_price": 49.99, "currency": "USD",
    }, admin_token)
    ok("Idex Business Pro        ($49.99, $25 flat)", p3)
    biz_id = p3.get("id", "")

print(f"\n  starter_id:  {starter_id}")
print(f"  standard_id: {standard_id}")
print(f"  biz_id:      {biz_id}")

# ── 4. Marketing resources (admin) ────────────────────────────────────────────
print("\n── 4. Creating marketing resources ──────────────────────────────────")

if admin_token and starter_id:
    ok("Banner 728×90 — Starter", post("/api/v1/admin/resources", {
        "product_id": starter_id, "resource_type": "Banner",
        "title": "Idex Starter — Leaderboard 728×90",
        "asset_url": "https://cdn.emutare.io/banners/idex-starter-728x90.png",
        "html_template": '<a href="{link}"><img src="https://cdn.emutare.io/banners/idex-starter-728x90.png" width="728" height="90" alt="Idex Starter"/></a>',
    }, admin_token))
    ok("Logo 300×300 — Starter", post("/api/v1/admin/resources", {
        "product_id": starter_id, "resource_type": "Logo",
        "title": "Idex Starter — Square Logo",
        "asset_url": "https://cdn.emutare.io/logos/idex-logo-300x300.png",
    }, admin_token))

if admin_token and standard_id:
    ok("Banner 300×250 — Standard", post("/api/v1/admin/resources", {
        "product_id": standard_id, "resource_type": "Banner",
        "title": "Idex Standard — Rectangle 300×250",
        "asset_url": "https://cdn.emutare.io/banners/idex-standard-300x250.png",
        "html_template": '<a href="{link}"><img src="https://cdn.emutare.io/banners/idex-standard-300x250.png" width="300" height="250" alt="Idex Standard"/></a>',
    }, admin_token))

if admin_token and biz_id:
    ok("Banner 970×250 — Biz Pro", post("/api/v1/admin/resources", {
        "product_id": biz_id, "resource_type": "Banner",
        "title": "Idex Business Pro — Billboard 970×250",
        "asset_url": "https://cdn.emutare.io/banners/idex-biz-970x250.png",
        "html_template": '<a href="{link}"><img src="https://cdn.emutare.io/banners/idex-biz-970x250.png" width="970" height="250" alt="Idex Business Pro"/></a>',
    }, admin_token))
    ok("Video — Biz Pro demo", post("/api/v1/admin/resources", {
        "product_id": biz_id, "resource_type": "Video",
        "title": "Idex Business Pro — Product Demo Video",
        "asset_url": "https://cdn.emutare.io/videos/idex-biz-demo.mp4",
    }, admin_token))

# ── 5. Referral links (affiliates) ────────────────────────────────────────────
print("\n── 5. Generating referral links ─────────────────────────────────────")

alice_code_starter = alice_code_standard = bob_code_starter = bob_code_biz = ""

if alice_token and starter_id:
    r = post("/api/v1/links/generate", {"product_id": starter_id,  "source_platform": "Twitter"},   alice_token)
    ok("Alice → Starter  (Twitter)",   r); alice_code_starter  = r.get("referral_code", "")

if alice_token and standard_id:
    r = post("/api/v1/links/generate", {"product_id": standard_id, "source_platform": "Instagram"}, alice_token)
    ok("Alice → Standard (Instagram)", r); alice_code_standard = r.get("referral_code", "")

if bob_token and starter_id:
    r = post("/api/v1/links/generate", {"product_id": starter_id,  "source_platform": "LinkedIn"},  bob_token)
    ok("Bob   → Starter  (LinkedIn)",  r); bob_code_starter   = r.get("referral_code", "")

if bob_token and biz_id:
    r = post("/api/v1/links/generate", {"product_id": biz_id,      "source_platform": "YouTube"},   bob_token)
    ok("Bob   → Biz Pro  (YouTube)",   r); bob_code_biz       = r.get("referral_code", "")

print(f"\n  alice starter code:  {alice_code_starter}")
print(f"  alice standard code: {alice_code_standard}")
print(f"  bob starter code:    {bob_code_starter}")
print(f"  bob biz code:        {bob_code_biz}")

# ── 6. Conversions ────────────────────────────────────────────────────────────
print("\n── 6. Recording conversions ─────────────────────────────────────────")

def buyer(): return str(uuid.uuid4())

if alice_token and alice_code_starter and starter_id:
    ok("Alice starter → NG buyer 1 ($4.99)", post("/api/v1/links/record-conversion", {
        "referral_code": alice_code_starter, "purchasing_user_id": buyer(),
        "product_id": starter_id, "sale_amount": 4.99, "customer_country": "NG",
    }, alice_token))
    ok("Alice starter → NG buyer 2 ($4.99)", post("/api/v1/links/record-conversion", {
        "referral_code": alice_code_starter, "purchasing_user_id": buyer(),
        "product_id": starter_id, "sale_amount": 4.99, "customer_country": "NG",
    }, alice_token))

if alice_token and alice_code_standard and standard_id:
    ok("Alice standard → GH buyer  ($9.99)", post("/api/v1/links/record-conversion", {
        "referral_code": alice_code_standard, "purchasing_user_id": buyer(),
        "product_id": standard_id, "sale_amount": 9.99, "customer_country": "GH",
    }, alice_token))

if bob_token and bob_code_biz and biz_id:
    ok("Bob biz-pro → US buyer ($49.99)",    post("/api/v1/links/record-conversion", {
        "referral_code": bob_code_biz, "purchasing_user_id": buyer(),
        "product_id": biz_id, "sale_amount": 49.99, "customer_country": "US",
    }, bob_token))

if bob_token and bob_code_starter and starter_id:
    ok("Bob starter → CA buyer ($4.99)",     post("/api/v1/links/record-conversion", {
        "referral_code": bob_code_starter, "purchasing_user_id": buyer(),
        "product_id": starter_id, "sale_amount": 4.99, "customer_country": "CA",
    }, bob_token))

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("  SEED COMPLETE")
print("="*65)
print(f"\n  Swagger: https://abraham-emutare.duckdns.org/affiliate/docs")
print()
print("  ── Credentials ─────────────────────────────────────────────")
print("  SupportAdmin  admin / Admin123!")
print("  Affiliate     alice / Alice123!")
print("  Affiliate     bob   / Bob123!")
print()
print("  ── Key IDs ─────────────────────────────────────────────────")
for label, val in [
    ("admin user_id",     admin_resp.get("user_id", "")),
    ("alice user_id",     alice_resp.get("user_id", "")),
    ("alice profile_id",  alice_profile_id),
    ("bob user_id",       bob_resp.get("user_id", "")),
    ("bob profile_id",    bob_profile_id),
    ("Starter product",   starter_id),
    ("Standard product",  standard_id),
    ("Biz Pro product",   biz_id),
    ("Alice ref code",    alice_code_starter),
    ("Bob ref code",      bob_code_biz),
]:
    if val:
        print(f"  {label:<20} {val}")
print()
