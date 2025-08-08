import sounddevice as sd
import speech_recognition as sr
import threading
import tkinter as tk
from tkinter import messagebox


# List all available microphones
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
        import numpy as np

        if np.max(np.abs(test_audio)) > 100:  # Some threshold for activity
            return True
        return True  # Even if silent, if no error occurred, consider it active
    except Exception:
        return False


def get_microphone_list():
    """Get only active/working microphones"""
    active_mics = []
    all_devices = sd.query_devices()

    for idx, device in enumerate(all_devices):
        if device["max_input_channels"] > 0:
            # Check if it's the default input device or if it's explicitly active
            try:
                default_input = sd.default.device[0]
                if idx == default_input or is_microphone_active(idx):
                    active_mics.append((idx, device["name"]))
            except Exception:
                # If we can't determine, include it anyway
                active_mics.append((idx, device["name"]))

    return active_mics


def record_and_transcribe(device_index, output_box, start_event):
    recognizer = sr.Recognizer()
    duration = 20  # seconds
    try:
        samplerate = int(sd.query_devices(device_index)["default_samplerate"])
        output_box.insert(tk.END, f"Ready to record from device {device_index}...\n")
        output_box.update()

        # Wait for all microphones to be ready
        start_event.wait()

        output_box.insert(tk.END, f"Recording from device {device_index}...\n")
        output_box.update()

        audio = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="int16",
            device=device_index,
        )
        sd.wait()

        output_box.insert(tk.END, f"Processing audio from device {device_index}...\n")
        output_box.update()

        audio_bytes = audio.tobytes()
        audio_data = sr.AudioData(audio_bytes, samplerate, 2)

        text = recognizer.recognize_google(audio_data, language="pt-BR")
        output_box.insert(tk.END, f"Device {device_index} transcription: {text}\n")
    except sr.UnknownValueError:
        output_box.insert(
            tk.END, f"Device {device_index}: Could not understand audio.\n"
        )
    except sr.RequestError as e:
        output_box.insert(
            tk.END, f"Device {device_index}: Could not request results; {e}\n"
        )
    except Exception as e:
        output_box.insert(tk.END, f"Device {device_index}: Error - {e}\n")
    output_box.update()


def start_listening(selected_indices, output_box):
    start_event = threading.Event()
    threads = []

    output_box.insert(
        tk.END, "Preparing to record from both microphones simultaneously...\n"
    )
    output_box.update()

    # Start all threads
    for idx in selected_indices:
        t = threading.Thread(
            target=record_and_transcribe, args=(idx, output_box, start_event)
        )
        t.start()
        threads.append(t)

    # Wait a moment for all threads to be ready, then start recording
    threading.Timer(1.0, lambda: start_event.set()).start()

    # Wait for all threads to complete
    for t in threads:
        t.join()


def gui():
    mics = get_microphone_list()
    root = tk.Tk()
    root.title("Microphone Selector & Transcriber")

    tk.Label(root, text="Select two microphones:").pack()
    mic_vars = []
    for idx, name in mics:
        var = tk.IntVar()
        cb = tk.Checkbutton(root, text=f"{idx}: {name}", variable=var)
        cb.pack(anchor="w")
        mic_vars.append((var, idx))

    output_box = tk.Text(root, height=10, width=60)
    output_box.pack()

    status_var = tk.StringVar()
    status_label = tk.Label(root, textvariable=status_var)
    status_label.pack()

    def threaded_listen(selected):
        try:
            status_var.set("Listening...")
            start_listening(selected, output_box)
            status_var.set("Done.")
        except Exception as e:
            status_var.set(f"Error: {e}")

    def on_listen():
        selected = [idx for var, idx in mic_vars if var.get()]
        if len(selected) != 2:
            messagebox.showerror("Error", "Please select exactly two microphones.")
            return
        output_box.delete(1.0, tk.END)
        threading.Thread(target=threaded_listen, args=(selected,), daemon=True).start()

    listen_btn = tk.Button(root, text="Listen & Transcribe", command=on_listen)
    listen_btn.pack()

    root.mainloop()


if __name__ == "__main__":
    gui()
