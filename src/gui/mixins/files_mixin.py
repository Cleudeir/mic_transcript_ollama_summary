import os
from tkinter import filedialog, messagebox
import tkinter as tk


class FilesMixin:
    """Transcript and ATA file listings and basic operations."""

    def _get_src_base_dir(self) -> str:
        import os

        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    def _get_transcript_dir(self) -> str:
        return os.path.join(self._get_src_base_dir(), "output", "transcript")

    def _get_ata_dir(self) -> str:
        return os.path.join(self._get_src_base_dir(), "output", "ata")

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
            os.startfile(path)

    def save_transcript_as(self):
        name = self._get_selected_listbox_item(self.transcript_files_listbox)
        if not name:
            return
        src_path = os.path.join(self._get_transcript_dir(), name)
        if not os.path.exists(src_path):
            return
        dest = filedialog.asksaveasfilename(
            defaultextension=".md",
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
            os.startfile(path)

    def save_ata_as(self):
        name = self._get_selected_listbox_item(self.ata_files_listbox)
        if not name:
            return
        src_path = os.path.join(self._get_ata_dir(), name)
        if not os.path.exists(src_path):
            return
        dest = filedialog.asksaveasfilename(
            defaultextension=".md",
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
