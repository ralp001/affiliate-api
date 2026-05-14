"""Internationalization module for affiliate-api.

Public API:
    t(key, lang, **kwargs) — translate a dotted key
    get_request_language — FastAPI dependency
    LanguageMiddleware — registered in app/main.py
    SupportedLanguage / DEFAULT_LANGUAGE / is_supported / normalize / supported_codes
    resolve_from_headers / resolve_for_user — used by middleware and auth dependencies
"""
from app.i18n.dependencies import get_request_language
from app.i18n.languages import (
    DEFAULT_LANGUAGE,
    SupportedLanguage,
    is_supported,
    normalize,
    supported_codes,
)
from app.i18n.middleware import LanguageMiddleware
from app.i18n.resolver import resolve_for_user, resolve_from_headers
from app.i18n.translator import preload_all, t

__all__ = [
    "DEFAULT_LANGUAGE",
    "LanguageMiddleware",
    "SupportedLanguage",
    "get_request_language",
    "is_supported",
    "normalize",
    "preload_all",
    "resolve_for_user",
    "resolve_from_headers",
    "supported_codes",
    "t",
]
