#!/usr/bin/env python3
"""
Script to fix the GUI file by adding language selection and translations
"""

import re


def fix_gui_file():
    # Read the original file
    with open("src/gui.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Fix the tab text for transcript files
    old_tab_text = 'text="� Transcript Files"'
    new_tab_text = 'text=t("tab_transcript_files", "📁 Transcript Files")'
    content = content.replace(old_tab_text, new_tab_text)

    # Fix the label frame text
    old_label_text = 'text="📄    "'
    new_label_text = 'text=t("tab_transcript_files", "📄 Transcript Files")'
    content = content.replace(old_label_text, new_label_text)

    # Add language selection UI after main_container
    main_container_line = (
        "main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)"
    )

    language_selection_code = """
        # Language selection section
        language_frame = tk.Frame(main_container)
        language_frame.pack(fill=tk.X, pady=(0, 10))

        language_label = tk.Label(
            language_frame, 
            text=t("menu_language", "🌐 Language:"), 
            font=("Arial", 10, "bold")
        )
        language_label.pack(side=tk.LEFT, padx=(0, 10))

        # Language selection dropdown
        self.language_var = tk.StringVar(value=self.config.get("language", "pt-BR"))
        language_combo = ttk.Combobox(
            language_frame,
            textvariable=self.language_var,
            values=list(self.translation_manager.get_available_languages().keys()),
            state="readonly",
            width=15
        )
        language_combo.pack(side=tk.LEFT, padx=(0, 10))
        language_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        # Current language display
        self.current_lang_label = tk.Label(
            language_frame,
            text=self.translation_manager.get_language_name(self.config.get("language", "pt-BR")),
            font=("Arial", 10),
            fg="blue"
        )
        self.current_lang_label.pack(side=tk.LEFT)
"""

    content = content.replace(
        main_container_line, main_container_line + language_selection_code
    )

    # Update button texts with translations
    button_replacements = [
        ('text="🔄 Refresh"', 'text=t("button_refresh", "🔄 Refresh")'),
        ('text="📖 Open"', 'text=t("button_open", "📖 Open")'),
        ('text="💾 Save As"', 'text=t("button_save_as", "💾 Save As")'),
        (
            'text="🤖 Regenerate ATA"',
            'text=t("button_regenerate_ata", "🤖 Regenerate ATA")',
        ),
        ('text="📁 Open Folder"', 'text=t("button_open_folder", "📁 Open Folder")'),
    ]

    for old, new in button_replacements:
        content = content.replace(old, new)

    # Also handle the save as button which has a problematic character
    content = content.replace(
        'text="💾 Save As"', 'text=t("button_save_as", "💾 Save As")'
    )

    # Write the updated content back
    with open("src/gui.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("Successfully updated gui.py with language selection and translations")


if __name__ == "__main__":
    fix_gui_file()
