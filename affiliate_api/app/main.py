# Source: AffiliateMarketing.API/Program.cs
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routers import dashboard, links, tracking, admin, users
from app.infrastructure.kafka import producer as kafka_producer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Affiliate FastAPI...")
    yield
    # Shutdown
    await kafka_producer.stop_producer()
    print("Kafka producer stopped.")

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
