"""Supported languages and language-code utilities."""
from enum import Enum
from typing import List


class SupportedLanguage(str, Enum):
    EN = "en"
    FR = "fr"
    ES = "es"
    JA = "ja"
    ZH = "zh"
    KO = "ko"
    IT = "it"
    DE = "de"
    AR = "ar"
    PT = "pt"


DEFAULT_LANGUAGE: str = SupportedLanguage.EN.value


def supported_codes() -> List[str]:
    return [lang.value for lang in SupportedLanguage]


def normalize(code: str) -> str:
    """Strip region/script and lowercase (e.g. 'en-US' -> 'en'). Does not validate."""
    if not code:
        return ""
    return code.lower().split("-")[0].strip()


def is_supported(code: str) -> bool:
    if not code:
        return False
    return code.lower() in supported_codes()
