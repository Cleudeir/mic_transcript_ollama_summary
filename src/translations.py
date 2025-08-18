"""
Internationalization support for the Meeting Transcriber application
"""

# Translation dictionaries for different languages
TRANSLATIONS = {
    "pt-BR": {
        # UI Labels
        "app_title": "Meeting Audio Transcriber",
        "start_button": "🎤 Iniciar",
        """Legacy shim for translations.

        This module re-exports the i18n API from src.i18n.core to preserve backwards
        compatibility. Please migrate imports to `from src.i18n import ...`.
        """

        from src.i18n.core import (
            TRANSLATIONS,
            TranslationManager,
            get_translation_manager,
            set_global_language,
            t,
        )

        __all__ = [
            "TRANSLATIONS",
            "TranslationManager",
            "get_translation_manager",
            "set_global_language",
            "t",
        ]
        # Menu Items
