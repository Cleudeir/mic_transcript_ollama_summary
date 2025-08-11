import threading
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
import os
import datetime
from src.capture_audio import (
    get_microphone_list,
    capture_audio_with_callback,
    capture_audio_realtime,
)
from src.transcribe_text import transcribe_and_display
import tkinter as tk
from tkinter import messagebox
from src.capture_audio import get_microphone_list, capture_audio_with_callback
from src.transcribe_text import transcribe_and_display
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
        self.transcript_outputs = (
            {}
        )  # Dictionary to store transcript outputs for each device

        # Real-time markdown saving
        self.markdown_file_path = None
        self.markdown_file = None
        self.session_start_time = None

        # Setup GUI components
        self.setup_gui()

        # Load saved microphone preferences
        self.load_mic_preferences()

    def setup_gui(self):
        """Setup all GUI components"""
        # Create menu bar
        self.setup_menu_bar()

        # Title
        title_label = tk.Label(
            self.root, text="Meeting Audio Transcriber", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        # Instructions
        instruction_label = tk.Label(
            self.root,
            text="Available Microphones - Select exactly two for simultaneous recording:",
            font=("Arial", 11, "bold"),
            fg="blue",
        )
        instruction_label.pack(pady=5)

        # Status bar (create early so it's available for load_microphones)
        self.status_var = tk.StringVar()
        self.status_var.set("Loading microphones...")

        # Microphone selection frame
        self.mic_frame = tk.Frame(self.root)
        self.mic_frame.pack(pady=10, padx=20, fill=tk.X)

        # Load and display microphones immediately
        self.load_microphones()

        # Load and display microphones
        self.load_microphones()

        # Control buttons frame (moved up for better layout)
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Listen button
        self.listen_btn = tk.Button(
            button_frame,
            text="🎤 Start Continuous Recording & Transcription",
            command=self.toggle_recording,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5,
        )
        self.listen_btn.pack(side=tk.LEFT, padx=5)

        # Auto-save status label
        self.auto_save_label = tk.Label(
            button_frame,
            text="Auto-save: OFF",
            font=("Arial", 8),
            fg="gray",
        )
        self.auto_save_label.pack(side=tk.LEFT, padx=5)

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

    def setup_menu_bar(self):
        """Setup the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Microphone menu
        mic_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🎤 Microphones", menu=mic_menu)

        mic_menu.add_command(
            label="🔍 Scan for Microphones", command=self.refresh_microphones
        )
        mic_menu.add_command(
            label="⚙️ Configure Microphones", command=self.open_mic_config_dialog
        )
        mic_menu.add_separator()
        mic_menu.add_command(
            label="💾 Save Current Selection", command=self.save_mic_preferences
        )
        mic_menu.add_command(
            label="📁 Load Saved Selection", command=self.load_mic_preferences
        )
        mic_menu.add_separator()
        mic_menu.add_command(
            label="🧪 Test Microphones", command=self.test_all_microphones
        )

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⚙️ Settings", menu=settings_menu)

        settings_menu.add_command(
            label="🌐 Language Settings", command=self.open_language_settings
        )
        settings_menu.add_command(
            label="🔊 Audio Settings", command=self.open_audio_settings
        )
        settings_menu.add_separator()
        settings_menu.add_command(
            label="📊 Performance Monitor", command=self.toggle_performance_monitor
        )

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 File", menu=file_menu)

        file_menu.add_command(
            label="💾 Save Transcripts", command=self.save_transcripts
        )
        file_menu.add_command(
            label="📂 Open Transcript Folder", command=self.open_transcript_folder
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="🔄 Reset Application", command=self.reset_application
        )
        file_menu.add_separator()
        file_menu.add_command(label="❌ Exit", command=self.on_closing)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Help", menu=help_menu)

        help_menu.add_command(label="📖 User Guide", command=self.show_user_guide)
        help_menu.add_command(
            label="🔧 Troubleshooting", command=self.show_troubleshooting
        )
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ About", command=self.show_about)

    def open_mic_config_dialog(self):
        """Open microphone configuration dialog"""
        config_window = tk.Toplevel(self.root)
        config_window.title("🎤 Microphone Configuration")
        config_window.geometry("600x500")
        config_window.resizable(True, True)

        # Make window modal
        config_window.transient(self.root)
        config_window.grab_set()

        # Center the window
        config_window.geometry(
            "+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50)
        )

        # Title
        title_frame = tk.Frame(config_window)
        title_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(
            title_frame, text="🎤 Microphone Configuration", font=("Arial", 14, "bold")
        ).pack()

        tk.Label(
            title_frame,
            text="Configure your microphones for optimal recording",
            font=("Arial", 10),
        ).pack(pady=5)

        # Available microphones section
        available_frame = tk.LabelFrame(
            config_window, text="📋 Available Microphones", font=("Arial", 11, "bold")
        )
        available_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Microphone list with details
        list_frame = tk.Frame(available_frame)
        list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Create treeview for microphone list
        columns = ("Device", "Name", "Channels", "Sample Rate", "Status")
        self.mic_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=10
        )

        # Configure columns
        self.mic_tree.heading("Device", text="Device ID")
        self.mic_tree.heading("Name", text="Microphone Name")
        self.mic_tree.heading("Channels", text="Channels")
        self.mic_tree.heading("Sample Rate", text="Sample Rate")
        self.mic_tree.heading("Status", text="Status")

        self.mic_tree.column("Device", width=80, anchor="center")
        self.mic_tree.column("Name", width=250)
        self.mic_tree.column("Channels", width=80, anchor="center")
        self.mic_tree.column("Sample Rate", width=100, anchor="center")
        self.mic_tree.column("Status", width=100, anchor="center")

        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.mic_tree.yview
        )
        self.mic_tree.configure(yscrollcommand=tree_scroll.set)

        self.mic_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate microphone list
        self.populate_mic_tree()

        # Selection section
        selection_frame = tk.LabelFrame(
            config_window, text="✅ Current Selection", font=("Arial", 11, "bold")
        )
        selection_frame.pack(pady=10, padx=20, fill=tk.X)

        self.selection_text = tk.Text(selection_frame, height=4, wrap=tk.WORD)
        selection_scroll = tk.Scrollbar(
            selection_frame, orient=tk.VERTICAL, command=self.selection_text.yview
        )
        self.selection_text.configure(yscrollcommand=selection_scroll.set)

        self.selection_text.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )
        selection_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Update selection display
        self.update_selection_display()

        # Buttons
        button_frame = tk.Frame(config_window)
        button_frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Button(
            button_frame,
            text="🔄 Refresh List",
            command=self.refresh_mic_tree,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="🧪 Test Selected",
            command=self.test_selected_mics,
            font=("Arial", 10),
            bg="#FF9800",
            fg="white",
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="💾 Save & Apply",
            command=lambda: self.apply_mic_config(config_window),
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
        ).pack(side=tk.RIGHT, padx=5)

        tk.Button(
            button_frame,
            text="❌ Cancel",
            command=config_window.destroy,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
        ).pack(side=tk.RIGHT, padx=5)

        # Bind double-click to select/deselect
        self.mic_tree.bind("<Double-1>", self.on_mic_double_click)

    def create_combined_tab(self):
        """Create the combined view tab showing both logs and transcripts"""
        combined_frame = ttk.Frame(self.notebook)
        self.notebook.add(combined_frame, text="📊 Combined View")

        # Combined output area
        combined_text_frame = tk.Frame(combined_frame)
        combined_text_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.combined_output = tk.Text(
            combined_text_frame, height=20, width=100, wrap=tk.WORD
        )
        combined_scrollbar = tk.Scrollbar(
            combined_text_frame, orient=tk.VERTICAL, command=self.combined_output.yview
        )
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
        mic1_log_scroll = tk.Scrollbar(
            mic1_log_frame, orient=tk.VERTICAL, command=self.mic1_log_text.yview
        )
        self.mic1_log_text.configure(yscrollcommand=mic1_log_scroll.set)

        self.mic1_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mic1_log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Microphone 2 logs
        mic2_log_frame = ttk.LabelFrame(logs_paned, text="Microphone 2 - System Logs")
        logs_paned.add(mic2_log_frame, weight=1)

        self.mic2_log_text = tk.Text(mic2_log_frame, height=20, wrap=tk.WORD)
        mic2_log_scroll = tk.Scrollbar(
            mic2_log_frame, orient=tk.VERTICAL, command=self.mic2_log_text.yview
        )
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
        mic1_transcript_frame = ttk.LabelFrame(
            transcripts_paned, text="Microphone 1 - Transcripts"
        )
        transcripts_paned.add(mic1_transcript_frame, weight=1)

        self.mic1_transcript_text = tk.Text(
            mic1_transcript_frame, height=20, wrap=tk.WORD
        )
        mic1_transcript_scroll = tk.Scrollbar(
            mic1_transcript_frame,
            orient=tk.VERTICAL,
            command=self.mic1_transcript_text.yview,
        )
        self.mic1_transcript_text.configure(yscrollcommand=mic1_transcript_scroll.set)

        self.mic1_transcript_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mic1_transcript_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Microphone 2 transcripts
        mic2_transcript_frame = ttk.LabelFrame(
            transcripts_paned, text="Microphone 2 - Transcripts"
        )
        transcripts_paned.add(mic2_transcript_frame, weight=1)

        self.mic2_transcript_text = tk.Text(
            mic2_transcript_frame, height=20, wrap=tk.WORD
        )
        mic2_transcript_scroll = tk.Scrollbar(
            mic2_transcript_frame,
            orient=tk.VERTICAL,
            command=self.mic2_transcript_text.yview,
        )
        self.mic2_transcript_text.configure(yscrollcommand=mic2_transcript_scroll.set)

        self.mic2_transcript_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mic2_transcript_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def save_transcripts(self):
        """Save transcripts to files"""
        if (
            not self.mic1_transcript_text.get(1.0, tk.END).strip()
            and not self.mic2_transcript_text.get(1.0, tk.END).strip()
        ):
            messagebox.showwarning("Warning", "No transcripts to save!")
            return

        # Get current timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # Ask user for save location
            initial_filename = f"meeting_transcripts_{timestamp}.md"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[
                    ("Markdown files", "*.md"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ],
                initialname=initial_filename,
                title="Save Transcripts",
            )

            if file_path:
                self._save_transcripts_to_markdown(file_path)
                self.status_var.set(f"Transcripts saved to: {file_path}")
                messagebox.showinfo(
                    "Success",
                    f"Transcripts saved successfully!\n\nLocation: {file_path}",
                )

        except Exception as e:
            self.status_var.set(f"Error saving transcripts: {e}")
            messagebox.showerror("Error", f"Failed to save transcripts: {e}")

    def _save_transcripts_to_markdown(self, file_path):
        """Save transcripts to a markdown file with proper formatting"""
        with open(file_path, "w", encoding="utf-8") as f:
            # Write header
            f.write(f"# Meeting Transcripts\n\n")
            f.write(
                f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
            f.write("---\n\n")

            # Get content from both microphones
            mic1_content = self.mic1_transcript_text.get(1.0, tk.END).strip()
            mic2_content = self.mic2_transcript_text.get(1.0, tk.END).strip()

            # Create combined transcript in chronological order
            if mic1_content or mic2_content:
                f.write("## Combined Transcript\n\n")

                # Parse timestamps and combine both microphone transcripts
                combined_transcripts = []

                # Parse mic1 transcripts
                if mic1_content:
                    for line in mic1_content.split("\n"):
                        if line.strip() and "[" in line and "]" in line:
                            try:
                                timestamp_end = line.index("]")
                                timestamp_str = line[1:timestamp_end]
                                text = line[timestamp_end + 1 :].strip()
                                if text:
                                    combined_transcripts.append(
                                        (timestamp_str, "Microphone 1", text)
                                    )
                            except:
                                continue

                # Parse mic2 transcripts
                if mic2_content:
                    for line in mic2_content.split("\n"):
                        if line.strip() and "[" in line and "]" in line:
                            try:
                                timestamp_end = line.index("]")
                                timestamp_str = line[1:timestamp_end]
                                text = line[timestamp_end + 1 :].strip()
                                if text:
                                    combined_transcripts.append(
                                        (timestamp_str, "Microphone 2", text)
                                    )
                            except:
                                continue

                # Sort by timestamp
                combined_transcripts.sort(key=lambda x: x[0])

                # Write combined transcript
                for timestamp, mic_name, text in combined_transcripts:
                    f.write(f"**[{timestamp}] {mic_name}:** {text}\n")

                f.write("---\n\n")

            # Write individual microphone sections
            if mic1_content:
                f.write("## Microphone 1 Transcripts\n\n")
                for line in mic1_content.split("\n"):
                    if line.strip():
                        f.write(f"{line}\n\n")
                f.write("---\n\n")

            if mic2_content:
                f.write("## Microphone 2 Transcripts\n\n")
                for line in mic2_content.split("\n"):
                    if line.strip():
                        f.write(f"{line}\n\n")

    def start_realtime_markdown_save(self):
        """Initialize real-time markdown file for auto-saving"""
        if not os.path.exists("src/output"):
            os.makedirs("src/output")

        # Create filename with timestamp
        self.session_start_time = datetime.datetime.now()
        timestamp = self.session_start_time.strftime("%Y%m%d_%H%M%S")
        self.markdown_file_path = f"src/output/meeting_transcripts_{timestamp}.md"

        try:
            # Initialize markdown file
            self.markdown_file = open(self.markdown_file_path, "w", encoding="utf-8")

            # Write header
            self.markdown_file.write(f"# Meeting Transcripts - Live Session\n\n")
            self.markdown_file.write(
                f"**Session Started:** {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
            self.markdown_file.write("**Participants:** Microphone 1, Microphone 2\n\n")
            self.markdown_file.write("---\n\n")
            self.markdown_file.write("## Live Transcript\n\n")
            self.markdown_file.flush()

            # Update UI
            self.auto_save_label.config(
                text=f"Auto-save: ON ({os.path.basename(self.markdown_file_path)})",
                fg="green",
            )
            self.status_var.set(f"Real-time saving to: {self.markdown_file_path}")

        except Exception as e:
            self.status_var.set(f"Error initializing auto-save: {e}")
            self.markdown_file = None

    def stop_realtime_markdown_save(self):
        """Stop real-time markdown saving and finalize file"""
        if self.markdown_file:
            try:
                # Write session end info
                end_time = datetime.datetime.now()
                duration = (
                    end_time - self.session_start_time
                    if self.session_start_time
                    else "Unknown"
                )

                self.markdown_file.write("\n---\n\n")
                self.markdown_file.write(
                    f"**Session Ended:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
                if isinstance(duration, datetime.timedelta):
                    self.markdown_file.write(
                        f"**Duration:** {str(duration).split('.')[0]}\n\n"
                    )

                self.markdown_file.close()
                self.markdown_file = None

                # Update UI
                self.auto_save_label.config(text="Auto-save: OFF", fg="gray")
                self.status_var.set(f"Session saved to: {self.markdown_file_path}")

            except Exception as e:
                self.status_var.set(f"Error closing auto-save file: {e}")

    def append_to_realtime_markdown(self, device_index, transcript, selected_indices):
        """Append transcript to real-time markdown file"""
        if not self.markdown_file:
            return

        try:
            # Determine which microphone this is
            mic_name = (
                "Microphone 1"
                if device_index == selected_indices[0]
                else "Microphone 2"
            )
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")

            # Write to markdown file
            self.markdown_file.write(f"**[{timestamp}] {mic_name}:** {transcript}\n\n")
            self.markdown_file.flush()  # Ensure immediate write to disk

        except Exception as e:
            self.status_var.set(f"Error writing to auto-save file: {e}")

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
                "timestamp": threading.current_thread().name,
            }

            try:
                with open(self.config_file, "w") as f:
                    json.dump(config, f, indent=2)
                self.status_var.set("Microphone preferences saved!")
                messagebox.showinfo("Saved", "Microphone preferences have been saved!")
            except Exception as e:
                self.status_var.set(f"Error saving preferences: {e}")
                messagebox.showerror("Error", f"Failed to save preferences: {e}")
        else:
            messagebox.showwarning(
                "Warning", "Please select exactly two microphones before saving."
            )

    def load_mic_preferences(self):
        """Load previously saved microphone preferences"""
        if not os.path.exists(self.config_file):
            return

        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)

            saved_mics = config.get("saved_microphones", [])
            if len(saved_mics) == 2:
                # Try to select the saved microphones
                saved_indices = [mic["index"] for mic in saved_mics]
                self.auto_select_microphones(saved_indices)

                mic_names = [mic["name"] for mic in saved_mics]
                self.status_var.set(
                    f"Loaded preferences: {mic_names[0][:20]}... & {mic_names[1][:20]}..."
                )

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
            "mic2_transcript": self.mic2_transcript_text,
        }

    def get_output_widgets_for_device(self, device_index, selected_indices):
        """Get the appropriate output widgets for a device"""
        # Determine if this is mic1 or mic2 based on selection order
        mic_position = "mic1" if device_index == selected_indices[0] else "mic2"

        return {
            "combined": self.output_widgets["combined"],
            "log": self.output_widgets[f"{mic_position}_log"],
            "transcript": self.output_widgets[f"{mic_position}_transcript"],
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
        widgets["combined"].insert(
            tk.END, f"Device {device_index} TRANSCRIPT: {transcript_message}"
        )
        widgets["combined"].see(tk.END)

        # Add to device-specific transcript area
        widgets["transcript"].insert(tk.END, transcript_message)
        widgets["transcript"].see(tk.END)

        # Save to real-time markdown file
        self.append_to_realtime_markdown(device_index, transcript, selected_indices)

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

    def transcribe_and_display_separated(
        self, device_index, audio_data, samplerate, selected_indices
    ):
        """Ultra-fast transcription with minimal blocking for continuous pipeline"""
        from src.transcribe_text import transcribe_audio_async

        # Quick pre-check before processing
        import numpy as np
        import time

        # Skip silent audio immediately
        if np.max(np.abs(audio_data)) < 100:
            return  # Don't even log silent audio to reduce UI updates

        start_time = time.time()

        # Use non-blocking async transcription
        try:
            transcript = transcribe_audio_async(audio_data, samplerate, "pt-BR")
            processing_time = time.time() - start_time

            # Only update UI for meaningful results
            if transcript and transcript not in [None, "Transcription timeout"]:
                if transcript.startswith(("Could not", "Error", "Network error")):
                    self.add_log_message(
                        device_index,
                        f"⚠️ {transcript} ({processing_time:.1f}s)",
                        selected_indices,
                    )
                else:
                    # Show successful transcription with minimal logging
                    self.add_log_message(
                        device_index,
                        f"✅ Transcribed in {processing_time:.1f}s",
                        selected_indices,
                    )
                    self.add_transcript_message(
                        device_index, transcript, selected_indices
                    )
            else:
                # Only log timeouts and errors, not empty results
                if transcript == "Transcription timeout":
                    self.add_log_message(
                        device_index,
                        f"⏱️ Timeout ({processing_time:.1f}s)",
                        selected_indices,
                    )

        except Exception as e:
            # Log exceptions but don't block the pipeline
            self.add_log_message(device_index, f"❌ Exception: {e}", selected_indices)

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
            self.listen_btn.config(text="🛑 Stop Continuous Recording", bg="#f44336")
            self.status_var.set("Continuous recording active - audio never stops...")

            # Start real-time markdown saving
            self.start_realtime_markdown_save()

            # Create stop events for each microphone
            self.stop_events = [threading.Event() for _ in selected]
            self.recording_threads = []

            # Start recording threads
            for i, device_index in enumerate(selected):
                stop_event = self.stop_events[i]
                thread = threading.Thread(
                    target=self.realtime_record_and_transcribe,
                    args=(device_index, stop_event, selected),
                    daemon=True,
                )
                thread.start()
                self.recording_threads.append(thread)

                # Add initial log message
                self.add_log_message(
                    device_index,
                    f"🔴 CONTINUOUS: Non-stop recording and transcription from device {device_index}",
                    selected,
                )

    def stop_realtime_recording(self):
        """Stop real-time recording"""
        self.is_recording = False

        # Signal all threads to stop
        for stop_event in self.stop_events:
            stop_event.set()

        # Stop real-time markdown saving
        self.stop_realtime_markdown_save()

        # Update UI
        self.listen_btn.config(
            text="🎤 Start Continuous Recording & Transcription", bg="#4CAF50"
        )
        self.status_var.set("Continuous recording stopped")

        # Add log message
        self.combined_output.insert(tk.END, "\n=== RECORDING STOPPED ===\n\n")
        self.combined_output.see(tk.END)

    def realtime_record_and_transcribe(
        self, device_index, stop_event, selected_indices
    ):
        """Handle real-time recording and transcription with continuous non-blocking pipeline"""

        # Create a high-performance queue for transcription tasks
        import queue

        transcription_queue = queue.Queue(maxsize=10)  # Larger queue to handle bursts

        # Multiple transcription workers for parallel processing
        num_workers = 2  # Multiple workers to handle transcription load
        workers = []

        def transcription_worker(worker_id):
            """Process transcription requests in parallel workers"""
            while not stop_event.is_set():
                try:
                    # Get transcription task from queue with short timeout
                    task = transcription_queue.get(timeout=0.3)
                    if task is None:  # Shutdown signal
                        break

                    device_idx, audio_data, samplerate, timestamp = task

                    # Add processing start log
                    self.add_log_message(
                        device_idx,
                        f"Worker {worker_id}: Starting transcription...",
                        selected_indices,
                    )

                    # Use optimized real-time transcription
                    self.transcribe_and_display_separated(
                        device_idx, audio_data, samplerate, selected_indices
                    )
                    transcription_queue.task_done()

                except queue.Empty:
                    continue
                except Exception as e:
                    self.add_log_message(
                        device_index, f"Worker {worker_id} error: {e}", selected_indices
                    )

        # Start multiple transcription processing workers
        for i in range(num_workers):
            worker = threading.Thread(
                target=transcription_worker, args=(i + 1,), daemon=True
            )
            worker.start()
            workers.append(worker)

        def on_audio_chunk(device_idx, audio_data, samplerate):
            """Queue transcription task - completely non-blocking"""
            import time

            timestamp = time.time()

            try:
                # Try to queue without blocking - if queue is full, drop oldest
                if transcription_queue.full():
                    # Remove oldest item to make room
                    try:
                        transcription_queue.get_nowait()
                        transcription_queue.task_done()
                    except queue.Empty:
                        pass

                # Add new transcription task
                transcription_queue.put(
                    (device_idx, audio_data, samplerate, timestamp), block=False
                )

            except queue.Full:
                # Even if we can't queue, don't block audio capture
                # Just log that we're dropping frames due to processing load
                self.add_log_message(
                    device_index,
                    "High processing load - dropping frame",
                    selected_indices,
                )

        # Add initial status
        self.add_log_message(
            device_index,
            f"🎤 Starting continuous audio capture (non-blocking pipeline)",
            selected_indices,
        )

        # Start real-time capture with continuous mode (2-second chunks for responsiveness)
        capture_audio_realtime(
            device_index, on_audio_chunk, stop_event, chunk_duration=2
        )

        # Signal all transcription workers to shutdown
        for _ in range(num_workers):
            transcription_queue.put(None)

        # Wait for workers to complete with timeout
        for worker in workers:
            worker.join(timeout=1.0)

        # Add completion message when thread ends
        if not stop_event.is_set():  # If stopped due to error, not user action
            self.add_log_message(
                device_index,
                f"Recording from device {device_index} ended unexpectedly",
                selected_indices,
            )

    def record_and_transcribe(self, device_index, start_event, selected_indices):
        """Capture audio and transcribe it for a specific device"""

        def on_audio_captured(device_index, audio_data, samplerate, output_box):
            # Use our custom transcribe function
            self.transcribe_and_display_separated(
                device_index, audio_data, samplerate, selected_indices
            )

        # Add initial log message
        self.add_log_message(
            device_index,
            f"Ready to record from device {device_index}...",
            selected_indices,
        )

        capture_audio_with_callback(device_index, None, start_event, on_audio_captured)

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
                target=self.record_and_transcribe,
                args=(idx, start_event, selected_indices),
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

    def on_closing(self):
        """Handle application closing"""
        # Stop recording if active
        if self.is_recording:
            self.stop_realtime_recording()

        # Ensure markdown file is closed
        if self.markdown_file:
            try:
                self.markdown_file.close()
            except:
                pass

        # Close the application
        self.root.destroy()

    def run(self):
        """Start the GUI application"""
        # Add cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Handle application closing"""
        if self.is_recording:
            if messagebox.askokcancel(
                "Quit", "Recording is in progress. Do you want to stop and quit?"
            ):
                self.stop_realtime_recording()
                self.root.destroy()
        else:
            self.root.destroy()

    def populate_mic_tree(self):
        """Populate the microphone tree with device information"""
        # Clear existing items
        for item in self.mic_tree.get_children():
            self.mic_tree.delete(item)

        # Get microphone list
        try:
            import sounddevice as sd

            devices = sd.query_devices()

            for idx, device in enumerate(devices):
                if device["max_input_channels"] > 0:  # Only input devices
                    name = device["name"]
                    channels = device["max_input_channels"]
                    sample_rate = int(device["default_samplerate"])

                    # Test if microphone is active
                    try:
                        from src.capture_audio import is_microphone_active

                        status = (
                            "✅ Active" if is_microphone_active(idx) else "⚠️ Inactive"
                        )
                    except:
                        status = "❓ Unknown"

                    # Check if currently selected
                    is_selected = any(
                        var.get() and mic_idx == idx for var, mic_idx in self.mic_vars
                    )
                    if is_selected:
                        status += " [SELECTED]"

                    self.mic_tree.insert(
                        "", "end", values=(idx, name, channels, sample_rate, status)
                    )

        except Exception as e:
            self.status_var.set(f"Error loading microphone details: {e}")

    def refresh_mic_tree(self):
        """Refresh the microphone tree"""
        self.status_var.set("Refreshing microphone list...")
        self.populate_mic_tree()
        self.update_selection_display()
        self.status_var.set("Microphone list refreshed")

    def update_selection_display(self):
        """Update the selection display text"""
        selected = [idx for var, idx in self.mic_vars if var.get()]

        self.selection_text.delete(1.0, tk.END)

        if not selected:
            self.selection_text.insert(
                tk.END,
                "No microphones selected.\n\nDouble-click on microphones in the list above to select them.\nYou need exactly 2 microphones for recording.",
            )
        elif len(selected) == 1:
            device_name = next(
                name for mic_idx, name in self.mics if mic_idx == selected[0]
            )
            self.selection_text.insert(
                tk.END,
                f"1 microphone selected:\n• Device {selected[0]}: {device_name}\n\nSelect 1 more microphone to start recording.",
            )
        elif len(selected) == 2:
            device_names = [name for mic_idx, name in self.mics if mic_idx in selected]
            self.selection_text.insert(
                tk.END,
                f"✅ Ready to record with 2 microphones:\n• Device {selected[0]}: {device_names[0]}\n• Device {selected[1]}: {device_names[1]}\n\nYou can now start recording!",
            )
        else:
            self.selection_text.insert(
                tk.END,
                f"⚠️ Too many microphones selected ({len(selected)}).\n\nPlease deselect some microphones. You need exactly 2 for recording.",
            )

    def on_mic_double_click(self, event):
        """Handle double-click on microphone in tree"""
        item = self.mic_tree.selection()[0]
        device_id = int(self.mic_tree.item(item, "values")[0])

        # Find the corresponding checkbox and toggle it
        for var, idx in self.mic_vars:
            if idx == device_id:
                var.set(1 - var.get())  # Toggle selection
                break

        # Refresh displays
        self.refresh_mic_tree()
        self.update_selection_display()

    def test_selected_mics(self):
        """Test the currently selected microphones"""
        selected = [idx for var, idx in self.mic_vars if var.get()]

        if not selected:
            messagebox.showwarning("No Selection", "Please select microphones to test.")
            return

        test_window = tk.Toplevel(self.root)
        test_window.title("🧪 Microphone Test")
        test_window.geometry("500x400")
        test_window.transient(self.root)
        test_window.grab_set()

        tk.Label(
            test_window, text="🧪 Microphone Test Results", font=("Arial", 14, "bold")
        ).pack(pady=10)

        # Test results area
        results_text = tk.Text(test_window, height=15, wrap=tk.WORD)
        results_scroll = tk.Scrollbar(
            test_window, orient=tk.VERTICAL, command=results_text.yview
        )
        results_text.configure(yscrollcommand=results_scroll.set)

        results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        results_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Close button
        tk.Button(
            test_window, text="Close", command=test_window.destroy, font=("Arial", 10)
        ).pack(pady=10)

        # Perform tests
        results_text.insert(tk.END, "Starting microphone tests...\n\n")
        results_text.update()

        for device_id in selected:
            device_name = next(
                name for mic_idx, name in self.mics if mic_idx == device_id
            )
            results_text.insert(tk.END, f"Testing Device {device_id}: {device_name}\n")
            results_text.insert(tk.END, "=" * 50 + "\n")

            try:
                # Test audio capture
                from src.capture_audio import is_microphone_active
                import sounddevice as sd

                # Get device info
                device_info = sd.query_devices(device_id)
                results_text.insert(
                    tk.END, f"• Channels: {device_info['max_input_channels']}\n"
                )
                results_text.insert(
                    tk.END, f"• Sample Rate: {device_info['default_samplerate']} Hz\n"
                )
                results_text.insert(
                    tk.END,
                    f"• Host API: {sd.query_hostapis(device_info['hostapi'])['name']}\n",
                )

                # Test if active
                if is_microphone_active(device_id):
                    results_text.insert(
                        tk.END, "• Status: ✅ ACTIVE - Ready for recording\n"
                    )
                else:
                    results_text.insert(
                        tk.END, "• Status: ⚠️ INACTIVE - May not work properly\n"
                    )

                # Test short recording
                results_text.insert(tk.END, "• Testing 1-second recording...\n")
                results_text.update()

                import numpy as np

                test_audio = sd.rec(
                    int(device_info["default_samplerate"]),
                    samplerate=int(device_info["default_samplerate"]),
                    channels=1,
                    dtype="int16",
                    device=device_id,
                )
                sd.wait()

                max_amplitude = np.max(np.abs(test_audio))
                if max_amplitude > 100:
                    results_text.insert(
                        tk.END, f"• Audio Level: ✅ GOOD (Peak: {max_amplitude})\n"
                    )
                else:
                    results_text.insert(
                        tk.END,
                        f"• Audio Level: ⚠️ LOW (Peak: {max_amplitude}) - Check volume\n",
                    )

            except Exception as e:
                results_text.insert(tk.END, f"• ERROR: {e}\n")

            results_text.insert(tk.END, "\n")
            results_text.update()

        results_text.insert(tk.END, "Testing completed!\n")

    def apply_mic_config(self, config_window):
        """Apply microphone configuration and close dialog"""
        selected = [idx for var, idx in self.mic_vars if var.get()]

        if len(selected) != 2:
            messagebox.showerror(
                "Invalid Selection",
                f"Please select exactly 2 microphones.\nCurrently selected: {len(selected)}",
            )
            return

        # Save preferences
        self.save_mic_preferences()

        # Update main window status
        device_names = [name for mic_idx, name in self.mics if mic_idx in selected]
        self.status_var.set(
            f"Configuration saved: {device_names[0][:15]}... & {device_names[1][:15]}..."
        )

        messagebox.showinfo(
            "Configuration Saved",
            "Microphone configuration has been saved successfully!",
        )

        config_window.destroy()

    def test_all_microphones(self):
        """Test all available microphones"""
        if not self.mics:
            messagebox.showwarning(
                "No Microphones",
                "No microphones found. Please refresh the microphone list first.",
            )
            return

        test_window = tk.Toplevel(self.root)
        test_window.title("🧪 Test All Microphones")
        test_window.geometry("600x500")
        test_window.transient(self.root)
        test_window.grab_set()

        # Center the window
        test_window.geometry(
            "+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50)
        )

        tk.Label(
            test_window,
            text="🧪 Testing All Available Microphones",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        # Test results area
        results_frame = tk.Frame(test_window)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        results_text = tk.Text(results_frame, height=20, wrap=tk.WORD)
        results_scroll = tk.Scrollbar(
            results_frame, orient=tk.VERTICAL, command=results_text.yview
        )
        results_text.configure(yscrollcommand=results_scroll.set)

        results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Progress bar
        progress_frame = tk.Frame(test_window)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)

        progress_var = tk.StringVar()
        progress_var.set("Starting tests...")
        progress_label = tk.Label(progress_frame, textvariable=progress_var)
        progress_label.pack()

        # Close button
        close_btn = tk.Button(
            test_window,
            text="Close",
            command=test_window.destroy,
            font=("Arial", 10),
            state=tk.DISABLED,
        )
        close_btn.pack(pady=10)

        # Start testing in a separate thread
        def run_tests():
            try:
                results_text.insert(
                    tk.END, "Starting comprehensive microphone tests...\n"
                )
                results_text.insert(
                    tk.END, f"Found {len(self.mics)} microphone(s) to test\n\n"
                )
                results_text.update()

                for i, (device_id, device_name) in enumerate(self.mics):
                    progress_var.set(
                        f"Testing microphone {i+1}/{len(self.mics)}: {device_name[:30]}..."
                    )
                    test_window.update()

                    results_text.insert(
                        tk.END, f"Testing Device {device_id}: {device_name}\n"
                    )
                    results_text.insert(tk.END, "=" * 60 + "\n")

                    try:
                        import sounddevice as sd
                        import numpy as np

                        # Get device info
                        device_info = sd.query_devices(device_id)
                        results_text.insert(
                            tk.END, f"• Device Type: Input Microphone\n"
                        )
                        results_text.insert(
                            tk.END, f"• Channels: {device_info['max_input_channels']}\n"
                        )
                        results_text.insert(
                            tk.END,
                            f"• Sample Rate: {device_info['default_samplerate']} Hz\n",
                        )
                        results_text.insert(
                            tk.END,
                            f"• Host API: {sd.query_hostapis(device_info['hostapi'])['name']}\n",
                        )

                        # Test if active using our function
                        try:
                            from src.capture_audio import is_microphone_active

                            if is_microphone_active(device_id):
                                results_text.insert(
                                    tk.END,
                                    "• Activity Test: ✅ ACTIVE - Device responds to audio\n",
                                )
                            else:
                                results_text.insert(
                                    tk.END,
                                    "• Activity Test: ⚠️ SILENT - No audio detected\n",
                                )
                        except Exception as e:
                            results_text.insert(
                                tk.END, f"• Activity Test: ❌ ERROR - {e}\n"
                            )

                        # Test recording capability
                        results_text.insert(
                            tk.END, "• Recording Test: Testing 2-second capture...\n"
                        )
                        results_text.update()

                        try:
                            test_audio = sd.rec(
                                int(2 * device_info["default_samplerate"]),
                                samplerate=int(device_info["default_samplerate"]),
                                channels=1,
                                dtype="int16",
                                device=device_id,
                            )
                            sd.wait()

                            max_amplitude = np.max(np.abs(test_audio))
                            mean_amplitude = np.mean(np.abs(test_audio))

                            if max_amplitude > 1000:
                                results_text.insert(
                                    tk.END,
                                    f"• Audio Level: ✅ EXCELLENT (Peak: {max_amplitude}, Avg: {mean_amplitude:.0f})\n",
                                )
                            elif max_amplitude > 100:
                                results_text.insert(
                                    tk.END,
                                    f"• Audio Level: ✅ GOOD (Peak: {max_amplitude}, Avg: {mean_amplitude:.0f})\n",
                                )
                            elif max_amplitude > 10:
                                results_text.insert(
                                    tk.END,
                                    f"• Audio Level: ⚠️ LOW (Peak: {max_amplitude}, Avg: {mean_amplitude:.0f})\n",
                                )
                            else:
                                results_text.insert(
                                    tk.END,
                                    f"• Audio Level: ❌ VERY LOW (Peak: {max_amplitude}, Avg: {mean_amplitude:.0f})\n",
                                )

                        except Exception as e:
                            results_text.insert(
                                tk.END, f"• Recording Test: ❌ FAILED - {e}\n"
                            )

                        # Overall recommendation
                        if device_info["max_input_channels"] > 0:
                            results_text.insert(
                                tk.END, "• Recommendation: ✅ SUITABLE for recording\n"
                            )
                        else:
                            results_text.insert(
                                tk.END,
                                "• Recommendation: ❌ NOT SUITABLE - No input channels\n",
                            )

                    except Exception as e:
                        results_text.insert(tk.END, f"• CRITICAL ERROR: {e}\n")
                        results_text.insert(
                            tk.END, "• Recommendation: ❌ DEVICE NOT WORKING\n"
                        )

                    results_text.insert(tk.END, "\n")
                    results_text.see(tk.END)
                    results_text.update()

                progress_var.set("Testing completed!")
                results_text.insert(tk.END, "🎉 All microphone tests completed!\n\n")
                results_text.insert(
                    tk.END,
                    "Recommendation: Choose microphones marked as 'SUITABLE' with 'GOOD' or 'EXCELLENT' audio levels.\n",
                )
                results_text.see(tk.END)

            except Exception as e:
                results_text.insert(tk.END, f"\n❌ Testing failed: {e}\n")
            finally:
                close_btn.config(state=tk.NORMAL)

        # Start testing thread
        import threading

        threading.Thread(target=run_tests, daemon=True).start()

    # Placeholder functions for other menu items
    def open_language_settings(self):
        """Open language settings dialog"""
        messagebox.showinfo(
            "Language Settings",
            "Language settings dialog will be implemented in future update.",
        )

    def open_audio_settings(self):
        """Open audio settings dialog"""
        messagebox.showinfo(
            "Audio Settings",
            "Audio settings dialog will be implemented in future update.",
        )

    def toggle_performance_monitor(self):
        """Toggle performance monitoring"""
        messagebox.showinfo(
            "Performance Monitor",
            "Performance monitoring will be implemented in future update.",
        )

    def open_transcript_folder(self):
        """Open the folder containing saved transcripts"""
        import os
        import subprocess

        try:
            # Open current directory (where transcripts are saved)
            if os.name == "nt":  # Windows
                os.startfile(".")
            elif os.name == "posix":  # macOS and Linux
                subprocess.call(["open", "."])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")

    def reset_application(self):
        """Reset application to default state"""
        if messagebox.askyesno(
            "Reset Application",
            "This will clear all settings and stop any recording. Continue?",
        ):
            if self.is_recording:
                self.stop_realtime_recording()
            self.clear_all_output()
            # Clear microphone selection
            for var, idx in self.mic_vars:
                var.set(0)
            self.status_var.set("Application reset")

    def show_user_guide(self):
        """Show user guide"""
        guide_text = """
🎤 Meeting Audio Transcriber - User Guide

1. SETUP:
   • Use the Microphones menu to configure your devices
   • Select exactly 2 microphones for recording
   • Test microphones to ensure they work properly

2. RECORDING:
   • Click "Start Continuous Recording & Transcription"
   • Speak normally - transcription happens in real-time
   • Audio is captured continuously without pauses

3. TRANSCRIPTS:
   • View results in the Combined View, Logs, or Transcripts tabs
   • Save transcripts using File menu or the Save button
   • Transcripts include timestamps and device identification

4. CONFIGURATION:
   • Save your microphone selection for future use
   • Use the menu system for advanced configuration
   • Monitor performance through status indicators

For technical support, see Help > Troubleshooting
        """
        messagebox.showinfo("User Guide", guide_text)

    def show_troubleshooting(self):
        """Show troubleshooting information"""
        troubleshoot_text = """
🔧 Troubleshooting Guide

COMMON ISSUES:

1. No Microphones Detected:
   • Check physical connections
   • Verify Windows recognizes the devices
   • Try refreshing the microphone list

2. Poor Transcription Quality:
   • Check internet connection (uses Google API)
   • Verify microphone volume levels
   • Reduce background noise
   • Test microphones using the test function

3. High CPU Usage:
   • Close other applications
   • Reduce number of microphones
   • Check system resources

4. Audio Lag or Delays:
   • Check microphone drivers
   • Reduce chunk duration in settings
   • Verify system performance

5. Transcription Errors:
   • Check Google API quota/limits
   • Verify internet connectivity
   • Try speaking more clearly
        """
        messagebox.showinfo("Troubleshooting", troubleshoot_text)

    def show_about(self):
        """Show about dialog"""
        about_text = """
🎤 Meeting Audio Transcriber
Version 2.0 - Continuous Recording Edition

Features:
• Real-time continuous audio recording
• Simultaneous transcription from multiple microphones
• No-pause audio pipeline
• Advanced microphone configuration
• Performance monitoring
• Multi-language support

Technology:
• Python with Tkinter GUI
• SoundDevice for audio capture
• Google Speech Recognition API
• Multi-threaded processing

Created for professional meeting transcription
with focus on continuous, uninterrupted operation.
        """
        messagebox.showinfo("About", about_text)


def create_gui():
    """Factory function to create and return GUI instance"""
    return MicrophoneTranscriberGUI()


def run_gui():
    """Convenience function to create and run the GUI"""
    gui = create_gui()
    gui.run()


if __name__ == "__main__":
    run_gui()
