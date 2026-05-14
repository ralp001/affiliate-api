"""
Realistic demo seed data for Swagger testing.

Run from project root:
    cd affiliate_api && python seed.py

Creates:
  - 2 SupportAdmin users
  - 5 Affiliate users (different countries)
  - 8 products (Emutare Idex Individual/Business, Nixus, Emutare Payroll)
  - AffiliateProfiles for all affiliates
  - Multiple referral links per affiliate
  - Click events with geo/platform variety
  - Conversions (some clean, some flagged for fraud review)
  - Marketing resources with HTML templates
  - Audit log entries
"""
import asyncio
import uuid
import sys
import os
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.core.db import Base
from app.models.user import User
from app.models.affiliate_profile import AffiliateProfile
from app.models.product import Product
from app.models.referral_link import ReferralLink
from app.models.click_event import ClickEvent
from app.models.conversion import Conversion
from app.models.audit_log import AuditLog
from app.models.marketing_resource import MarketingResource

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


def now(delta_days: int = 0) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=delta_days)


async def run_seed():
    # Create all tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        print("Seeding users...")

        # ── Support Admins ───────────────────────────────────────────────────
        admin1 = User(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            username="admin_sarah",
            email="sarah.admin@emutare.com",
            password_hash=pwd_context.hash("Admin1234!"),
            role="SupportAdmin",
            home_country="NG",
            is_verified=True,
            created_at=now(60),
        )
        admin2 = User(
            id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
            username="admin_james",
            email="james.admin@emutare.com",
            password_hash=pwd_context.hash("Admin1234!"),
            role="SupportAdmin",
            home_country="NG",
            is_verified=True,
            created_at=now(55),
        )

        # ── Affiliate Users ──────────────────────────────────────────────────
        aff_users = [
            User(
                id=uuid.UUID("00000000-0000-0000-0001-000000000001"),
                username="aff_blessing",
                email="blessing@affiliates.com",
                password_hash=pwd_context.hash("Aff1234!"),
                role="Affiliate",
                home_country="NG",
                is_verified=True,
                created_at=now(45),
            ),
            User(
                id=uuid.UUID("00000000-0000-0000-0001-000000000002"),
                username="aff_mike",
                email="mike@affiliates.com",
                password_hash=pwd_context.hash("Aff1234!"),
                role="Affiliate",
                home_country="US",
                is_verified=True,
                created_at=now(40),
            ),
            User(
                id=uuid.UUID("00000000-0000-0000-0001-000000000003"),
                username="aff_david",
                email="david@affiliates.com",
                password_hash=pwd_context.hash("Aff1234!"),
                role="Affiliate",
                home_country="GB",
                is_verified=True,
                created_at=now(35),
            ),
            User(
                id=uuid.UUID("00000000-0000-0000-0001-000000000004"),
                username="aff_chen",
                email="chen@affiliates.com",
                password_hash=pwd_context.hash("Aff1234!"),
                role="Affiliate",
                home_country="CN",
                is_verified=True,
                created_at=now(30),
            ),
            User(
                id=uuid.UUID("00000000-0000-0000-0001-000000000005"),
                username="aff_fatima",
                email="fatima@affiliates.com",
                password_hash=pwd_context.hash("Aff1234!"),
                role="Affiliate",
                home_country="AE",
                is_verified=True,
                created_at=now(20),
            ),
        ]

        for obj in [admin1, admin2] + aff_users:
            db.add(obj)
        await db.flush()

        # ── Affiliate Profiles ────────────────────────────────────────────────
        profiles = [
            AffiliateProfile(
                id=uuid.UUID(f"00000000-0000-0000-0002-00000000000{i+1}"),
                user_id=aff_users[i].id,
                tracking_id=f"AFF-{['BLESS01','MIKE01','DAVID01','CHEN01','FATIM01'][i]}",
                terms_accepted=True,
                is_active=True,
                created_at=aff_users[i].created_at,
            )
            for i in range(5)
        ]
        for p in profiles:
            db.add(p)
        await db.flush()

        print("Seeding products...")

        # ── Products ─────────────────────────────────────────────────────────
        # Emutare Idex — Individual
        idex_individual_products = [
            Product(id=uuid.uuid4(), name="Emutare Idex", description="AI productivity suite for individuals", product_type="Individual", subscription_plan="Platinum", commission_type="Percentage", commission_value=40, base_price=200, currency="USD"),
            Product(id=uuid.uuid4(), name="Emutare Idex", description="AI productivity suite for individuals", product_type="Individual", subscription_plan="Gold", commission_type="Percentage", commission_value=35, base_price=150, currency="USD"),
            Product(id=uuid.uuid4(), name="Emutare Idex", description="AI productivity suite for individuals", product_type="Individual", subscription_plan="Diamond", commission_type="Percentage", commission_value=30, base_price=100, currency="USD"),
        ]
        # Emutare Idex — Business
        idex_business_products = [
            Product(id=uuid.uuid4(), name="Emutare Idex", description="AI productivity suite for businesses", product_type="Business", subscription_plan="Small", commission_type="Percentage", commission_value=25, base_price=500, currency="USD"),
            Product(id=uuid.uuid4(), name="Emutare Idex", description="AI productivity suite for businesses", product_type="Business", subscription_plan="Medium", commission_type="Percentage", commission_value=22, base_price=800, currency="USD"),
            Product(id=uuid.uuid4(), name="Emutare Idex", description="AI productivity suite for businesses", product_type="Business", subscription_plan="Large", commission_type="Percentage", commission_value=20, base_price=1200, currency="USD"),
        ]
        # Nixus
        nixus_products = [
            Product(id=uuid.uuid4(), name="Nixus", description="Cloud collaboration platform", product_type="Individual", subscription_plan="Starter", commission_type="Fixed", commission_value=30, base_price=120, currency="USD"),
            Product(id=uuid.uuid4(), name="Nixus", description="Cloud collaboration platform for companies", product_type="Business", subscription_plan="Corporate", commission_type="Fixed", commission_value=80, base_price=400, currency="USD"),
        ]

        all_products = idex_individual_products + idex_business_products + nixus_products
        for prod in all_products:
            db.add(prod)
        await db.flush()

        print("Seeding referral links...")

        # ── Referral Links (multiple per affiliate across different products/platforms) ──
        platforms = ["Facebook", "Instagram", "YouTube", "Google", "Blog"]
        referral_links = []
        for i, profile in enumerate(profiles):
            for j, product in enumerate(all_products[:4]):  # Each affiliate promotes first 4 products
                platform = platforms[(i + j) % len(platforms)]
                prefix = product.name[:3].upper()
                code = f"{profile.tracking_id}-{prefix}-{str(uuid.uuid4())[:4].upper()}"
                link = ReferralLink(
                    id=uuid.uuid4(),
                    affiliate_profile_id=profile.id,
                    product_id=product.id,
                    generated_code=code,
                    source_platform=platform,
                    is_active=True,
                    created_at=now(25 - i),
                )
                db.add(link)
                referral_links.append(link)
        await db.flush()

        print("Seeding click events...")

        # ── Click Events ──────────────────────────────────────────────────────
        click_countries = ["NG", "US", "GB", "NG", "CN", "AE", "CA", "ZA", "NG", "US"]
        click_platforms = ["Facebook", "Instagram", "YouTube", "Google", "Blog", "Organic"]
        for idx, link in enumerate(referral_links[:15]):  # First 15 links get clicks
            num_clicks = 8 + (idx % 12)
            for k in range(num_clicks):
                db.add(ClickEvent(
                    id=uuid.uuid4(),
                    tracking_id=link.generated_code,
                    ip_address=f"102.{(idx * 7 + k) % 255}.{(idx + k * 3) % 255}.{k % 255}",
                    user_agent="Mozilla/5.0",
                    platform=click_platforms[(idx + k) % len(click_platforms)],
                    product_id=link.product_id,
                    clicked_at=now(20 - k),
                    country_code=click_countries[(idx + k) % len(click_countries)],
                    city=["Lagos", "New York", "London", "Beijing", "Dubai"][k % 5],
                    region="Region",
                    location=f"City, {click_countries[(idx + k) % len(click_countries)]}",
                ))
        await db.flush()

        print("Seeding conversions...")

        # ── Conversions ───────────────────────────────────────────────────────
        buyer_ids = [uuid.uuid4() for _ in range(10)]
        conversion_data = [
            # (link_index, buyer_index, sale_amount, country, is_under_review, fraud_reason)
            (0, 0, 200.0, "NG", False, None),
            (0, 1, 200.0, "US", False, None),
            (1, 2, 150.0, "GB", False, None),
            (1, 3, 150.0, "NG", False, None),
            (2, 4, 100.0, "CN", False, None),
            (3, 5, 500.0, "AE", False, None),
            (4, 6, 800.0, "US", False, None),
            (5, 7, 200.0, "NG", False, None),
            # Fraud-flagged conversions
            (6, 8, 120.0, "NG", True, "Suspicious: 3 conversions from same buyer in 24h"),
            (7, 9, 400.0, "US", True, "Self-referral detected"),
        ]
        for link_idx, buyer_idx, amount, country, under_review, fraud_reason in conversion_data:
            link = referral_links[link_idx]
            product = next((p for p in all_products if p.id == link.product_id), None)
            if not product:
                continue
            if product.commission_type == "Percentage":
                commission = (amount * float(product.commission_value)) / 100
            else:
                commission = float(product.commission_value)

            db.add(Conversion(
                id=uuid.uuid4(),
                affiliate_user_id=link.affiliate_profile_id,
                buyer_user_id=buyer_ids[buyer_idx],
                product_id=link.product_id,
                sale_amount=amount,
                commission_earned=0.0 if under_review else commission,
                referral_code=link.generated_code,
                customer_country=country,
                referral_source=link.source_platform,
                is_under_review=under_review,
                fraud_reason=fraud_reason,
                processed_at=now(10 - link_idx),
            ))
        await db.flush()

        print("Seeding marketing resources...")

        # ── Marketing Resources ───────────────────────────────────────────────
        for product in all_products[:3]:
            db.add(MarketingResource(
                id=uuid.uuid4(),
                product_id=product.id,
                resource_type="Banner",
                title=f"{product.name} {product.subscription_plan} — 728x90 Banner",
                asset_url=f"https://cdn.emutare.com/banners/{product.name.lower().replace(' ','-')}-728x90.png",
                html_template=(
                    f'<a href="{{base_url}}/api/v1/r/{{tracking_id}}" target="_blank">'
                    f'<img src="https://cdn.emutare.com/banners/{product.name.lower().replace(" ","-")}-728x90.png" '
                    f'alt="{product.name}" /></a>'
                ),
                created_by="admin_sarah",
            ))
            db.add(MarketingResource(
                id=uuid.uuid4(),
                product_id=product.id,
                resource_type="Logo",
                title=f"{product.name} Logo",
                asset_url=f"https://cdn.emutare.com/logos/{product.name.lower().replace(' ','-')}-logo.svg",
                html_template=(
                    f'<img src="https://cdn.emutare.com/logos/{product.name.lower().replace(" ","-")}-logo.svg" '
                    f'data-affiliate="{{tracking_id}}" data-product="{{product_id}}" />'
                ),
                created_by="admin_sarah",
            ))
        await db.flush()

        print("Seeding audit logs...")

        # ── Audit Logs ────────────────────────────────────────────────────────
        audit_entries = [
            AuditLog(entity_name="Product", action="Create_Product", new_values="Emutare Idex Platinum created", performed_by="admin_sarah", created_at=now(50)),
            AuditLog(entity_name="AffiliateProfile", action="Register_Affiliate", new_values="aff_blessing registered", performed_by="System", created_at=now(45)),
            AuditLog(entity_name="Security_Alert", action="Self_Referral_Blocked", new_values="Blocked self-referral attempt", performed_by="System", created_at=now(8)),
            AuditLog(entity_name="Conversion", action="Conversion_Flagged", new_values="Suspicious velocity detected", performed_by="System", created_at=now(5)),
        ]
        for entry in audit_entries:
            db.add(entry)

        await db.commit()
        print("\n✅ Seed complete!")
        print("\n📋 Test Credentials:")
        print("  SupportAdmin : username=admin_sarah      password=Admin1234!")
        print("  SupportAdmin : username=admin_james      password=Admin1234!")
        print("  Affiliate    : username=aff_blessing     password=Aff1234!")
        print("  Affiliate    : username=aff_mike         password=Aff1234!")
        print("  Affiliate    : username=aff_david        password=Aff1234!")
        print("  Affiliate    : username=aff_chen         password=Aff1234!")
        print("  Affiliate    : username=aff_fatima       password=Aff1234!")
        print("\nLogin at POST /affiliate/api/v1/users/login to get a JWT token.")


if __name__ == "__main__":
    asyncio.run(run_seed())
