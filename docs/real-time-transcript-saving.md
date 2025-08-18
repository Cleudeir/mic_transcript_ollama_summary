# Real-time Transcript Saving

This release adds automatic, real-time saving of transcripts while recording.

## What it does
- When you press Start, the app creates a new Markdown file under:
  - `src/output/transcript/<YYYYMMDD_HHMMSS>_transcript.md`
- Every recognized chunk is appended immediately with a timestamp and mic label.
- On Stop, the file is finalized and the Transcript Files tab is refreshed.

## File format
- Header with start time and selected devices.
- One line per transcript update:
  - `- [HH:MM:SS] [Mic1|Mic2] recognized text`

## Where to find files
- Use the menu File → “📄 Open Transcript Folder”.
- Or open the “📁 Transcript Files” tab and click “📁 Open Folder”.

## Notes
- If two microphones are selected, the app labels them “Mic1” and “Mic2” based on the selection order.
- The folder `src/output/transcript` is created automatically if it doesn’t exist.

## Troubleshooting
- Transcript file not appearing:
  - Confirm you clicked Start and selected at least one microphone in the Microphone Configuration tab.
  - Check the status bar for the active filename.
  - Verify you have write permission to the workspace folder.
- Empty lines:
  - The app only writes when the recognizer returns non-empty text.
