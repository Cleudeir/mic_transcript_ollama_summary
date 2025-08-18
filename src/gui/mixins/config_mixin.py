import json
import os


class ConfigMixin:
    """Configuration load/save helpers and simple migrations."""

    config_file: str

    def load_main_config(self) -> dict:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        # defaults
        return {
            "language": "pt-BR",
            "auto_generate_ata": True,
            "ollama": {},
        }

    def ensure_config_file_exists(self):
        if not os.path.exists(self.config_file):
            self.save_main_config()

    def save_main_config(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            try:
                self.status_var.set(f"Error saving config: {e}")
            except Exception:
                pass

    def migrate_old_mic_config(self):
        """Migrate legacy mic_config.json into the unified config.json if present."""
        legacy = "mic_config.json"
        try:
            if os.path.exists(legacy):
                with open(legacy, "r", encoding="utf-8") as f:
                    legacy_conf = json.load(f)
                if legacy_conf:
                    self.config.setdefault("microphones", legacy_conf)
                    self.save_main_config()
                # Do not delete legacy automatically
        except Exception:
            pass

    def reset_application(self):
        from tkinter import messagebox

        if messagebox.askyesno(
            "Reset", "Reset application state? This will clear some settings."
        ):
            self.config = self.load_main_config()
            self.save_main_config()
            try:
                self.status_var.set("Application reset.")
            except Exception:
                pass
