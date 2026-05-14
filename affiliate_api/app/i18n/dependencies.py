"""FastAPI dependency that exposes the resolved request language."""
from fastapi import Request

from app.i18n.languages import DEFAULT_LANGUAGE


def get_request_language(request: Request) -> str:
    """Return the language resolved for the current request.

    Resolution is performed by LanguageMiddleware (header-based) and refined by
    get_current_user (when an authenticated user has a preferred_language set in JWT).
    """
    return getattr(request.state, "language", DEFAULT_LANGUAGE)
