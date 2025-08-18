from tkinter import messagebox
from src.i18n import t


class MenuActionsMixin:
    def open_language_settings(self):
        try:
            idx = [self.notebook.tab(i, "text") for i in self.notebook.tabs()].index(
                t("menu_language", "🌐 Language Settings")
            )
            self.notebook.select(idx)
        except Exception:
            pass

    def open_audio_settings(self):
        # Focus microphone tab if present
        try:
            for i in range(self.notebook.index("end")):
                if "Microphone" in self.notebook.tab(i, "text"):
                    self.notebook.select(i)
                    break
        except Exception:
            messagebox.showinfo(
                "Audio Settings", "Audio settings dialog not yet implemented."
            )

    def toggle_auto_ata_generation(self):
        self.auto_generate_ata = not getattr(self, "auto_generate_ata", True)
        self.config["auto_generate_ata"] = self.auto_generate_ata
        self.save_main_config()
        try:
            self.status_var.set(
                f"Auto-generate ATA: {'ON' if self.auto_generate_ata else 'OFF'}"
            )
        except Exception:
            pass

    def toggle_performance_monitor(self):
        messagebox.showinfo(
            "Performance Monitor", "Performance monitor not yet implemented."
        )

    def generate_meeting_minutes_dialog(self):
        messagebox.showinfo(
            "Generate Minutes", "This feature is not yet implemented in the refactor."
        )

    def show_user_guide(self):
        messagebox.showinfo("User Guide", "See docs/ for usage instructions.")

    def show_troubleshooting(self):
        messagebox.showinfo(
            "Troubleshooting",
            "If microphones are not listed, click Refresh. If transcription does not start, ensure two different microphones are selected in the Microphone Configuration tab.",
        )

    def show_about(self):
        messagebox.showinfo(
            "About", "Meeting Audio Transcriber\nRefactored GUI package."
        )
