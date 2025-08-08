import threading
import tkinter as tk
from tkinter import messagebox
from src.capture_audio import get_microphone_list, capture_audio_with_callback
from src.transcribe_text import transcribe_and_display


class MicrophoneTranscriberGUI:
    """Main GUI class for the Microphone Transcriber application"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Microphone Selector & Transcriber")
        self.root.geometry("600x500")

        # Initialize variables
        self.mic_vars = []
        self.mics = []

        # Setup GUI components
        self.setup_gui()

    def setup_gui(self):
        """Setup all GUI components"""
        # Title
        title_label = tk.Label(
            self.root, text="Meeting Audio Transcriber", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        # Instructions
        instruction_label = tk.Label(
            self.root,
            text="Select exactly two microphones for simultaneous recording:",
            font=("Arial", 10),
        )
        instruction_label.pack(pady=5)

        # Status bar (create early so it's available for load_microphones)
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")

        # Microphone selection frame
        self.mic_frame = tk.Frame(self.root)
        self.mic_frame.pack(pady=10, padx=20, fill=tk.X)

        # Load and display microphones
        self.load_microphones()

        # Output text area
        output_label = tk.Label(
            self.root, text="Transcription Output:", font=("Arial", 10, "bold")
        )
        output_label.pack(pady=(20, 5))

        # Text area with scrollbar
        text_frame = tk.Frame(self.root)
        text_frame.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        self.output_box = tk.Text(text_frame, height=15, width=70, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.output_box.yview
        )
        self.output_box.configure(yscrollcommand=scrollbar.set)

        self.output_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Control buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Listen button
        self.listen_btn = tk.Button(
            button_frame,
            text="🎤 Listen & Transcribe",
            command=self.on_listen,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5,
        )
        self.listen_btn.pack(side=tk.LEFT, padx=5)

        # Clear button
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear Output",
            command=self.clear_output,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=15,
            pady=5,
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Refresh microphones button
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh Mics",
            command=self.refresh_microphones,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=5,
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # Status bar (display at bottom)
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9),
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def load_microphones(self):
        """Load and display available microphones"""
        try:
            self.mics = get_microphone_list()

            # Clear existing checkboxes
            for widget in self.mic_frame.winfo_children():
                widget.destroy()
            self.mic_vars.clear()

            if not self.mics:
                no_mic_label = tk.Label(
                    self.mic_frame,
                    text="No microphones found. Please check your audio devices.",
                    fg="red",
                )
                no_mic_label.pack()
                return

            # Create checkboxes for each microphone
            for idx, name in self.mics:
                var = tk.IntVar()
                cb = tk.Checkbutton(
                    self.mic_frame,
                    text=f"Device {idx}: {name}",
                    variable=var,
                    font=("Arial", 9),
                    anchor=tk.W,
                )
                cb.pack(anchor="w", pady=2)
                self.mic_vars.append((var, idx))

            self.status_var.set(f"Found {len(self.mics)} microphone(s)")

        except Exception as e:
            error_label = tk.Label(
                self.mic_frame, text=f"Error loading microphones: {str(e)}", fg="red"
            )
            error_label.pack()
            self.status_var.set("Error loading microphones")

    def refresh_microphones(self):
        """Refresh the microphone list"""
        self.status_var.set("Refreshing microphones...")
        self.root.update()
        self.load_microphones()

    def clear_output(self):
        """Clear the output text area"""
        self.output_box.delete(1.0, tk.END)
        self.status_var.set("Output cleared")

    def record_and_transcribe(self, device_index, start_event):
        """Capture audio and transcribe it for a specific device"""

        def on_audio_captured(device_index, audio_data, samplerate, output_box):
            transcribe_and_display(device_index, audio_data, samplerate, output_box)

        capture_audio_with_callback(
            device_index, self.output_box, start_event, on_audio_captured
        )

    def start_listening(self, selected_indices):
        """Start listening from selected microphones"""
        start_event = threading.Event()
        threads = []

        self.output_box.insert(
            tk.END, "Preparing to record from both microphones simultaneously...\n"
        )
        self.output_box.update()

        # Start all threads
        for idx in selected_indices:
            t = threading.Thread(
                target=self.record_and_transcribe, args=(idx, start_event)
            )
            t.start()
            threads.append(t)

        # Wait a moment for all threads to be ready, then start recording
        threading.Timer(1.0, lambda: start_event.set()).start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

    def threaded_listen(self, selected):
        """Run listening in a separate thread"""
        try:
            self.status_var.set("Listening...")
            self.listen_btn.config(state=tk.DISABLED, text="🎤 Recording...")
            self.root.update()

            self.start_listening(selected)

            self.status_var.set("Done.")
        except Exception as e:
            self.status_var.set(f"Error: {e}")
            self.output_box.insert(tk.END, f"Error during recording: {str(e)}\n")
        finally:
            self.listen_btn.config(state=tk.NORMAL, text="🎤 Listen & Transcribe")
            self.root.update()

    def on_listen(self):
        """Handle listen button click"""
        selected = [idx for var, idx in self.mic_vars if var.get()]

        if len(selected) != 2:
            messagebox.showerror(
                "Selection Error",
                "Please select exactly two microphones.\n\n"
                f"You have selected {len(selected)} microphone(s).",
            )
            return

        # Confirm before starting
        device_names = [name for idx, name in self.mics if idx in selected]
        confirm_msg = (
            f"Start recording from:\n"
            f"• {device_names[0]}\n"
            f"• {device_names[1]}\n\n"
            f"Recording will last 20 seconds."
        )

        if messagebox.askyesno("Confirm Recording", confirm_msg):
            self.output_box.delete(1.0, tk.END)
            threading.Thread(
                target=self.threaded_listen, args=(selected,), daemon=True
            ).start()

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def create_gui():
    """Factory function to create and return GUI instance"""
    return MicrophoneTranscriberGUI()


def run_gui():
    """Convenience function to create and run the GUI"""
    gui = create_gui()
    gui.run()


if __name__ == "__main__":
    run_gui()
