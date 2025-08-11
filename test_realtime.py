#!/usr/bin/env python3
"""
Test script for real-time transcription improvements
"""

import sys
import time
from src.capture_audio import get_microphone_list
from src.transcribe_text import transcribe_audio_realtime, transcribe_audio_async
import numpy as np


def test_microphones():
    """Test microphone detection"""
    print("🎤 Testing microphone detection...")
    mics = get_microphone_list()

    if not mics:
        print("❌ No microphones found!")
        return False

    print(f"✅ Found {len(mics)} microphone(s):")
    for idx, name in mics:
        print(f"   Device {idx}: {name}")

    return True


def test_transcription_performance():
    """Test transcription performance with sample audio"""
    print("\n🔄 Testing transcription performance...")

    # Create a sample audio chunk (silence for testing)
    samplerate = 16000
    duration = 2  # seconds
    audio_data = np.random.randint(
        -1000, 1000, int(duration * samplerate), dtype=np.int16
    )

    # Test regular transcription
    print("Testing async transcription...")
    start_time = time.time()
    result = transcribe_audio_async(audio_data, samplerate, "pt-BR")
    elapsed = time.time() - start_time

    print(f"   Result: {result}")
    print(f"   Time: {elapsed:.2f} seconds")

    return True


def main():
    """Main test function"""
    print("🚀 Real-time Transcription Test")
    print("=" * 40)

    try:
        # Test microphone detection
        if not test_microphones():
            return

        # Test transcription performance
        test_transcription_performance()

        print("\n✅ All tests completed!")
        print("\n💡 To test full real-time functionality:")
        print("   1. Run: python main.py")
        print("   2. Select exactly 2 microphones")
        print("   3. Click 'Start Live Recording & Transcription'")
        print("   4. Speak into the microphones")
        print("   5. Watch real-time transcription appear")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
