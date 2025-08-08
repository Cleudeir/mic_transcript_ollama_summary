import threading
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
import os
import datetime
from src.capture_audio import get_microphone_list, capture_audio_with_callback, capture_audio_realtime
from src.transcribe_text import transcribe_and_display
import tkinter as tk
from tkinter import messagebox
from src.capture_audio import get_microphone_list, capture_audio_with_callback
from src.transcribe_text import transcribe_and_display


class MicrophoneTranscriberGUI:
    """Main GUI class for the Microphone Transcriber application"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Microphone Selector & Transcriber")
        self.root.geometry("900x700")

        # Initialize variables
        self.mic_vars = []
        self.mics = []
        self.config_file = "mic_config.json"
        self.is_recording = False
        self.stop_events = []  # List of stop events for real-time recording
        self.recording_threads = []  # List of recording threads
        
        # Create separate text widgets for logs and transcripts
        self.log_outputs = {}  # Dictionary to store log outputs for each device
        self.transcript_outputs = {}  # Dictionary to store transcript outputs for each device

        # Setup GUI components
        self.setup_gui()
        
        # Load saved microphone preferences
        self.load_mic_preferences()

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

        # Control buttons frame (moved up for better layout)
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Listen button
        self.listen_btn = tk.Button(
            button_frame,
            text="🎤 Start Real-time Transcription",
            command=self.toggle_recording,
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
            text="🗑️ Clear All",
            command=self.clear_all_output,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=15,
            pady=5,
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Save button
        save_btn = tk.Button(
            button_frame,
            text="💾 Save Transcripts",
            command=self.save_transcripts,
            font=("Arial", 10),
            bg="#9C27B0",
            fg="white",
            padx=15,
            pady=5,
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        # Refresh microphones button
        refresh_btn = tk.Button(
            button_frame,
            text="� Refresh Mics",
            command=self.refresh_microphones,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=5,
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # Save preferences button
        save_btn = tk.Button(
            button_frame,
            text="� Save Mic Choice",
            command=self.save_mic_preferences,
            font=("Arial", 10),
            bg="#FF9800",
            fg="white",
            padx=15,
            pady=5,
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Create tabs for different views
        self.create_combined_tab()
        self.create_logs_tab()
        self.create_transcripts_tab()

        # Set up output mapping after tabs are created
        self.setup_output_mapping()

        # Status bar (display at bottom)
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9),
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def create_combined_tab(self):
        """Create the combined view tab showing both logs and transcripts"""
        combined_frame = ttk.Frame(self.notebook)
        self.notebook.add(combined_frame, text="📊 Combined View")
        
        # Combined output area
        combined_text_frame = tk.Frame(combined_frame)
        combined_text_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        self.combined_output = tk.Text(combined_text_frame, height=20, width=100, wrap=tk.WORD)
        combined_scrollbar = tk.Scrollbar(combined_text_frame, orient=tk.VERTICAL, command=self.combined_output.yview)
        self.combined_output.configure(yscrollcommand=combined_scrollbar.set)
        
        self.combined_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        combined_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_logs_tab(self):
        """Create the logs tab showing system messages and status"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📝 System Logs")
        
        # Create paned window for two microphones
        logs_paned = ttk.PanedWindow(logs_frame, orient=tk.HORIZONTAL)
        logs_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Microphone 1 logs
        mic1_log_frame = ttk.LabelFrame(logs_paned, text="Microphone 1 - System Logs")
        logs_paned.add(mic1_log_frame, weight=1)
        
        self.mic1_log_text = tk.Text(mic1_log_frame, height=20, wrap=tk.WORD)
        mic1_log_scroll = tk.Scrollbar(mic1_log_frame, orient=tk.VERTICAL, command=self.mic1_log_text.yview)
        self.mic1_log_text.configure(yscrollcommand=mic1_log_scroll.set)
        
        self.mic1_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mic1_log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Microphone 2 logs
        mic2_log_frame = ttk.LabelFrame(logs_paned, text="Microphone 2 - System Logs")
        logs_paned.add(mic2_log_frame, weight=1)
        
        self.mic2_log_text = tk.Text(mic2_log_frame, height=20, wrap=tk.WORD)
        mic2_log_scroll = tk.Scrollbar(mic2_log_frame, orient=tk.VERTICAL, command=self.mic2_log_text.yview)
        self.mic2_log_text.configure(yscrollcommand=mic2_log_scroll.set)
        
        self.mic2_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mic2_log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def create_transcripts_tab(self):
        """Create the transcripts tab showing only the transcribed text"""
        transcripts_frame = ttk.Frame(self.notebook)
        self.notebook.add(transcripts_frame, text="📄 Transcripts Only")
        
        # Create paned window for two microphones
        transcripts_paned = ttk.PanedWindow(transcripts_frame, orient=tk.HORIZONTAL)
        transcripts_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Microphone 1 transcripts
        mic1_transcript_frame = ttk.LabelFrame(transcripts_paned, text="Microphone 1 - Transcripts")
        transcripts_paned.add(mic1_transcript_frame, weight=1)
        
        self.mic1_transcript_text = tk.Text(mic1_transcript_frame, height=20, wrap=tk.WORD)
        mic1_transcript_scroll = tk.Scrollbar(mic1_transcript_frame, orient=tk.VERTICAL, command=self.mic1_transcript_text.yview)
        self.mic1_transcript_text.configure(yscrollcommand=mic1_transcript_scroll.set)
        
        self.mic1_transcript_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mic1_transcript_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Microphone 2 transcripts
        mic2_transcript_frame = ttk.LabelFrame(transcripts_paned, text="Microphone 2 - Transcripts")
        transcripts_paned.add(mic2_transcript_frame, weight=1)
        
        self.mic2_transcript_text = tk.Text(mic2_transcript_frame, height=20, wrap=tk.WORD)
        mic2_transcript_scroll = tk.Scrollbar(mic2_transcript_frame, orient=tk.VERTICAL, command=self.mic2_transcript_text.yview)
        self.mic2_transcript_text.configure(yscrollcommand=mic2_transcript_scroll.set)
        
        self.mic2_transcript_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mic2_transcript_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def save_transcripts(self):
        """Save transcripts to files"""
        if not self.mic1_transcript_text.get(1.0, tk.END).strip() and not self.mic2_transcript_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "No transcripts to save!")
            return
        
        # Get current timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Ask user for save location
            initial_filename = f"meeting_transcripts_{timestamp}.txt"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialname=initial_filename,
                title="Save Transcripts"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Meeting Transcripts - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    # Save Microphone 1 transcripts
                    mic1_content = self.mic1_transcript_text.get(1.0, tk.END).strip()
                    if mic1_content:
                        f.write("MICROPHONE 1 TRANSCRIPTS:\n")
                        f.write("-" * 30 + "\n")
                        f.write(mic1_content + "\n\n")
                    
                    # Save Microphone 2 transcripts
                    mic2_content = self.mic2_transcript_text.get(1.0, tk.END).strip()
                    if mic2_content:
                        f.write("MICROPHONE 2 TRANSCRIPTS:\n")
                        f.write("-" * 30 + "\n")
                        f.write(mic2_content + "\n\n")
                
                self.status_var.set(f"Transcripts saved to: {file_path}")
                messagebox.showinfo("Success", f"Transcripts saved successfully!\n\nLocation: {file_path}")
                
        except Exception as e:
            self.status_var.set(f"Error saving transcripts: {e}")
            messagebox.showerror("Error", f"Failed to save transcripts: {e}")

    def save_mic_preferences(self):
        """Save the currently selected microphones to a config file"""
        selected = [idx for var, idx in self.mic_vars if var.get()]
        
        if len(selected) == 2:
            # Get microphone names for the selected indices
            selected_mics = []
            for idx in selected:
                for mic_idx, mic_name in self.mics:
                    if mic_idx == idx:
                        selected_mics.append({"index": idx, "name": mic_name})
                        break
            
            config = {
                "saved_microphones": selected_mics,
                "timestamp": threading.current_thread().name
            }
            
            try:
                with open(self.config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                self.status_var.set("Microphone preferences saved!")
                messagebox.showinfo("Saved", "Microphone preferences have been saved!")
            except Exception as e:
                self.status_var.set(f"Error saving preferences: {e}")
                messagebox.showerror("Error", f"Failed to save preferences: {e}")
        else:
            messagebox.showwarning("Warning", "Please select exactly two microphones before saving.")

    def load_mic_preferences(self):
        """Load previously saved microphone preferences"""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            saved_mics = config.get("saved_microphones", [])
            if len(saved_mics) == 2:
                # Try to select the saved microphones
                saved_indices = [mic["index"] for mic in saved_mics]
                self.auto_select_microphones(saved_indices)
                
                mic_names = [mic["name"] for mic in saved_mics]
                self.status_var.set(f"Loaded preferences: {mic_names[0][:20]}... & {mic_names[1][:20]}...")
            
        except Exception as e:
            self.status_var.set(f"Error loading preferences: {e}")

    def auto_select_microphones(self, indices):
        """Automatically select microphones by their indices"""
        for var, idx in self.mic_vars:
            if idx in indices:
                var.set(1)
            else:
                var.set(0)

    def setup_output_mapping(self):
        """Set up the mapping between device indices and output text widgets"""
        # This will be called after microphones are loaded to set up the output mapping
        self.output_widgets = {
            "combined": self.combined_output,
            "mic1_log": self.mic1_log_text,
            "mic2_log": self.mic2_log_text,
            "mic1_transcript": self.mic1_transcript_text,
            "mic2_transcript": self.mic2_transcript_text
        }

    def get_output_widgets_for_device(self, device_index, selected_indices):
        """Get the appropriate output widgets for a device"""
        # Determine if this is mic1 or mic2 based on selection order
        mic_position = "mic1" if device_index == selected_indices[0] else "mic2"
        
        return {
            "combined": self.output_widgets["combined"],
            "log": self.output_widgets[f"{mic_position}_log"],
            "transcript": self.output_widgets[f"{mic_position}_transcript"]
        }

    def add_log_message(self, device_index, message, selected_indices):
        """Add a log message to the appropriate widgets"""
        widgets = self.get_output_widgets_for_device(device_index, selected_indices)
        
        # Add timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # Add to combined view
        widgets["combined"].insert(tk.END, f"Device {device_index}: {log_message}")
        widgets["combined"].see(tk.END)
        
        # Add to device-specific log
        widgets["log"].insert(tk.END, log_message)
        widgets["log"].see(tk.END)
        
        # Update UI
        self.root.update()

    def add_transcript_message(self, device_index, transcript, selected_indices):
        """Add a transcript message to the appropriate widgets"""
        widgets = self.get_output_widgets_for_device(device_index, selected_indices)
        
        # Add timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        transcript_message = f"[{timestamp}] {transcript}\n\n"
        
        # Add to combined view
        widgets["combined"].insert(tk.END, f"Device {device_index} TRANSCRIPT: {transcript_message}")
        widgets["combined"].see(tk.END)
        
        # Add to device-specific transcript area
        widgets["transcript"].insert(tk.END, transcript_message)
        widgets["transcript"].see(tk.END)
        
        # Update UI
        self.root.update()

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
        # Re-apply saved preferences after refresh
        self.load_mic_preferences()

    def clear_all_output(self):
        """Clear all output text areas"""
        self.combined_output.delete(1.0, tk.END)
        self.mic1_log_text.delete(1.0, tk.END)
        self.mic2_log_text.delete(1.0, tk.END)
        self.mic1_transcript_text.delete(1.0, tk.END)
        self.mic2_transcript_text.delete(1.0, tk.END)
        self.status_var.set("All output cleared")

    def transcribe_and_display_separated(self, device_index, audio_data, samplerate, selected_indices):
        """Custom transcribe function that separates logs and transcripts"""
        from src.transcribe_text import transcribe_audio
        
        # Add processing log
        self.add_log_message(device_index, "Processing audio...", selected_indices)
        
        # Transcribe the audio
        transcript = transcribe_audio(audio_data, samplerate, "pt-BR")
        
        # Display results
        if transcript.startswith("Could not") or transcript.startswith("Error"):
            self.add_log_message(device_index, transcript, selected_indices)
        else:
            self.add_log_message(device_index, "Transcription completed successfully", selected_indices)
            self.add_transcript_message(device_index, transcript, selected_indices)

    def toggle_recording(self):
        """Toggle between start and stop recording"""
        if not self.is_recording:
            self.start_realtime_recording()
        else:
            self.stop_realtime_recording()

    def start_realtime_recording(self):
        """Start real-time recording and transcription"""
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
            f"Start real-time recording from:\n"
            f"• {device_names[0]}\n"
            f"• {device_names[1]}\n\n"
            f"Recording will continue until you stop it."
        )

        if messagebox.askyesno("Confirm Recording", confirm_msg):
            self.clear_all_output()
            
            # Update UI state
            self.is_recording = True
            self.listen_btn.config(text="🛑 Stop Recording", bg="#f44336")
            self.status_var.set("Real-time recording started...")
            
            # Create stop events for each microphone
            self.stop_events = [threading.Event() for _ in selected]
            self.recording_threads = []
            
            # Start recording threads
            for i, device_index in enumerate(selected):
                stop_event = self.stop_events[i]
                thread = threading.Thread(
                    target=self.realtime_record_and_transcribe,
                    args=(device_index, stop_event, selected),
                    daemon=True
                )
                thread.start()
                self.recording_threads.append(thread)
                
                # Add initial log message
                self.add_log_message(device_index, f"Started real-time recording from device {device_index}", selected)

    def stop_realtime_recording(self):
        """Stop real-time recording"""
        self.is_recording = False
        
        # Signal all threads to stop
        for stop_event in self.stop_events:
            stop_event.set()
        
        # Update UI
        self.listen_btn.config(text="🎤 Start Real-time Transcription", bg="#4CAF50")
        self.status_var.set("Recording stopped")
        
        # Add log message
        self.combined_output.insert(tk.END, "\n=== RECORDING STOPPED ===\n\n")
        self.combined_output.see(tk.END)

    def realtime_record_and_transcribe(self, device_index, stop_event, selected_indices):
        """Handle real-time recording and transcription for a specific device"""
        def on_audio_chunk(device_idx, audio_data, samplerate):
            # Use our custom transcribe function for real-time chunks
            self.transcribe_and_display_separated(device_idx, audio_data, samplerate, selected_indices)

        # Start real-time capture
        capture_audio_realtime(device_index, on_audio_chunk, stop_event, chunk_duration=5)
        
        # Add completion message when thread ends
        if not stop_event.is_set():  # If stopped due to error, not user action
            self.add_log_message(device_index, f"Recording from device {device_index} ended unexpectedly", selected_indices)

    def record_and_transcribe(self, device_index, start_event, selected_indices):
        """Capture audio and transcribe it for a specific device"""
        def on_audio_captured(device_index, audio_data, samplerate, output_box):
            # Use our custom transcribe function
            self.transcribe_and_display_separated(device_index, audio_data, samplerate, selected_indices)

        # Add initial log message
        self.add_log_message(device_index, f"Ready to record from device {device_index}...", selected_indices)
        
        capture_audio_with_callback(
            device_index, None, start_event, on_audio_captured
        )

    def refresh_microphones(self):
        """Refresh the microphone list"""
        self.status_var.set("Refreshing microphones...")
        self.root.update()
        self.load_microphones()

    def start_listening(self, selected_indices):
        """Start listening from selected microphones"""
        start_event = threading.Event()
        threads = []

        # Add initial message to combined view
        self.combined_output.insert(
            tk.END, "Preparing to record from both microphones simultaneously...\n"
        )
        self.combined_output.update()

        # Start all threads
        for idx in selected_indices:
            t = threading.Thread(
                target=self.record_and_transcribe, args=(idx, start_event, selected_indices)
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
            self.combined_output.insert(tk.END, f"Error during recording: {str(e)}\n")
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
            self.clear_all_output()
            threading.Thread(
                target=self.threaded_listen, args=(selected,), daemon=True
            ).start()

    def run(self):
        """Start the GUI application"""
        # Add cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_recording:
            if messagebox.askokcancel("Quit", "Recording is in progress. Do you want to stop and quit?"):
                self.stop_realtime_recording()
                self.root.destroy()
        else:
            self.root.destroy()


def create_gui():
    """Factory function to create and return GUI instance"""
    return MicrophoneTranscriberGUI()


def run_gui():
    """Convenience function to create and run the GUI"""
    gui = create_gui()
    gui.run()


if __name__ == "__main__":
    run_gui()
