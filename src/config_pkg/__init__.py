"""Config shims: re-export configuration constants and helpers.

This allows importing as `from src.config_pkg import CHUNK_DURATION` while
keeping the original `src.config` module as the single source of truth.
"""

from src.config import *  # noqa: F401,F403

__all__ = [name for name in dir() if not name.startswith("_")]
