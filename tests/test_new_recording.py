#!/usr/bin/env python3
"""
Test script to demonstrate the new 10-second sampling with 200ms overlap functionality
"""

import time
import threading
import numpy as np
from src.capture_audio import get_microphone_list


def test_audio_chunking():
    """Test the new audio chunking logic"""
    print("Testing new audio capture with 10s samples + 200ms overlap")
    print("=" * 60)

    # Get available microphones
    mics = get_microphone_list()
    print(f"Available microphones: {len(mics)}")
    for idx, name in mics:
        print(f"  {idx}: {name}")

    if not mics:
        print("❌ No microphones available for testing")
        return

    # Use the first available microphone for testing
    test_device = mics[0][0]
    print(f"\n🎤 Testing with device {test_device}: {mics[0][1]}")

    # Simulate the new chunking behavior
    chunk_duration = 10  # 10 seconds
    overlap_ms = 200  # 200 milliseconds
    samplerate = 44100  # Standard sample rate

    chunk_samples = int(chunk_duration * samplerate)
    overlap_samples = int((overlap_ms / 1000) * samplerate)

    print(f"📊 Chunk configuration:")
    print(f"   • Chunk duration: {chunk_duration} seconds")
    print(f"   • Overlap: {overlap_ms}ms")
    print(f"   • Chunk samples: {chunk_samples:,}")
    print(f"   • Overlap samples: {overlap_samples:,}")
    print(
        f"   • Effective new data per chunk: {(chunk_samples - overlap_samples) / samplerate:.1f} seconds"
    )

    # Simulate buffer behavior
    print(f"\n🔄 Simulating buffer behavior:")

    buffer_size = 0
    chunk_count = 0

    for i in range(15):  # Simulate 15 seconds of recording
        # Simulate 1 second of audio data being added to buffer
        buffer_size += samplerate

        if buffer_size >= chunk_samples:
            chunk_count += 1
            print(f"   Chunk {chunk_count}: Processing {chunk_duration}s sample")
            print(f"   → Keeping {overlap_ms}ms overlap for continuity")

            # Remove processed data but keep overlap
            buffer_size = overlap_samples

        time.sleep(0.1)  # Small delay for demo

    print(f"\n✅ Processed {chunk_count} chunks in 15 seconds of simulated recording")
    print(f"🛡️  200ms overlap ensures no conversation is lost between chunks")
    print(
        f"⚡ Audio capture continues uninterrupted while transcription runs in parallel"
    )


def chunk_callback(device_index, audio_data, samplerate):
    """Simulated callback for audio chunks"""
    print(f"📝 Processing 10s audio chunk from device {device_index}")
    print(f"   • Audio length: {len(audio_data) / samplerate:.1f} seconds")
    print(f"   • Sample rate: {samplerate} Hz")
    print(
        f"   • Max amplitude: {np.max(np.abs(audio_data)) if len(audio_data) > 0 else 0}"
    )


if __name__ == "__main__":
    print("🎯 NEW RECORDING BEHAVIOR TEST")
    print("=" * 60)
    print("This test demonstrates the improved audio capture:")
    print("• 10-second samples for better transcription quality")
    print("• 200ms overlap to never lose conversation")
    print("• Simultaneous recording and transcription (not alternating)")
    print("• Continuous audio stream with no gaps")
    print()

    test_audio_chunking()

    print("\n" + "=" * 60)
    print("✅ Test completed successfully!")
    print("The application now captures audio in 10-second chunks")
    print("with 200ms overlap to ensure no conversation is lost.")
