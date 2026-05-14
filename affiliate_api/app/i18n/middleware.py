"""Middleware that resolves request language from headers and stores it on request.state."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.i18n.resolver import resolve_from_request


class LanguageMiddleware(BaseHTTPMiddleware):
    """Resolve request language for every request and store it on request.state.language.

    Checks in order: X-Language header | ?lang= query param > Accept-Language > default.
    Authenticated routes may refine this further in get_current_user once the user's
    preferred_language is known from the JWT payload.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.language = resolve_from_request(request)
        return await call_next(request)
