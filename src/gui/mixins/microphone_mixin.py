import tkinter as tk
from tkinter import ttk
from src.i18n import t
from ..theme import create_select, create_button
from src.audio import get_microphone_list, is_microphone_active


class MicrophoneTabMixin:
    """Microphone configuration tab and helpers."""

    def _format_mic_option(self, idx, name):
        return f"{idx} | {name}"

    def _parse_mic_option(self, value):
        try:
            idx_str = value.split("|", 1)[0].strip()
            return int(idx_str)
        except Exception:
            return None

    def refresh_microphone_list(self):
        try:
            devices = get_microphone_list()
            self._mic_devices = devices
            options = [self._format_mic_option(i, n) for i, n in devices]
            self.mic1_combo["values"] = options
            self.mic2_combo["values"] = options
            self.mic_status_label.config(
                text=(
                    f"{len(devices)} microphone(s) found"
                    if devices
                    else "No microphones found"
                ),
                fg=("green" if devices else "red"),
            )
        except Exception as e:
            self.mic_status_label.config(text=f"Error: {e}", fg="red")

    def load_microphone_selection_into_ui(self):
        mconf = self.config.get("microphones", {})
        mic1 = mconf.get("mic1")
        mic2 = mconf.get("mic2")

        def set_combo_from_index(combo, idx):
            if idx is None:
                return
            for i, n in self._mic_devices:
                if i == idx:
                    combo.set(self._format_mic_option(i, n))
                    break

        set_combo_from_index(self.mic1_combo, mic1)
        set_combo_from_index(self.mic2_combo, mic2)

    def save_microphone_selection(self):
        from tkinter import messagebox

        mic1_idx = self._parse_mic_option(self.mic1_var.get())
        mic2_idx = self._parse_mic_option(self.mic2_var.get())

        if mic1_idx is not None and mic2_idx is not None and mic1_idx == mic2_idx:
            from src.i18n import t

            messagebox.showwarning(
                t("mic_warning_title", "Microphone Selection"),
                t("mic_warning_same", "Please choose two different microphones."),
            )
            return

        self.config.setdefault("microphones", {})
        self.config["microphones"]["mic1"] = mic1_idx
        self.config["microphones"]["mic2"] = mic2_idx
        self.save_main_config()
        try:
            self.status_var.set("Microphone selection saved")
        except Exception:
            pass

    def test_selected_microphones(self):
        results = []
        for label, val in (
            ("Mic1", self.mic1_var.get()),
            ("Mic2", self.mic2_var.get()),
        ):
            idx = self._parse_mic_option(val)
            if idx is None:
                results.append(f"{label}: not selected")
            else:
                try:
                    active = is_microphone_active(idx)
                    results.append(
                        f"{label}: {'OK' if active else 'No input'} (#{idx})"
                    )
                except Exception as e:
                    results.append(f"{label}: error ({e})")
        self.mic_status_label.config(text=" | ".join(results), fg="blue")

    def create_mic_config_tab(self):

        frame = ttk.Frame(self.notebook)
        self.notebook.add(
            frame, text=t("tab_mic_config", "🎤 Microphone Configuration")
        )

        container = ttk.LabelFrame(
            frame, text=t("mic_config_title", "🎤 Select input microphones"), padding=10
        )
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._mic_devices = []
        self.mic1_var = tk.StringVar()
        self.mic2_var = tk.StringVar()

        refresh_btn = ttk.Button(
            container,
            text=t("button_refresh", "🔄 Refresh"),
            command=self.refresh_microphone_list,
        )
        refresh_btn.grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.mic_status_label = tk.Label(container, text="", fg="gray")
        self.mic_status_label.grid(row=0, column=1, columnspan=2, sticky="w")

        tk.Label(container, text=t("mic1_label", "Microphone 1")).grid(
            row=1, column=0, sticky="w"
        )
        self.mic1_combo = create_select(
            container, variable=self.mic1_var, values=[], state="readonly", width=55
        )
        self.mic1_combo.grid(row=1, column=1, columnspan=2, sticky="we", padx=5, pady=2)

        tk.Label(container, text=t("mic2_label", "Microphone 2")).grid(
            row=2, column=0, sticky="w"
        )
        self.mic2_combo = create_select(
            container, variable=self.mic2_var, values=[], state="readonly", width=55
        )
        self.mic2_combo.grid(row=2, column=1, columnspan=2, sticky="we", padx=5, pady=2)

        actions = tk.Frame(container)
        actions.grid(row=3, column=0, columnspan=3, sticky="w", pady=(8, 0))
        save_btn = create_button(
            actions,
            text=t("button_save", "💾 Save"),
            command=self.save_microphone_selection,
        )
        save_btn.pack(side=tk.LEFT)
        test_btn = create_button(
            actions,
            text=t("button_test", "🧪 Test"),
            command=self.test_selected_microphones,
        )
        test_btn.pack(side=tk.LEFT, padx=6)

        self.mic_info_label = tk.Label(
            container,
            text=t(
                "mic_info_help",
                "Pick up to two different input devices. Use Refresh if a new device was plugged in.",
            ),
            fg="gray",
            justify=tk.LEFT,
            anchor="w",
        )
        self.mic_info_label.grid(
            row=4, column=0, columnspan=3, sticky="we", pady=(10, 0)
        )

        for i in range(3):
            container.grid_columnconfigure(i, weight=1)

        self.refresh_microphone_list()
        self.load_microphone_selection_into_ui()
