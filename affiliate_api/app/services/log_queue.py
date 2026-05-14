"""
Module-level log queue registry — avoids circular imports between main.py and the decorator.
"""
import asyncio
from typing import Optional

_queue: Optional[asyncio.Queue] = None


def set_log_queue(q: asyncio.Queue) -> None:
    global _queue
    _queue = q


def get_log_queue() -> Optional[asyncio.Queue]:
    return _queue
