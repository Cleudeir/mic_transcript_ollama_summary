# Project structure and module organization

This refactor introduces a clearer, layered package layout while keeping backward-compatible imports. No runtime behavior was changed.

- src/audio/: Runtime audio input APIs (shim that re-exports from legacy `src.capture_audio`).
- src/transcription/: Speech-to-text helpers (implementation in `src/transcription/core.py`).
- src/services/: External integrations such as OllamaService (re-exports `src.ollama_service.OllamaService`).
- src/i18n/: Internationalization helpers (re-exports from `src.translations`).
- src/gui/: Modular GUI app (unchanged public API). Import with `from src.gui import run_gui`.
- src/config_pkg/: Config shim re-exporting constants from `src.config`.

Backwards compatibility

- Preferred imports are `from src.audio import ...` and `from src.transcription import ...`.

- New organized imports are available: `from src.audio import capture_audio_realtime`, `from src.transcription import transcribe_audio_async`, `from src.services import OllamaService`, `from src.i18n import t`.

Notes

- Output directories remain under `src/output/` as before.
- The smoke test `python -m src.smoke_gui_import` should pass.
