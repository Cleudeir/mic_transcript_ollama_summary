#!/usr/bin/env python3
"""
Test script for the internationalization implementation
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from translations import TranslationManager, set_global_language, t


def test_translations():
    """Test the translation system"""
    print("=== Testing Translation System ===\n")

    # Test Portuguese
    print("Testing Portuguese (pt-BR):")
    set_global_language("pt-BR")
    print(f"App Title: {t('app_title')}")
    print(f"Start Button: {t('start_button')}")
    print(f"Stop Button: {t('stop_button')}")
    print(f"Menu Settings: {t('menu_settings')}")
    print(f"Language Settings: {t('menu_language')}")
    print(f"ATA Title: {t('ata_title')}")
    print(f"Recording Started: {t('recording_started')}")
    print()

    # Test English
    print("Testing English (en):")
    set_global_language("en")
    print(f"App Title: {t('app_title')}")
    print(f"Start Button: {t('start_button')}")
    print(f"Stop Button: {t('stop_button')}")
    print(f"Menu Settings: {t('menu_settings')}")
    print(f"Language Settings: {t('menu_language')}")
    print(f"ATA Title: {t('ata_title')}")
    print(f"Recording Started: {t('recording_started')}")
    print()

    # Test fallback
    print("Testing fallback for non-existent key:")
    print(f"Non-existent key: {t('non_existent_key', 'Default Value')}")
    print()

    # Test TranslationManager directly
    print("Testing TranslationManager:")
    tm = TranslationManager("pt-BR")
    print(f"Available languages: {tm.get_available_languages()}")
    print(f"Current language: {tm.current_language}")
    print(f"Language name for pt-BR: {tm.get_language_name('pt-BR')}")
    print(f"Language name for en: {tm.get_language_name('en')}")
    print()

    print("=== Translation Test Complete ===")


if __name__ == "__main__":
    test_translations()
