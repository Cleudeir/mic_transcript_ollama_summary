"""
Configuration settings for the Meeting Audio Transcriber application.
Centralized configuration to manage all timing and audio parameters.
"""

# Audio Capture Settings
CHUNK_DURATION = 30  # Duration in seconds for each audio chunk
OVERLAP_DURATION = 0.1  # Overlap duration in seconds (50ms)
SILENCE_THRESHOLD = 50  # Minimum amplitude to consider as meaningful audio

# Audio Quality Settings
AUDIO_BLOCKSIZE = 512  # Smaller block size for lower latency
AUDIO_LATENCY = "low"  # Request low latency mode
AUDIO_DTYPE = "int16"  # Audio data type

# Speech Recognition Settings
SPEECH_RECOGNITION_ENERGY_THRESHOLD = 200  # Lower threshold for sensitivity
SPEECH_RECOGNITION_PAUSE_THRESHOLD = 0.3  # Shorter pause threshold for real-time
SPEECH_RECOGNITION_PHRASE_THRESHOLD = 0.2  # Shorter phrase threshold

# Transcription Timeout Settings
TRANSCRIPTION_TIMEOUT = 5  # Operation timeout for transcription (seconds)
ASYNC_TIMEOUT = 8  # Async future timeout (seconds)
SLOW_TRANSCRIPTION_THRESHOLD = (
    2  # Log if transcription takes longer than this (seconds)
)

# Aliases for consistent naming convention
TRANSCRIPTION_OPERATION_TIMEOUT = TRANSCRIPTION_TIMEOUT  # Alias for consistent naming
TRANSCRIPTION_ASYNC_TIMEOUT = ASYNC_TIMEOUT  # Alias for consistent naming

# Recording Settings
DEFAULT_RECORDING_DURATION = (
    20  # Default duration for fixed-length recordings (seconds)
)
MICROPHONE_TEST_DURATION = 0.1  # Duration for microphone activity test (seconds)
MICROPHONE_ACTIVITY_THRESHOLD = 100  # Threshold for microphone activity detection

# Buffer and Processing Settings
AUDIO_SLEEP_INTERVAL = 0.05  # Sleep interval in audio processing loop (seconds)
ERROR_SLEEP_INTERVAL = 0.1  # Sleep interval when errors occur (seconds)

# Language Settings
DEFAULT_LANGUAGE = "pt-BR"  # Default language for transcription

# Performance Settings
MAX_TRANSCRIPTION_WORKERS = 2  # Number of parallel transcription workers
TRANSCRIPTION_QUEUE_SIZE = 10  # Maximum size of transcription queue


def get_overlap_samples(samplerate):
    """
    Calculate the number of samples for overlap based on sample rate.

    Args:
        samplerate (int): Audio sample rate

    Returns:
        int: Number of samples for overlap
    """
    return int(OVERLAP_DURATION * samplerate)


def get_chunk_samples(samplerate):
    """
    Calculate the number of samples for chunk based on sample rate.

    Args:
        samplerate (int): Audio sample rate

    Returns:
        int: Number of samples for chunk
    """
    return int(CHUNK_DURATION * samplerate)


def get_test_samples(samplerate):
    """
    Calculate the number of samples for microphone test based on sample rate.

    Args:
        samplerate (int): Audio sample rate

    Returns:
        int: Number of samples for microphone test
    """
    return int(MICROPHONE_TEST_DURATION * samplerate)


def get_recording_samples(samplerate, duration=None):
    """
    Calculate the number of samples for recording based on sample rate and duration.

    Args:
        samplerate (int): Audio sample rate
        duration (int, optional): Recording duration. Defaults to DEFAULT_RECORDING_DURATION.

    Returns:
        int: Number of samples for recording
    """
    if duration is None:
        duration = DEFAULT_RECORDING_DURATION
    return int(duration * samplerate)


def format_status_message(operation_type="recording"):
    """
    Format status messages with current configuration.

    Args:
        operation_type (str): Type of operation (recording, processing, etc.)

    Returns:
        str: Formatted status message
    """
    overlap_ms = int(OVERLAP_DURATION * 1000)
    if operation_type == "recording":
        return f"Recording: {CHUNK_DURATION}s samples with {overlap_ms}ms overlap"
    elif operation_type == "starting":
        return f"🎤 Starting continuous audio capture with {CHUNK_DURATION}s samples + {overlap_ms}ms overlap"
    elif operation_type == "processing":
        return f"Processing {CHUNK_DURATION}s sample with {overlap_ms}ms overlap"
    elif operation_type == "continuous":
        return f"🔴 CONTINUOUS: {CHUNK_DURATION}s sampling + {overlap_ms}ms overlap from device {{device_index}}"
    elif operation_type == "stopped":
        return f"Recording stopped - {CHUNK_DURATION}s samples with {overlap_ms}ms overlap completed"
    else:
        return f"{CHUNK_DURATION}s samples with {overlap_ms}ms overlap"


# Convenience functions for specific status messages
def format_overlap_message():
    """Format message for when recording is stopped."""
    return format_status_message("stopped")


def format_continuous_message(device_index):
    """Format message for continuous recording."""
    message = format_status_message("continuous")
    return message.format(device_index=device_index)


def format_worker_message(worker_id):
    """Format message for worker processing."""
    return f"Worker {worker_id}: " + format_status_message("processing")


def format_recording_start_message():
    """Format message for when recording starts."""
    return format_status_message("starting")


# Configuration validation
def validate_config():
    """
    Validate configuration values to ensure they are reasonable.

    Raises:
        ValueError: If configuration values are invalid
    """
    if CHUNK_DURATION <= 0:
        raise ValueError("CHUNK_DURATION must be positive")

    if OVERLAP_DURATION < 0:
        raise ValueError("OVERLAP_DURATION must be non-negative")

    if OVERLAP_DURATION >= CHUNK_DURATION:
        raise ValueError("OVERLAP_DURATION must be less than CHUNK_DURATION")

    if TRANSCRIPTION_TIMEOUT <= 0:
        raise ValueError("TRANSCRIPTION_TIMEOUT must be positive")

    if ASYNC_TIMEOUT <= TRANSCRIPTION_TIMEOUT:
        raise ValueError("ASYNC_TIMEOUT should be greater than TRANSCRIPTION_TIMEOUT")


def validate_speech_recognition_config():
    """
    Validate speech recognition configuration.

    Raises:
        ValueError: If speech recognition configuration values are invalid
    """
    if SPEECH_RECOGNITION_ENERGY_THRESHOLD <= 0:
        raise ValueError("SPEECH_RECOGNITION_ENERGY_THRESHOLD must be positive")

    if SPEECH_RECOGNITION_PAUSE_THRESHOLD <= 0:
        raise ValueError("SPEECH_RECOGNITION_PAUSE_THRESHOLD must be positive")

    if SPEECH_RECOGNITION_PHRASE_THRESHOLD <= 0:
        raise ValueError("SPEECH_RECOGNITION_PHRASE_THRESHOLD must be positive")


# Auto-validate configuration on import
validate_config()
validate_speech_recognition_config()

# Export commonly used values for convenience
__all__ = [
    "CHUNK_DURATION",
    "OVERLAP_DURATION",
    "SILENCE_THRESHOLD",
    "TRANSCRIPTION_TIMEOUT",
    "ASYNC_TIMEOUT",
    "DEFAULT_LANGUAGE",
    "get_overlap_samples",
    "get_chunk_samples",
    "format_status_message",
    "format_overlap_message",
    "format_continuous_message",
    "format_worker_message",
    "format_recording_start_message",
]
