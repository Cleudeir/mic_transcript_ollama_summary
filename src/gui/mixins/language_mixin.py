from tkinter import ttk, messagebox
import tkinter as tk
from src.i18n import get_translation_manager, set_global_language, t


class LanguageMixin:
    def create_language_settings_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=t("menu_language", "🌐 Language Settings"))

        lbl = tk.Label(
            frame,
            text=t(
                "language_description",
                "Select your preferred language for the application interface",
            ),
        )
        lbl.pack(padx=10, pady=(10, 5), anchor="w")

        current_lang = tk.StringVar(value=self.config.get("language", "pt-BR"))
        lang_combo = self._create_select(
            frame,
            variable=current_lang,
            values=list(get_translation_manager().get_available_languages().keys()),
            state="readonly",
        )
        lang_combo.pack(padx=10, pady=5, anchor="w")

        def apply_lang():
            lang = current_lang.get()
            set_global_language(lang)
            self.config["language"] = lang
            self.save_main_config()
            messagebox.showinfo(
                t("language_settings_title", "Language Settings"),
                t(
                    "language_changed",
                    "Language changed successfully! Please restart the application to see changes.",
                ),
            )

        ttk.Button(
            frame, text=t("button_apply", "✅ Apply Changes"), command=apply_lang
        ).pack(padx=10, pady=(5, 10), anchor="w")

    # Adapter so we can reuse theme.create_select without import cycle here
    def _create_select(self, parent, variable, values, state="readonly"):
        from ..theme import create_select

        return create_select(parent, variable=variable, values=values, state=state)
