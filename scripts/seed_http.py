"""
HTTP-based seed script for Affiliate API.
Calls the running API's own endpoints — no direct DB connection needed.

Usage:
    python scripts/seed_http.py [BASE_URL]

Defaults to https://abraham-emutare.duckdns.org/affiliate
Override:  python scripts/seed_http.py http://localhost:8000

What gets created
─────────────────
  SupportAdmin  username=admin    email=admin@emutare.io    password=Admin123!
  Affiliate     username=alice    email=alice@emutare.io    password=Alice123!
  Affiliate     username=bob      email=bob@emutare.io      password=Bob123!

  3 Products (Idex Starter, Standard, Business Pro)
  5 Marketing Resources (banners, logo, video)
  4 Referral Links (2 per affiliate)
  5 Conversions  (3 for Alice, 2 for Bob)
"""

import sys
import json
import urllib.request
import urllib.error
import uuid

BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "https://abraham-emutare.duckdns.org"
# Routers already embed the full /affiliate/api/v1 prefix, so we just use the host.
API      = BASE_URL

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _req(method: str, path: str, body=None, token: str | None = None) -> dict:
    url     = f"{API}{path}"
    data    = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode    = ssl.CERT_NONE
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="ignore")
        print(f"  ✗  HTTP {e.code}  {method} {path}  — {body_text[:200]}")
        return {}
    except Exception as exc:
        print(f"  ✗  {exc}  {method} {path}")
        return {}


def post(path, body, token=None):
    return _req("POST", path, body, token)

def get(path, token=None):
    return _req("GET", path, token=token)

def put(path, body=None, token=None):
    return _req("PUT", body, token)

def ok(label: str, resp: dict) -> bool:
    if resp:
        print(f"  ✓  {label}")
        return True
    print(f"  ✗  {label}  (empty response — may already exist)")
    return False


# ─── Step 1 — Register users ──────────────────────────────────────────────────
print("\n── 1. Registering users ─────────────────────────────────────────────")

ok("Register admin (SupportAdmin)", post("/users/register", {
    "username": "admin", "email": "admin@emutare.io",
    "password": "Admin123!", "role": "SupportAdmin",
    "home_country": "NG", "terms_accepted": False,
}))

ok("Register alice (Affiliate)", post("/users/register", {
    "username": "alice", "email": "alice@emutare.io",
    "password": "Alice123!", "role": "Affiliate",
    "home_country": "NG", "terms_accepted": True,
}))

ok("Register bob (Affiliate)", post("/users/register", {
    "username": "bob", "email": "bob@emutare.io",
    "password": "Bob123!", "role": "Affiliate",
    "home_country": "US", "terms_accepted": True,
}))


# ─── Step 2 — Login ───────────────────────────────────────────────────────────
print("\n── 2. Logging in ────────────────────────────────────────────────────")

admin_resp = post("/users/login", {"username": "admin", "password": "Admin123!"})
alice_resp = post("/users/login", {"username": "alice", "password": "Alice123!"})
bob_resp   = post("/users/login", {"username": "bob",   "password": "Bob123!"})

admin_token = admin_resp.get("access_token", "")
alice_token = alice_resp.get("access_token", "")
bob_token   = bob_resp.get("access_token", "")

print(f"  ✓  admin  token: {admin_token[:40]}..." if admin_token else "  ✗  admin login failed")
print(f"  ✓  alice  token: {alice_token[:40]}..." if alice_token else "  ✗  alice login failed")
print(f"  ✓  bob    token: {bob_token[:40]}..."   if bob_token   else "  ✗  bob login failed")

alice_profile_id = alice_resp.get("affiliate_profile_id", "")
bob_profile_id   = bob_resp.get("affiliate_profile_id",   "")
print(f"\n  Alice affiliate_profile_id: {alice_profile_id}")
print(f"  Bob   affiliate_profile_id: {bob_profile_id}")


# ─── Step 3 — Create products (SupportAdmin) ──────────────────────────────────
print("\n── 3. Creating products ─────────────────────────────────────────────")

if not admin_token:
    print("  ✗  Skipping products — no admin token")
    starter_id = standard_id = biz_id = ""
