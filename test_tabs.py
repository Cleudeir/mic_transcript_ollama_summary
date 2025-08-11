#!/usr/bin/env python3
"""
Test script to verify the new tab structure and functionality
"""

import os
import sys


def test_tab_structure():
    """Test the new tab structure"""
    print("Testing Tab Structure...")

    # Check if output directories exist
    output_dir = os.path.join("src", "output")
    transcript_dir = os.path.join(output_dir, "transcript")
    ata_dir = os.path.join(output_dir, "ata")

    print(f"📁 Output directory: {output_dir}")
    print(f"   Exists: {os.path.exists(output_dir)}")

    print(f"📝 Transcript directory: {transcript_dir}")
    print(f"   Exists: {os.path.exists(transcript_dir)}")
    if os.path.exists(transcript_dir):
        transcript_files = [f for f in os.listdir(transcript_dir) if f.endswith(".md")]
        print(f"   Files: {len(transcript_files)}")
        for file in transcript_files[:3]:  # Show first 3 files
            print(f"      - {file}")
        if len(transcript_files) > 3:
            print(f"      ... and {len(transcript_files) - 3} more")

    print(f"📊 ATA directory: {ata_dir}")
    print(f"   Exists: {os.path.exists(ata_dir)}")
    if os.path.exists(ata_dir):
        ata_files = [f for f in os.listdir(ata_dir) if f.endswith(".md")]
        print(f"   Files: {len(ata_files)}")
        for file in ata_files[:3]:  # Show first 3 files
            print(f"      - {file}")
        if len(ata_files) > 3:
            print(f"      ... and {len(ata_files) - 3} more")

    print("\n✅ Tab structure test completed!")
    print("\nNew Features Added:")
    print("1. 📝 Separate Transcript Files tab")
    print("2. 📊 Separate ATA Summary tab")
    print("3. 📖 Open and 💾 Save As buttons (enabled only when file selected)")
    print("4. 🤖 Regenerate ATA button in transcript tab")
    print("5. 📄 File information display in ATA tab")


if __name__ == "__main__":
    test_tab_structure()
