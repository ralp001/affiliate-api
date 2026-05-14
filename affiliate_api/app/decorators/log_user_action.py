"""
@log_user_action decorator — automatic per-route audit logging with outbox Kafka delivery.

Usage:
    @router.post("/login")
    @log_user_action(action=UserAction.LOGIN)
    async def login(req: Request, body: LoginRequest, db: AsyncSession = Depends(get_db)):
        ...

IMPORTANT: The FastAPI `Request` object must appear somewhere in the function signature.
"""
import functools
import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request

from app.models.log_model import ActionStatus, LogFailureReason, UserAction, UserActionLog

logger = logging.getLogger(__name__)


def log_user_action(action: UserAction):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # ── locate Request object ─────────────────────────────────────
            request: Optional[Request] = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if request is None:
                for v in kwargs.values():
                    if isinstance(v, Request):
                        request = v
                        break

            user_ctx = await _extract_user_context(request, kwargs)

            log_entry = UserActionLog(
                user_id=user_ctx.get("user_id"),
                email=user_ctx.get("email"),
                responsibility_category=user_ctx.get("responsibility_category"),
                action=action,
                status=ActionStatus.SUCCESS,
                failure_reason=None,
                ip_address=_get_client_ip(request),
                location=await _get_location_from_ip(_get_client_ip(request)),
            )

            try:
                result = await func(*args, **kwargs)
                await _save_log(log_entry)
                _enqueue(log_entry.id)
                return result

            except HTTPException as exc:
                log_entry.status = ActionStatus.FAILED
                log_entry.failure_reason = _http_to_reason(exc.status_code)
                await _save_log(log_entry)
                _enqueue(log_entry.id)
                raise

            except Exception as exc:
                log_entry.status = ActionStatus.FAILED
                log_entry.failure_reason = _exc_to_reason(exc)
                await _save_log(log_entry)
                _enqueue(log_entry.id)
                logger.error("Action %s failed: %s", action.value, exc)
                raise

        return wrapper
    return decorator


# ── helpers ────────────────────────────────────────────────────────────────────

async def _extract_user_context(request: Optional[Request], kwargs: Dict[str, Any]) -> Dict[str, Any]:
    ctx: Dict[str, Any] = {"user_id": None, "email": None, "responsibility_category": None}
    try:
        # Already authenticated (JWT decoded into request.state.user)
        if request and hasattr(request.state, "user"):
            user = request.state.user
            ctx["user_id"] = user.get("id")
            ctx["email"] = user.get("email")
            ctx["responsibility_category"] = user.get("responsibility_category")
            return ctx

        # Unauthenticated — try to extract identifier from kwargs (Pydantic body)
        identifier: Optional[str] = None
        lookup_by_username = False
        for v in kwargs.values():
            if hasattr(v, "email") and v.email:
                identifier = v.email
                break
            if hasattr(v, "username") and v.username:
                identifier = v.username
                lookup_by_username = True
                break

        # Fall back to raw JSON body
        if not identifier and request:
            try:
                body = await request.json()
                if isinstance(body, dict):
                    for field in ("email", "username"):
                        if body.get(field):
                            identifier = body[field]
                            lookup_by_username = field == "username"
                            break
            except Exception:
                pass

        ctx["email"] = identifier if identifier and not lookup_by_username else None

        if identifier:
            try:
                from sqlalchemy import select
                from app.core.db import AsyncSessionLocal
                from app.models.user import User

                async with AsyncSessionLocal() as db:
                    if lookup_by_username:
                        q = select(User).where(User.username == identifier)
                    else:
                        q = select(User).where(User.email == identifier)
                    user = (await db.execute(q)).scalar_one_or_none()
                    if user:
                        ctx["user_id"] = user.id
                        ctx["email"] = user.email
                        ctx["responsibility_category"] = user.role
            except Exception as e:
                logger.warning("Could not look up user for logging: %s", e)

    except Exception as e:
        logger.warning("_extract_user_context failed: %s", e)
    return ctx


def _get_client_ip(request: Optional[Request]) -> Optional[str]:
    if not request:
        return None
    try:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        if request.client:
            return request.client.host
    except Exception:
        pass
    return None


async def _get_location_from_ip(ip: Optional[str]) -> Optional[str]:
    if not ip or ip in ("127.0.0.1", "localhost", "::1"):
        return None
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    parts = [p for p in (data.get("city"), data.get("regionName"), data.get("country")) if p]
                    return ", ".join(parts) or None
    except Exception:
        pass
    return None


def _http_to_reason(code: int) -> Optional[LogFailureReason]:
    return {
        400: LogFailureReason.INVALID_INPUT,
        401: LogFailureReason.INVALID_CREDENTIALS,
        403: LogFailureReason.INSUFFICIENT_PERMISSIONS,
        409: LogFailureReason.EMAIL_ALREADY_EXISTS,
        429: LogFailureReason.RATE_LIMIT_EXCEEDED,
        500: LogFailureReason.DATABASE_ERROR,
        502: LogFailureReason.NETWORK_ERROR,
        503: LogFailureReason.NETWORK_ERROR,
    }.get(code)


def _exc_to_reason(exc: Exception) -> LogFailureReason:
    s = str(exc).lower()
    if "invalid" in s and "credential" in s:
        return LogFailureReason.INVALID_CREDENTIALS
    if "account" in s and "lock" in s:
        return LogFailureReason.ACCOUNT_LOCKED
    if "email" in s and ("exist" in s or "duplicate" in s):
        return LogFailureReason.EMAIL_ALREADY_EXISTS
    if "password" in s and ("weak" in s or "invalid" in s):
        return LogFailureReason.WEAK_PASSWORD
    if "token" in s and "expir" in s:
        return LogFailureReason.TOKEN_EXPIRED
    if "kafka" in s:
        return LogFailureReason.KAFKA_ERROR
    if "database" in s or "sqlalchemy" in s:
        return LogFailureReason.DATABASE_ERROR
    return LogFailureReason.DATABASE_ERROR


async def _save_log(entry: UserActionLog) -> None:
    try:
        from app.core.db import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            db.add(entry)
            await db.commit()
            await db.refresh(entry)
    except Exception as e:
        logger.error("Failed to persist log entry: %s", e)


def _enqueue(log_id) -> None:
    try:
        from app.services.log_queue import get_log_queue
        q = get_log_queue()
        if q and not q.full():
            q.put_nowait(log_id)
    except Exception as e:
        logger.warning("Could not enqueue log for Kafka: %s", e)
