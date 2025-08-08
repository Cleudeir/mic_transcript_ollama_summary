# Meet```
reuniao/
├── main.py                 # Entry point (3 lines!)
├── mic_config.json        # Saved microphone preferences (auto-generated)
├── requirements.txt       # Python dependencies
├── src/
│   ├── __init__.py        # Package initialization
│   ├── capture_audio.py   # Audio capture functionality
│   ├── transcribe_text.py # Speech transcription functionality
│   └── gui.py             # GUI interface
└── README.md              # This file
```Transcription Tool

A Python application for capturing audio from multiple microphones simultaneously and transcribing the speech to text.

## Project Structure

```
reuniao/
├── main.py                 # Main application entry point
├── src/
│   ├── __init__.py        # Package initialization
│   ├── capture_audio.py   # Audio capture functionality
│   ├── transcribe_text.py # Speech transcription functionality
│   └── gui.py             # GUI interface
└── README.md              # This file
```

## Modules

### `main.py`
Simple entry point that imports and runs the GUI application.

### `src/gui.py`
Contains the main GUI class `MicrophoneTranscriberGUI` with:
- Enhanced user interface with modern styling
- Microphone selection with checkboxes
- Real-time status updates
- Output text area with scrollbar
- Control buttons (Listen, Clear, Refresh)
- Error handling and user feedback
- Threading for non-blocking operations

### `src/capture_audio.py`
Contains functions for audio capture:
- `get_microphone_list()` - Get list of active microphones
- `is_microphone_active(device_index)` - Test if a microphone is working
- `capture_audio(device_index, duration)` - Capture audio from a device
- `capture_audio_with_callback()` - Capture audio with callback for GUI integration

### `src/transcribe_text.py`
Contains functions for speech transcription:
- `transcribe_audio(audio_data, samplerate, language)` - Transcribe audio to text
- `transcribe_and_display()` - Transcribe and display in GUI
- `batch_transcribe()` - Transcribe multiple audio files

## Features

### Enhanced GUI with Tabbed Interface
- **📊 Combined View**: Shows all logs and transcripts together in chronological order
- **📝 System Logs**: Separate view for system messages and recording status per microphone
- **📄 Transcripts Only**: Clean view showing only the transcribed text per microphone
- **Side-by-side Layout**: Each tab shows Microphone 1 and Microphone 2 data separately

### Smart Microphone Management
- **💾 Remember Preferences**: Save your preferred microphone selection
- **🔄 Auto-load Settings**: Automatically selects previously saved microphones on startup
- **🔄 Refresh Capability**: Update microphone list when devices change
- **Visual Feedback**: Clear device identification and status updates

### Enhanced Controls
- **🎤 Listen & Transcribe**: Start recording with confirmation dialog
- **🗑️ Clear All**: Clear all output areas simultaneously
- **🔄 Refresh Mics**: Reload microphone list
- **💾 Save Mic Choice**: Save current microphone selection for future use

### Audio Processing
- **Dual Microphone Support**: Record from two microphones simultaneously
- **20-second Recording**: Fixed duration recording sessions
- **Real-time Status**: Progress updates during recording and processing
- **Automatic Threading**: Non-blocking operations for smooth UI
- **Separate Logging**: System messages separated from transcription results

## Dependencies

- `sounddevice` - Audio recording
- `speech_recognition` - Speech to text conversion
- `tkinter` - GUI framework (included with Python)
- `numpy` - Audio data processing
- `threading` - Concurrent audio processing

## Usage

Run the main application:
```bash
python main.py
```

### Steps:
1. **Launch Application**: The GUI will open and automatically detect microphones
2. **Auto-load Preferences**: Previously saved microphone choices will be automatically selected
3. **Select Microphones**: Choose exactly two microphones from the list (or modify auto-selected ones)
4. **Save Preferences**: Click "💾 Save Mic Choice" to remember your selection for next time
5. **Start Recording**: Click "🎤 Listen & Transcribe"
6. **Confirm Settings**: Review the selected microphones and confirm
7. **Monitor Progress**: Watch the recording progress in the "📝 System Logs" tab
8. **View Results**: Check transcriptions in:
   - **📊 Combined View**: All information together
   - **📄 Transcripts Only**: Clean transcript text only

### GUI Tabs:
- **📊 Combined View**: Shows all logs and transcripts in chronological order
- **📝 System Logs**: Recording status and system messages for each microphone
- **📄 Transcripts Only**: Clean view of transcribed text for each microphone

### GUI Controls:
- **🎤 Listen & Transcribe**: Start recording session
- **🗑️ Clear All**: Clear all output areas
- **🔄 Refresh Mics**: Reload microphone list if devices change
- **💾 Save Mic Choice**: Save current microphone selection

## Language

The transcription is configured for Portuguese (pt-BR) but can be modified in the transcription functions.

## Configuration

### Microphone Preferences
The application automatically saves your microphone choices in `mic_config.json`. This file:
- **Auto-generated**: Created when you first save microphone preferences
- **Persistent**: Your choices are remembered between sessions
- **Editable**: You can manually edit the JSON file if needed
- **Recoverable**: If microphones change, the app will try to match by name

Example `mic_config.json`:
```json
{
  "saved_microphones": [
    {
      "index": 1,
      "name": "Microphone Array (Intel Smart Sound Technology for USB Audio)"
    },
    {
      "index": 3,
      "name": "Microphone (USB Audio Device)"
    }
  ],
  "timestamp": "MainThread"
}
```

## Architecture Benefits

- **Separation of Concerns**: GUI, audio capture, and transcription are separate modules
- **Modularity**: Each component can be used independently
- **Maintainability**: Easy to modify individual features
- **Reusability**: Functions can be imported for other projects
- **Extensibility**: Simple to add new features or interfaces
