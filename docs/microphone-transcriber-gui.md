# MicrophoneTranscriberGUI (src/gui/app.py) — Module Summary

## Overview

This module implements the main Tkinter GUI for the meeting audio transcriber. It orchestrates:

- Microphone discovery, selection, and testing
- Real-time dual-microphone capture with non-blocking transcription
- Live transcript display and auto-saving to Markdown
- AI-powered meeting minutes (ATA) generation via Ollama
- File management for transcripts and atas
- Language and configuration management persisted in `config.json`

Primary class: `MicrophoneTranscriberGUI`

Helper factory/runner: `create_gui()`, `run_gui()`

## UI structure

- Window: Tk root 1000x700 with title from translations
- Recording controls: Start, Pause/Resume, Stop + status indicator
- Tabs (ttk.Notebook):

  - 📄 Transcripts Only: Side-by-side text areas for Mic 1/Mic 2 transcripts
  - 📝 System Logs: Side-by-side log areas for Mic 1/Mic 2
  - 📁 Transcript Files: List, open, save-as, regenerate ATA, open folder
  - 📝 ATA Files: List, open, save-as, open folder, info panel
  - 🎤 Microphone Configuration: Checkbox list, refresh, preference load
  - 🤖 Ollama Configuration: Base URL, connection test, model selection/refresh
  - 🌐 Language Settings: Radio selection, apply/reset, current language display

An optional menu bar exists with Settings/File/Help entries and is enabled during init.

## Recording & transcription pipeline

- Exactly two microphones are required (checkbox selection). Preferences auto-load.
- Start real-time recording: clears outputs, updates control states, initializes realtime Markdown session file (`src/output/transcript`).
- For each selected device:

  - A background thread calls `realtime_record_and_transcribe` which:
    - Starts a bounded queue for audio chunks and spawns multiple transcription workers
    - Enqueues chunks via `capture_audio_realtime` callback without blocking
    - Transcribes in workers using `transcribe_audio_async` (from `src/transcribe_text`)
    - Logs concise status per chunk; writes transcripts to proper Mic 1/Mic 2 widgets
    - Appends to the live Markdown file with timestamps

- Pause/Resume supported by signaling stop events and re-spawning threads
- Stop recording:

  - Finalizes the live Markdown file
  - Auto-saves combined transcripts to a timestamped file
  - Optionally auto-generates ATA if Ollama is available and `auto_generate_ata` is true
  - Refreshes file lists

## File management

- Transcript files: `src/output/transcript/*.md`
- ATA files: `src/output/ata/*.md`
- Features:
  - List, open (system default), delete, save-as
  - Regenerate ATA from a selected transcript
  - Open folders (platform-aware: Windows/macOS/Linux)
  - Legacy files in `src/output` are still recognized

## Configuration & persistence

- Unified `config.json` holds:
  - `ollama`: `base_url`, `model_name`, `temperature`, `top_p`, `num_predict`
  - `auto_generate_ata` (bool)
  - `language` (e.g., `pt-BR`)
  - `microphones.saved_microphones` (list of index/name)
- On startup:
  - Ensures `config.json` exists with defaults
  - Migrates legacy `mic_config.json` into `config.json`
  - Loads language and initializes translations
  - Synchronizes `OllamaService` with stored URL/model (no hardcoded defaults in UI)
  - Optionally tests connection and loads models, updating UI labels
- Changing the Ollama URL/model updates `OllamaService` and saves to `config.json`.

## Ollama integration (AI meeting minutes)

- `OllamaService` is used for:
  - Connection availability checks
  - Model listing, pulling, and basic greeting test
  - Generating structured meeting minutes (ATA) from a transcript file
- UI:
  - URL entry with connection test and status
  - Model combobox with refresh and selection persistence
  - On startup, connection is tested; models may be fetched; a greeting test runs
- ATA generation:
  - Manual: from Transcript Files tab or dialog
  - Automatic: after recording stops if enabled
  - Output saved under `src/output/ata` with timestamped names

## Microphone management

- Discovery: `get_microphone_list()` and `sounddevice` for detailed info
- Selection UI: checkboxes with validation for exactly two devices
- Tree view: detailed device info, active/inactive status, double-click to toggle
- Testing utilities: selected and all microphones (short recording and levels)
- Preferences: auto-select saved microphones from `config.json`

## Language settings

- Dedicated tab with available languages from the translation manager
- Applies selection to `config.json` and global translation setting
- UI updates status and current language display

## Public API

- `create_gui() -> MicrophoneTranscriberGUI`
- `run_gui()` to instantiate and start the Tk main loop

## Notable methods (by responsibility)

- UI/tabs: `create_*_tab`, `setup_menu_bar`
- Recording controls: `start_realtime_recording`, `pause_recording`, `resume_recording`, `stop_realtime_recording`, `update_recording_controls_state`
- Real-time pipeline: `realtime_record_and_transcribe`, `transcribe_and_display_separated`, `add_log_message`, `add_transcript_message`
- Markdown I/O: `start_realtime_markdown_save`, `append_to_realtime_markdown`, `stop_realtime_markdown_save`, `_save_transcripts_to_markdown`, `auto_save_transcripts`
- Files: `refresh_transcript_files_list`, `open_selected_transcript_file`, `delete_selected_transcript_file`, `save_transcript_as`, `refresh_ata_files_list`, `open_selected_ata_file`, `delete_selected_ata_file`, `save_ata_as`
- Ollama: `initialize_ollama_on_startup`, `test_ollama_connection`, `refresh_ollama_models`, `send_greeting_to_model`, `generate_ata_from_file`, `auto_generate_meeting_minutes`, `toggle_auto_ata_generation`
- Config: `load_main_config`, `save_main_config`, `ensure_config_file_exists`, `migrate_old_mic_config`, `sync_ollama_service_with_config`, `ensure_config_loaded_in_ui`
- Microphones: `load_microphones`, `on_microphone_selection_change`, `save_microphone_config`, `populate_mic_tree`, `test_selected_mics`, `test_all_microphones`, `apply_mic_config`
- Language: `create_language_settings_tab`, `apply_language_change`, `reset_language_selection`

## Dependencies

- Standard: `threading`, `tkinter`, `json`, `os`, `datetime`
- Third-party: `ollama`, `sounddevice` (queried within methods)
- Internal: `src.capture_audio`, `src.transcribe_text`, `src.ollama_service`, `src.translations`, `src.config`

## Notes & edge cases

- Graceful UI updates during shutdown with thread-safe helpers
- High-load handling: drops oldest queue item when full to keep UI responsive
- Platform-aware file opening via `os.startfile` (Windows) and `open`/`xdg-open`
- Status messages centralized via `status_var`
