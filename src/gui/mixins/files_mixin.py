import os
from tkinter import filedialog, messagebox
import tkinter as tk


class FilesMixin:
    """Transcript and ATA file listings and basic operations."""

    def _get_src_base_dir(self) -> str:
        import os

        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    def _get_transcript_dir(self) -> str:
        # Save transcripts under the user's Documents folder by default.
        # Prefer localized 'Documentos' then 'Documents', fallback to home.
        user_home = os.path.expanduser("~")
        candidates = [
            os.path.join(user_home, "Documentos"),
            os.path.join(user_home, "Documents"),
        ]
        user_docs = next((p for p in candidates if os.path.isdir(p)), user_home)
        return os.path.join(user_docs, "meet_audio", "transcript")

    def _get_ata_dir(self) -> str:
        # Save ATA (meeting minutes) under the user's Documents folder by default.
        user_home = os.path.expanduser("~")
        candidates = [
            os.path.join(user_home, "Documentos"),
            os.path.join(user_home, "Documents"),
        ]
        user_docs = next((p for p in candidates if os.path.isdir(p)), user_home)
        return os.path.join(user_docs, "meet_audio", "ata")

    # Transcript files tab helpers
    def refresh_transcript_files_list(self):
        if not hasattr(self, "transcript_files_listbox"):
            return
        self.transcript_files_listbox.delete(0, tk.END)
        path = self._get_transcript_dir()
        try:
            files = [f for f in os.listdir(path) if f.lower().endswith(".md")]
            files.sort(reverse=True)
            for f in files:
                self.transcript_files_listbox.insert(tk.END, f)
        except Exception:
            pass
        if hasattr(self, "open_transcript_btn"):
            self.open_transcript_btn.config(state="disabled")
        if hasattr(self, "save_transcript_as_btn"):
            self.save_transcript_as_btn.config(state="disabled")
        if hasattr(self, "regenerate_ata_btn"):
            self.regenerate_ata_btn.config(state="disabled")

    def on_transcript_file_select(self, event=None):
        if not hasattr(self, "transcript_files_listbox"):
            return
        selection = self.transcript_files_listbox.curselection()
        enabled = bool(selection)
        if hasattr(self, "open_transcript_btn"):
            self.open_transcript_btn.config(state=("normal" if enabled else "disabled"))
        if hasattr(self, "save_transcript_as_btn"):
            self.save_transcript_as_btn.config(
                state=("normal" if enabled else "disabled")
            )
        if hasattr(self, "regenerate_ata_btn"):
            self.regenerate_ata_btn.config(state=("normal" if enabled else "disabled"))

    def _get_selected_listbox_item(self, listbox: tk.Listbox) -> str | None:
        sel = listbox.curselection()
        if not sel:
            return None
        return listbox.get(sel[0])

    def open_selected_transcript_file(self, event=None):
        name = self._get_selected_listbox_item(self.transcript_files_listbox)
        if not name:
            return
        path = os.path.join(self._get_transcript_dir(), name)
        if os.path.exists(path):
            # Open an internal editable document window so users can save changes
            try:
                self._open_document_window(path, title=name)
            except Exception:
                # Fall back to opening with the OS if internal editor fails
                os.startfile(path)

    def save_transcript_as(self):
        name = self._get_selected_listbox_item(self.transcript_files_listbox)
        if not name:
            return
        src_path = os.path.join(self._get_transcript_dir(), name)
        if not os.path.exists(src_path):
            return
        # Prefer localized Documents folder (Portuguese 'Documentos') then 'Documents', else home
        user_home = os.path.expanduser("~")
        candidates = [
            os.path.join(user_home, "Documentos"),
            os.path.join(user_home, "Documents"),
        ]
        user_docs = next((p for p in candidates if os.path.isdir(p)), user_home)

        dest = filedialog.asksaveasfilename(
            defaultextension=".md",
            initialdir=user_docs,
            initialfile=name,
            filetypes=[("Markdown", "*.md"), ("All Files", "*.*")],
        )
        if dest:
            import shutil

            try:
                shutil.copy2(src_path, dest)
                self.status_var.set(f"Saved to {dest}")
            except Exception as e:
                messagebox.showerror("Save As", f"Failed to save: {e}")

    def regenerate_ata_from_selected(self):
        name = self._get_selected_listbox_item(self.transcript_files_listbox)
        if not name:
            return
        try:
            transcript_path = os.path.join(self._get_transcript_dir(), name)
            if not os.path.exists(transcript_path):
                messagebox.showerror("ATA", f"Transcript not found: {transcript_path}")
                return
            self._start_ata_generation(transcript_path, open_after=True)
        except Exception as e:
            try:
                self.status_var.set(f"ATA regeneration error: {e}")
            except Exception:
                pass

    # ATA files tab helpers
    def refresh_ata_files_list(self):
        if not hasattr(self, "ata_files_listbox"):
            return
        self.ata_files_listbox.delete(0, tk.END)
        path = self._get_ata_dir()
        try:
            files = [f for f in os.listdir(path) if f.lower().endswith(".md")]
            files.sort(reverse=True)
            for f in files:
                self.ata_files_listbox.insert(tk.END, f)
        except Exception:
            pass
        if hasattr(self, "open_ata_btn"):
            self.open_ata_btn.config(state="disabled")
        if hasattr(self, "save_ata_as_btn"):
            self.save_ata_as_btn.config(state="disabled")

    def on_ata_file_select(self, event=None):
        selection = self.ata_files_listbox.curselection()
        enabled = bool(selection)
        if hasattr(self, "open_ata_btn"):
            self.open_ata_btn.config(state=("normal" if enabled else "disabled"))
        if hasattr(self, "save_ata_as_btn"):
            self.save_ata_as_btn.config(state=("normal" if enabled else "disabled"))
        if hasattr(self, "ata_info_label"):
            name = self._get_selected_listbox_item(self.ata_files_listbox)
            if name:
                path = os.path.join(self._get_ata_dir(), name)
                try:
                    size = os.path.getsize(path)
                    self.ata_info_label.config(text=f"{name} - {size} bytes")
                except Exception:
                    self.ata_info_label.config(text=name)

    def open_selected_ata_file(self, event=None):
        name = self._get_selected_listbox_item(self.ata_files_listbox)
        if not name:
            return
        path = os.path.join(self._get_ata_dir(), name)
        if os.path.exists(path):
            try:
                self._open_document_window(path, title=name)
            except Exception:
                os.startfile(path)

    def _open_document_window(self, file_path: str, title: str | None = None):
        """Open a simple editable document window for markdown files with Save and Save As."""
        if not hasattr(self, "root"):
            raise RuntimeError("No application root available")

        win = tk.Toplevel(self.root)
        win.title(title or os.path.basename(file_path))
        win.geometry("800x600")

        # Text area with scrollbar
        text_frame = tk.Frame(win)
        text_frame.pack(fill=tk.BOTH, expand=True)
        txt = tk.Text(text_frame, wrap=tk.WORD)
        scr = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=txt.yview)
        txt.configure(yscrollcommand=scr.set)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scr.pack(side=tk.RIGHT, fill=tk.Y)

        # Load file content
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            from tkinter import messagebox

            messagebox.showerror("Open", f"Failed to open file: {e}")
            win.destroy()
            return

        txt.insert("1.0", content)
        original_content = content

        # Status label
        status = tk.Label(win, text="", anchor="w")
        status.pack(fill=tk.X, padx=6, pady=(0, 6))

        def _set_status(msg: str):
            try:
                status.config(text=msg)
                if hasattr(self, "status_var"):
                    self.status_var.set(msg)
            except Exception:
                pass

        def save_to(path: str):
            try:
                data = txt.get("1.0", tk.END)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(data)
                _set_status(f"Saved to {path}")
                return True
            except Exception as e:
                from tkinter import messagebox

                messagebox.showerror("Save", f"Failed to save file: {e}")
                return False

        def on_save():
            if save_to(file_path):
                nonlocal original_content
                original_content = txt.get("1.0", tk.END)

        def on_save_as():
            user_home = os.path.expanduser("~")
            candidates = [
                os.path.join(user_home, "Documentos"),
                os.path.join(user_home, "Documents"),
            ]
            user_docs = next((p for p in candidates if os.path.isdir(p)), user_home)

            dest = filedialog.asksaveasfilename(
                defaultextension=".md",
                initialdir=user_docs,
                initialfile=os.path.basename(file_path),
                filetypes=[("Markdown", "*.md"), ("All Files", "*.*")],
            )
            if dest:
                if save_to(dest):
                    win.title(os.path.basename(dest))

        # Buttons
        btn_frame = tk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=6, pady=6)
        save_btn = tk.Button(btn_frame, text="Save", command=on_save)
        save_btn.pack(side=tk.LEFT)
        save_as_btn = tk.Button(btn_frame, text="Save As", command=on_save_as)
        save_as_btn.pack(side=tk.LEFT, padx=(6, 0))
        close_btn = tk.Button(btn_frame, text="Close", command=win.destroy)
        close_btn.pack(side=tk.RIGHT)

        # Prompt on close if modified
        def on_close():
            current = txt.get("1.0", tk.END)
            if current != original_content:
                if messagebox.askyesno(
                    "Save", "You changed the document. Save before closing?"
                ):
                    if not save_to(file_path):
                        return
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

        # Key bindings
        def _on_ctrl_s(event=None):
            on_save()
            return "break"

        txt.bind("<Control-s>", _on_ctrl_s)
        txt.focus_set()

    def save_ata_as(self):
        name = self._get_selected_listbox_item(self.ata_files_listbox)
        if not name:
            return
        src_path = os.path.join(self._get_ata_dir(), name)
        if not os.path.exists(src_path):
            return
        # Prefer localized Documents folder (Portuguese 'Documentos') then 'Documents', else home
        user_home = os.path.expanduser("~")
        candidates = [
            os.path.join(user_home, "Documentos"),
            os.path.join(user_home, "Documents"),
        ]
        user_docs = next((p for p in candidates if os.path.isdir(p)), user_home)

        dest = filedialog.asksaveasfilename(
            defaultextension=".md",
            initialdir=user_docs,
            initialfile=name,
            filetypes=[("Markdown", "*.md"), ("All Files", "*.*")],
        )
        if dest:
            import shutil

            try:
                shutil.copy2(src_path, dest)
                self.status_var.set(f"Saved to {dest}")
            except Exception as e:
                messagebox.showerror("Save As", f"Failed to save: {e}")

    # Folder open helpers
    def open_transcript_folder(self):
        path = self._get_transcript_dir()
        if os.path.isdir(path):
            os.startfile(path)
        else:
            messagebox.showwarning("Folder", f"Folder not found: {path}")

    def view_all_transcripts(self):
        self.open_transcript_folder()

    def open_ata_folder(self):
        path = self._get_ata_dir()
        if os.path.isdir(path):
            os.startfile(path)
        else:
            messagebox.showwarning("Folder", f"Folder not found: {path}")

    def view_all_atas(self):
        self.open_ata_folder()