else:
    p1 = post("/admin/products", {
        "name": "Idex Individual Starter",
        "description": "Entry-level plan for individual users. Great for freelancers and students.",
        "product_type": "Individual", "subscription_plan": "Starter",
        "commission_type": "Percentage", "commission_value": 10.0,
        "base_price": 4.99, "currency": "USD",
    }, admin_token)
    ok("Product: Idex Individual Starter", p1)
    starter_id = p1.get("id", "")

    p2 = post("/admin/products", {
        "name": "Idex Individual Standard",
        "description": "Standard plan with premium features for power users.",
        "product_type": "Individual", "subscription_plan": "Standard",
        "commission_type": "Percentage", "commission_value": 15.0,
        "base_price": 9.99, "currency": "USD",
    }, admin_token)
    ok("Product: Idex Individual Standard", p2)
    standard_id = p2.get("id", "")

    p3 = post("/admin/products", {
        "name": "Idex Business Pro",
        "description": "Full-featured business plan with team management and analytics.",
        "product_type": "Business", "subscription_plan": "Pro",
        "commission_type": "Fixed", "commission_value": 25.0,
        "base_price": 49.99, "currency": "USD",
    }, admin_token)
    ok("Product: Idex Business Pro", p3)
    biz_id = p3.get("id", "")

print(f"\n  starter_id:  {starter_id}")
print(f"  standard_id: {standard_id}")
print(f"  biz_id:      {biz_id}")


# ─── Step 4 — Create marketing resources (SupportAdmin) ───────────────────────
print("\n── 4. Creating marketing resources ──────────────────────────────────")

if admin_token and starter_id:
    ok("Banner: Idex Starter 728x90", post("/admin/resources", {
        "product_id": starter_id,
        "resource_type": "Banner",
        "title": "Idex Starter — 728×90 Leaderboard",
        "asset_url": "https://cdn.emutare.io/banners/idex-starter-728x90.png",
        "html_template": '<a href="{base_url}/go/{tracking_id}/{product_id}"><img src="https://cdn.emutare.io/banners/idex-starter-728x90.png" width="728" height="90" alt="Idex Starter"/></a>',
    }, admin_token))

    ok("Logo: Idex Starter", post("/admin/resources", {
        "product_id": starter_id,
        "resource_type": "Logo",
        "title": "Idex Starter — Square Logo",
        "asset_url": "https://cdn.emutare.io/logos/idex-logo-300x300.png",
    }, admin_token))

if admin_token and standard_id:
    ok("Banner: Idex Standard 300x250", post("/admin/resources", {
        "product_id": standard_id,
        "resource_type": "Banner",
        "title": "Idex Standard — 300×250 Rectangle",
        "asset_url": "https://cdn.emutare.io/banners/idex-standard-300x250.png",
        "html_template": '<a href="{base_url}/go/{tracking_id}/{product_id}"><img src="https://cdn.emutare.io/banners/idex-standard-300x250.png" width="300" height="250" alt="Idex Standard"/></a>',
    }, admin_token))

if admin_token and biz_id:
    ok("Banner: Idex Business Pro 970x250", post("/admin/resources", {
        "product_id": biz_id,
        "resource_type": "Banner",
        "title": "Idex Business Pro — 970×250 Billboard",
        "asset_url": "https://cdn.emutare.io/banners/idex-biz-970x250.png",
        "html_template": '<a href="{base_url}/go/{tracking_id}/{product_id}"><img src="https://cdn.emutare.io/banners/idex-biz-970x250.png" width="970" height="250" alt="Idex Business Pro"/></a>',
    }, admin_token))

    ok("Video: Idex Business Pro demo", post("/admin/resources", {
        "product_id": biz_id,
        "resource_type": "Video",
        "title": "Idex Business Pro — Product Demo",
        "asset_url": "https://cdn.emutare.io/videos/idex-biz-demo.mp4",
    }, admin_token))


# ─── Step 5 — Generate referral links (Affiliates) ────────────────────────────
print("\n── 5. Generating referral links ─────────────────────────────────────")

alice_link_starter = alice_link_standard = ""
bob_link_starter   = bob_link_biz = ""

if alice_token and starter_id:
    r = post("/links/generate", {"product_id": starter_id,  "source_platform": "Twitter"},   alice_token)
    ok("Alice → Idex Starter link",   r)
    alice_link_starter = r.get("referral_code", "")

if alice_token and standard_id:
    r = post("/links/generate", {"product_id": standard_id, "source_platform": "Instagram"}, alice_token)
    ok("Alice → Idex Standard link",  r)
    alice_link_standard = r.get("referral_code", "")

