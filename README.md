# Meeting Audio Transcription Tool

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

### Enhanced GUI
- **Modern Interface**: Clean, professional design with styled buttons
- **Status Bar**: Real-time feedback on application status
- **Scrollable Output**: Large text area with scrollbar for transcription results
- **Button Controls**: 
  - 🎤 Listen & Transcribe - Start recording
  - 🗑️ Clear Output - Clear the text area
  - 🔄 Refresh Mics - Reload microphone list
- **Confirmation Dialog**: Confirms recording settings before starting
- **Error Handling**: User-friendly error messages

### Audio Processing
- **Dual Microphone Support**: Record from two microphones simultaneously
- **20-second Recording**: Fixed duration recording sessions
- **Real-time Status**: Progress updates during recording and processing
- **Automatic Threading**: Non-blocking operations for smooth UI

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
2. **Select Microphones**: Choose exactly two microphones from the list
3. **Start Recording**: Click "🎤 Listen & Transcribe"
4. **Confirm Settings**: Review the selected microphones and confirm
5. **Wait for Results**: The app will record for 20 seconds and transcribe
6. **View Output**: Transcribed text appears in the output area

### GUI Controls:
- **🎤 Listen & Transcribe**: Start recording session
- **🗑️ Clear Output**: Clear transcription results
- **🔄 Refresh Mics**: Reload microphone list if devices change

## Language

The transcription is configured for Portuguese (pt-BR) but can be modified in the transcription functions.

## Architecture Benefits

- **Separation of Concerns**: GUI, audio capture, and transcription are separate modules
- **Modularity**: Each component can be used independently
- **Maintainability**: Easy to modify individual features
- **Reusability**: Functions can be imported for other projects
- **Extensibility**: Simple to add new features or interfaces
