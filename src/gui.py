import threading
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
import os
import datetime
import ollama
from src.capture_audio import (
    get_microphone_list,
    capture_audio_with_callback,
    capture_audio_realtime,
)
import tkinter as tk
from tkinter import messagebox
from src.capture_audio import get_microphone_list, capture_audio_with_callback
from tkinter import messagebox
from src.capture_audio import get_microphone_list, capture_audio_with_callback
from src.ollama_service import OllamaService
from src.translations import get_translation_manager, set_global_language, t


class MicrophoneTranscriberGUI:
    """Main GUI class for the Microphone Transcriber application"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("900x700")

        # Initialize configuration early
        self.config_file = "config.json"

        # Initialize other attributes that might be accessed early
        self.auto_generate_ata = True
        self.ollama_available = False
        self.markdown_file = None
        self.markdown_file_path = None

        # Recording state
        self.is_recording = False
        # Microphone variables for selection
        self.mic_vars = []
        # Create menu bar
        # self.setup_menu_bar()

        # Status bar variable (must be initialized before usage)
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Use tabs to configure settings")

        # Load and ensure main config exists with defaults (need this before setting title)
        self.config = self.load_main_config()
        self.ensure_config_file_exists()
        
        # Sync instance variables with config
        self.auto_generate_ata = self.config.get("auto_generate_ata", True)

        # Initialize translation system with language from config
        set_global_language(self.config.get("language", "pt-BR"))
        self.translation_manager = get_translation_manager()
        
        # Set window title using translation
        self.root.title(t("app_title", "Meeting Audio Transcriber"))

        # Title
        title_label = tk.Label(
            self.root, text=t("app_title", "Meeting Audio Transcriber"), font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        # Control buttons frame (moved up for better layout)
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Listen button
        self.listen_btn = tk.Button(
            button_frame,
            text=t("start_button", "🎤 Start"),
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
            text=t("auto_save_off", "Auto-save: OFF"),
            font=("Arial", 8),
            fg="gray",
        )
        self.auto_save_label.pack(side=tk.LEFT, padx=5)

        # Ollama status label
        self.ollama_status_label = tk.Label(
            button_frame,
            text=t("ollama_checking", "🌐 Ollama Remote: Checking..."),
            font=("Arial", 8),
            fg="orange",
        )
        self.ollama_status_label.pack(side=tk.LEFT, padx=5)

        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Create tabs for different views
        self.create_combined_tab()
        self.create_logs_tab()
        self.create_transcripts_tab()
        self.create_transcript_files_tab()
        self.create_ata_files_tab()
        self.create_mic_config_tab()
        self.create_ollama_config_tab()

        # Set up output mapping after tabs are created
        self.setup_output_mapping()

        # Initialize missing components
        # Initialize OllamaService with current config values (only if they exist)
        ollama_config = self.config.get("ollama", {})
        self.ollama_service = OllamaService(
            model_name=ollama_config.get("model_name") if "model_name" in ollama_config else None,
            base_url=ollama_config.get("base_url") if "base_url" in ollama_config else None
        )

        # Migrate old mic_config.json to unified config.json if needed
        self.migrate_old_mic_config()
        
        # Ensure service is synchronized with current config
        self.sync_ollama_service_with_config()

        # Initialize Ollama connection and load models on startup
        self.root.after(1000, self.initialize_ollama_on_startup)

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
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t("menu_settings", "⚙️ Settings"), menu=settings_menu)

        settings_menu.add_command(
            label=t("menu_language", "🌐 Language Settings"), command=self.open_language_settings
        )
        settings_menu.add_command(
            label=t("menu_audio", "🔊 Audio Settings"), command=self.open_audio_settings
        )
        settings_menu.add_separator()
        settings_menu.add_command(
            label=t("menu_auto_ata", "🤖 Auto-generate Ata"), command=self.toggle_auto_ata_generation
        )
        settings_menu.add_separator()
        settings_menu.add_command(
            label=t("menu_performance", "📊 Performance Monitor"), command=self.toggle_performance_monitor
        )

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t("menu_file", "📁 File"), menu=file_menu)

        file_menu.add_command(
            label=t("menu_open_transcript_folder", "📄 Open Transcript Folder"), command=self.open_transcript_folder
        )
        file_menu.add_command(
            label=t("menu_view_transcripts", "📋 View All Transcripts"), command=self.view_all_transcripts
        )
        file_menu.add_separator()
        file_menu.add_command(
            label=t("menu_generate_minutes", "🤖 Generate Meeting Minutes"),
            command=self.generate_meeting_minutes_dialog,
        )
        file_menu.add_command(label=t("menu_view_atas", "📝 View All Atas"), command=self.view_all_atas)
        file_menu.add_separator()
        file_menu.add_command(
            label=t("menu_reset", "🔄 Reset Application"), command=self.reset_application
        )
        file_menu.add_separator()
        file_menu.add_command(label=t("menu_exit", "❌ Exit"), command=self.on_closing)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t("menu_help", "❓ Help"), menu=help_menu)

        help_menu.add_command(label=t("menu_user_guide", "📖 User Guide"), command=self.show_user_guide)
        help_menu.add_command(
            label=t("menu_troubleshooting", "🔧 Troubleshooting"), command=self.show_troubleshooting
        )
        help_menu.add_separator()
        help_menu.add_command(label=t("menu_about", "ℹ️ About"), command=self.show_about)

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
        self.notebook.add(combined_frame, text=t("tab_combined", "📊 Combined View"))

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
        self.notebook.add(logs_frame, text=t("tab_logs", "📝 System Logs"))

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
        self.notebook.add(transcripts_frame, text=t("tab_transcripts", "📄 Transcripts Only"))

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

    def create_transcript_files_tab(self):
        """Create the transcript files management tab"""
        transcript_files_frame = ttk.Frame(self.notebook)
        self.notebook.add(transcript_files_frame, text="� Transcript Files")

        # Main container
        main_container = tk.Frame(transcript_files_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Transcript files list section
        transcript_section = ttk.LabelFrame(
            main_container, text="📄 Transcript Files", padding=10
        )
        transcript_section.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Files listbox with scrollbar
        transcript_list_frame = tk.Frame(transcript_section)
        transcript_list_frame.pack(fill=tk.BOTH, expand=True)

        self.transcript_files_listbox = tk.Listbox(transcript_list_frame, selectmode=tk.SINGLE)
        transcript_scrollbar = tk.Scrollbar(
            transcript_list_frame, orient=tk.VERTICAL, command=self.transcript_files_listbox.yview
        )
        self.transcript_files_listbox.configure(yscrollcommand=transcript_scrollbar.set)
        self.transcript_files_listbox.bind("<Double-Button-1>", self.open_selected_transcript_file)
        self.transcript_files_listbox.bind("<<ListboxSelect>>", self.on_transcript_file_select)

        self.transcript_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        transcript_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Control buttons
        transcript_buttons_frame = tk.Frame(transcript_section)
        transcript_buttons_frame.pack(fill=tk.X, pady=(10, 0))

        refresh_transcript_btn = tk.Button(
            transcript_buttons_frame,
            text="🔄 Refresh",
            command=self.refresh_transcript_files_list,
            bg="#e3f2fd",
            relief="groove",
        )
        refresh_transcript_btn.pack(side=tk.LEFT, padx=(0, 5))

        # File operation buttons (shown when file is selected)
        self.transcript_file_ops_frame = tk.Frame(transcript_buttons_frame)
        self.transcript_file_ops_frame.pack(side=tk.LEFT, padx=(10, 0))

        self.open_transcript_btn = tk.Button(
            self.transcript_file_ops_frame,
            text="📖 Open",
            command=self.open_selected_transcript_file,
            bg="#e8f5e8",
            relief="groove",
            state="disabled"
        )
        self.open_transcript_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.save_transcript_as_btn = tk.Button(
            self.transcript_file_ops_frame,
            text="� Save As",
            command=self.save_transcript_as,
            bg="#fff3e0",
            relief="groove",
            state="disabled"
        )
        self.save_transcript_as_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.regenerate_ata_btn = tk.Button(
            self.transcript_file_ops_frame,
            text="🤖 Regenerate ATA",
            command=self.regenerate_ata_from_selected,
            bg="#4CAF50",
            fg="white",
            relief="groove",
            state="disabled"
        )
        self.regenerate_ata_btn.pack(side=tk.LEFT, padx=(0, 5))

        open_transcript_folder_btn = tk.Button(
            transcript_buttons_frame,
            text="📁 Open Folder",
            command=self.open_transcript_folder,
            bg="#fff3e0",
            relief="groove",
        )
        open_transcript_folder_btn.pack(side=tk.RIGHT)

        # Initialize transcript files list
        self.refresh_transcript_files_list()

    def create_ata_files_tab(self):
        """Create the ATA summary files management tab"""
        ata_files_frame = ttk.Frame(self.notebook)
        self.notebook.add(ata_files_frame, text=t("tab_ata_files", "� ATA Files"))

        # Main container
        main_container = tk.Frame(ata_files_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ATA files list section
        ata_section = ttk.LabelFrame(
            main_container, text="📊 Meeting Minutes (ATA) Files", padding=10
        )
        ata_section.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Files listbox with scrollbar
        ata_list_frame = tk.Frame(ata_section)
        ata_list_frame.pack(fill=tk.BOTH, expand=True)

        self.ata_files_listbox = tk.Listbox(ata_list_frame, selectmode=tk.SINGLE)
        ata_scrollbar = tk.Scrollbar(
            ata_list_frame, orient=tk.VERTICAL, command=self.ata_files_listbox.yview
        )
        self.ata_files_listbox.configure(yscrollcommand=ata_scrollbar.set)
        self.ata_files_listbox.bind("<Double-Button-1>", self.open_selected_ata_file)
        self.ata_files_listbox.bind("<<ListboxSelect>>", self.on_ata_file_select)

        self.ata_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ata_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Control buttons
        ata_buttons_frame = tk.Frame(ata_section)
        ata_buttons_frame.pack(fill=tk.X, pady=(10, 0))

        refresh_ata_btn = tk.Button(
            ata_buttons_frame,
            text="🔄 Refresh",
            command=self.refresh_ata_files_list,
            bg="#e3f2fd",
            relief="groove",
        )
        refresh_ata_btn.pack(side=tk.LEFT, padx=(0, 5))

        # File operation buttons (shown when file is selected)
        self.ata_file_ops_frame = tk.Frame(ata_buttons_frame)
        self.ata_file_ops_frame.pack(side=tk.LEFT, padx=(10, 0))

        self.open_ata_btn = tk.Button(
            self.ata_file_ops_frame,
            text="📖 Open",
            command=self.open_selected_ata_file,
            bg="#e8f5e8",
            relief="groove",
            state="disabled"
        )
        self.open_ata_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.save_ata_as_btn = tk.Button(
            self.ata_file_ops_frame,
            text="� Save As",
            command=self.save_ata_as,
            bg="#fff3e0",
            relief="groove",
            state="disabled"
        )
        self.save_ata_as_btn.pack(side=tk.LEFT, padx=(0, 5))

        open_ata_folder_btn = tk.Button(
            ata_buttons_frame,
            text="📁 Open Folder",
            command=self.open_ata_folder,
            bg="#fff3e0",
            relief="groove",
        )
        open_ata_folder_btn.pack(side=tk.RIGHT)

        # ATA file info section
        ata_info_section = ttk.LabelFrame(
            main_container, text="📄 File Information", padding=10
        )
        ata_info_section.pack(fill=tk.X, pady=(5, 0))

        self.ata_info_label = tk.Label(
            ata_info_section,
            text="Select an ATA file to view information",
            font=("Arial", 9),
            fg="gray",
            justify=tk.LEFT,
            anchor="w"
        )
        self.ata_info_label.pack(fill=tk.X, pady=5)

        # Initialize ATA files list
        self.refresh_ata_files_list()

    def create_mic_config_tab(self):
        """Create the microphone configuration tab"""
        mic_config_frame = ttk.Frame(self.notebook)
        self.notebook.add(mic_config_frame, text=t("tab_mic_config", "🎤 Microphone Configuration"))

        # Create main container with scrollable frame
        canvas = tk.Canvas(mic_config_frame)
        scrollbar = ttk.Scrollbar(
            mic_config_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Microphone Configuration Section
        mic_section = ttk.LabelFrame(
            scrollable_frame, text="🎤 Microphone Selection", padding=10
        )
        mic_section.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            mic_section,
            text="Select exactly two microphones for recording:",
            font=("Arial", 10, "bold"),
        ).pack(anchor=tk.W, pady=(0, 5))

        # Container for main microphone checkboxes
        self.mic_frame = tk.Frame(mic_section)
        self.mic_frame.pack(fill=tk.X, pady=5)

        # Refresh microphones button
        refresh_mic_btn = tk.Button(
            mic_section,
            text="🔄 Refresh Microphones",
            command=self.refresh_microphones,
            bg="#e3f2fd",
            relief="groove",
        )
        refresh_mic_btn.pack(anchor=tk.W, pady=5)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load microphones for main interface (now in tab)
        self.load_microphones()

    def create_ollama_config_tab(self):
        """Create the Ollama configuration tab"""
        ollama_config_frame = ttk.Frame(self.notebook)
        self.notebook.add(ollama_config_frame, text=t("tab_ollama_config", "🤖 Ollama Configuration"))

        # Create main container with scrollable frame
        canvas = tk.Canvas(ollama_config_frame)
        scrollbar = ttk.Scrollbar(
            ollama_config_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Ollama Configuration Section
        ollama_section = ttk.LabelFrame(
            scrollable_frame, text="🤖 Ollama Configuration", padding=10
        )
        ollama_section.pack(fill=tk.X, padx=10, pady=5)

        # Ollama URL
        url_frame = tk.Frame(ollama_section)
        url_frame.pack(fill=tk.X, pady=5)

        tk.Label(url_frame, text="Ollama URL:", font=("Arial", 10, "bold")).pack(
            anchor=tk.W
        )
        
        # Add help text
        tk.Label(url_frame, text="Enter your Ollama server URL (e.g., http://localhost:11434)", 
                font=("Arial", 8), fg="gray").pack(anchor=tk.W)
        
        self.ollama_url_var = tk.StringVar()
        self.ollama_url_entry = tk.Entry(
            url_frame, textvariable=self.ollama_url_var, width=50
        )
        self.ollama_url_entry.pack(fill=tk.X, pady=(2, 5))

        # Set placeholder text when empty
        # Remove auto-population - let users enter their own values

        self.ollama_url_var.trace("w", self.on_ollama_url_change)

        # Test connection button
        test_btn = tk.Button(
            url_frame,
            text="🔗 Test Connection",
            command=self.test_ollama_connection,
            bg="#fff3e0",
            relief="groove",
        )
        test_btn.pack(anchor=tk.W, pady=2)

        # Connection status
        self.connection_status_label = tk.Label(
            url_frame, text="Status: Not tested", font=("Arial", 9), fg="gray"
        )
        self.connection_status_label.pack(anchor=tk.W, pady=2)

        # Model Selection
        model_frame = tk.Frame(ollama_section)
        model_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            model_frame, text="Available Models:", font=("Arial", 10, "bold")
        ).pack(anchor=tk.W)

        model_container = tk.Frame(model_frame)
        model_container.pack(fill=tk.X, pady=2)

        self.model_var = tk.StringVar()
        self.model_combobox = ttk.Combobox(
            model_container, textvariable=self.model_var, state="readonly", width=47
        )
        self.model_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.model_combobox.bind("<<ComboboxSelected>>", self.on_model_change)

        # Refresh models button
        refresh_models_btn = tk.Button(
            model_container,
            text="🔄",
            command=self.refresh_ollama_models,
            width=3,
            bg="#e8f5e8",
            relief="groove",
        )
        refresh_models_btn.pack(side=tk.RIGHT)

        # Model status
        self.model_status_label = tk.Label(
            model_frame,
            text="Click refresh to load models",
            font=("Arial", 9),
            fg="gray",
        )
        self.model_status_label.pack(anchor=tk.W, pady=2)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load current configuration
        self.load_config_tab_values()

    def load_config_tab_values(self):
        """Load current configuration values into the config tab from unified config.json"""
        try:
            # Load from unified config file
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)

            # Get Ollama config from file
            ollama_config = config.get("ollama", {})
            
            # Only populate URL if it exists in config (don't use defaults)
            if "base_url" in ollama_config:
                current_url = ollama_config["base_url"]
                
                # Update the service with the config file values
                if current_url and current_url != self.ollama_service.base_url:
                    self.ollama_service.base_url = current_url
                    # Reinitialize client with new URL
                    self.ollama_service.client = ollama.Client(host=current_url, timeout=30)
                
                self.ollama_url_var.set(current_url)
            else:
                # Leave URL field empty if no config exists
                self.ollama_url_var.set("")

            # Only populate model if it exists in config (don't use defaults)
            if "model_name" in ollama_config:
                current_model = ollama_config["model_name"]
                
                # Update the service with the config file values
                if current_model and current_model != self.ollama_service.model_name:
                    self.ollama_service.model_name = current_model
                
                self.model_var.set(current_model)
            else:
                # Leave model field empty if no config exists
                self.model_var.set("")

            # Only auto-test connection if URL was actually loaded from config
            if "base_url" in ollama_config and ollama_config["base_url"]:
                self.root.after(100, self._auto_test_connection_and_load_models)

        except Exception as e:
            self.status_var.set(f"Error loading config: {e}")

    def sync_ollama_service_with_config(self):
        """Ensure OllamaService is synchronized with the current configuration"""
        try:
            ollama_config = self.config.get("ollama", {})
            
            # Only update URL if it exists in config (no defaults)
            if "base_url" in ollama_config:
                config_url = ollama_config["base_url"]
                if config_url and config_url != self.ollama_service.base_url:
                    self.ollama_service.base_url = config_url
                    self.ollama_service.client = ollama.Client(host=config_url, timeout=30)
            
            # Only update model if it exists in config (no defaults)
            if "model_name" in ollama_config:
                config_model = ollama_config["model_name"]
                if config_model and config_model != self.ollama_service.model_name:
                    self.ollama_service.model_name = config_model
                
        except Exception as e:
            print(f"Error syncing Ollama service with config: {e}")

    def _auto_test_connection_and_load_models(self):
        """Automatically test connection and load models after URL is set"""
        try:
            # Show that we're testing
            self.connection_status_label.config(
                text="🔄 Testing connection...", fg="orange"
            )
            self.model_status_label.config(
                text="Waiting for connection test...", fg="gray"
            )
            self.root.update_idletasks()

            # Test connection
            if self.ollama_service.is_ollama_available():
                self.connection_status_label.config(
                    text="✅ Connection successful", fg="green"
                )
                # Automatically load models
                self.model_status_label.config(text="Loading models...", fg="orange")
                self.root.update_idletasks()
                self.refresh_ollama_models()
            else:
                self.connection_status_label.config(
                    text="⚠️ Connection not available", fg="gray"
                )
                self.model_status_label.config(
                    text="Test connection to load models", fg="gray"
                )
        except Exception as e:
            self.connection_status_label.config(
                text="⚠️ Connection test failed", fg="gray"
            )
            self.model_status_label.config(
                text="Check URL and test connection", fg="gray"
            )

    def on_microphone_selection_change(self):
        """Handle microphone selection changes in the main interface"""
        try:
            selected_indices = [idx for var, idx in self.mic_vars if var.get()]
            selected_with_names = []

            # Get names for selected microphones
            for idx in selected_indices:
                for mic_idx, mic_name in self.mics:
                    if mic_idx == idx:
                        selected_with_names.append((idx, mic_name))
                        break

            # Limit to 2 selections
            if len(selected_with_names) > 2:
                # Uncheck the last selected (allow only 2)
                for var, idx in self.mic_vars:
                    if var.get() and idx not in [s[0] for s in selected_with_names[:2]]:
                        var.set(0)
                selected_with_names = selected_with_names[:2]

            # Save microphone configuration
            self.save_microphone_config(selected_with_names)

            # Update status
            if len(selected_with_names) == 2:
                self.status_var.set(
                    f"Selected: {selected_with_names[0][1][:20]}... & {selected_with_names[1][1][:20]}..."
                )
            elif len(selected_with_names) == 1:
                self.status_var.set(
                    f"Selected: {selected_with_names[0][1][:30]}... (select 1 more)"
                )
            else:
                self.status_var.set("Select exactly 2 microphones to start recording")

        except Exception as e:
            self.status_var.set(f"Error updating microphone selection: {e}")

    def save_microphone_config(self, selected_mics):
        """Save microphone configuration to unified config.json file"""
        try:
            # Load existing config or create new one
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)

            # Update microphone configuration
            config["microphones"] = {
                "saved_microphones": [
                    {"index": index, "name": name} for index, name in selected_mics
                ],
                "timestamp": datetime.datetime.now().isoformat(),
            }

            # Ensure ollama config exists with defaults if not present
            if "ollama" not in config:
                config["ollama"] = {
                    "base_url": "http://localhost:11434",
                    "model_name": "llama3.2",
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "num_predict": 2048,
                }

            # Ensure other defaults
            if "auto_generate_ata" not in config:
                config["auto_generate_ata"] = True
            if "language" not in config:
                config["language"] = "pt-BR"

            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)

            self.status_var.set(
                f"Microphone configuration saved ({len(selected_mics)} mics)"
            )

        except Exception as e:
            self.status_var.set(f"Error saving microphone config: {e}")

    def on_ollama_url_change(self, *args):
        """Handle Ollama URL changes"""
        try:
            new_url = self.ollama_url_var.get().strip()
            if new_url and new_url != self.ollama_service.base_url:
                # Update configuration in both service and GUI
                success = self.ollama_service.update_config(ollama_url=new_url)
                if success:
                    # Also update the GUI's config
                    self.config.setdefault("ollama", {})["base_url"] = new_url
                    self.save_main_config()
                    
                    self.status_var.set("Ollama URL updated and saved")
                    # Clear models list since URL changed
                    self.model_combobox["values"] = []
                    self.model_var.set("")
                    # Auto-test connection and load models after URL change
                    self.root.after(200, self._auto_test_connection_and_load_models)
                else:
                    self.status_var.set("Failed to save Ollama URL")
        except Exception as e:
            self.status_var.set(f"Error updating Ollama URL: {e}")

    def on_model_change(self, event=None):
        """Handle model selection changes"""
        try:
            new_model = self.model_var.get()
            if new_model and new_model != self.ollama_service.model_name:
                # Update configuration in both service and GUI
                success = self.ollama_service.update_config(model_name=new_model)
                if success:
                    # Also update the GUI's config
                    self.config.setdefault("ollama", {})["model_name"] = new_model
                    self.save_main_config()
                    
                    self.status_var.set(f"Model updated and saved: {new_model}")
                    self.model_status_label.config(
                        text=f"Active model: {new_model}", fg="green"
                    )
                else:
                    self.status_var.set(f"Failed to save model: {new_model}")
        except Exception as e:
            self.status_var.set(f"Error updating model: {e}")

    def test_ollama_connection(self):
        """Test connection to Ollama"""
        try:
            self.connection_status_label.config(
                text="Testing connection...", fg="orange"
            )
            self.root.update_idletasks()

            if self.ollama_service.is_ollama_available():
                self.connection_status_label.config(
                    text="✅ Connection successful", fg="green"
                )
                self.refresh_ollama_models()
            else:
                self.connection_status_label.config(
                    text="❌ Connection failed", fg="red"
                )
                self.model_combobox["values"] = []
                self.model_var.set("")
                self.model_status_label.config(
                    text="Fix connection to load models", fg="red"
                )

        except Exception as e:
            self.connection_status_label.config(
                text=f"❌ Error: {str(e)[:30]}...", fg="red"
            )

    def refresh_ollama_models(self):
        """Refresh the list of available Ollama models"""
        try:
            self.model_status_label.config(text="Loading models...", fg="orange")
            self.root.update_idletasks()

            models = self.ollama_service.get_available_models()

            if models:
                self.model_combobox["values"] = models

                # Set current model if it exists in the list
                current_model = self.ollama_service.model_name
                if current_model in models:
                    self.model_var.set(current_model)
                    self.model_status_label.config(
                        text=f"Active model: {current_model}", fg="green"
                    )
                else:
                    # Set first model as default
                    self.model_var.set(models[0])
                    self.model_status_label.config(
                        text=f"Available models loaded ({len(models)})", fg="blue"
                    )

            else:
                self.model_combobox["values"] = []
                self.model_var.set("")
                self.model_status_label.config(text="No models available", fg="red")

        except Exception as e:
            self.model_status_label.config(
                text=f"Error loading models: {str(e)[:30]}...", fg="red"
            )

    def initialize_ollama_on_startup(self):
        """Initialize Ollama connection, load models, and send greeting on app startup"""
        try:
            # Only initialize if we have a valid URL configured
            if not hasattr(self.ollama_service, 'base_url') or not self.ollama_service.base_url:
                self.status_var.set("Configure Ollama URL in the Ollama Configuration tab")
                return
                
            self.status_var.set("Initializing Ollama connection...")
            self.root.update_idletasks()
            
            # Test connection first
            if self.ollama_service.is_ollama_available():
                self.status_var.set("Ollama connected! Loading models...")
                self.root.update_idletasks()
                
                # Update connection status in the config tab
                if hasattr(self, 'connection_status_label'):
                    self.connection_status_label.config(
                        text="✅ Connection successful", fg="green"
                    )
                
                # Load models
                models = self.ollama_service.get_available_models()
                
                if models:
                    # Update model combobox if it exists
                    if hasattr(self, 'model_combobox'):
                        self.model_combobox["values"] = models
                        
                        # Set current model only if one is configured
                        current_model = self.ollama_service.model_name
                        if current_model in models:
                            self.model_var.set(current_model)
                            if hasattr(self, 'model_status_label'):
                                self.model_status_label.config(
                                    text=f"Active model: {current_model}", fg="green"
                                )
                        else:
                            # Set first model as default
                            self.model_var.set(models[0])
                            if hasattr(self, 'model_status_label'):
                                self.model_status_label.config(
                                    text=f"Available models loaded ({len(models)})", fg="blue"
                                )
                    
                    self.status_var.set(f"Models loaded! ({len(models)} available)")
                    self.root.update_idletasks()
                    
                    # Send a "hi" greeting to the model
                    self.root.after(500, self.send_greeting_to_model)
                    
                else:
                    self.status_var.set("Ollama connected but no models available")
                    if hasattr(self, 'model_status_label'):
                        self.model_status_label.config(text="No models available", fg="red")
                
            else:
                self.status_var.set("Could not connect to Ollama service")
                if hasattr(self, 'connection_status_label'):
                    self.connection_status_label.config(
                        text="❌ Connection failed", fg="red"
                    )
                if hasattr(self, 'model_status_label'):
                    self.model_status_label.config(
                        text="Fix connection to load models", fg="red"
                    )
                    
        except Exception as e:
            self.status_var.set(f"Error initializing Ollama: {str(e)[:50]}...")
            print(f"Ollama initialization error: {e}")

    def send_greeting_to_model(self):
        """Send a greeting message to test the model"""
        try:
            self.status_var.set("Testing model with greeting...")
            self.root.update_idletasks()
            
            # Use the existing test method in OllamaService
            result = self.ollama_service.test_model_with_hello()
            
            if result.get("success", False):
                response = result.get("response", "")
                self.status_var.set(f"✅ Model ready! Response: {response[:30]}...")
                print(f"Model greeting response: {response}")
            else:
                error = result.get("error", "Unknown error")
                self.status_var.set(f"Model test failed: {error[:40]}...")
                print(f"Model greeting error: {error}")
                
        except Exception as e:
            self.status_var.set(f"Model test error: {str(e)[:40]}...")
            print(f"Model greeting error: {e}")

    def refresh_files_list(self):
        """Refresh the list of generated files"""
        try:
            self.files_listbox.delete(0, tk.END)

            # Check if output directory exists
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            transcript_dir = os.path.join(output_dir, "transcript")
            ata_dir = os.path.join(output_dir, "ata")

            # Create directories if they don't exist
            if not os.path.exists(transcript_dir):
                os.makedirs(transcript_dir)
            if not os.path.exists(ata_dir):
                os.makedirs(ata_dir)

            # Get files from both directories
            files = []

            # Scan transcript directory
            if os.path.exists(transcript_dir):
                for file_name in os.listdir(transcript_dir):
                    file_path = os.path.join(transcript_dir, file_name)
                    if os.path.isfile(file_path) and file_name.endswith(".md"):
                        stat = os.stat(file_path)
                        modified_time = datetime.datetime.fromtimestamp(stat.st_mtime)
                        files.append(
                            {
                                "name": file_name,
                                "path": file_path,
                                "type": "📄 Transcript",
                                "folder": "transcript/",
                                "modified": modified_time,
                                "size": stat.st_size,
                            }
                        )

            # Scan ATA directory
            if os.path.exists(ata_dir):
                for file_name in os.listdir(ata_dir):
                    file_path = os.path.join(ata_dir, file_name)
                    if os.path.isfile(file_path) and file_name.endswith(".md"):
                        stat = os.stat(file_path)
                        modified_time = datetime.datetime.fromtimestamp(stat.st_mtime)
                        files.append(
                            {
                                "name": file_name,
                                "path": file_path,
                                "type": "🤖 ATA",
                                "folder": "ata/",
                                "modified": modified_time,
                                "size": stat.st_size,
                            }
                        )

            # Also scan main output directory for legacy files
            for file_name in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file_name)
                if os.path.isfile(file_path) and file_name.endswith(".md"):
                    # Get file stats
                    stat = os.stat(file_path)
                    modified_time = datetime.datetime.fromtimestamp(stat.st_mtime)

                    # Determine file type
                    if file_name.endswith("_ata.md"):
                        file_type = "🤖 ATA (Legacy)"
                    else:
                        file_type = "� Transcript (Legacy)"

                    files.append(
                        {
                            "name": file_name,
                            "path": file_path,
                            "type": file_type,
                            "folder": "",
                            "modified": modified_time,
                            "size": stat.st_size,
                        }
                    )

            # Sort by modification time (newest first)
            files.sort(key=lambda x: x["modified"], reverse=True)

            # Add files to listbox
            for file_info in files:
                size_str = self.format_file_size(file_info["size"])
                time_str = file_info["modified"].strftime("%Y-%m-%d %H:%M")
                folder_info = file_info.get("folder", "")
                display_text = f"{file_info['type']} | {folder_info}{file_info['name']} | {size_str} | {time_str}"
                self.files_listbox.insert(tk.END, display_text)

            if not files:
                self.files_listbox.insert(tk.END, "No files found")

        except Exception as e:
            self.files_listbox.delete(0, tk.END)
            self.files_listbox.insert(tk.END, f"Error loading files: {e}")

    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def open_selected_file(self, event=None):
        """Open the selected file"""
        try:
            selection = self.files_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a file to open")
                return

            # Parse the selected file name from display text
            display_text = self.files_listbox.get(selection[0])
            if " | " not in display_text:
                return

            parts = display_text.split(" | ")
            if len(parts) < 2:
                return

            file_name = parts[1]
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            file_path = os.path.join(output_dir, file_name)

            if os.path.exists(file_path):
                # Open file with default system application
                import subprocess
                import sys

                if sys.platform.startswith("win"):
                    os.startfile(file_path)
                elif sys.platform.startswith("darwin"):
                    subprocess.call(["open", file_path])
                else:
                    subprocess.call(["xdg-open", file_path])

                self.status_var.set(f"Opened: {file_name}")
            else:
                messagebox.showerror("Error", f"File not found: {file_name}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

    def delete_selected_file(self):
        """Delete the selected file"""
        try:
            selection = self.files_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a file to delete")
                return

            # Parse the selected file name from display text
            display_text = self.files_listbox.get(selection[0])
            if " | " not in display_text:
                return

            parts = display_text.split(" | ")
            if len(parts) < 2:
                return

            file_name = parts[1]

            # Confirm deletion
            if not messagebox.askyesno(
                "Confirm Delete", f"Are you sure you want to delete '{file_name}'?"
            ):
                return

            output_dir = os.path.join(os.path.dirname(__file__), "output")
            file_path = os.path.join(output_dir, file_name)

            if os.path.exists(file_path):
                os.remove(file_path)
                self.status_var.set(f"Deleted: {file_name}")
                self.refresh_files_list()
            else:
                messagebox.showerror("Error", f"File not found: {file_name}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete file: {e}")

    def open_output_folder(self):
        """Open the output folder in file explorer"""
        try:
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            import subprocess
            import sys

            if sys.platform.startswith("win"):
                os.startfile(output_dir)
            elif sys.platform.startswith("darwin"):
                subprocess.call(["open", output_dir])
            else:
                subprocess.call(["xdg-open", output_dir])

            self.status_var.set("Output folder opened")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open output folder: {e}")

    # Transcript Files Management Methods
    def refresh_transcript_files_list(self):
        """Refresh the list of transcript files"""
        try:
            self.transcript_files_listbox.delete(0, tk.END)

            # Check transcript directory
            transcript_dir = os.path.join(os.path.dirname(__file__), "output", "transcript")
            if not os.path.exists(transcript_dir):
                os.makedirs(transcript_dir)
                return

            # Get transcript files
            files = []
            for file in os.listdir(transcript_dir):
                if file.endswith('.md'):
                    file_path = os.path.join(transcript_dir, file)
                    file_time = os.path.getmtime(file_path)
                    files.append((file, file_time))

            # Sort by modification time (newest first)
            files.sort(key=lambda x: x[1], reverse=True)

            # Add to listbox
            for file, _ in files:
                self.transcript_files_listbox.insert(tk.END, file)

        except Exception as e:
            self.status_var.set(f"Error refreshing transcript files: {e}")

    def open_selected_transcript_file(self, event=None):
        """Open the selected transcript file"""
        try:
            selection = self.transcript_files_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a transcript file to open")
                return

            filename = self.transcript_files_listbox.get(selection[0])
            transcript_dir = os.path.join(os.path.dirname(__file__), "output", "transcript")
            file_path = os.path.join(transcript_dir, filename)

            if os.path.exists(file_path):
                import subprocess
                import sys

                if sys.platform.startswith("win"):
                    os.startfile(file_path)
                elif sys.platform.startswith("darwin"):
                    subprocess.call(["open", file_path])
                else:
                    subprocess.call(["xdg-open", file_path])

                self.status_var.set(f"Opened: {filename}")
            else:
                messagebox.showerror("Error", f"File not found: {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open transcript file: {e}")

    def delete_selected_transcript_file(self):
        """Delete the selected transcript file"""
        try:
            selection = self.transcript_files_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a transcript file to delete")
                return

            filename = self.transcript_files_listbox.get(selection[0])
            
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{filename}'?"):
                transcript_dir = os.path.join(os.path.dirname(__file__), "output", "transcript")
                file_path = os.path.join(transcript_dir, filename)
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.refresh_transcript_files_list()
                    self.status_var.set(f"Deleted: {filename}")
                else:
                    messagebox.showerror("Error", f"File not found: {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete transcript file: {e}")

    def open_transcript_folder(self):
        """Open the transcript folder in file explorer"""
        try:
            transcript_dir = os.path.join(os.path.dirname(__file__), "output", "transcript")
            if not os.path.exists(transcript_dir):
                os.makedirs(transcript_dir)

            import subprocess
            import sys

            if sys.platform.startswith("win"):
                os.startfile(transcript_dir)
            elif sys.platform.startswith("darwin"):
                subprocess.call(["open", transcript_dir])
            else:
                subprocess.call(["xdg-open", transcript_dir])

            self.status_var.set("Transcript folder opened")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open transcript folder: {e}")

    # ATA Files Management Methods
    def refresh_ata_files_list(self):
        """Refresh the list of ATA files"""
        try:
            self.ata_files_listbox.delete(0, tk.END)

            # Check ATA directory
            ata_dir = os.path.join(os.path.dirname(__file__), "output", "ata")
            if not os.path.exists(ata_dir):
                os.makedirs(ata_dir)
                return

            # Get ATA files
            files = []
            for file in os.listdir(ata_dir):
                if file.endswith('.md'):
                    file_path = os.path.join(ata_dir, file)
                    file_time = os.path.getmtime(file_path)
                    files.append((file, file_time))

            # Sort by modification time (newest first)
            files.sort(key=lambda x: x[1], reverse=True)

            # Add to listbox
            for file, _ in files:
                self.ata_files_listbox.insert(tk.END, file)

            # Update info label
            if files:
                self.ata_info_label.config(
                    text=f"Found {len(files)} ATA summary file(s). Double-click to open.",
                    fg="blue"
                )
            else:
                self.ata_info_label.config(
                    text="No ATA summary files found. Generate meeting minutes from transcript files.",
                    fg="gray"
                )

        except Exception as e:
            self.status_var.set(f"Error refreshing ATA files: {e}")

    def open_selected_ata_file(self, event=None):
        """Open the selected ATA file"""
        try:
            selection = self.ata_files_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an ATA file to open")
                return

            filename = self.ata_files_listbox.get(selection[0])
            ata_dir = os.path.join(os.path.dirname(__file__), "output", "ata")
            file_path = os.path.join(ata_dir, filename)

            if os.path.exists(file_path):
                import subprocess
                import sys

                if sys.platform.startswith("win"):
                    os.startfile(file_path)
                elif sys.platform.startswith("darwin"):
                    subprocess.call(["open", file_path])
                else:
                    subprocess.call(["xdg-open", file_path])

                self.status_var.set(f"Opened: {filename}")
            else:
                messagebox.showerror("Error", f"File not found: {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ATA file: {e}")

    def delete_selected_ata_file(self):
        """Delete the selected ATA file"""
        try:
            selection = self.ata_files_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an ATA file to delete")
                return

            filename = self.ata_files_listbox.get(selection[0])
            
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{filename}'?"):
                ata_dir = os.path.join(os.path.dirname(__file__), "output", "ata")
                file_path = os.path.join(ata_dir, filename)
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.refresh_ata_files_list()
                    self.status_var.set(f"Deleted: {filename}")
                else:
                    messagebox.showerror("Error", f"File not found: {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete ATA file: {e}")

    def open_ata_folder(self):
        """Open the ATA folder in file explorer"""
        try:
            ata_dir = os.path.join(os.path.dirname(__file__), "output", "ata")
            if not os.path.exists(ata_dir):
                os.makedirs(ata_dir)

            import subprocess
            import sys

            if sys.platform.startswith("win"):
                os.startfile(ata_dir)
            elif sys.platform.startswith("darwin"):
                subprocess.call(["open", ata_dir])
            else:
                subprocess.call(["xdg-open", ata_dir])

            self.status_var.set("ATA folder opened")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ATA folder: {e}")

    # File Selection Event Handlers
    def on_transcript_file_select(self, event=None):
        """Handle transcript file selection"""
        try:
            selection = self.transcript_files_listbox.curselection()
            if selection:
                # Enable file operation buttons
                self.open_transcript_btn.config(state="normal")
                self.save_transcript_as_btn.config(state="normal")
                self.regenerate_ata_btn.config(state="normal")
            else:
                # Disable file operation buttons
                self.open_transcript_btn.config(state="disabled")
                self.save_transcript_as_btn.config(state="disabled")
                self.regenerate_ata_btn.config(state="disabled")
        except Exception as e:
            self.status_var.set(f"Error handling transcript selection: {e}")

    def on_ata_file_select(self, event=None):
        """Handle ATA file selection"""
        try:
            selection = self.ata_files_listbox.curselection()
            if selection:
                # Enable file operation buttons
                self.open_ata_btn.config(state="normal")
                self.save_ata_as_btn.config(state="normal")
                
                # Update info label with file details
                filename = self.ata_files_listbox.get(selection[0])
                ata_dir = os.path.join(os.path.dirname(__file__), "output", "ata")
                file_path = os.path.join(ata_dir, filename)
                
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    mod_time = os.path.getmtime(file_path)
                    mod_time_str = datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
                    
                    self.ata_info_label.config(
                        text=f"File: {filename}\nSize: {file_size} bytes\nModified: {mod_time_str}",
                        fg="blue"
                    )
            else:
                # Disable file operation buttons
                self.open_ata_btn.config(state="disabled")
                self.save_ata_as_btn.config(state="disabled")
                self.ata_info_label.config(
                    text="Select an ATA file to view information",
                    fg="gray"
                )
        except Exception as e:
            self.status_var.set(f"Error handling ATA selection: {e}")

    # Save As Methods
    def save_transcript_as(self):
        """Save selected transcript file to a different location"""
        try:
            selection = self.transcript_files_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a transcript file first")
                return

            filename = self.transcript_files_listbox.get(selection[0])
            transcript_dir = os.path.join(os.path.dirname(__file__), "output", "transcript")
            source_path = os.path.join(transcript_dir, filename)

            if not os.path.exists(source_path):
                messagebox.showerror("Error", f"File not found: {filename}")
                return

            # Ask user where to save
            save_path = filedialog.asksaveasfilename(
                title="Save Transcript As",
                defaultextension=".md",
                filetypes=[
                    ("Markdown files", "*.md"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ],
                initialfilename=filename
            )

            if save_path:
                import shutil
                shutil.copy2(source_path, save_path)
                self.status_var.set(f"Transcript saved to: {os.path.basename(save_path)}")
                messagebox.showinfo("Success", f"File saved successfully to:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save transcript: {e}")

    def save_ata_as(self):
        """Save selected ATA file to a different location"""
        try:
            selection = self.ata_files_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an ATA file first")
                return

            filename = self.ata_files_listbox.get(selection[0])
            ata_dir = os.path.join(os.path.dirname(__file__), "output", "ata")
            source_path = os.path.join(ata_dir, filename)

            if not os.path.exists(source_path):
                messagebox.showerror("Error", f"File not found: {filename}")
                return

            # Ask user where to save
            save_path = filedialog.asksaveasfilename(
                title="Save ATA As",
                defaultextension=".md",
                filetypes=[
                    ("Markdown files", "*.md"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ],
                initialfilename=filename
            )

            if save_path:
                import shutil
                shutil.copy2(source_path, save_path)
                self.status_var.set(f"ATA saved to: {os.path.basename(save_path)}")
                messagebox.showinfo("Success", f"File saved successfully to:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save ATA: {e}")

    def regenerate_ata_from_selected(self):
        """Regenerate ATA from selected transcript file"""
        try:
            selection = self.transcript_files_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a transcript file first")
                return

            filename = self.transcript_files_listbox.get(selection[0])
            transcript_dir = os.path.join(os.path.dirname(__file__), "output", "transcript")
            transcript_path = os.path.join(transcript_dir, filename)

            if not os.path.exists(transcript_path):
                messagebox.showerror("Error", f"File not found: {filename}")
                return

            # Confirm regeneration
            if not messagebox.askyesno(
                "Confirm Regeneration", 
                f"Generate new ATA from '{filename}'?\n\nThis will create a new ATA file."
            ):
                return

            # Set the selected file path and generate ATA directly
            self.selected_transcript_path = transcript_path
            self.status_var.set("Generating ATA...")
            
            # Generate ATA directly
            self.generate_ata_from_file()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to regenerate ATA: {e}")

    def select_transcript_file(self):
        """Select a transcript file for ATA generation"""
        try:
            # Start in the transcript directory
            transcript_dir = os.path.join(
                os.path.dirname(__file__), "output", "transcript"
            )
            if not os.path.exists(transcript_dir):
                # Fallback to main output directory
                transcript_dir = os.path.join(os.path.dirname(__file__), "output")

            file_path = filedialog.askopenfilename(
                title="Select Transcript File",
                filetypes=[
                    ("Markdown files", "*.md"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ],
                initialdir=transcript_dir,
            )

            if file_path:
                self.status_var.set(f"Selected: {os.path.basename(file_path)}")
                self.selected_transcript_path = file_path

        except Exception as e:
            messagebox.showerror("Error", f"Failed to select file: {e}")

    def generate_ata_from_file(self):
        """Generate ATA from selected transcript file"""
        try:
            if (
                not hasattr(self, "selected_transcript_path")
                or not self.selected_transcript_path
            ):
                messagebox.showwarning(
                    "Warning", "Please select a transcript file first"
                )
                return

            if not os.path.exists(self.selected_transcript_path):
                messagebox.showerror("Error", "Selected file no longer exists")
                return

            # First, validate Ollama connection
            self.status_var.set("🔍 Checking Ollama connection...")
            self.root.update_idletasks()

            if not self.ollama_service.is_ollama_available():
                self.status_var.set(t("ollama_service_unavailable", "❌ Ollama service not available"))
                messagebox.showerror(
                    "Connection Error", 
                    f"Cannot connect to Ollama service at {self.ollama_service.base_url}\n\n"
                    "Please check:\n"
                    "1. Ollama is running\n"
                    "2. The URL in config is correct\n"
                    "3. Network connectivity"
                )
                return

            self.status_var.set("🤖 Generating meeting minutes...")
            self.root.update_idletasks()

            # Generate output file name in ATA directory
            base_name = os.path.splitext(
                os.path.basename(self.selected_transcript_path)
            )[0]
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{base_name}_ata_{timestamp}.md"

            # Create ATA directory if it doesn't exist
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            ata_dir = os.path.join(output_dir, "ata")
            if not os.path.exists(ata_dir):
                os.makedirs(ata_dir)

            output_path = os.path.join(ata_dir, output_name)

            # Run ATA generation in a separate thread to avoid UI freezing
            def generate_in_thread():
                try:
                    result = self.ollama_service.generate_and_save_minutes(
                        self.selected_transcript_path,
                        output_path,
                        self.config.get("language", "pt-BR"),
                    )
                    
                    # Update UI from main thread
                    self.root.after(0, lambda: self._handle_ata_generation_result(result, output_name, output_path))
                    
                except Exception as e:
                    # Handle errors from main thread
                    error_msg = str(e)
                    self.root.after(0, lambda: self._handle_ata_generation_error(error_msg))

            # Start generation in background thread
            generation_thread = threading.Thread(target=generate_in_thread, daemon=True)
            generation_thread.start()

        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)[:50]}...")
            messagebox.showerror("Error", f"Failed to start ATA generation: {e}")

    def _handle_ata_generation_result(self, result, output_name, output_path):
        """Handle ATA generation result in main thread"""
        try:
            if result.get("success"):
                self.status_var.set(f"✅ ATA generated: {output_name}")
                self.refresh_ata_files_list()

                # Ask if user wants to open the generated file
                if messagebox.askyesno(
                    "Success",
                    f"Meeting minutes generated successfully!\n\nOpen the file now?",
                ):
                    self.open_file(output_path)
            else:
                error_msg = result.get("error", "Unknown error")
                self.status_var.set(f"❌ Generation failed: {error_msg[:50]}...")
                messagebox.showerror(
                    "Error", f"Failed to generate meeting minutes:\n{error_msg}"
                )
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)[:50]}...")

    def _handle_ata_generation_error(self, error_msg):
        """Handle ATA generation error in main thread"""
        try:
            self.status_var.set(f"❌ Error: {error_msg[:50]}...")
            messagebox.showerror("Error", f"Failed to generate ATA:\n{error_msg}")
        except Exception as e:
            print(f"Error handling ATA generation error: {e}")

    def open_file(self, file_path):
        """Open a file with the default system application"""
        try:
            import subprocess
            import sys

            if sys.platform.startswith("win"):
                os.startfile(file_path)
            elif sys.platform.startswith("darwin"):
                subprocess.call(["open", file_path])
            else:
                subprocess.call(["xdg-open", file_path])

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

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
            f.write(f"# Meeting Transcripts\n")
            f.write(
                f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write("---\n")

            # Get content from both microphones
            mic1_content = self.mic1_transcript_text.get(1.0, tk.END).strip()
            mic2_content = self.mic2_transcript_text.get(1.0, tk.END).strip()

            # Create combined transcript in chronological order
            if mic1_content or mic2_content:
                f.write("## Combined Transcript\n")

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

                f.write("---\n")

            # Write individual microphone sections
            if mic1_content:
                f.write("## Microphone 1 Transcripts\n")
                for line in mic1_content.split("\n"):
                    if line.strip():
                        f.write(f"{line}\n")
                f.write("---\n")

            if mic2_content:
                f.write("## Microphone 2 Transcripts\n")
                for line in mic2_content.split("\n"):
                    if line.strip():
                        f.write(f"{line}\n")

    def auto_save_transcripts(self):
        """Automatically save transcripts to the output folder"""
        try:
            # Check if there's any content to save
            mic1_content = self.mic1_transcript_text.get(1.0, tk.END).strip()
            mic2_content = self.mic2_transcript_text.get(1.0, tk.END).strip()

            if not mic1_content and not mic2_content:
                return

            # Create output directories if they don't exist
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            transcript_dir = os.path.join(output_dir, "transcript")
            if not os.path.exists(transcript_dir):
                os.makedirs(transcript_dir)

            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meeting_transcripts_{timestamp}.md"
            file_path = os.path.join(transcript_dir, filename)

            # Save transcripts using the existing method
            self._save_transcripts_to_markdown(file_path)

            self.status_var.set(f"Transcripts auto-saved: {filename}")

            # Auto-generate ATA if enabled and Ollama is available
            if self.auto_generate_ata and self.ollama_available:
                self.auto_generate_ata_for_file(file_path)

        except Exception as e:
            self.status_var.set(f"Error auto-saving transcripts: {e}")

    def auto_generate_ata_for_file(self, transcript_path):
        """Automatically generate ATA for a transcript file"""
        try:
            # Create ATA directory if it doesn't exist
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            ata_dir = os.path.join(output_dir, "ata")
            if not os.path.exists(ata_dir):
                os.makedirs(ata_dir)

            # Generate ATA filename
            base_name = os.path.splitext(os.path.basename(transcript_path))[0]
            ata_filename = f"{base_name}_ata.md"
            ata_path = os.path.join(ata_dir, ata_filename)

            # Generate ATA using Ollama service
            result = self.ollama_service.generate_and_save_minutes(
                transcript_path, ata_path, self.config.get("language", "pt-BR")
            )

            if result.get("success"):
                self.status_var.set(f"ATA auto-generated: {ata_filename}")
            else:
                error_msg = result.get("error", "Unknown error")
                self.status_var.set(f"ATA generation failed: {error_msg[:50]}...")

        except Exception as e:
            self.status_var.set(f"Error auto-generating ATA: {e}")

    def start_realtime_markdown_save(self):
        """Initialize real-time markdown file for auto-saving"""
        transcript_dir = "src/output/transcript"
        if not os.path.exists(transcript_dir):
            os.makedirs(transcript_dir)

        # Create filename with timestamp
        self.session_start_time = datetime.datetime.now()
        timestamp = self.session_start_time.strftime("%Y%m%d_%H%M%S")
        self.markdown_file_path = f"{transcript_dir}/meeting_transcripts_{timestamp}.md"

        try:
            # Initialize markdown file
            self.markdown_file = open(self.markdown_file_path, "w", encoding="utf-8")

            # Write header
            self.markdown_file.write(f"# Meeting Transcripts - Live Session\n")
            self.markdown_file.write(
                f"**Session Started:** {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            self.markdown_file.write("**Participants:** Microphone 1, Microphone 2\n")
            self.markdown_file.write("---\n")
            self.markdown_file.write("## Live Transcript\n")
            self.markdown_file.flush()

            # Update UI
            self.auto_save_label.config(
                text=f"{t('auto_save_on', 'Auto-save: ON')} ({os.path.basename(self.markdown_file_path)})",
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

                self.markdown_file.write("\n---\n")
                self.markdown_file.write(
                    f"**Session Ended:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                if isinstance(duration, datetime.timedelta):
                    self.markdown_file.write(
                        f"**Duration:** {str(duration).split('.')[0]}\n"
                    )

                self.markdown_file.close()
                self.markdown_file = None

                # Update UI
                self.auto_save_label.config(text=t("auto_save_off", "Auto-save: OFF"), fg="gray")
                self.status_var.set(f"Session saved to: {self.markdown_file_path}")

                # Ask user if they want to generate meeting minutes with Ollama
                if self.ollama_available and self.markdown_file_path:
                    if self.auto_generate_ata:
                        # Automatically generate ata in background
                        self.auto_generate_meeting_minutes()
                    else:
                        # Prompt user to generate manually
                        self.prompt_for_meeting_minutes()

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
            self.markdown_file.write(f"**[{timestamp}] {mic_name}:** {transcript}\n")
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

    def load_main_config(self):
        """Load main configuration from config.json"""
        try:
            config_path = "config.json"
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading main config: {e}")

        # Return default config
        return {
            "ollama": {
                "base_url": "http://localhost:11434",
                "model_name": "llama3.2",
                "temperature": 0.3,
                "top_p": 0.8,
                "num_predict": 2048,
            },
            "auto_generate_ata": True,
            "language": "pt-BR",
        }

    def save_main_config(self):
        """Save main configuration to config.json"""
        try:
            config_path = "config.json"
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving main config: {e}")
            return False

    def ensure_config_file_exists(self):
        """Ensure config.json exists with default values"""
        config_path = "config.json"
        if not os.path.exists(config_path):
            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
                self.status_var.set(
                    "Created default config.json with Ollama URL: http://localhost:11434"
                )
            except Exception as e:
                self.status_var.set(f"Error creating config file: {e}")

    def migrate_old_mic_config(self):
        """Migrate microphone configuration from old mic_config.json to unified config.json"""
        old_config_path = "mic_config.json"
        if not os.path.exists(old_config_path):
            return

        try:
            # Load old mic config
            with open(old_config_path, "r") as f:
                old_config = json.load(f)

            # Load current unified config
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)

            # Only migrate if microphones section doesn't exist in new config
            if "microphones" not in config:
                config["microphones"] = {
                    "saved_microphones": old_config.get("saved_microphones", []),
                    "timestamp": old_config.get(
                        "timestamp", datetime.datetime.now().isoformat()
                    ),
                }

                # Save updated unified config
                with open(self.config_file, "w") as f:
                    json.dump(config, f, indent=2)

                # Remove old config file
                os.remove(old_config_path)
                self.status_var.set("Migrated microphone configuration to config.json")

        except Exception as e:
            self.status_var.set(f"Error migrating mic config: {e}")

    def load_mic_preferences(self):
        """Load previously saved microphone preferences from unified config.json"""
        if not os.path.exists(self.config_file):
            return

        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)

            # Load from unified config structure
            microphone_config = config.get("microphones", {})
            saved_mics = microphone_config.get("saved_microphones", [])

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
        transcript_message = f"[{timestamp}] {transcript}\n"

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
                    command=self.on_microphone_selection_change,
                )
                cb.pack(anchor="w", pady=2)
                self.mic_vars.append((var, idx))

            # Load saved preferences
            self.load_mic_preferences()

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
                "Please select exactly two microphones.\n"
                f"You have selected {len(selected)} microphone(s).",
            )
            return

        # Confirm before starting
        device_names = [name for idx, name in self.mics if idx in selected]
        confirm_msg = (
            f"Start real-time recording from:\n"
            f"• {device_names[0]}\n"
            f"• {device_names[1]}\n"
            f"Recording will continue until you stop it."
        )

        if messagebox.askyesno("Confirm Recording", confirm_msg):
            self.clear_all_output()

            # Update UI state
            self.is_recording = True
            self.listen_btn.config(text=t("stop_button", "🛑 Stop"), bg="#f44336")
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

        # Auto-save transcripts to output folder
        self.auto_save_transcripts()

        # Update UI
        self.listen_btn.config(text=t("start_button", "🎤 Start"), bg="#4CAF50")
        self.status_var.set("Continuous recording stopped - transcripts auto-saved")

        # Add log message
        self.combined_output.insert(tk.END, "\n=== RECORDING STOPPED ===\n")
        self.combined_output.see(tk.END)

        # Refresh files list if files tab exists
        if hasattr(self, "files_listbox"):
            self.refresh_files_list()

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
                "Please select exactly two microphones.\n"
                f"You have selected {len(selected)} microphone(s).",
            )
            return

        # Confirm before starting
        device_names = [name for idx, name in self.mics if idx in selected]
        confirm_msg = (
            f"Start recording from:\n"
            f"• {device_names[0]}\n"
            f"• {device_names[1]}\n"
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
        self.is_shutting_down = True  # Set shutdown flag
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
        results_text.insert(tk.END, "Starting microphone tests...\n")
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
                    tk.END, f"Found {len(self.mics)} microphone(s) to test\n"
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
                results_text.insert(tk.END, "🎉 All microphone tests completed!\n")
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
        from src.translations import get_translation_manager, set_global_language
        
        # Create language settings window
        lang_window = tk.Toplevel(self.root)
        lang_window.title("Language Settings")
        lang_window.geometry("400x300")
        lang_window.resizable(False, False)
        
        # Make window modal
        lang_window.transient(self.root)
        lang_window.grab_set()
        
        # Center the window
        lang_window.geometry(
            "+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100)
        )
        
        # Get translation manager
        tm = get_translation_manager()
        
        # Title
        title_label = tk.Label(
            lang_window, 
            text="🌐 Language Settings", 
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=20)
        
        # Current language display
        current_frame = tk.Frame(lang_window)
        current_frame.pack(pady=10, padx=20, fill=tk.X)
        
        current_label = tk.Label(
            current_frame, 
            text="Current Language:", 
            font=("Arial", 10, "bold")
        )
        current_label.pack(anchor=tk.W)
        
        current_value = tk.Label(
            current_frame, 
            text=tm.get_language_name(self.config.get("language", "pt-BR")),
            font=("Arial", 10),
            fg="blue"
        )
        current_value.pack(anchor=tk.W, pady=(5, 0))
        
        # Language selection
        select_frame = tk.Frame(lang_window)
        select_frame.pack(pady=20, padx=20, fill=tk.X)
        
        select_label = tk.Label(
            select_frame, 
            text="Select Language:", 
            font=("Arial", 10, "bold")
        )
        select_label.pack(anchor=tk.W)
        
        # Language variable
        selected_language = tk.StringVar(value=self.config.get("language", "pt-BR"))
        
        # Create radio buttons for each language
        for lang_code, lang_name in tm.get_available_languages().items():
            radio = tk.Radiobutton(
                select_frame,
                text=f"{lang_name} ({lang_code})",
                variable=selected_language,
                value=lang_code,
                font=("Arial", 10)
            )
            radio.pack(anchor=tk.W, pady=2)
        
        # Button frame
        button_frame = tk.Frame(lang_window)
        button_frame.pack(pady=30, padx=20, fill=tk.X)
        
        def save_language():
            """Save the selected language"""
            new_language = selected_language.get()
            try:
                # Update config
                self.config["language"] = new_language
                self.save_main_config()
                
                # Update global translation manager
                set_global_language(new_language)
                
                # Show success message
                messagebox.showinfo(
                    "Language Changed",
                    "Language changed successfully! Please restart the application to see all changes.",
                    parent=lang_window
                )
                
                lang_window.destroy()
                
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Error saving language configuration: {str(e)}",
                    parent=lang_window
                )
        
        def cancel_settings():
            """Cancel and close dialog"""
            lang_window.destroy()
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="💾 Save",
            command=save_language,
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Cancel",
            command=cancel_settings,
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        cancel_btn.pack(side=tk.LEFT)

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
   • Click "Start"
   • Speak normally - transcription happens in real-time
   • Audio is captured continuously without pauses

3. TRANSCRIPTS:
   • View results in the Combined View, Logs, or Transcripts tabs
   • Transcripts are automatically saved to markdown files in real-time
   • Transcripts include timestamps and device identification

4. CONFIGURATION:
   • Load saved microphone selections from File menu
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

    def check_ollama_availability(self):
        """Check if Ollama is available and update status"""

        def check_in_background():
            try:
                # Check if we're shutting down before starting
                if self.is_shutting_down:
                    return

                self.ollama_available = self.ollama_service.is_ollama_available()

                # Check again before proceeding with UI updates
                if self.is_shutting_down:
                    return

                if self.ollama_available:
                    if self.ollama_service.is_model_available():
                        self._safe_update_ollama_status(
                            t("ollama_ready", "🌐 Ollama Remote: Ready"), "green"
                        )
                    else:
                        self._safe_update_ollama_status(
                            t("ollama_downloading", "🌐 Ollama Remote: Downloading model..."), "orange"
                        )
                        # Try to pull the model
                        if not self.is_shutting_down:
                            success = self.ollama_service.pull_model()
                            if not self.is_shutting_down and success:
                                self._safe_update_ollama_status(
                                    t("ollama_ready", "🌐 Ollama Remote: Ready"), "green"
                                )
                            elif not self.is_shutting_down:
                                self._safe_update_ollama_status(
                                    t("ollama_download_failed", "🌐 Ollama Remote: Model download failed"), "red"
                                )
                else:
                    self._safe_update_ollama_status(
                        t("ollama_unavailable", "🌐 Ollama Remote: Not available"), "red"
                    )
            except Exception as e:
                if not self.is_shutting_down:
                    self.ollama_available = False
                    self._safe_update_ollama_status(
                        t("ollama_connection_error", "🌐 Ollama Remote: Connection Error"), "red"
                    )
                    print(f"Ollama check failed: {e}")

        # Run check in background thread only if not shutting down
        if not self.is_shutting_down:
            threading.Thread(target=check_in_background, daemon=True).start()

    def _safe_update_ollama_status(self, text, color):
        """Safely update Ollama status from background thread"""
        try:
            # Check if we're shutting down
            if self.is_shutting_down:
                return

            # Check if root window still exists and is valid
            if self.root and not self.is_shutting_down:
                try:
                    # Verify the window still exists
                    self.root.winfo_exists()
                    # Schedule the update in the main thread
                    self.root.after(
                        0, lambda: self._update_ollama_label_if_valid(text, color)
                    )
                except tk.TclError:
                    # Window has been destroyed
                    return
        except Exception as e:
            # Silently handle any errors during shutdown
            pass

    def _update_ollama_label_if_valid(self, text, color):
        """Update the Ollama label only if it's still valid"""
        try:
            if not self.is_shutting_down and hasattr(self, "ollama_status_label"):
                self.ollama_status_label.config(text=text, fg=color)
        except Exception:
            # Silently handle any errors during shutdown
            pass

    def _pull_ollama_model(self):
        """Pull Ollama model in background"""
        try:
            self.status_var.set("Downloading Ollama model in background...")
            success = self.ollama_service.pull_model()
            if success:
                self.status_var.set("Ollama model ready for meeting minutes generation")
            else:
                self.status_var.set("Failed to download Ollama model")
        except Exception as e:
            self.status_var.set(f"Error downloading model: {e}")

    def prompt_for_meeting_minutes(self):
        """Prompt user to generate meeting minutes after recording ends"""
        if not self.ollama_available:
            return

        response = messagebox.askyesno(
            "Gerar Ata da Reunião",
            "A gravação foi finalizada. Deseja gerar uma ata da reunião automaticamente?\n\n"
            "A ata será organizada por temas abordados e incluirá um resumo dos pontos principais.",
            icon="question",
        )

        if response:
            self.generate_meeting_minutes_from_file(self.markdown_file_path)

    def generate_meeting_minutes_dialog(self):
        """Open dialog to select transcript file and generate meeting minutes"""
        if not self.ollama_available:
            messagebox.showerror(
                "Ollama Indisponível",
                "O serviço Ollama não está disponível.\n\n"
                "Verificando conexão com o servidor remoto:\n"
                "https://api.apps.tec.br/ollama\n\n"
                "Por favor, verifique sua conexão com a internet.",
            )
            return

        # Select transcript file
        file_path = filedialog.askopenfilename(
            title="Selecionar Transcrição da Reunião",
            filetypes=[
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
            initialdir="src/output" if os.path.exists("src/output") else ".",
        )

        if file_path:
            self.generate_meeting_minutes_from_file(file_path)

    def generate_meeting_minutes_from_file(self, transcript_file_path):
        """Generate meeting minutes from a transcript file"""
        if not os.path.exists(transcript_file_path):
            messagebox.showerror(
                "Erro", f"Arquivo não encontrado: {transcript_file_path}"
            )
            return

        # Create progress dialog
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Gerando Ata da Reunião")
        progress_window.geometry("400x200")
        progress_window.transient(self.root)
        progress_window.grab_set()

        # Center the window
        progress_window.geometry(
            "+%d+%d" % (self.root.winfo_rootx() + 250, self.root.winfo_rooty() + 150)
        )

        tk.Label(
            progress_window,
            text="🤖 Gerando Ata da Reunião com IA",
            font=("Arial", 14, "bold"),
        ).pack(pady=20)

        progress_text = tk.Text(progress_window, height=6, wrap=tk.WORD)
        progress_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Cancel button (initially disabled)
        cancel_btn = tk.Button(
            progress_window,
            text="Fechar",
            command=progress_window.destroy,
            state=tk.DISABLED,
        )
        cancel_btn.pack(pady=10)

        def update_progress(message):
            progress_text.insert(tk.END, f"{message}\n")
            progress_text.see(tk.END)
            progress_window.update()

        def generate_in_thread():
            try:
                update_progress("📖 Lendo transcrição...")

                # Determine output file path
                base_name = os.path.splitext(transcript_file_path)[0]
                output_file_path = f"{base_name}_ata.md"

                update_progress("🤖 Enviando para Ollama...")
                update_progress(
                    "⏳ Processando com IA (pode demorar alguns minutos)..."
                )

                # Generate meeting minutes
                result = self.ollama_service.generate_and_save_minutes(
                    transcript_file_path, output_file_path, language=self.config.get("language", "pt-BR")
                )

                if result["success"]:
                    update_progress("✅ Ata gerada com sucesso!")
                    update_progress(f"📄 Salva em: {output_file_path}")

                    # Show success message with option to open file
                    def show_success():
                        response = messagebox.askyesno(
                            "Ata Gerada com Sucesso!",
                            f"A ata da reunião foi gerada e salva em:\n{output_file_path}\n\n"
                            "Deseja abrir o arquivo agora?",
                            parent=progress_window,
                        )

                        if response:
                            try:
                                os.startfile(output_file_path)  # Windows
                            except:
                                try:
                                    import subprocess

                                    subprocess.call(["open", output_file_path])  # macOS
                                except:
                                    messagebox.showinfo(
                                        "Arquivo Salvo",
                                        f"Ata salva em: {output_file_path}",
                                        parent=progress_window,
                                    )

                        progress_window.destroy()

                    self.root.after(0, show_success)

                else:
                    error_msg = result.get("error", "Erro desconhecido")
                    update_progress(f"❌ Erro: {error_msg}")

                    def show_error():
                        messagebox.showerror(
                            "Erro ao Gerar Ata",
                            f"Não foi possível gerar a ata da reunião:\n\n{error_msg}\n\n"
                            "Verifique se o Ollama está executando e tente novamente.",
                            parent=progress_window,
                        )

                    self.root.after(0, show_error)

            except Exception as e:
                update_progress(f"❌ Erro inesperado: {e}")

                def show_exception():
                    messagebox.showerror(
                        "Erro Inesperado",
                        f"Ocorreu um erro inesperado:\n\n{e}",
                        parent=progress_window,
                    )

                self.root.after(0, show_exception)

            finally:
                # Enable close button
                def enable_close():
                    cancel_btn.config(state=tk.NORMAL, text="Fechar")

                self.root.after(0, enable_close)

        # Start generation in background thread
        threading.Thread(target=generate_in_thread, daemon=True).start()

    def toggle_auto_ata_generation(self):
        """Toggle automatic ata generation on/off"""
        self.auto_generate_ata = not self.auto_generate_ata
        
        # Update config and save
        self.config["auto_generate_ata"] = self.auto_generate_ata
        self.save_main_config()
        
        status = "ATIVADA" if self.auto_generate_ata else "DESATIVADA"
        messagebox.showinfo(
            "Geração Automática de Ata",
            f"Geração automática de ata {status}.\n\n"
            f"{'✅' if self.auto_generate_ata else '❌'} Atas serão geradas automaticamente após o fim da transcrição.",
        )

    def auto_generate_meeting_minutes(self):
        """Automatically generate meeting minutes without user prompt"""
        if not self.ollama_available or not self.markdown_file_path:
            return

        # Show status in the interface
        self.status_var.set("🤖 Gerando ata automaticamente...")

        def generate_in_background():
            try:
                # Determine output file path
                base_name = os.path.splitext(self.markdown_file_path)[0]
                output_file_path = f"{base_name}_ata.md"

                # Generate meeting minutes
                result = self.ollama_service.generate_and_save_minutes(
                    self.markdown_file_path, output_file_path, language=self.config.get("language", "pt-BR")
                )

                if result["success"]:
                    # Update status on success
                    self.root.after(
                        0,
                        lambda: self.status_var.set(
                            f"✅ Ata gerada automaticamente: {os.path.basename(output_file_path)}"
                        ),
                    )

                    # Show notification
                    def show_notification():
                        messagebox.showinfo(
                            "Ata Gerada Automaticamente",
                            f"✅ Ata da reunião foi gerada automaticamente!\n\n"
                            f"📄 Arquivo: {os.path.basename(output_file_path)}\n"
                            f"📂 Local: {os.path.dirname(output_file_path)}\n\n"
                            f"Acesse pelo menu: Arquivo > Ver Todas as Atas",
                        )

                    self.root.after(0, show_notification)

                else:
                    error_msg = result.get("error", "Erro desconhecido")
                    self.root.after(
                        0,
                        lambda: self.status_var.set(
                            f"❌ Erro na geração automática: {error_msg}"
                        ),
                    )

            except Exception as e:
                self.root.after(
                    0,
                    lambda: self.status_var.set(
                        f"❌ Erro inesperado na geração automática: {e}"
                    ),
                )

        # Start generation in background thread
        threading.Thread(target=generate_in_background, daemon=True).start()

    def view_all_transcripts(self):
        """Show window with all transcript files"""
        transcript_window = tk.Toplevel(self.root)
        transcript_window.title("📋 Todas as Transcrições")
        transcript_window.geometry("800x600")
        transcript_window.transient(self.root)

        # Center the window
        transcript_window.geometry(
            "+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 50)
        )

        # Title
        tk.Label(
            transcript_window,
            text="📋 Transcrições de Reuniões",
            font=("Arial", 16, "bold"),
        ).pack(pady=10)

        # Create frame for file list
        list_frame = tk.Frame(transcript_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create treeview for file listing
        columns = ("Nome", "Data", "Tamanho", "Caminho")
        transcript_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=15
        )

        # Configure columns
        transcript_tree.heading("Nome", text="Nome do Arquivo")
        transcript_tree.heading("Data", text="Data de Criação")
        transcript_tree.heading("Tamanho", text="Tamanho")
        transcript_tree.heading("Caminho", text="Caminho Completo")

        transcript_tree.column("Nome", width=200)
        transcript_tree.column("Data", width=150)
        transcript_tree.column("Tamanho", width=100)
        transcript_tree.column("Caminho", width=300)

        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=transcript_tree.yview
        )
        transcript_tree.configure(yscrollcommand=tree_scroll.set)

        transcript_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons frame
        button_frame = tk.Frame(transcript_window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            button_frame,
            text="🔄 Atualizar Lista",
            command=lambda: self.refresh_transcript_list(transcript_tree),
            font=("Arial", 10),
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="📄 Abrir Selecionado",
            command=lambda: self.open_selected_file(transcript_tree),
            font=("Arial", 10),
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="🤖 Gerar Ata",
            command=lambda: self.generate_ata_from_selected(transcript_tree),
            font=("Arial", 10),
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="🗑️ Excluir",
            command=lambda: self.delete_selected_transcript(transcript_tree),
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
        ).pack(side=tk.RIGHT, padx=5)

        tk.Button(
            button_frame,
            text="❌ Fechar",
            command=transcript_window.destroy,
            font=("Arial", 10),
        ).pack(side=tk.RIGHT, padx=5)

        # Load transcript files
        self.refresh_transcript_list(transcript_tree)

    def view_all_atas(self):
        """Show window with all ata (meeting minutes) files"""
        ata_window = tk.Toplevel(self.root)
        ata_window.title("📝 Todas as Atas")
        ata_window.geometry("800x600")
        ata_window.transient(self.root)

        # Center the window
        ata_window.geometry(
            "+%d+%d" % (self.root.winfo_rootx() + 120, self.root.winfo_rooty() + 70)
        )

        # Title
        tk.Label(
            ata_window, text="📝 Atas de Reuniões Geradas", font=("Arial", 16, "bold")
        ).pack(pady=10)

        # Create frame for file list
        list_frame = tk.Frame(ata_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create treeview for file listing
        columns = ("Nome", "Data", "Tamanho", "Transcrição Original", "Caminho")
        ata_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        # Configure columns
        ata_tree.heading("Nome", text="Nome da Ata")
        ata_tree.heading("Data", text="Data de Criação")
        ata_tree.heading("Tamanho", text="Tamanho")
        ata_tree.heading("Transcrição Original", text="Transcrição Original")
        ata_tree.heading("Caminho", text="Caminho Completo")

        ata_tree.column("Nome", width=200)
        ata_tree.column("Data", width=150)
        ata_tree.column("Tamanho", width=100)
        ata_tree.column("Transcrição Original", width=200)
        ata_tree.column("Caminho", width=300)

        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=ata_tree.yview
        )
        ata_tree.configure(yscrollcommand=tree_scroll.set)

        ata_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons frame
        button_frame = tk.Frame(ata_window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            button_frame,
            text="🔄 Atualizar Lista",
            command=lambda: self.refresh_ata_list(ata_tree),
            font=("Arial", 10),
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="📄 Abrir Selecionado",
            command=lambda: self.open_selected_file(ata_tree),
            font=("Arial", 10),
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="📋 Ver Transcrição Original",
            command=lambda: self.open_original_transcript(ata_tree),
            font=("Arial", 10),
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="🗑️ Excluir",
            command=lambda: self.delete_selected_ata(ata_tree),
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
        ).pack(side=tk.RIGHT, padx=5)

        tk.Button(
            button_frame,
            text="❌ Fechar",
            command=ata_window.destroy,
            font=("Arial", 10),
        ).pack(side=tk.RIGHT, padx=5)

        # Load ata files
        self.refresh_ata_list(ata_tree)

    def refresh_transcript_list(self, tree):
        """Refresh the transcript file list"""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)

        # Search for transcript files
        transcript_files = []
        search_dirs = ["src/output", "."]

        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                for file in os.listdir(search_dir):
                    if (
                        file.endswith(".md")
                        and "meeting_transcripts_" in file
                        and "_ata" not in file
                    ):
                        file_path = os.path.join(search_dir, file)
                        transcript_files.append(file_path)

        # Add files to tree
        for file_path in sorted(
            transcript_files, key=lambda x: os.path.getmtime(x), reverse=True
        ):
            try:
                file_name = os.path.basename(file_path)
                file_size = f"{os.path.getsize(file_path) / 1024:.1f} KB"
                file_date = datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                ).strftime("%Y-%m-%d %H:%M")

                tree.insert(
                    "", "end", values=(file_name, file_date, file_size, file_path)
                )
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    def refresh_ata_list(self, tree):
        """Refresh the ata file list"""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)

        # Search for ata files
        ata_files = []
        search_dirs = ["src/output", "."]

        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                for file in os.listdir(search_dir):
                    if file.endswith(".md") and "_ata" in file:
                        file_path = os.path.join(search_dir, file)
                        ata_files.append(file_path)

        # Add files to tree
        for file_path in sorted(
            ata_files, key=lambda x: os.path.getmtime(x), reverse=True
        ):
            try:
                file_name = os.path.basename(file_path)
                file_size = f"{os.path.getsize(file_path) / 1024:.1f} KB"
                file_date = datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                ).strftime("%Y-%m-%d %H:%M")

                # Find original transcript file
                original_transcript = file_name.replace("_ata.md", ".md")
                original_path = os.path.join(
                    os.path.dirname(file_path), original_transcript
                )
                if not os.path.exists(original_path):
                    original_transcript = "Não encontrado"

                tree.insert(
                    "",
                    "end",
                    values=(
                        file_name,
                        file_date,
                        file_size,
                        original_transcript,
                        file_path,
                    ),
                )
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    def open_selected_file(self, tree):
        """Open the selected file in the default application"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Seleção", "Por favor, selecione um arquivo.")
            return

        # Get file path from the last column
        item = tree.item(selection[0])
        file_path = item["values"][-1]  # Last column contains the path

        try:
            if os.name == "nt":  # Windows
                os.startfile(file_path)
            elif os.name == "posix":  # macOS and Linux
                import subprocess

                subprocess.call(["open", file_path])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo:\n{e}")

    def generate_ata_from_selected(self, tree):
        """Generate ata from selected transcript"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Seleção", "Por favor, selecione uma transcrição.")
            return

        # Get file path from the last column
        item = tree.item(selection[0])
        file_path = item["values"][-1]  # Last column contains the path

        self.generate_meeting_minutes_from_file(file_path)

    def open_original_transcript(self, tree):
        """Open the original transcript for the selected ata"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Seleção", "Por favor, selecione uma ata.")
            return

        # Get ata file path
        item = tree.item(selection[0])
        ata_file_path = item["values"][-1]  # Last column contains the path

        # Calculate original transcript path
        original_path = ata_file_path.replace("_ata.md", ".md")

        if os.path.exists(original_path):
            try:
                if os.name == "nt":  # Windows
                    os.startfile(original_path)
                elif os.name == "posix":  # macOS and Linux
                    import subprocess

                    subprocess.call(["open", original_path])
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o arquivo:\n{e}")
        else:
            messagebox.showerror(
                "Erro", "Arquivo de transcrição original não encontrado."
            )

    def delete_selected_transcript(self, tree):
        """Delete selected transcript file"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Seleção", "Por favor, selecione uma transcrição.")
            return

        # Get file info
        item = tree.item(selection[0])
        file_name = item["values"][0]
        file_path = item["values"][-1]

        # Confirm deletion
        response = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a transcrição?\n\n"
            f"📄 Arquivo: {file_name}\n"
            f"⚠️ Esta ação não pode ser desfeita.",
        )

        if response:
            try:
                os.remove(file_path)
                messagebox.showinfo("Sucesso", "Transcrição excluída com sucesso!")
                self.refresh_transcript_list(tree)
            except Exception as e:
                messagebox.showerror(
                    "Erro", f"Não foi possível excluir o arquivo:\n{e}"
                )

    def delete_selected_ata(self, tree):
        """Delete selected ata file"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Seleção", "Por favor, selecione uma ata.")
            return

        # Get file info
        item = tree.item(selection[0])
        file_name = item["values"][0]
        file_path = item["values"][-1]

        # Confirm deletion
        response = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a ata?\n\n"
            f"📄 Arquivo: {file_name}\n"
            f"⚠️ Esta ação não pode ser desfeita.",
        )

        if response:
            try:
                os.remove(file_path)
                messagebox.showinfo("Sucesso", "Ata excluída com sucesso!")
                self.refresh_ata_list(tree)
            except Exception as e:
                messagebox.showerror(
                    "Erro", f"Não foi possível excluir o arquivo:\n{e}"
                )


def create_gui():
    """Factory function to create and return GUI instance"""
    return MicrophoneTranscriberGUI()


def run_gui():
    """Convenience function to create and run the GUI"""
    gui = create_gui()
    gui.run()


if __name__ == "__main__":
    run_gui()
