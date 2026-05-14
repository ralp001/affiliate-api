"""
Permission Emission System — Permission Cache
Consumes permission updates from the Permission API via Kafka and exposes
a FastAPI dependency for field-level access control.

Topic consumed: {API_NAME}-permissions   (API-specific)
               permission-updates         (global, optional)
"""
import logging
from typing import Dict, Any, Set, Tuple
from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user

logger = logging.getLogger(__name__)


class PermissionCache:
    """
    In-memory cache: (clearance_type, clearance_level, field_path) → set[str]
    Populated by Kafka events from the Permission API.
    """

    def __init__(self):
        self._store: Dict[Tuple[str, str, str], Set[str]] = {}

    def update(self, clearance_type: str, clearance_level: str, field_path: str, permissions: list):
        key = (clearance_type, clearance_level, field_path)
        self._store[key] = set(permissions)
        logger.info(
            "Permission updated — clearance=%s/%s field=%s perms=%s",
            clearance_type, clearance_level, field_path, permissions,
        )

    def revoke(self, clearance_type: str, clearance_level: str, field_path: str):
        key = (clearance_type, clearance_level, field_path)
        self._store.pop(key, None)
        logger.info(
            "Permission revoked — clearance=%s/%s field=%s",
            clearance_type, clearance_level, field_path,
        )

    def get(self, clearance_type: str, clearance_level: str, field_path: str) -> Set[str]:
        return self._store.get((clearance_type, clearance_level, field_path), set())

    def can_read(self, ct: str, cl: str, fp: str) -> bool:
        return "read" in self.get(ct, cl, fp)

    def can_create(self, ct: str, cl: str, fp: str) -> bool:
        return "create" in self.get(ct, cl, fp)

    def can_update(self, ct: str, cl: str, fp: str) -> bool:
        return "update" in self.get(ct, cl, fp)

    def can_delete(self, ct: str, cl: str, fp: str) -> bool:
        return "delete" in self.get(ct, cl, fp)

    def snapshot(self) -> dict:
        """Return a copy of the full cache (for debug endpoints)."""
        return {str(k): list(v) for k, v in self._store.items()}


# ── Singleton instance ────────────────────────────────────────────────────────
permission_cache = PermissionCache()


# ── Event handler (called by the Kafka consumer) ──────────────────────────────
async def handle_permission_event(event: Dict[str, Any]):
    """Route incoming Kafka event to the correct cache operation."""
    event_type = event.get("event_type")
    action = event.get("action", "")

    try:
        if event_type == "permission_update":
            field = event["data_field"]
            if action == "revoked":
                permission_cache.revoke(
                    event["clearance_type"], event["clearance_level"], field["field_path"]
                )
            else:
                permission_cache.update(
                    event["clearance_type"], event["clearance_level"],
                    field["field_path"], event["permissions"],
                )

        elif event_type == "bulk_permission_update":
            for field in event.get("data_fields", []):
                permission_cache.update(
                    event["clearance_type"], event["clearance_level"],
                    field["field_path"], field["permissions"],
                )

        elif event_type == "clearance_type_permission_update":
            for level in event.get("clearance_levels", []):
                for field in level.get("data_fields", []):
                    permission_cache.update(
                        event["clearance_type"], level["level_name"],
                        field["field_path"], field["permissions"],
                    )
        else:
            logger.debug("Unknown permission event_type: %s — ignored", event_type)

    except (KeyError, TypeError) as exc:
        logger.warning("Malformed permission event — %s: %s", exc, event)


# ── FastAPI dependency ────────────────────────────────────────────────────────
def require_permission(permission: str, field_path: str):
    """
    Returns a FastAPI dependency that checks `permission` on `field_path`
    using the requesting user's clearance_type / clearance_level from their JWT.

    If the token does not carry clearance info (e.g. local dev tokens) the
    check is skipped so existing role-based auth continues to work.
    """
    async def _checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        ct = current_user.get("clearance_type")
        cl = current_user.get("clearance_level")

        # No clearance claims in token → fall back to role-based auth only
        if not ct or not cl:
            return current_user

        checker = {
            "read":   permission_cache.can_read,
            "create": permission_cache.can_create,
            "update": permission_cache.can_update,
            "delete": permission_cache.can_delete,
        }.get(permission)

        if checker and not checker(ct, cl, field_path):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient clearance: '{permission}' on '{field_path}' denied",
            )

        return current_user

    return _checker
