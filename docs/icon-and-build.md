# App icon and Windows build

This app ships a Windows .ico and displays it in two places:

- The compiled EXE icon: configured via PyInstaller `--icon icon.ico` (and in `MicrophoneTranscriber.spec`).
- The window/taskbar icon at runtime: set by the GUI using `root.iconbitmap("icon.ico")`, with a PyInstaller-aware path.

Notes

- The build script `build_windows.bat` installs PyInstaller if needed and builds a one-file, windowed EXE.
- The icon file is also added to the PyInstaller bundle as runtime data via `--add-data "icon.ico;."` to ensure the GUI can load it when packaged.

How to build

- Double-click `build_windows.bat`, or run it from a terminal in the repo root.
- The artifact `MicrophoneTranscriber.exe` is copied to the project root for convenience.

How to run

- Double-click `run_windows.bat`, or launch `MicrophoneTranscriber.exe` directly.
