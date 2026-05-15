"""
One-time DB repair script — run on the VM before seeding.

Safely adds any columns / tables that exist in the SQLAlchemy models but were
not present in the initial Alembic migration (common when columns are added to
models after the first migration was already applied to the live DB).

Usage (on VM, from repo root, with venv active):
    cd /home/abraham/apps/affiliate-api
    python3 scripts/db_repair.py
"""
import asyncio
import os
import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# ── Read DATABASE_URL straight from .env (no app imports needed) ──────────────
def _load_db_url() -> str:
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    env_path = os.path.normpath(env_path)
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                if key.strip() == "DATABASE_URL":
                    return val.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    # Fallback to environment variable
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL not found in .env or environment")
    return url

_db_url = _load_db_url()
# asyncpg requires postgresql+asyncpg:// scheme
if _db_url.startswith("postgresql://") and "+asyncpg" not in _db_url:
    _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(_db_url, echo=False)

# Each entry: (table, column, sql_type, default_clause)
MISSING_COLUMNS = [
    # affiliate_profiles
    ("affiliate_profiles", "is_active", "BOOLEAN", "DEFAULT TRUE NOT NULL"),

    # products — columns added after initial migration
    ("products", "product_type",              "VARCHAR",       "DEFAULT 'Individual' NOT NULL"),
    ("products", "subscription_plan",         "VARCHAR",       "DEFAULT 'Starter' NOT NULL"),
    ("products", "currency",                  "VARCHAR",       "DEFAULT 'NGN' NOT NULL"),
    ("products", "is_available_for_affiliates","BOOLEAN",      "DEFAULT TRUE NOT NULL"),

    # referral_links
    ("referral_links", "source_platform", "VARCHAR", ""),   # nullable — no default

    # marketing_resources
    ("marketing_resources", "html_template", "TEXT",    ""),                         # nullable
    ("marketing_resources", "created_by",    "VARCHAR", "DEFAULT 'System' NOT NULL"),

    # conversions
    ("conversions", "referral_source",  "VARCHAR", ""),   # nullable
    ("conversions", "fraud_reason",     "VARCHAR", ""),   # nullable
    ("conversions", "is_under_review",  "BOOLEAN", "DEFAULT FALSE NOT NULL"),
]


async def repair():
    async with engine.begin() as conn:
        print("▶ Adding missing columns …")
        for table, column, col_type, default in MISSING_COLUMNS:
            # Check whether column already exists
            exists = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = :tbl AND column_name = :col
                )
            """), {"tbl": table, "col": column})
            if exists.scalar():
                print(f"  –  {table}.{column} already exists, skipping")
                continue

            ddl = f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"
            if default:
                ddl += f" {default}"
            await conn.execute(text(ddl))
            print(f"  ✓  Added {table}.{column}")

    print("\n✅ DB repair complete — safe to run the seed script now.")


if __name__ == "__main__":
    asyncio.run(repair())
