# Meeting Transcription Tool with AI-Powered Minutes

A Python application for capturing audio from multiple microphones simultaneously, transcribing speech to text in real-time, and automatically generating organized meeting minutes using Ollama AI.

## ✨ New Features

### 🤖 AI-Powered Meeting Minutes with Automatic Pipeline

- **Automatic generation**: Atas are automatically generated when transcription stops (can be toggled)
- **Remote AI processing**: Uses cloud-based Ollama service (<https://api.apps.tec.br/ollama>)
- **Background processing**: AI processing happens in the background without blocking the interface
- **Topic organization**: AI analyzes the transcript and organizes content by themes discussed
- **Smart summaries**: Each topic gets a concise summary with key points, decisions, and action items
- **Portuguese optimized**: Specially designed prompts for Brazilian Portuguese meetings
- **No local setup required**: No need to install Ollama locally

### � File Management Interface

- **View All Transcripts**: Browse all meeting transcriptions with details (date, size, path)
- **View All Atas**: Browse all generated meeting minutes with links to original transcripts
- **File Operations**: Open, delete, and manage transcript and ata files
- **Quick Actions**: Generate atas from existing transcripts, view original transcripts from atas

### �📝 Enhanced Transcription

- **Real-time transcription**: Audio is transcribed as you speak
- **Continuous recording**: No interruptions - records until you manually stop
- **Auto-save**: Transcripts automatically saved to markdown files
- **Multi-microphone support**: Handle multiple speakers simultaneously
- **Automatic pipeline**: Transcription → AI Analysis → Ata Generation (seamless workflow)

## Project Structure

```
reuniao/
├── main.py                 # Entry point (3 lines!)
├── mic_config.json        # Saved microphone preferences (auto-generated)
├── requirements.txt       # Python dependencies
├── test_ollama.py         # Test script for AI integration
├── src/
│   ├── __init__.py        # Package initialization
│   ├── capture_audio.py   # Audio capture functionality
│   ├── transcribe_text.py # Speech transcription functionality
│   ├── gui.py             # GUI interface with AI integration
│   ├── ollama_service.py  # AI service for meeting minutes
│   └── output/            # Generated transcripts and minutes
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

### Steps

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

### GUI Tabs

- **📊 Combined View**: Shows all logs and transcripts in chronological order
- **📝 System Logs**: Recording status and system messages for each microphone
- **📄 Transcripts Only**: Clean view of transcribed text for each microphone

### GUI Controls

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

## 🚀 Installation & Setup

### Prerequisites

1. **Python 3.11+** installed on your system
2. **Internet connection** for AI-powered meeting minutes generation
3. **Microphones** connected to your computer

### Install the Application

1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Quick Start Guide

### Basic Usage

1. **Run the application**: `python main.py`
2. **Configure microphones**: Select exactly 2 microphones from the list
3. **Start recording**: Click "🎤 Start Continuous Recording & Transcription"
4. **Speak normally**: The app transcribes in real-time
5. **Stop recording**: Click "🛑 Stop Continuous Recording"
6. **Auto-generation**: If Ollama is available, ata is generated automatically

### File Management

- **View Transcripts**: File → View All Transcripts
- **View Atas**: File → View All Atas
- **Generate Ata**: Select transcript → Generate Ata button
- **Open Files**: Double-click or use Open button

### Settings

- **Auto-generation**: Settings → Auto-generate Ata (toggle on/off)
- **Language**: Currently optimized for Portuguese (pt-BR)
- **Microphone Preferences**: Automatically saved and restored

## 📁 Output Files

### Transcripts

- **Location**: `src/output/` directory
- **Format**: `meeting_transcripts_YYYYMMDD_HHMMSS.md`
- **Content**: Real-time transcript with timestamps and speaker identification

### Atas (Meeting Minutes)

- **Location**: Same as transcript
- **Format**: `meeting_transcripts_YYYYMMDD_HHMMSS_ata.md`
- **Content**: AI-generated structured meeting minutes organized by topics

## Architecture Benefits

- **Separation of Concerns**: GUI, audio capture, and transcription are separate modules
- **Modularity**: Each component can be used independently
- **Maintainability**: Easy to modify individual features
- **Reusability**: Functions can be imported for other projects
- **Extensibility**: Simple to add new features or interfaces
