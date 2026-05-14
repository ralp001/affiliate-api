"""Translation lookup with locale loading and caching."""
import json
import logging
from pathlib import Path
from typing import Any, Dict

from app.i18n.languages import DEFAULT_LANGUAGE, supported_codes

logger = logging.getLogger(__name__)

_LOCALES_DIR = Path(__file__).parent / "locales"
_CACHE: Dict[str, Dict[str, Any]] = {}


def _load_locale(lang: str) -> Dict[str, Any]:
    path = _LOCALES_DIR / f"{lang}.json"
    if not path.exists():
        logger.warning(f"Locale file missing for '{lang}': {path}")
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load locale '{lang}': {e}")
        return {}


def _get_locale(lang: str) -> Dict[str, Any]:
    if lang not in _CACHE:
        _CACHE[lang] = _load_locale(lang)
    return _CACHE[lang]


def _lookup(table: Dict[str, Any], key: str) -> Any:
    """Resolve dotted key (e.g. 'auth.account_locked') against a nested dict."""
    node: Any = table
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, str) else None


def t(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs: Any) -> str:
    """Translate a key into the requested language.

    Falls back to the default language if the key is missing in the requested locale.
    Returns the key itself if missing in the default locale (loud failure).
    Variable interpolation via kwargs uses str.format() semantics.
    """
    target = (lang or DEFAULT_LANGUAGE).lower()
    value = _lookup(_get_locale(target), key)

    if value is None and target != DEFAULT_LANGUAGE:
        value = _lookup(_get_locale(DEFAULT_LANGUAGE), key)

    if value is None:
        return key

    if kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, IndexError, ValueError) as e:
            logger.warning(f"Translation interpolation failed for '{key}' ({lang}): {e}")
            return value
    return value


def preload_all() -> None:
    """Eagerly load all supported locales (call at app startup if desired)."""
    for code in supported_codes():
        _get_locale(code)
