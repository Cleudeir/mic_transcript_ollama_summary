"""
Internationalization support for the Meeting Transcriber application.

This module contains the implementation of the translation system and is the
single source of truth for i18n logic. The package entry point (src.i18n)
re-exports its public API.
"""

# Translation dictionaries for different languages
TRANSLATIONS = {
    "pt-BR": {
        # UI Labels
        "app_title": "Meeting Audio Transcriber",
        "start_button": "\ud83c\udfa4 Iniciar",
        "pause_button": "\u23f8\ufe0f Pausar",
        "resume_button": "\u25b6\ufe0f Retomar",
        "stop_button": "\ud83c\udfa4 Parar",
        "auto_save_off": "Auto-salvar: DESLIGADO",
        "auto_save_on": "Auto-salvar: LIGADO",
        "ollama_checking": "\ud83c\udf10 Ollama Remoto: Verificando...",
        "ollama_available": "\ud83c\udf10 Ollama Remoto: Disponível",
        "ollama_unavailable": "\ud83c\udf10 Ollama Remoto: Indisponível",
        "ollama_ready": "\ud83c\udf10 Ollama Remoto: Pronto",
        "ollama_downloading": "\ud83c\udf10 Ollama Remoto: Baixando modelo...",
        "ollama_download_failed": "\ud83c\udf10 Ollama Remoto: Falha no download do modelo",
        "ollama_connection_error": "\ud83c\udf10 Ollama Remoto: Erro de Conexão",
        "ollama_service_unavailable": "\u274c Serviço Ollama não disponível",
        # Tab Names
        "tab_combined": "\ud83d\udcca Logs & Transcrições",
        "tab_logs": "\ud83d\udccb Logs Apenas",
        "tab_transcripts": "\ud83d\udcc4 Transcrições",
        "tab_transcript_files": "\ud83d\udcc1 Arquivos de Transcrição",
        "tab_ata_files": "\ud83d\udcdd Arquivos de Ata",
        "tab_mic_config": "\ud83c\udfa4 Configuração do Microfone",
        "tab_ollama_config": "\ud83e\udd16 Configuração Ollama",
        # Menu Items
        "menu_settings": "\u2699\ufe0f Configurações",
        "menu_language": "\ud83c\udf10 Configurações de Idioma",
        "menu_audio": "\ud83d\udd0a Configurações de Áudio",
        "menu_auto_ata": "\ud83e\udd16 Gerar Ata Automaticamente",
        "menu_performance": "\ud83d\udcca Monitor de Performance",
        "menu_file": "\ud83d\udcc1 Arquivo",
        "menu_open_transcript_folder": "\ud83d\udcc4 Abrir Pasta de Transcrições",
        "menu_view_transcripts": "\ud83d\udccb Ver Todas as Transcrições",
        "menu_generate_minutes": "\ud83e\udd16 Gerar Ata da Reunião",
        "menu_view_atas": "\ud83d\udcdd Ver Todas as Atas",
        "menu_reset": "\ud83d\udd04 Resetar Aplicação",
        "menu_exit": "\u274c Sair",
        "menu_help": "\u2753 Ajuda",
        "menu_user_guide": "\ud83d\udcd6 Guia do Usuário",
        "menu_troubleshooting": "\ud83d\udd27 Solução de Problemas",
        "menu_about": "\u2139\ufe0f Sobre",
        # Messages
        "language_settings_title": "Configurações de Idioma",
        "language_current": "Idioma Atual:",
        "language_select": "Selecionar Idioma:",
        "language_changed": "Idioma alterado com sucesso! Reinicie a aplicação para ver as mudanças.",
        "language_error": "Erro ao salvar configuração de idioma.",
        # File operations
        "transcript_saved": "Transcrição salva em:",
        "ata_generated": "Ata gerada em:",
        "generating_ata": "Gerando ata da reunião...",
        "ata_generation_failed": "Falha ao gerar ata da reunião:",
        # Recording status
        "recording_started": "Gravação iniciada",
        "recording_stopped": "Gravação parada",
        "microphone_selected": "Microfone selecionado:",
        "no_microphone": "Nenhum microfone selecionado",
        # Errors
        "error_ollama_connection": "Erro de conexão com Ollama",
        "error_file_save": "Erro ao salvar arquivo",
        "error_microphone": "Erro no microfone",
        "error_general": "Erro geral",
        # ATA specific terms
        "ata_title": "Ata da Reunião",
        "meeting_date": "Data da Reunião",
        "participants": "Participantes",
        "topics_discussed": "Tópicos Discutidos",
        "decisions_made": "Decisões Tomadas",
        "next_steps": "Próximos Passos",
        "action_items": "Itens de Ação",
        # Column headers
        "column_file": "Arquivo",
        "column_date": "Data",
        "column_size": "Tamanho",
        "column_status": "Status",
        # Buttons
        "button_save": "Salvar",
        "button_cancel": "Cancelar",
        "button_ok": "OK",
        "button_yes": "Sim",
        "button_no": "Não",
        "button_browse": "Procurar...",
        "button_refresh": "\ud83d\udd04 Atualizar",
        "button_delete": "Excluir",
        "button_generate": "Gerar",
        "button_open": "\ud83d\udcd6 Abrir",
        "button_save_as": "\ud83d\udcbe Salvar Como",
        "button_regenerate_ata": "\ud83e\udd16 Regenerar ATA",
        "button_open_folder": "\ud83d\udcc1 Abrir Pasta",
        "button_apply": "\u2705 Aplicar Mudanças",
        "button_reset": "\ud83d\udd04 Resetar para Atual",
        # Language settings specific
        "language_description": "Selecione seu idioma preferido para a interface da aplicação",
        # Configuration overview
        "config_overview": "\u2699\ufe0f Visão Geral da Configuração",
        "config_hide": "\u25bc Ocultar Configuração",
        "config_show": "\u25b6 Mostrar Configuração",
        "config_refresh": "\ud83d\udd04 Atualizar",
        "config_ollama_settings": "\ud83e\udd16 Configurações Ollama",
        "config_audio_settings": "\ud83c\udfa4 Configurações de Áudio",
        "config_general_settings": "\u2699\ufe0f Configurações Gerais",
        "config_url": "URL",
        "config_model": "Modelo",
        "config_temperature": "Temperatura",
        "config_language": "Idioma",
        "config_auto_ata": "Auto-gerar ATA",
        "config_microphones_count": "Microfones Configurados",
        "config_no_microphones": "Nenhum microfone configurado",
        "config_enabled": "Habilitado",
        "config_disabled": "Desabilitado",
        "config_not_set": "Não configurado",
    },
    "en": {
        # UI Labels
        "app_title": "Meeting Audio Transcriber",
        "start_button": "\ud83c\udfa4 Start",
        "pause_button": "\u23f8\ufe0f Pause",
        "resume_button": "\u25b6\ufe0f Resume",
        "stop_button": "\ud83c\udfa4 Stop",
        "auto_save_off": "Auto-save: OFF",
        "auto_save_on": "Auto-save: ON",
        "ollama_checking": "\ud83c\udf10 Ollama Remote: Checking...",
        "ollama_available": "\ud83c\udf10 Ollama Remote: Available",
        "ollama_unavailable": "\ud83c\udf10 Ollama Remote: Unavailable",
        "ollama_ready": "\ud83c\udf10 Ollama Remote: Ready",
        "ollama_downloading": "\ud83c\udf10 Ollama Remote: Downloading model...",
        "ollama_download_failed": "\ud83c\udf10 Ollama Remote: Model download failed",
        "ollama_connection_error": "\ud83c\udf10 Ollama Remote: Connection Error",
        "ollama_service_unavailable": "\u274c Ollama service not available",
        # Tab Names
        "tab_combined": "\ud83d\udcca Logs & Transcripts",
        "tab_logs": "\ud83d\udccb Logs Only",
        "tab_transcripts": "\ud83d\udcc4 Transcripts",
        "tab_transcript_files": "\ud83d\udcc1 Transcript Files",
        "tab_ata_files": "\ud83d\udcdd Meeting Minutes Files",
        "tab_mic_config": "\ud83c\udfa4 Microphone Configuration",
        "tab_ollama_config": "\ud83e\udd16 Ollama Configuration",
        # Menu Items
        "menu_settings": "\u2699\ufe0f Settings",
        "menu_language": "\ud83c\udf10 Language Settings",
        "menu_audio": "\ud83d\udd0a Audio Settings",
        "menu_auto_ata": "\ud83e\udd16 Auto-generate Meeting Minutes",
        "menu_performance": "\ud83d\udcca Performance Monitor",
        "menu_file": "\ud83d\udcc1 File",
        "menu_open_transcript_folder": "\ud83d\udcc4 Open Transcript Folder",
        "menu_view_transcripts": "\ud83d\udccb View All Transcripts",
        "menu_generate_minutes": "\ud83e\udd16 Generate Meeting Minutes",
        "menu_view_atas": "\ud83d\udcdd View All Meeting Minutes",
        "menu_reset": "\ud83d\udd04 Reset Application",
        "menu_exit": "\u274c Exit",
        "menu_help": "\u2753 Help",
        "menu_user_guide": "\ud83d\udcd6 User Guide",
        "menu_troubleshooting": "\ud83d\udd27 Troubleshooting",
        "menu_about": "\u2139\ufe0f About",
        # Messages
        "language_settings_title": "Language Settings",
        "language_current": "Current Language:",
        "language_select": "Select Language:",
        "language_changed": "Language changed successfully! Please restart the application to see changes.",
        "language_error": "Error saving language configuration.",
        # File operations
        "transcript_saved": "Transcript saved to:",
        "ata_generated": "Meeting minutes generated at:",
        "generating_ata": "Generating meeting minutes...",
        "ata_generation_failed": "Failed to generate meeting minutes:",
        # Recording status
        "recording_started": "Recording started",
        "recording_stopped": "Recording stopped",
        "microphone_selected": "Microphone selected:",
        "no_microphone": "No microphone selected",
        # Errors
        "error_ollama_connection": "Ollama connection error",
        "error_file_save": "File save error",
        "error_microphone": "Microphone error",
        "error_general": "General error",
        # ATA specific terms
        "ata_title": "Meeting Minutes",
        "meeting_date": "Meeting Date",
        "participants": "Participants",
        "topics_discussed": "Topics Discussed",
        "decisions_made": "Decisions Made",
        "next_steps": "Next Steps",
        "action_items": "Action Items",
        # Column headers
        "column_file": "File",
        "column_date": "Date",
        "column_size": "Size",
        "column_status": "Status",
        # Buttons
        "button_save": "Save",
        "button_cancel": "Cancel",
        "button_ok": "OK",
        "button_yes": "Yes",
        "button_no": "No",
        "button_browse": "Browse...",
        "button_refresh": "\ud83d\udd04 Refresh",
        "button_delete": "Delete",
        "button_generate": "Generate",
        "button_open": "\ud83d\udcd6 Open",
        "button_save_as": "\ud83d\udcbe Save As",
        "button_regenerate_ata": "\ud83e\udd16 Regenerate ATA",
        "button_open_folder": "\ud83d\udcc1 Open Folder",
        "button_apply": "\u2705 Apply Changes",
        "button_reset": "\ud83d\udd04 Reset to Current",
        # Language settings specific
        "language_description": "Select your preferred language for the application interface",
        # Configuration overview
        "config_overview": "\u2699\ufe0f Configuration Overview",
        "config_hide": "\u25bc Hide Configuration",
        "config_show": "\u25b6 Show Configuration",
        "config_refresh": "\ud83d\udd04 Refresh",
        "config_ollama_settings": "\ud83e\udd16 Ollama Settings",
        "config_audio_settings": "\ud83c\udfa4 Audio Settings",
        "config_general_settings": "\u2699\ufe0f General Settings",
        "config_url": "URL",
        "config_model": "Model",
        "config_temperature": "Temperature",
        "config_language": "Language",
        "config_auto_ata": "Auto-generate ATA",
        "config_microphones_count": "Configured Microphones",
        "config_no_microphones": "No microphones configured",
        "config_enabled": "Enabled",
        "config_disabled": "Disabled",
        "config_not_set": "Not set",
    },
}


