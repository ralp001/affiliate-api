# Source: AffiliateMarketing.API/Program.cs
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from typing import Dict, Any
from app.api.routers import dashboard, links, tracking, admin, users, products, resources
from app.infrastructure.kafka import producer as kafka_producer
from app.events.permission_consumer import start_permission_consumer, stop_permission_consumer
from app.core.permissions import permission_cache
from app.core.security import require_support_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Affiliate FastAPI...")
    await start_permission_consumer()
    yield
    # Shutdown
    await stop_permission_consumer()
    await kafka_producer.stop_producer()
    print("Shutdown complete.")

app = FastAPI(
    title="Emutare Affiliate API",
    version="1.0",
    root_path="/affiliate",
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(links.router)
app.include_router(tracking.router)
app.include_router(admin.router)
app.include_router(products.router)
app.include_router(resources.router)


@app.get("/affiliate/api/v1/debug/permissions", tags=["Debug"], include_in_schema=False)
async def debug_permissions(_: Dict[str, Any] = Depends(require_support_admin)):
    """[SupportAdmin only] Inspect the in-memory permission cache."""
    return permission_cache.snapshot()

