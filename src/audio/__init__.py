"""Audio package: microphone discovery and capture utilities.

This package provides a clean namespace while re-exporting the existing
implementations from the legacy modules under ``src.capture_audio``.
"""

from .capture import (
    get_microphone_list,
    capture_audio,
    capture_audio_with_callback,
    capture_audio_realtime,
    is_microphone_active,
)

__all__ = [
    "get_microphone_list",
    "capture_audio",
    "capture_audio_with_callback",
    "capture_audio_realtime",
    "is_microphone_active",
]
