"""
Internationalization support for the Meeting Transcriber application
"""

# Translation dictionaries for different languages
TRANSLATIONS = {
    "pt-BR": {
        # UI Labels
        "app_title": "Meeting Audio Transcriber",
        "start_button": "🎤 Iniciar",
        "stop_button": "🎤 Parar",
        "auto_save_off": "Auto-salvar: DESLIGADO",
        "auto_save_on": "Auto-salvar: LIGADO",
        "ollama_checking": "🌐 Ollama Remoto: Verificando...",
        "ollama_available": "🌐 Ollama Remoto: Disponível",
        "ollama_unavailable": "🌐 Ollama Remoto: Indisponível",
        "ollama_ready": "🌐 Ollama Remoto: Pronto",
        "ollama_downloading": "🌐 Ollama Remoto: Baixando modelo...",
        "ollama_download_failed": "🌐 Ollama Remoto: Falha no download do modelo",
        "ollama_connection_error": "🌐 Ollama Remoto: Erro de Conexão",
        "ollama_service_unavailable": "❌ Serviço Ollama não disponível",
        # Tab Names
        "tab_combined": "📊 Logs & Transcrições",
        "tab_logs": "📋 Logs Apenas",
        "tab_transcripts": "📄 Transcrições Apenas",
        "tab_transcript_files": "📁 Arquivos de Transcrição",
        "tab_ata_files": "📝 Arquivos de Ata",
        "tab_mic_config": "🎤 Configuração do Microfone",
        "tab_ollama_config": "🤖 Configuração Ollama",
        # Menu Items
        "menu_settings": "⚙️ Configurações",
        "menu_language": "🌐 Configurações de Idioma",
        "menu_audio": "🔊 Configurações de Áudio",
        "menu_auto_ata": "🤖 Gerar Ata Automaticamente",
        "menu_performance": "📊 Monitor de Performance",
        "menu_file": "📁 Arquivo",
        "menu_open_transcript_folder": "📄 Abrir Pasta de Transcrições",
        "menu_view_transcripts": "📋 Ver Todas as Transcrições",
        "menu_generate_minutes": "🤖 Gerar Ata da Reunião",
        "menu_view_atas": "📝 Ver Todas as Atas",
        "menu_reset": "🔄 Resetar Aplicação",
        "menu_exit": "❌ Sair",
        "menu_help": "❓ Ajuda",
        "menu_user_guide": "📖 Guia do Usuário",
        "menu_troubleshooting": "🔧 Solução de Problemas",
        "menu_about": "ℹ️ Sobre",
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
        "button_refresh": "Atualizar",
        "button_delete": "Excluir",
        "button_generate": "Gerar",
        # Configuration overview
        "config_overview": "⚙️ Visão Geral da Configuração",
        "config_hide": "▼ Ocultar Configuração",
        "config_show": "▶ Mostrar Configuração",
        "config_refresh": "🔄 Atualizar",
        "config_ollama_settings": "🤖 Configurações Ollama",
        "config_audio_settings": "🎤 Configurações de Áudio",
        "config_general_settings": "⚙️ Configurações Gerais",
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
        "start_button": "🎤 Start",
        "stop_button": "🎤 Stop",
        "auto_save_off": "Auto-save: OFF",
        "auto_save_on": "Auto-save: ON",
        "ollama_checking": "🌐 Ollama Remote: Checking...",
        "ollama_available": "🌐 Ollama Remote: Available",
        "ollama_unavailable": "🌐 Ollama Remote: Unavailable",
        "ollama_ready": "🌐 Ollama Remote: Ready",
        "ollama_downloading": "🌐 Ollama Remote: Downloading model...",
        "ollama_download_failed": "🌐 Ollama Remote: Model download failed",
        "ollama_connection_error": "🌐 Ollama Remote: Connection Error",
        "ollama_service_unavailable": "❌ Ollama service not available",
        # Tab Names
        "tab_combined": "📊 Logs & Transcripts",
        "tab_logs": "📋 Logs Only",
        "tab_transcripts": "📄 Transcripts Only",
        "tab_transcript_files": "📁 Transcript Files",
        "tab_ata_files": "📝 Meeting Minutes Files",
        "tab_mic_config": "🎤 Microphone Configuration",
        "tab_ollama_config": "🤖 Ollama Configuration",
        # Menu Items
        "menu_settings": "⚙️ Settings",
        "menu_language": "🌐 Language Settings",
        "menu_audio": "🔊 Audio Settings",
        "menu_auto_ata": "🤖 Auto-generate Meeting Minutes",
        "menu_performance": "📊 Performance Monitor",
        "menu_file": "📁 File",
        "menu_open_transcript_folder": "📄 Open Transcript Folder",
        "menu_view_transcripts": "📋 View All Transcripts",
        "menu_generate_minutes": "🤖 Generate Meeting Minutes",
        "menu_view_atas": "📝 View All Meeting Minutes",
        "menu_reset": "🔄 Reset Application",
        "menu_exit": "❌ Exit",
        "menu_help": "❓ Help",
        "menu_user_guide": "📖 User Guide",
        "menu_troubleshooting": "🔧 Troubleshooting",
        "menu_about": "ℹ️ About",
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
        "button_refresh": "Refresh",
        "button_delete": "Delete",
        "button_generate": "Generate",
        # Configuration overview
        "config_overview": "⚙️ Configuration Overview",
        "config_hide": "▼ Hide Configuration",
        "config_show": "▶ Show Configuration",
        "config_refresh": "🔄 Refresh",
        "config_ollama_settings": "🤖 Ollama Settings",
        "config_audio_settings": "🎤 Audio Settings",
        "config_general_settings": "⚙️ General Settings",
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
