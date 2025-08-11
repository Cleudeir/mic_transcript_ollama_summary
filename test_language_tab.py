#!/usr/bin/env python3
"""
Test script to demonstrate the new language settings tab functionality
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.translations import get_translation_manager, set_global_language, t


def test_language_functionality():
    """Test the language functionality"""
    print("Testing Language Settings Functionality")
    print("=" * 50)

    # Get translation manager
    tm = get_translation_manager()

    # Show available languages
    print("Available Languages:")
    for code, name in tm.get_available_languages().items():
        print(f"  - {name} ({code})")

    print("\nTesting translations in Portuguese (pt-BR):")
    set_global_language("pt-BR")
    print(f"- Tab title: {t('menu_language', 'Language Settings')}")
    print(f"- Apply button: {t('button_apply', 'Apply Changes')}")
    print(f"- Reset button: {t('button_reset', 'Reset to Current')}")
    print(
        f"- Description: {t('language_description', 'Select your preferred language')}"
    )

    print("\nTesting translations in English (en):")
    set_global_language("en")
    print(f"- Tab title: {t('menu_language', 'Language Settings')}")
    print(f"- Apply button: {t('button_apply', 'Apply Changes')}")
    print(f"- Reset button: {t('button_reset', 'Reset to Current')}")
    print(
        f"- Description: {t('language_description', 'Select your preferred language')}"
    )

    print("\nLanguage functionality test completed successfully!")


if __name__ == "__main__":
    test_language_functionality()