class TranslationManager:
    """Manages translations for the application"""

    def __init__(self, language: str = "pt-BR"):
        """
        Initialize the translation manager

        Args:
            language: Language code (pt-BR or en)
        """
        self.current_language = language
        self.available_languages = {"pt-BR": "Português (Brasil)", "en": "English"}

    def set_language(self, language: str):
        """Set the current language"""
        if language in self.available_languages:
            self.current_language = language
        else:
            self.current_language = "pt-BR"  # Default fallback

    def get_language_name(self, language_code: str) -> str:
        """Get the display name for a language code"""
        return self.available_languages.get(language_code, language_code)

    def get_available_languages(self) -> dict:
        """Get all available languages"""
        return self.available_languages.copy()

    def translate(self, key: str, default: str = None) -> str:
        """
        Get translated text for a key

        Args:
            key: Translation key
            default: Default text if translation not found

        Returns:
            Translated text or default
        """
        # Try current language first
        if self.current_language in TRANSLATIONS:
            if key in TRANSLATIONS[self.current_language]:
                return TRANSLATIONS[self.current_language][key]

        # Fallback to pt-BR
        if "pt-BR" in TRANSLATIONS and key in TRANSLATIONS["pt-BR"]:
            return TRANSLATIONS["pt-BR"][key]

        # Return default or key as last resort
        return default if default is not None else key

    def t(self, key: str, default: str = None) -> str:
        """Short alias for translate method"""
        return self.translate(key, default)


# Global translation manager instance
_translation_manager = None


def get_translation_manager() -> TranslationManager:
    """Get the global translation manager instance"""
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager()
    return _translation_manager


def set_global_language(language: str):
    """Set the global language for the application"""
    manager = get_translation_manager()
    manager.set_language(language)


def t(key: str, default: str = None) -> str:
    """Global translation function"""
    manager = get_translation_manager()
    return manager.translate(key, default)


__all__ = [
    "TRANSLATIONS",
    "TranslationManager",
    "get_translation_manager",
    "set_global_language",
    "t",
]
