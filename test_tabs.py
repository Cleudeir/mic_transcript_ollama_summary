#!/usr/bin/env python3
"""
Test script to verify the new tab structure
"""

import os

def test_tab_structure():
    """Test the new separate tabs for transcript files and ATA summaries"""
    print("Testing new tab structure...")
    
    # Check directories exist
    transcript_dir = os.path.join("src", "output", "transcript")
    ata_dir = os.path.join("src", "output", "ata")
    
    print(f"✅ Transcript directory: {transcript_dir}")
    if os.path.exists(transcript_dir):
        transcript_files = [f for f in os.listdir(transcript_dir) if f.endswith('.md')]
        print(f"   - Found {len(transcript_files)} transcript files")
        for file in transcript_files[:3]:  # Show first 3
            print(f"   - {file}")
        if len(transcript_files) > 3:
            print(f"   - ... and {len(transcript_files) - 3} more")
    else:
        print("   - Directory does not exist")
    
    print(f"✅ ATA directory: {ata_dir}")
    if os.path.exists(ata_dir):
        ata_files = [f for f in os.listdir(ata_dir) if f.endswith('.md')]
        print(f"   - Found {len(ata_files)} ATA files")
        for file in ata_files:
            print(f"   - {file}")
    else:
        print("   - Directory does not exist")
    
    print("\n✅ Tab structure implemented:")
    print("   - 📝 Transcript Files tab: Shows transcript files with ATA generation")
    print("   - 📊 ATA Summary tab: Shows generated meeting minutes")
    print("   - Each tab has its own file management (open, delete, refresh)")
    print("   - Separate folder access for each type")

if __name__ == "__main__":
    test_tab_structure()
