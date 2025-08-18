# Microphone Configuration

This app can record from up to two microphones simultaneously. Use the Microphone Configuration tab to:

- Refresh and list available input devices
- Select Microphone 1 and Microphone 2 (must be different devices)
- Test the selected microphones for basic input activity
- Save your selection to `config.json`

## How it works

- Devices are enumerated with `sounddevice.query_devices()` and filtered to inputs.
- We avoid duplicated names and provide a simple drop-down like `<index> | <name>`.
- When you click Save, the app writes:

```json
{
  "microphones": {
    "mic1": 3,
    "mic2": 7
  }
}
```

into your `config.json` (combined with other app settings).

## Troubleshooting

- Click Refresh after plugging a new mic.
- If a mic shows as "No input" during Test, check OS privacy permissions and default levels.
- On Windows, you may need to enable the microphone for desktop apps in System Settings.
- If no devices appear, ensure the `sounddevice` backend works on your system and audio drivers are installed.
