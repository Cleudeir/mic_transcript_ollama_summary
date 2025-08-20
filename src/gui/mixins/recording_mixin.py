import datetime
import os
import threading
import tkinter as tk

from src.i18n import t


class RecordingMixin:
    """Recording controls, real-time file writing and ATA generation."""

    def start_recording_button_clicked(self):
        """Start continuous recording and transcription threads for selected mics."""
        if self.is_recording:
            return

        # Determine selected microphones
        mic1_idx = (
            self._parse_mic_option(self.mic1_var.get())
            if hasattr(self, "mic1_var")
            else None
        )
        mic2_idx = (
            self._parse_mic_option(self.mic2_var.get())
            if hasattr(self, "mic2_var")
            else None
        )
        if mic1_idx is None or mic2_idx is None:
            mconf = self.config.get("microphones", {})
            mic1_idx = mconf.get("mic1") if mic1_idx is None else mic1_idx
            mic2_idx = mconf.get("mic2") if mic2_idx is None else mic2_idx

        selected = [i for i in (mic1_idx, mic2_idx) if isinstance(i, int)]
        if not selected:
            from tkinter import messagebox

            messagebox.showwarning(
                t("mic_warning_title", "Microphone Selection"),
                t(
                    "mic_warning_select",
                    "Please select at least one microphone in the Microphone Configuration tab.",
                ),
            )
            return

        # Persist selection
        self.config.setdefault("microphones", {})
        self.config["microphones"]["mic1"] = mic1_idx
        self.config["microphones"]["mic2"] = mic2_idx
        self.save_main_config()

        # Reset runtime state
        self._selected_indices = selected
        self._stop_events = {}
        self._capture_threads = {}

        # Begin transcript file session
        try:
            self._start_transcript_file_session()
        except Exception as e:
            self.status_var.set(f"Transcript file init error: {e}")

        # Chunk handler used by capture threads
        def on_audio_chunk(device_index, audio_chunk, samplerate):
            if self.is_paused or not self.is_recording:
                return
            from src.transcription import transcribe_audio_async

            text = transcribe_audio_async(audio_chunk, samplerate)
            if text is None or (isinstance(text, str) and text.strip() == ""):
                return
            try:
                self._append_transcript_line(device_index, text)
            except Exception:
                pass

            def ui_update():
                outs = self.get_output_widgets_for_device(
                    device_index, self._selected_indices
                )
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                try:
                    outs["log"].insert(
                        tk.END,
                        f"[{timestamp}] Device {device_index}: chunk processed\n",
                    )
                    outs["log"].see(tk.END)
                except Exception:
                    pass
                try:
                    outs["transcript"].insert(tk.END, f"[{timestamp}] {text}\n")
                    outs["transcript"].see(tk.END)
                except Exception:
                    pass

            try:
                self.root.after(0, ui_update)
            except Exception:
                ui_update()

        # Start capture threads
        from src.audio import capture_audio_realtime

        for idx in selected:
            stop_evt = threading.Event()
            self._stop_events[idx] = stop_evt
            th = threading.Thread(
                target=capture_audio_realtime,
                args=(idx, on_audio_chunk, stop_evt),
                daemon=True,
                name=f"Capture-{idx}",
            )
            self._capture_threads[idx] = th
            th.start()

        # UI state
        self.is_recording = True
        self.is_paused = False
        self.recording_status_label.config(
            text=t("recording_started", "Recording started"), fg="green"
        )
        if self._transcript_file_path:
            self.status_var.set(
                f"Recording from: {', '.join(map(str, selected))} → Saving to {os.path.basename(self._transcript_file_path)}"
            )
        else:
            self.status_var.set(
                f"Recording from: {', '.join(map(str, selected))} (real-time)"
            )
        self.update_recording_controls_state()

    def pause_recording_button_clicked(self):
        if self.is_recording:
            self.is_paused = not self.is_paused
            self.recording_status_label.config(
                text=(
                    t("resume_button", "▶️ Resume")
                    if self.is_paused
                    else t("pause_button", "⏸️ Pause")
                )
            )
            self.update_recording_controls_state()

    def stop_recording_button_clicked(self):
        try:
            for evt in self._stop_events.values():
                evt.set()
        except Exception:
            pass
        self.is_recording = False
        self.is_paused = False
        self.recording_status_label.config(
            text=t("recording_stopped", "Recording stopped"), fg="red"
        )
        last_path = getattr(self, "_transcript_file_path", None)
        try:
            self._finalize_transcript_session()
        except Exception:
            pass
        self.status_var.set("Recording stopped")
        try:
            self.root.after(250, self.refresh_transcript_files_list)
        except Exception:
            pass
        try:
            if (
                self.config.get("auto_generate_ata", True)
                and last_path
                and os.path.exists(last_path)
            ):
                self._start_ata_generation(last_path)
        except Exception:
            pass
        self.update_recording_controls_state()

    def stop_realtime_recording(self):
        try:
            for evt in self._stop_events.values():
                evt.set()
        except Exception:
            pass
        self.is_recording = False
        try:
            self._finalize_transcript_session()
        except Exception:
            pass

    def update_recording_controls_state(self):
        if (
            hasattr(self, "start_btn")
            and hasattr(self, "pause_btn")
            and hasattr(self, "stop_btn")
        ):
            if self.is_recording:
                self.start_btn.config(state=tk.DISABLED)
                self.pause_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.NORMAL)
                self.pause_btn.config(
                    text=(
                        t("resume_button", "▶️ Resume")
                        if self.is_paused
                        else t("pause_button", "⏸️ Pause")
                    )
                )
            else:
                self.start_btn.config(state=tk.NORMAL)
                self.pause_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.DISABLED)

    def auto_start_recording(self):
        return

    # --- Realtime transcript saving helpers ---
    def _start_transcript_file_session(self):
        try:
            base_dir = self._get_transcript_dir()
        except Exception:
            user_home = os.path.expanduser("~")
            candidates = [
                os.path.join(user_home, "Documentos"),
                os.path.join(user_home, "Documents"),
            ]
            user_docs = next((p for p in candidates if os.path.isdir(p)), user_home)
            base_dir = os.path.join(user_docs, "meet_audio", "transcript")
        os.makedirs(base_dir, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{ts}_transcript.md"
        path = os.path.join(base_dir, fname)
        header_lines = [
            "# Meeting Transcript",
            f"- Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- Devices: {', '.join(map(str, getattr(self, '_selected_indices', []) or []))}",
            "",
        ]
        with self._file_write_lock:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(header_lines))
        self._transcript_file_path = path
        self._last_transcript_file_path = path

    def _append_transcript_line(self, device_index: int, text: str):
        if not self._transcript_file_path:
            self._start_transcript_file_session()
        label = f"Device {device_index}"
        try:
            if self._selected_indices:
                pos = self._selected_indices.index(device_index)
                label = f"Mic{pos + 1}"
        except Exception:
            pass
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        safe_text = (text or "").strip().replace("\r", " ").replace("\n", " ")
        line = f"- [{ts}] [{label}] {safe_text}\n"
        with self._file_write_lock:
            with open(self._transcript_file_path, "a", encoding="utf-8") as f:
                f.write(line)

    def _finalize_transcript_session(self):
        self._transcript_file_path = None

    # --- ATA generation helpers ---
    def _ensure_ata_dir(self) -> str:
        try:
            base = self._get_ata_dir()
        except Exception:
            user_home = os.path.expanduser("~")
            candidates = [
                os.path.join(user_home, "Documentos"),
                os.path.join(user_home, "Documents"),
            ]
            user_docs = next((p for p in candidates if os.path.isdir(p)), user_home)
            base = os.path.join(user_docs, "meet_audio", "ata")
        os.makedirs(base, exist_ok=True)
        return base

    def _derive_ata_path(self, transcript_path: str) -> str:
        ata_dir = self._ensure_ata_dir()
        name = os.path.basename(transcript_path)
        if name.endswith("_transcript.md"):
            name = name.replace("_transcript.md", "_ata.md")
        else:
            stem, _ = os.path.splitext(name)
            name = f"{stem}_ata.md"
        return os.path.join(ata_dir, name)

    def _start_ata_generation(self, transcript_path: str, open_after: bool = True):
        def _worker():
            try:
                ata_path = self._derive_ata_path(transcript_path)
                lang = self.config.get("language", "pt-BR")
                self.status_var.set(
                    f"Generating ATA from {os.path.basename(transcript_path)}..."
                )
                result = self.ollama_service.generate_and_save_minutes(
                    transcript_path, ata_path, language=lang
                )

                def _ui_done():
                    from tkinter import messagebox

                    if result.get("success") and os.path.exists(ata_path):
                        self.status_var.set(
                            f"ATA generated: {os.path.basename(ata_path)}"
                        )
                        try:
                            self.refresh_ata_files_list()
                        except Exception:
                            pass
                        if open_after:
                            try:
                                os.startfile(ata_path)
                            except Exception:
                                messagebox.showinfo("ATA", f"Saved to: {ata_path}")
                    else:
                        msg = result.get("error") or "Failed to generate ATA"
                        messagebox.showerror("ATA", msg)

                try:
                    self.root.after(0, _ui_done)
                except Exception:
                    _ui_done()
            except Exception as e:
                try:
                    self.status_var.set(f"ATA generation error: {e}")
                except Exception:
                    pass

        threading.Thread(target=_worker, daemon=True, name="Generate-ATA").start()
