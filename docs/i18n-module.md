# Internationalization (i18n) Module

This project now centralizes translation logic under `src/i18n`.

- Implementation: `src/i18n/core.py`
- Public API: `src/i18n/__init__.py` re-exports from core
- Legacy shim: `src/translations.py` re-exports from `src.i18n.core` for backward compatibility

## Usage

Prefer importing from the package:

- `from src.i18n import t, set_global_language, get_translation_manager`
- `text = t("app_title")`

## Migration

Old imports like `from src.translations import t` will continue to work via the shim, but new code should switch to `src.i18n`.

## Notes

- The `TRANSLATIONS` dictionary lives in `src/i18n/core.py`.
- The global translation manager can be accessed via `get_translation_manager()`.
