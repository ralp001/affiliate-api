"""
One-time DB repair script — run on the VM before seeding.

Safely adds any columns / tables that exist in the SQLAlchemy models but were
not present in the initial Alembic migration (common when columns are added to
models after the first migration was already applied to the live DB).

Usage (on VM, from repo root):
    cd /home/abraham/apps/affiliate-api
    python3 scripts/db_repair.py
"""
import asyncio
import sys
import os

# Allow running from repo root without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Import all models so Base.metadata knows about every table
from affiliate_api.app.core.config import settings  # noqa: F401
from affiliate_api.app.core.db import Base

import affiliate_api.app.models.user               # noqa: F401
import affiliate_api.app.models.affiliate_profile  # noqa: F401
import affiliate_api.app.models.product            # noqa: F401
import affiliate_api.app.models.referral_link      # noqa: F401
import affiliate_api.app.models.click_event        # noqa: F401
import affiliate_api.app.models.conversion         # noqa: F401
import affiliate_api.app.models.marketing_resource # noqa: F401
import affiliate_api.app.models.audit_log          # noqa: F401
import affiliate_api.app.models.log_model          # noqa: F401

engine = create_async_engine(settings.DATABASE_URL, echo=False)

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
        # 1. Create any completely missing tables
        print("▶ Creating missing tables (if any) …")
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
        print("  ✓ Tables OK")

        # 2. Add missing columns
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
