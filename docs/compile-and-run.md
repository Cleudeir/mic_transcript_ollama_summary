# Compile and Run Helper

This repository includes a convenience PowerShell script, `compile_and_run.ps1`, to build the application with PyInstaller and optionally run it.

Files
- `compile_and_run.ps1` — PowerShell helper to build and run the app.

Usage

From the repository root in PowerShell (ensure you have execution policy that allows running local scripts):

- Build and launch the EXE (default):

```powershell
.\compile_and_run.ps1
```

- Build only (do not run):

```powershell
.\compile_and_run.ps1 -NoRun
```

- Build and run main.py via the venv Python (useful to capture console logs):

```powershell
.\compile_and_run.ps1 -RunMode python
```

- Skip installing packages into the venv (if already set up):

```powershell
.\compile_and_run.ps1 -SkipInstall
```

- Clean previous build artifacts before building:

```powershell
.\compile_and_run.ps1 -CleanDist
```

Notes
- The script expects a virtual environment at `.venv` with `python.exe`. If not found, it falls back to system `python`.
- The script installs `requirements.txt` and `pyinstaller` into the venv by default.
- The generated EXE is named `MicrophoneTranscriber.exe` and is moved to the repository root for convenience.

If you want, I can also add a short `Makefile` or further CI steps to build automatically on push. Feedback welcome.
