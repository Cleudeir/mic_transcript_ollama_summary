import sounddevice as sd
import numpy as np
import threading
import tkinter as tk


def is_microphone_active(device_index):
    """Test if a microphone is active by trying to record a small sample"""
    try:
        device_info = sd.query_devices(device_index)
        if device_info["max_input_channels"] == 0:
            return False

        # Try to record a very short sample to test if mic is working
        samplerate = int(device_info["default_samplerate"])
        test_audio = sd.rec(
            int(0.1 * samplerate),  # 0.1 second test
            samplerate=samplerate,
            channels=1,
            dtype="int16",
            device=device_index,
        )
        sd.wait()

        # Check if we got any audio data (not just silence)
        if np.max(np.abs(test_audio)) > 100:  # Some threshold for activity
            return True
        return True  # Even if silent, if no error occurred, consider it active
    except Exception:
        return False


def get_microphone_list():
    """Get only active/working microphones and prevent duplicates"""
    active_mics = []
    seen_names = set()
    all_devices = sd.query_devices()

    for idx, device in enumerate(all_devices):
        if device["max_input_channels"] > 0:
            device_name = device["name"]

            # Prevent duplicate microphone names
            if device_name in seen_names:
                continue
            seen_names.add(device_name)

            # Check if it's the default input device or if it's explicitly active
            try:
                default_input = sd.default.device[0]
                if idx == default_input or is_microphone_active(idx):
                    active_mics.append((idx, device_name))
            except Exception:
                # If we can't determine, include it anyway
                active_mics.append((idx, device_name))

    return active_mics


def capture_audio(device_index, duration=20):
    """
    Capture audio from a specific microphone device

    Args:
        device_index (int): The index of the audio device
        duration (int): Duration in seconds to record

    Returns:
        tuple: (audio_data, samplerate) or (None, None) if error
    """
    try:
        samplerate = int(sd.query_devices(device_index)["default_samplerate"])

        audio = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="int16",
            device=device_index,
        )
        sd.wait()

        return audio, samplerate
    except Exception as e:
        print(f"Error capturing audio from device {device_index}: {e}")
        return None, None


def capture_audio_realtime(device_index, on_audio_chunk, stop_event, chunk_duration=5):
    """
    Capture audio in real-time chunks for continuous transcription

    Args:
        device_index (int): The index of the audio device
        on_audio_chunk: Callback function to call with each audio chunk
        stop_event: Threading event to signal when to stop recording
        chunk_duration (int): Duration in seconds for each audio chunk
    """
    try:
        samplerate = int(sd.query_devices(device_index)["default_samplerate"])
        chunk_samples = int(chunk_duration * samplerate)

        while not stop_event.is_set():
            try:
                # Record a chunk
                audio_chunk = sd.rec(
                    chunk_samples,
                    samplerate=samplerate,
                    channels=1,
                    dtype="int16",
                    device=device_index,
                )
                sd.wait()

                # Check if we got meaningful audio (not just silence)
                if np.max(np.abs(audio_chunk)) > 100:  # Threshold for meaningful audio
                    on_audio_chunk(device_index, audio_chunk, samplerate)

            except Exception as e:
                print(f"Error in audio chunk from device {device_index}: {e}")
                break

    except Exception as e:
        print(f"Error setting up real-time capture for device {device_index}: {e}")


def capture_audio_with_callback(
    device_index, output_box, start_event, on_audio_captured
):
    """
    Capture audio and call a callback function when done

    Args:
        device_index (int): The index of the audio device
        output_box: GUI text box for status updates (can be None)
        start_event: Threading event to synchronize start
        on_audio_captured: Callback function to call with captured audio
    """
    duration = 20  # seconds
    try:
        samplerate = int(sd.query_devices(device_index)["default_samplerate"])

        if output_box is not None:
            output_box.insert(
                tk.END, f"Ready to record from device {device_index}...\n"
            )
            output_box.update()

        # Wait for all microphones to be ready
        start_event.wait()

        if output_box is not None:
            output_box.insert(tk.END, f"Recording from device {device_index}...\n")
            output_box.update()

        audio, samplerate = capture_audio(device_index, duration)

        if audio is not None:
            if output_box is not None:
                output_box.insert(
                    tk.END, f"Audio captured from device {device_index}...\n"
                )
                output_box.update()

            # Call the callback with the captured audio
            on_audio_captured(device_index, audio, samplerate, output_box)
        else:
            if output_box is not None:
                output_box.insert(
                    tk.END, f"Failed to capture audio from device {device_index}\n"
                )
                output_box.update()

    except Exception as e:
        if output_box is not None:
            output_box.insert(tk.END, f"Device {device_index}: Error - {e}\n")
            output_box.update()
        else:
            print(f"Device {device_index}: Error - {e}")
