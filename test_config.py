#!/usr/bin/env python3
"""
Test script to verify unified configuration system
"""

import json
import os


def test_unified_config():
    """Test the unified configuration system"""
    config_file = "config.json"

    print("Testing unified configuration system...")

    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)

        print(f"✅ Config file exists: {config_file}")

        # Check Ollama configuration
        if "ollama" in config:
            ollama_config = config["ollama"]
            print(f"✅ Ollama config found:")
            print(f"   - URL: {ollama_config.get('base_url', 'Not set')}")
            print(f"   - Model: {ollama_config.get('model_name', 'Not set')}")
        else:
            print("❌ Ollama config not found")

        # Check microphone configuration
        if "microphones" in config:
            mic_config = config["microphones"]
            saved_mics = mic_config.get("saved_microphones", [])
            print(f"✅ Microphone config found:")
            print(f"   - Saved microphones: {len(saved_mics)}")
            for i, mic in enumerate(saved_mics):
                print(
                    f"   - Mic {i+1}: {mic.get('name', 'Unknown')} (Index: {mic.get('index', 'Unknown')})"
                )
        else:
            print("❌ Microphone config not found")

        # Check other settings
        print(f"✅ Other settings:")
        print(f"   - Auto generate ATA: {config.get('auto_generate_ata', 'Not set')}")
        print(f"   - Language: {config.get('language', 'Not set')}")

    else:
        print(f"❌ Config file not found: {config_file}")

    # Check if old mic_config.json still exists
    old_config_file = "mic_config.json"
    if os.path.exists(old_config_file):
        print(f"⚠️ Old config file still exists: {old_config_file}")
        print("   Migration may not have completed successfully")
    else:
        print(f"✅ Old config file cleaned up: {old_config_file}")


if __name__ == "__main__":
    test_unified_config()
