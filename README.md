# Meeting Transcription Tool (AI-Powered Minutes)

A desktop app that records audio, transcribes speech in real time, and generates organized meeting minutes (atas) using a remote Ollama service.

## Highlights

- Real-time transcription with continuous recording
- Optional automatic ATA generation after sessions
- Remote Ollama integration (no local Ollama needed)
- Clean, tabbed GUI with file management for transcripts and atas
- Portuguese-first UX (pt-BR), with i18n support

## Project structure (key files)

```text
meet_audio/
├── main.py                      # Entry point
├── build_windows.bat            # Build one-file EXE (with icon)
├── run_windows.bat              # Launch built EXE
├── MicrophoneTranscriber.spec   # PyInstaller spec
├── icon.ico                     # App/EXE icon
├── requirements.txt
# Reunião — Meeting transcription and AI-powered minutes

Lightweight desktop app that records audio, transcribes speech in real time, and can generate organized meeting minutes (atas) using a remote Ollama service.

Key points
- Real-time, continuous transcription
- Optional automatic ATA (ata) generation via a remote Ollama API
- Simple tabbed GUI with file management for transcripts and atas
- pt-BR-first UI with i18n support

Quick start (Windows)
1. Install Python 3.11+ (recommended).
2. From the project root, install dependencies:

```powershell
pip install -r .\requirements.txt
```

3. Run from source:

```powershell
python .\main.py
```

What you'll find in this repository
- `main.py` — application entry point (runs the GUI)
- `requirements.txt` — Python dependencies
- `build_windows.bat` / `MicrophoneTranscriber.spec` — build helpers for a one-file EXE
- `src/` — application code (audio capture, GUI, services, i18n, output)
- `src/output/transcript/` — saved transcripts (*.md)
- `src/output/ata/` — generated atas (*.md)
- `docs/` — build and documentation notes (see `docs/icon-and-build.md`, `docs/compile-and-run.md`)

Running the GUI
- The GUI detects available recording devices and exposes controls for continuous recording and ATA generation.
- Use the Microphones tab to choose primary and (optional) secondary devices such as "Stereo Mix".

Windows build (one-file EXE)
- Build script packages the app with PyInstaller and embeds the icon. The produced EXE is placed under `build/` and the one-file output is copied to the project root when the script completes.
- To build (from project root):

```powershell
.\build_windows.bat
```

Configuration
- `config.json` — user-editable runtime settings (language, Ollama URL/model, auto-generate ATA)
- `src/config_pkg/config.py` — constants used by the app
- Ollama settings are also editable inside the app (Ollama tab)

Outputs
- Transcript files: `src/output/transcript/YYYYMMDD_HHMMSS_transcript.md`
- Atas (minutes): `src/output/ata/YYYYMMDD_HHMMSS_ata.md`

Troubleshooting: Stereo Mix (Windows)
"Stereo Mix" captures the system audio (what's playing on your PC) and is useful as a secondary input to transcribe meeting audio played on the same machine.

Enable Stereo Mix (Windows 10/11):
1. Right-click the system sound icon → Sound settings → More sound settings (or Control Panel → Sound).
2. In the Recording tab, right-click the device list and enable "Show Disabled Devices".
3. Right-click "Stereo Mix" (or "Mixagem Estéreo") → Enable.
4. Optionally set it as default or adjust levels in Properties.

If it doesn't appear: enable disabled devices, update audio drivers (e.g., Realtek), or use a virtual audio cable (VB-Audio / Voicemeeter) as an alternative.

Notes
- Prefer headphones to avoid feedback when using both a physical microphone and Stereo Mix.
- The app expects a working microphone and network access for the remote Ollama service when ATA generation is enabled.

Documentation
- For build and icon details: `docs/icon-and-build.md`
- For running and troubleshooting: `docs/compile-and-run.md`

License
MIT License © 2025 Cleudeir — see `LICENSE` for full text.

Contact / Contribution
- Issues and PRs are welcome. Open a GitHub issue or pull request against the `main` branch.
