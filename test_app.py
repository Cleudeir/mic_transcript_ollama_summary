#!/usr/bin/env python3
"""
Quick test script to verify the enhanced GUI works correctly
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported correctly"""
    try:
        from src.gui import MicrophoneTranscriberGUI, create_gui, run_gui
        from src.capture_audio import get_microphone_list, capture_audio
        from src.transcribe_text import transcribe_audio
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_microphone_detection():
    """Test microphone detection"""
    try:
        from src.capture_audio import get_microphone_list
        mics = get_microphone_list()
        print(f"✅ Found {len(mics)} microphone(s)")
        for idx, name in mics:
            print(f"   - Device {idx}: {name}")
        return len(mics) > 0
    except Exception as e:
        print(f"❌ Microphone detection error: {e}")
        return False

def test_gui_creation():
    """Test GUI creation without showing it"""
    try:
        from src.gui import MicrophoneTranscriberGUI
        # Create GUI instance but don't run it
        gui = MicrophoneTranscriberGUI()
        print("✅ GUI creation successful")
        # Destroy the GUI to prevent it from staying open
        gui.root.destroy()
        return True
    except Exception as e:
        print(f"❌ GUI creation error: {e}")
        return False

def main():
    print("🧪 Testing Enhanced Meeting Audio Transcriber")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Module Imports", test_imports),
        ("Microphone Detection", test_microphone_detection), 
        ("GUI Creation", test_gui_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        result = test_func()
        results.append(result)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        print("🚀 Run 'python main.py' to start the enhanced GUI")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
