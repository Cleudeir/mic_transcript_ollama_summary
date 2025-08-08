#!/usr/bin/env python3
"""
Demo script showing the new features of the Meeting Audio Transcriber

New Features:
1. Separate logs and transcripts in tabbed interface
2. Remember microphone choices
3. Enhanced GUI with better organization
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui import run_gui

def main():
    print("🎤 Meeting Audio Transcriber - Enhanced Version")
    print("=" * 50)
    print("New Features:")
    print("📊 Combined View - All logs and transcripts together")
    print("📝 System Logs - Recording status per microphone")
    print("📄 Transcripts Only - Clean transcription view")
    print("💾 Remember Mic Choice - Save preferred microphones")
    print("🔄 Auto-load Settings - Automatically select saved mics")
    print("=" * 50)
    print("Starting GUI...")
    
    # Run the enhanced GUI
    run_gui()

if __name__ == "__main__":
    main()
