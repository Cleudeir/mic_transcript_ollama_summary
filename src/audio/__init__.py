"""Audio package: microphone discovery and capture utilities.

This package exposes a clean namespace for audio operations; implementations
live in ``src.audio.capture``.
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
