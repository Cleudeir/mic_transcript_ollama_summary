import speech_recognition as sr
import tkinter as tk
import threading
import time
import queue
import numpy as np
import concurrent.futures
from .config import (
    SPEECH_RECOGNITION_ENERGY_THRESHOLD,
    SPEECH_RECOGNITION_PAUSE_THRESHOLD,
    SPEECH_RECOGNITION_PHRASE_THRESHOLD,
    TRANSCRIPTION_OPERATION_TIMEOUT,
    TRANSCRIPTION_ASYNC_TIMEOUT,
    CHUNK_DURATION,
    validate_speech_recognition_config,
)

# Validate configuration on import
validate_speech_recognition_config()

# Global recognizer instance to avoid recreation overhead
_recognizer = sr.Recognizer()
_recognizer.energy_threshold = SPEECH_RECOGNITION_ENERGY_THRESHOLD
_recognizer.dynamic_energy_threshold = True
_recognizer.pause_threshold = SPEECH_RECOGNITION_PAUSE_THRESHOLD
_recognizer.phrase_threshold = SPEECH_RECOGNITION_PHRASE_THRESHOLD

# Set operation timeout for configured audio chunks
_recognizer.operation_timeout = TRANSCRIPTION_OPERATION_TIMEOUT


def transcribe_audio(audio_data, samplerate, language="pt-BR"):
    """
    Transcribe audio data to text

    Args:
        audio_data: Raw audio data
        samplerate (int): Sample rate of the audio
        language (str): Language code for transcription

    Returns:
        str: Transcribed text or error message
    """
    global _recognizer

    try:
        # Convert audio data to speech_recognition format
        audio_bytes = audio_data.tobytes()
        audio_data_sr = sr.AudioData(audio_bytes, samplerate, 2)

        # Perform transcription with extended timeout for longer chunks
        text = _recognizer.recognize_google(audio_data_sr, language=language)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results; {e}"
    except Exception as e:
        return f"Error during transcription: {e}"


def transcribe_audio_realtime(audio_data, samplerate, language="pt-BR"):
    """
    Fast transcription optimized for real-time chunks with minimal audio preprocessing

    Args:
        audio_data: Raw audio data
        samplerate (int): Sample rate of the audio
        language (str): Language code for transcription

    Returns:
        str: Transcribed text or None if no meaningful audio
    """
    global _recognizer

    try:
        # Quick check for meaningful audio content
        if np.max(np.abs(audio_data)) < 100:
            return None  # Too quiet, skip transcription

        # Convert audio data to speech_recognition format
        audio_bytes = audio_data.tobytes()
        audio_data_sr = sr.AudioData(audio_bytes, samplerate, 2)

        # Perform transcription with extended timeout for 1-second chunks
        start_time = time.time()
        # Use shorter timeout for 1-second audio chunks
        text = _recognizer.recognize_google(audio_data_sr, language=language)

        # Log processing time for debugging
        processing_time = time.time() - start_time
        if processing_time > 2.0:  # Log if transcription takes longer than 2 seconds
            print(f"Slow transcription for 1s chunk: {processing_time:.2f}s")

        return text
    except sr.UnknownValueError:
        return None  # No speech detected
    except sr.RequestError as e:
        return f"Network error: {e}"
    except Exception as e:
        return f"Transcription error: {e}"


def transcribe_audio_async(audio_data, samplerate, language="pt-BR"):
    """
    Ultra-fast asynchronous transcription optimized for continuous real-time processing

    Returns:
        str: Transcribed text or status message
    """
    import concurrent.futures

    # Quick silence check - skip transcription for very quiet audio
    if np.max(np.abs(audio_data)) < 80:
        return None

    def transcribe_worker():
        """Fast transcription worker with extended timeout for 1s chunks"""
        global _recognizer

        try:
            # Convert audio data to speech_recognition format
            audio_bytes = audio_data.tobytes()
            audio_data_sr = sr.AudioData(audio_bytes, samplerate, 2)

            # Use shorter timeout for 1-second audio chunks
            _recognizer.operation_timeout = 5.0  # Extended timeout for 1s chunks

            # Perform transcription with extended timeout
            text = _recognizer.recognize_google(audio_data_sr, language=language)
            return text

        except sr.UnknownValueError:
            return None  # No speech detected
        except sr.RequestError as e:
            return f"Network error: {e}"
        except Exception as e:
            return f"Error: {e}"

    # Use ThreadPoolExecutor for better performance
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(transcribe_worker)
        try:
            # Wait for result with configured timeout for audio chunks
            result = future.result(timeout=TRANSCRIPTION_ASYNC_TIMEOUT)
            return result
        except concurrent.futures.TimeoutError:
            return f"Transcription timeout ({TRANSCRIPTION_ASYNC_TIMEOUT}s limit for {CHUNK_DURATION}s chunk)"
        except Exception as e:
            return f"Async error: {e}"


def transcribe_audio_fast(audio_data, samplerate, language="pt-BR"):
    """
    Fastest possible transcription for continuous pipeline - no timeout handling
    """
    global _recognizer

    try:
        # Ultra-quick silence check
        if np.max(np.abs(audio_data)) < 100:
            return None

        # Convert audio data to speech_recognition format
        audio_bytes = audio_data.tobytes()
        audio_data_sr = sr.AudioData(audio_bytes, samplerate, 2)

        # Direct transcription without timeout handling for speed
        text = _recognizer.recognize_google(audio_data_sr, language=language)
        return text

    except sr.UnknownValueError:
        return None  # No speech detected
    except sr.RequestError as e:
        return f"Network error: {e}"
    except Exception as e:
        return f"Error: {e}"


def transcribe_and_display(
    device_index, audio_data, samplerate, output_box, language="pt-BR"
):
    """
    Transcribe audio and display result in GUI

    Args:
        device_index (int): Device index for identification
        audio_data: Raw audio data
        samplerate (int): Sample rate of the audio
        output_box: GUI text box for output
        language (str): Language code for transcription
    """
    output_box.insert(tk.END, f"Processing audio from device {device_index}...\n")
    output_box.update()

    text = transcribe_audio(audio_data, samplerate, language)

    if text.startswith("Could not") or text.startswith("Error"):
        output_box.insert(tk.END, f"Device {device_index}: {text}\n")
    else:
        output_box.insert(tk.END, f"Device {device_index} transcription: {text}\n")

    output_box.update()


def batch_transcribe(audio_files, language="pt-BR"):
    """
    Transcribe multiple audio files

    Args:
        audio_files (list): List of tuples (device_index, audio_data, samplerate)
        language (str): Language code for transcription

    Returns:
        dict: Dictionary mapping device_index to transcription result
    """
    results = {}

    for device_index, audio_data, samplerate in audio_files:
        results[device_index] = transcribe_audio(audio_data, samplerate, language)

    return results
