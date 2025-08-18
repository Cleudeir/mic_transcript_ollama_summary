"""
Theme and root factory for the GUI.

It uses ttkbootstrap if available for a more modern look-and-feel,
falling back to standard Tk/ttk styles when not installed.
"""

from __future__ import annotations

try:
    import ttkbootstrap as ttkb  # type: ignore
    from ttkbootstrap.constants import PRIMARY

    _HAS_TTKB = True
except Exception:
    _HAS_TTKB = False

import tkinter as tk
from tkinter import ttk
import os
import sys

# --- Unified Button Component -------------------------------------------------

_KIND_TO_BOOTSTYLE = {
    "primary": "primary",
    "success": "success",
    "warning": "warning",
    "danger": "danger",
    "info": "info",
    "secondary": "secondary",
    "neutral": "secondary",
}

_KIND_TO_COLORS = {
    "primary": {"bg": "#4CAF50", "fg": "white", "active": "#43A047"},
    "success": {"bg": "#2e7d32", "fg": "white", "active": "#1b5e20"},
    "warning": {"bg": "#FF9800", "fg": "white", "active": "#FB8C00"},
    "danger": {"bg": "#F44336", "fg": "white", "active": "#E53935"},
    "info": {"bg": "#2196F3", "fg": "white", "active": "#1E88E5"},
    "secondary": {"bg": "#e0e0e0", "fg": "#212121", "active": "#d5d5d5"},
    "neutral": {"bg": "#e0e0e0", "fg": "#212121", "active": "#d5d5d5"},
}

_SIZE_TO_PAD = {"sm": (10, 6), "md": (16, 10), "lg": (22, 14)}


def create_button(
    parent: tk.Misc,
    text: str,
    command=None,
    *,
    kind: str = "primary",
    size: str = "md",
    state: str | None = None,
):
    """
    Create a consistently styled button.

    When ttkbootstrap is available, a ttkbootstrap Button with bootstyle is used.
    Otherwise, a Tk Button is created with color styling.
    """
    kind = kind if kind in _KIND_TO_COLORS else "neutral"
    pad_x, pad_y = _SIZE_TO_PAD.get(size, _SIZE_TO_PAD["md"])

    if _HAS_TTKB:
        try:
            import ttkbootstrap as ttkb  # type: ignore

            boot = _KIND_TO_BOOTSTYLE.get(kind, "secondary")
            btn = ttkb.Button(parent, text=text, command=command, bootstyle=boot)
            btn.configure(padding=(pad_x, pad_y))
            if state:
                btn.configure(state=state)
            return btn
        except Exception:
            # Fallback to standard TK if bootstrap fails at runtime
            pass

    colors = _KIND_TO_COLORS[kind]
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=colors["bg"],
        fg=colors["fg"],
        activebackground=colors["active"],
        padx=pad_x,
        pady=pad_y,
        font=(
            "Arial",
            12,
            "bold" if kind in {"primary", "danger", "warning", "success"} else "normal",
        ),
        relief="raised",
        bd=1,
    )
    if state:
        try:
            btn.configure(state=state)
        except Exception:
            pass
    return btn


# --- Unified Select (Combobox) Component --------------------------------------


def create_select(
    parent: tk.Misc,
    variable: tk.StringVar | None = None,
    *,
    values: list[str] | tuple[str, ...] | None = None,
    state: str = "readonly",
    width: int | None = None,
    on_change=None,
):
    """
    Create a consistently styled select (combobox).

    Uses ttkbootstrap's Combobox when available; otherwise falls back to ttk.Combobox.
    """
    values = values or []
    if _HAS_TTKB:
        try:
            import ttkbootstrap as ttkb  # type: ignore

            cb = ttkb.Combobox(
                parent, textvariable=variable, values=values, state=state
            )
            if width is not None:
                cb.configure(width=width)
            if on_change is not None:
                cb.bind("<<ComboboxSelected>>", on_change)
            return cb
        except Exception:
            pass

    # Create or reuse a centered combobox style to vertically center the arrow
    try:
        style = ttk.Style()
        style.configure(
            "Centered.TCombobox",
            padding=(8, 6, 28, 6),  # left, top, right (space for arrow), bottom
            arrowsize=14,
        )
        style.map("Centered.TCombobox", focuscolor=[("focus", "")])
        combobox_style = "Centered.TCombobox"
    except Exception:
        combobox_style = "TCombobox"

    cb = ttk.Combobox(
        parent, textvariable=variable, values=values, state=state, style=combobox_style
    )
    if width is not None:
        cb.configure(width=width)
    if on_change is not None:
        cb.bind("<<ComboboxSelected>>", on_change)
    return cb


def create_root(
    title: str = "Meeting Audio Transcriber", size: str = "1000x700"
) -> tk.Tk:
    """
    Create the Tk root window with a modern theme if possible.

    Returns a tk.Tk (ttkbootstrap Window is a subclass, still works the same for callers).
    """
    if _HAS_TTKB:
        root = ttkb.Window(themename="flatly")  # a clean modern Bootstrap theme
    else:
        root = tk.Tk()
        try:
            style = ttk.Style()
            # Prefer a dark/modern theme if present on the system
            preferred = [
                "vista",  # Windows
                "clam",  # Cross-platform
                "alt",
                "default",
            ]
            for name in preferred:
                if name in style.theme_names():
                    style.theme_use(name)
                    break
        except Exception:
            pass

    try:
        root.title(title)
        root.geometry(size)
    except Exception:
        pass

    # Try to set a window icon from icon.ico (works in dev and PyInstaller bundle)
    try:

        def _resource_path(rel: str) -> str:
            try:
                base_path = getattr(sys, "_MEIPASS")  # type: ignore[attr-defined]
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, rel)

        icon_path = _resource_path("icon.ico")
        if os.path.exists(icon_path):
            # iconbitmap expects .ico on Windows; this call is safe to ignore on other OSes
            root.iconbitmap(icon_path)
    except Exception:
        # Non-fatal if icon can't be set
        pass
    return root


def style_primary_button(widget: tk.Widget):
    """Apply a primary style if ttkbootstrap is available; no-op otherwise."""
    if _HAS_TTKB:
        try:
            widget.configure(bootstyle=PRIMARY)
        except Exception:
            pass
