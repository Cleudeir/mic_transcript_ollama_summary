import speech_recognition as sr
import tkinter as tk


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
    recognizer = sr.Recognizer()

    try:
        # Convert audio data to speech_recognition format
        audio_bytes = audio_data.tobytes()
        audio_data_sr = sr.AudioData(audio_bytes, samplerate, 2)

        # Perform transcription
        text = recognizer.recognize_google(audio_data_sr, language=language)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results; {e}"
    except Exception as e:
        return f"Error during transcription: {e}"


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
