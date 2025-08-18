# GUI architecture overview (post-refactor)

This document explains the new modular structure introduced by the GUI refactor. The goal was to split a large monolithic class into smaller, focused mixins and modules while preserving behavior.

## High-level structure

- Entry point: `src/gui/app.py` defines `MicrophoneTranscriberGUI`, which composes multiple mixins.
- Tabs and common UI scaffolding: `src/gui/ui_tabs.py`.
- Theming and common widgets: `src/gui/theme.py`.
- Ollama service integration: `src/gui/ollama_integration.py`.
- Mixins (per-responsibility): `src/gui/mixins/`.

## Mixins and responsibilities

- ConfigMixin (`mixins/config_mixin.py`)
  - Load/save main config (`config.json`)
  - Ensure config file exists and migrate legacy microphone config
  - Reset application state helper

- RecordingMixin (`mixins/recording_mixin.py`)
  - Start/Pause/Stop recording buttons behavior and UI state
  - Real-time transcript file session management
  - ATA file generation workflow

- MicrophoneTabMixin (`mixins/microphone_mixin.py`)
  - Build the Microphone Configuration tab
  - Refresh device list, save/test selection
  - Helpers to format/parse combobox values

- FilesMixin (`mixins/files_mixin.py`)
  - Transcript and ATA files listing, selection handlers, open/save-as
  - Helpers to locate `src/output/transcript` and `src/output/ata`

- LanguageMixin (`mixins/language_mixin.py`)
  - Build the Language Settings tab and apply language change

- MenuActionsMixin (`mixins/menu_mixin.py`)
  - Menu routing: open tabs, toggles, help/about

- OllamaIntegrationMixin (`../ollama_integration.py`)
  - Ollama URL/model sync, model loading, connection testing

## Where things live now

- The main class only wires the UI, creates tabs (via mixins), and delegates logic to mixins.
- Duplicate/legacy methods previously in `app.py` were removed to avoid confusion.

## Running a quick sanity import

- Use the existing task "Run GUI import smoke test" to verify imports. It prints `Imported GUI: True` on success.

## Notes

- No tests were added (per project policy).
- Behavior is intended to be equivalent to pre-refactor. If you spot any runtime regressions, report the exact action and error so we can adjust the mixins or wiring.
