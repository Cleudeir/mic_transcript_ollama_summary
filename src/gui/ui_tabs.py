import tkinter as tk
from tkinter import ttk
from src.i18n import t
from .theme import create_button


class UITabsMixin:
    def setup_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t("menu_settings", "⚙️ Settings"), menu=settings_menu)

        settings_menu.add_command(
            label=t("menu_language", "🌐 Language Settings"),
            command=self.open_language_settings,
        )
        settings_menu.add_command(
            label=t("menu_audio", "🔊 Audio Settings"), command=self.open_audio_settings
        )
        settings_menu.add_separator()
        settings_menu.add_command(
            label=t("menu_auto_ata", "🤖 Auto-generate Ata"),
            command=self.toggle_auto_ata_generation,
        )
        settings_menu.add_separator()
        settings_menu.add_command(
            label=t("menu_performance", "📊 Performance Monitor"),
            command=self.toggle_performance_monitor,
        )

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t("menu_file", "📁 File"), menu=file_menu)

        file_menu.add_command(
            label=t("menu_open_transcript_folder", "📄 Open Transcript Folder"),
            command=self.open_transcript_folder,
        )
        file_menu.add_command(
            label=t("menu_view_transcripts", "📋 View All Transcripts"),
            command=self.view_all_transcripts,
        )
        file_menu.add_separator()
        file_menu.add_command(
            label=t("menu_generate_minutes", "🤖 Generate Meeting Minutes"),
            command=self.generate_meeting_minutes_dialog,
        )
        file_menu.add_command(
            label=t("menu_view_atas", "📝 View All Atas"), command=self.view_all_atas
        )
        file_menu.add_separator()
        file_menu.add_command(
            label=t("menu_reset", "🔄 Reset Application"),
            command=self.reset_application,
        )
        file_menu.add_separator()
        file_menu.add_command(label=t("menu_exit", "❌ Exit"), command=self.on_closing)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t("menu_help", "❓ Help"), menu=help_menu)

        help_menu.add_command(
            label=t("menu_user_guide", "📖 User Guide"), command=self.show_user_guide
        )
        help_menu.add_command(
            label=t("menu_troubleshooting", "🔧 Troubleshooting"),
            command=self.show_troubleshooting,
        )
        help_menu.add_separator()
        help_menu.add_command(label=t("menu_about", "ℹ️ About"), command=self.show_about)

    def create_logs_tab(self):
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text=t("tab_logs", "📝 System Logs"))
        logs_paned = ttk.PanedWindow(logs_frame, orient=tk.HORIZONTAL)
        logs_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        mic1_log_frame = ttk.LabelFrame(logs_paned, text="Microphone 1 - System Logs")
        logs_paned.add(mic1_log_frame, weight=1)
        self.mic1_log_text = tk.Text(mic1_log_frame, height=20, wrap=tk.WORD)
        mic1_log_scroll = tk.Scrollbar(
            mic1_log_frame, orient=tk.VERTICAL, command=self.mic1_log_text.yview
        )
        self.mic1_log_text.configure(yscrollcommand=mic1_log_scroll.set)
        self.mic1_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mic1_log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        mic2_log_frame = ttk.LabelFrame(logs_paned, text="Microphone 2 - System Logs")
        logs_paned.add(mic2_log_frame, weight=1)
        self.mic2_log_text = tk.Text(mic2_log_frame, height=20, wrap=tk.WORD)
        mic2_log_scroll = tk.Scrollbar(
            mic2_log_frame, orient=tk.VERTICAL, command=self.mic2_log_text.yview
        )
        self.mic2_log_text.configure(yscrollcommand=mic2_log_scroll.set)
        self.mic2_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mic2_log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def create_recording_controls(self):
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=10, padx=20)
        self.recording_status_label = tk.Label(
            controls_frame, text="Ready to record", font=("Arial", 10), fg="blue"
        )
        self.recording_status_label.pack(pady=5)
        buttons_frame = tk.Frame(controls_frame)
        buttons_frame.pack()
        self.start_btn = create_button(
            buttons_frame,
            text=t("start_button", "🎤 Start"),
            command=self.start_recording_button_clicked,
            kind="primary",
            size="lg",
            state=tk.NORMAL,
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.pause_btn = create_button(
            buttons_frame,
            text=t("pause_button", "⏸️ Pause"),
            command=self.pause_recording_button_clicked,
            kind="warning",
            size="lg",
            state=tk.DISABLED,
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = create_button(
            buttons_frame,
            text=t("stop_button", "🎤 Stop"),
            command=self.stop_recording_button_clicked,
            kind="danger",
            size="lg",
            state=tk.DISABLED,
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

    def create_transcripts_tab(self):
        transcripts_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            transcripts_frame, text=t("tab_transcripts", "📄 Transcripts Only")
        )
        transcripts_paned = ttk.PanedWindow(transcripts_frame, orient=tk.HORIZONTAL)
        transcripts_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

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
        transcript_files_frame = ttk.Frame(self.notebook)
        self.notebook.add(
            transcript_files_frame,
            text=t("tab_transcript_files", "📁 Transcript Files"),
        )
        main_container = tk.Frame(transcript_files_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        transcript_section = ttk.LabelFrame(
            main_container,
            text=t("tab_transcript_files", "📄 Transcript Files"),
            padding=10,
        )
        transcript_section.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        transcript_list_frame = tk.Frame(transcript_section)
        transcript_list_frame.pack(fill=tk.BOTH, expand=True)
        self.transcript_files_listbox = tk.Listbox(
            transcript_list_frame, selectmode=tk.SINGLE
        )
        transcript_scrollbar = tk.Scrollbar(
            transcript_list_frame,
            orient=tk.VERTICAL,
            command=self.transcript_files_listbox.yview,
        )
        self.transcript_files_listbox.configure(yscrollcommand=transcript_scrollbar.set)
        self.transcript_files_listbox.bind(
            "<Double-Button-1>", self.open_selected_transcript_file
        )
        self.transcript_files_listbox.bind(
            "<<ListboxSelect>>", self.on_transcript_file_select
        )

        self.transcript_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        transcript_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        transcript_buttons_frame = tk.Frame(transcript_section)
        transcript_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        refresh_transcript_btn = create_button(
            transcript_buttons_frame,
            text=t("button_refresh", "🔄 Refresh"),
            command=self.refresh_transcript_files_list,
            kind="info",
            size="sm",
        )
        refresh_transcript_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.transcript_file_ops_frame = tk.Frame(transcript_buttons_frame)
        self.transcript_file_ops_frame.pack(side=tk.LEFT, padx=(10, 0))
        self.open_transcript_btn = create_button(
            self.transcript_file_ops_frame,
            text=t("button_open", "📖 Open"),
            command=self.open_selected_transcript_file,
            kind="success",
            size="sm",
            state="disabled",
        )
        self.open_transcript_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.save_transcript_as_btn = create_button(
            self.transcript_file_ops_frame,
            text=t("button_save_as", "💾 Save As"),
            command=self.save_transcript_as,
            kind="warning",
            size="sm",
            state="disabled",
        )
        self.save_transcript_as_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.regenerate_ata_btn = create_button(
            self.transcript_file_ops_frame,
            text=t("button_regenerate_ata", "🤖 Regenerate ATA"),
            command=self.regenerate_ata_from_selected,
            kind="primary",
            size="sm",
            state="disabled",
        )
        self.regenerate_ata_btn.pack(side=tk.LEFT, padx=(0, 5))

        open_transcript_folder_btn = create_button(
            transcript_buttons_frame,
            text=t("button_open_folder", "📁 Open Folder"),
            command=self.open_transcript_folder,
            kind="secondary",
            size="sm",
        )
        open_transcript_folder_btn.pack(side=tk.RIGHT)

        self.refresh_transcript_files_list()

    def create_ata_files_tab(self):
        ata_files_frame = ttk.Frame(self.notebook)
        self.notebook.add(ata_files_frame, text=t("tab_ata_files", "📝 ATA Files"))
        main_container = tk.Frame(ata_files_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        ata_section = ttk.LabelFrame(
            main_container, text="📊 Meeting Minutes (ATA) Files", padding=10
        )
        ata_section.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
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

        ata_buttons_frame = tk.Frame(ata_section)
        ata_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        refresh_ata_btn = create_button(
            ata_buttons_frame,
            text=t("button_refresh", "🔄 Refresh"),
            command=self.refresh_ata_files_list,
            kind="info",
            size="sm",
        )
        refresh_ata_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.ata_file_ops_frame = tk.Frame(ata_buttons_frame)
        self.ata_file_ops_frame.pack(side=tk.LEFT, padx=(10, 0))
        self.open_ata_btn = create_button(
            self.ata_file_ops_frame,
            text=t("button_open", "📖 Open"),
            command=self.open_selected_ata_file,
            kind="success",
            size="sm",
            state="disabled",
        )
        self.open_ata_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.save_ata_as_btn = create_button(
            self.ata_file_ops_frame,
            text=t("button_save_as", "💾 Save As"),
            command=self.save_ata_as,
            kind="warning",
            size="sm",
            state="disabled",
        )
        self.save_ata_as_btn.pack(side=tk.LEFT, padx=(0, 5))

        open_ata_folder_btn = create_button(
            ata_buttons_frame,
            text=t("button_open_folder", "📁 Open Folder"),
            command=self.open_ata_folder,
            kind="secondary",
            size="sm",
        )
        open_ata_folder_btn.pack(side=tk.RIGHT)

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
            anchor="w",
        )
        self.ata_info_label.pack(fill=tk.X, pady=5)
        self.refresh_ata_files_list()

    def setup_output_mapping(self):
        self.output_widgets = {
            "mic1_log": self.mic1_log_text,
            "mic2_log": self.mic2_log_text,
            "mic1_transcript": self.mic1_transcript_text,
            "mic2_transcript": self.mic2_transcript_text,
        }

    def get_output_widgets_for_device(self, device_index, selected_indices):
        mic_position = "mic1" if device_index == selected_indices[0] else "mic2"
        return {
            "log": self.output_widgets[f"{mic_position}_log"],
            "transcript": self.output_widgets[f"{mic_position}_transcript"],
        }
