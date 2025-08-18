"""
Legacy shim for the GUI module.

This file used to contain the entire Tkinter GUI. It now delegates to the
modular implementation in the package directory `src/gui/`.

Prefer importing from `src.gui` (the package) going forward:
    from src.gui import MicrophoneTranscriberGUI, create_gui, run_gui
"""

from .gui.app import MicrophoneTranscriberGUI, create_gui, run_gui  # type: ignore

__all__ = [
    "MicrophoneTranscriberGUI",
    "create_gui",
    "run_gui",
]
