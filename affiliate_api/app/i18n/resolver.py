"""Language resolution from request headers."""
import re
from typing import List, Optional

from fastapi import Request

from app.i18n.languages import DEFAULT_LANGUAGE, is_supported, normalize


_ACCEPT_LANGUAGE_RE = re.compile(
    r"([a-zA-Z]{1,8}(?:-[a-zA-Z0-9]{1,8})*)\s*(?:;\s*q\s*=\s*([0-9.]+))?"
)


def _parse_accept_language(header: str) -> List[str]:
    """Return language tags from an Accept-Language header, ordered by quality desc."""
    if not header:
        return []
    items = []
    for match in _ACCEPT_LANGUAGE_RE.finditer(header):
        code = match.group(1)
        if not code or code == "*":
            continue
        try:
            q = float(match.group(2)) if match.group(2) else 1.0
        except ValueError:
            q = 1.0
        items.append((code, q))
    items.sort(key=lambda x: x[1], reverse=True)
    return [code for code, _ in items]


def _try(code: Optional[str]) -> Optional[str]:
    if not code:
        return None
    base = normalize(code)
    return base if is_supported(base) else None


def _explicit_override(request: Request) -> Optional[str]:
    """Return the explicit language override from X-Language header or ?lang= query param, or None."""
    return _try(request.headers.get("X-Language")) or _try(request.query_params.get("lang"))


def resolve_from_request(request: Request) -> str:
    """Resolve language from the full request context (no DB).

    Priority: X-Language header | ?lang= query param > Accept-Language > default.
    The ?lang= query param exists specifically for Swagger UI testing.
    """
    override = _explicit_override(request)
    if override:
        return override

    accept = request.headers.get("Accept-Language")
    if accept:
        for code in _parse_accept_language(accept):
            picked = _try(code)
            if picked:
                return picked

    return DEFAULT_LANGUAGE


def resolve_from_headers(request: Request) -> str:
    """Resolve language from headers alone (kept for backwards compat). Delegates to resolve_from_request."""
    return resolve_from_request(request)


def resolve_for_user(request: Request, user_preferred: Optional[str]) -> str:
    """Resolve language for an authenticated user.

    Priority: X-Language header | ?lang= query param > user_preferred > Accept-Language > default.
    """
    override = _explicit_override(request)
    if override:
        return override

    user_choice = _try(user_preferred)
    if user_choice:
        return user_choice

    return resolve_from_request(request)
