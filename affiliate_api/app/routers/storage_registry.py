"""
Storage-registry self-service endpoints.

Exposes a manual registration endpoint on this service's Swagger so an
operator can register it with data-residency-api by filling in the
region and product fields, without restarting the pod or editing .env.
"""
from typing import Optional, Literal, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import require_support_admin
from app.services.storage_registry_publisher import _publisher

router = APIRouter(
    prefix="/api/v1/storage-registry",
    tags=["storage-registry"],
)


class RegistrationOut(BaseModel):
    api_name: str = Field(..., description="Underscore-form API identifier. Read-only.")
    region: str = Field(..., description="Deployment region for this pod.")
    product: str = Field(..., description="Product bucket data-residency-api attributes storage to.")
    key: str = Field(..., description="Redis key the publisher writes to.")
    ttl_seconds: int
    heartbeat_interval_seconds: int


class RegistrationIn(BaseModel):
    region: Literal["us", "eu", "asia", "default"] = Field(
        ...,
        description="Where this pod runs. Picks the regional DB and suffixes consumer groups.",
    )
    product: Literal["nixus", "cognita", "integria", "idex"] = Field(
        ...,
        description="Which product silo this API's storage rolls up to.",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional free-form key/value pairs (e.g. owner email, notes). Stored in the Redis blob.",
    )


@router.get(
    "",
    response_model=RegistrationOut,
    summary="Show this API's current data-residency registration",
)
async def get_registration(_user=Depends(require_support_admin)):
    """Return the in-memory state of this service's storage-registry publisher —
    the same blob being written to Redis under ``storage_apis:<api_name>``
    every ~120 s.

    Use this to confirm the registration that the auto-publisher created at
    startup, or to inspect what a recent POST took effect."""
    return _publisher.get_state()


@router.post(
    "/register",
    response_model=RegistrationOut,
    status_code=status.HTTP_200_OK,
    summary="Register this API with data-residency-api",
)
async def register(
    payload: RegistrationIn,
    _user=Depends(require_support_admin),
):
    """Manually register (or re-register) this service with data-residency-api
    by filling in the region and product fields.

    The registration is written immediately to shared Redis. Within ≤30 s it
    becomes visible at ``GET /data-residency/internal/storage-apis`` on
    data-residency-api's Swagger.

    Notes:
    - The auto-publisher running at startup already creates a registration.
      Calling this endpoint **overrides** it for the lifetime of the pod.
    - For permanent changes, also update ``.env`` so the values survive a restart.
    - In a multi-pod deployment, only the pod that received this POST has the
      new value in memory. For multi-pod, change ``.env`` and rolling-restart.
    """
    try:
        return await _publisher.register(
            region=payload.region,
            product=payload.product,
            metadata=payload.metadata,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to write registration to Redis: {exc}",
        )