if bob_token and starter_id:
    r = post("/links/generate", {"product_id": starter_id,  "source_platform": "LinkedIn"},  bob_token)
    ok("Bob   → Idex Starter link",   r)
    bob_link_starter = r.get("referral_code", "")

if bob_token and biz_id:
    r = post("/links/generate", {"product_id": biz_id,      "source_platform": "YouTube"},   bob_token)
    ok("Bob   → Idex Biz Pro link",   r)
    bob_link_biz = r.get("referral_code", "")

print(f"\n  alice_link_starter:  {alice_link_starter}")
print(f"  alice_link_standard: {alice_link_standard}")
print(f"  bob_link_starter:    {bob_link_starter}")
print(f"  bob_link_biz:        {bob_link_biz}")


# ─── Step 6 — Record conversions ──────────────────────────────────────────────
print("\n── 6. Recording conversions ─────────────────────────────────────────")

def fake_buyer():
    return str(uuid.uuid4())

if alice_token and alice_link_starter and starter_id:
    ok("Conversion: Alice starter (NG buyer)", post("/links/record-conversion", {
        "referral_code":       alice_link_starter,
        "purchasing_user_id":  fake_buyer(),
        "product_id":          starter_id,
        "sale_amount":         4.99,
        "customer_country":    "NG",
    }, alice_token))

    ok("Conversion: Alice starter (NG buyer 2)", post("/links/record-conversion", {
        "referral_code":       alice_link_starter,
        "purchasing_user_id":  fake_buyer(),
        "product_id":          starter_id,
        "sale_amount":         4.99,
        "customer_country":    "NG",
    }, alice_token))

if alice_token and alice_link_standard and standard_id:
    ok("Conversion: Alice standard (GH buyer)", post("/links/record-conversion", {
        "referral_code":       alice_link_standard,
        "purchasing_user_id":  fake_buyer(),
        "product_id":          standard_id,
        "sale_amount":         9.99,
        "customer_country":    "GH",
    }, alice_token))

if bob_token and bob_link_biz and biz_id:
    ok("Conversion: Bob biz-pro (US buyer)", post("/links/record-conversion", {
        "referral_code":       bob_link_biz,
        "purchasing_user_id":  fake_buyer(),
        "product_id":          biz_id,
        "sale_amount":         49.99,
        "customer_country":    "US",
    }, bob_token))

if bob_token and bob_link_starter and starter_id:
    ok("Conversion: Bob starter (CA buyer)", post("/links/record-conversion", {
        "referral_code":       bob_link_starter,
        "purchasing_user_id":  fake_buyer(),
        "product_id":          starter_id,
        "sale_amount":         4.99,
        "customer_country":    "CA",
    }, bob_token))


# ─── Summary ──────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("✓  SEED COMPLETE")
print("="*65)
print(f"\nSwagger:  {BASE_URL}/docs")
print()
print("─── Test Credentials ─────────────────────────────────────────")
print("  SupportAdmin  username=admin   password=Admin123!")
print("  Affiliate     username=alice   password=Alice123!")
print("  Affiliate     username=bob     password=Bob123!")
print()
print("─── Workflow ─────────────────────────────────────────────────")
print("  1. POST /users/login  →  copy 'access_token'")
print("  2. Click Authorize 🔒 in Swagger  →  paste token")
print("  3. Test any endpoint")
print()
print("─── Key IDs (for Swagger path params) ───────────────────────")
if admin_resp.get("user_id"):
    print(f"  admin user_id:           {admin_resp['user_id']}")
if alice_resp.get("user_id"):
    print(f"  alice user_id:           {alice_resp['user_id']}")
    print(f"  alice affiliate_profile: {alice_profile_id}")
if bob_resp.get("user_id"):
    print(f"  bob   user_id:           {bob_resp['user_id']}")
    print(f"  bob   affiliate_profile: {bob_profile_id}")
if starter_id:
    print(f"  Product (Starter):       {starter_id}")
if standard_id:
    print(f"  Product (Standard):      {standard_id}")
if biz_id:
    print(f"  Product (Biz Pro):       {biz_id}")
if alice_link_starter:
    print(f"  Alice referral code:     {alice_link_starter}")
if bob_link_biz:
    print(f"  Bob referral code:       {bob_link_biz}")
print()
