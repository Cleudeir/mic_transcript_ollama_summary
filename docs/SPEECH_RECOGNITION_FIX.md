# SPEECH RECOGNITION PARAMETER FIX

## Problem Identified

The application was experiencing errors with invalid keyword arguments:

```
⚠️ Error: Recognizer.recognize_google() got an unexpected keyword argument 'timeout' (0.0s)
```

## Root Cause

The `speech_recognition` library's `recognize_google()` method does not accept `timeout` or `phrase_time_limit` parameters directly. These parameters were incorrectly added in the timeout fix attempt.

## Solution Applied

### ❌ **Removed Invalid Parameters:**

```python
# BEFORE (causing errors):
text = _recognizer.recognize_google(
    audio_data_sr, 
    language=language,
    timeout=15,              # ❌ INVALID PARAMETER
    phrase_time_limit=15     # ❌ INVALID PARAMETER
)
```

### ✅ **Fixed to Use Valid Parameters:**

```python
# AFTER (working correctly):
text = _recognizer.recognize_google(audio_data_sr, language=language)
```

### ✅ **Kept Valid Timeout Configuration:**

```python
# This remains valid and provides the extended timeout:
_recognizer.operation_timeout = 15.0  # Extended timeout for 10s chunks
```

## Files Modified

- `src/transcribe_text.py` - Removed invalid parameters from all `recognize_google()` calls

## Valid Parameters for recognize_google()

Based on the speech_recognition library documentation, the valid parameters are:

- `audio_data` - The audio data to recognize
- `language` - The language code (e.g., "pt-BR")
- `show_all` - Whether to return all possible transcriptions
- `with_confidence` - Whether to include confidence scores

## How Timeout Control Works

The timeout is controlled at the recognizer level:

- `_recognizer.operation_timeout = 15.0` - Controls how long the recognizer waits
- `future.result(timeout=20.0)` - Controls how long the async wrapper waits

## Expected Behavior After Fix

✅ **Before Fix:**

```
❌ [16:21:14] ⚠️ Error: Recognizer.recognize_google() got an unexpected keyword argument 'timeout'
❌ [16:21:23] ⚠️ Error: Recognizer.recognize_google() got an unexpected keyword argument 'timeout'
```

✅ **After Fix:**

```
✅ [16:21:13] Worker 1: Processing 10s sample with 200ms overlap (no loss)
✅ [16:21:20] Transcription completed successfully
✅ [16:21:23] Worker 1: Processing 10s sample with 200ms overlap (no loss)
✅ [16:21:30] Transcription completed successfully
```

## Summary

The application should now work correctly with:

- ✅ 10-second audio sampling
- ✅ 200ms overlap for conversation continuity
- ✅ Extended 15-second operation timeout
- ✅ Valid speech recognition API calls
- ✅ No more "unexpected keyword argument" errors
