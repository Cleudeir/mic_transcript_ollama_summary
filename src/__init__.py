# Audio processing package for meeting transcription
__version__ = "1.0.0"

from .capture_audio import (
    get_microphone_list,
    capture_audio,
    capture_audio_with_callback,
    is_microphone_active,
)
from .transcribe_text import transcribe_audio, transcribe_and_display, batch_transcribe
from .gui import create_gui, run_gui, MicrophoneTranscriberGUI

__all__ = [
    "get_microphone_list",
    "capture_audio",
    "capture_audio_with_callback",
    "is_microphone_active",
    "transcribe_audio",
    "transcribe_and_display",
    "batch_transcribe",
    "create_gui",
    "run_gui",
    "MicrophoneTranscriberGUI",
]
