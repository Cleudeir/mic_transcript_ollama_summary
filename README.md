# Meeting Transcription Tool (AI-Powered Minutes)

A desktop app that records audio, transcribes speech in real time, and generates organized meeting minutes (atas) using a remote Ollama service.

## Highlights

- Real-time transcription with continuous recording
- Optional automatic ATA generation after sessions
- Remote Ollama integration (no local Ollama needed)
- Clean, tabbed GUI with file management for transcripts and atas
- Portuguese-first UX (pt-BR), with i18n support

## Project structure (key files)

```text
meet_audio/
├── main.py                      # Entry point
├── build_windows.bat            # Build one-file EXE (with icon)
├── run_windows.bat              # Launch built EXE
├── MicrophoneTranscriber.spec   # PyInstaller spec
├── icon.ico                     # App/EXE icon
├── requirements.txt
├── src/
│   ├── gui/
│   │   ├── app.py               # Main GUI class & runner
│   │   ├── ui_tabs.py           # UI composition (tabs)
│   │   ├── theme.py             # Root window, theme, icons
│   │   ├── ollama_integration.py
│   │   └── mixins/              # Config, files, language, mic, recording, menu
│   ├── audio/capture.py         # Audio capture helpers
│   ├── transcription/core.py    # Transcription pipeline (SpeechRecognition)
│   ├── services/ollama_service.py
│   ├── config_pkg/config.py     # App configuration knobs
│   ├── i18n/core.py             # Translation manager
│   └── output/
│       ├── transcript/          # Saved transcripts (*.md)
│       └── ata/                 # Generated atas (*.md)
└── docs/
    └── icon-and-build.md        # Icon & build notes
```

## Installation

1) Install Python 3.11+

2) Install dependencies

```powershell
pip install -r .\requirements.txt
```

## Run from source

```powershell
python .\main.py
```

The GUI opens, detects microphones, and can start continuous transcription. When enabled, ATA generation runs after sessions via the Ollama remote service.

## Windows build (one-file EXE)

- The build script embeds the app icon and bundles required files.
- The built EXE is copied to the project root as `MicrophoneTranscriber.exe`.

Build:

```powershell
.\build_windows.bat
```

Run the built app:

```powershell
.\run_windows.bat
```

Notes:

- The EXE icon is set via PyInstaller. The window/taskbar icon is also applied at runtime by the GUI.
- See `docs/icon-and-build.md` for details.

## Output files

- Transcripts: `src/output/transcript/YYYYMMDD_HHMMSS_transcript.md`
- Atas: `src/output/ata/YYYYMMDD_HHMMSS_ata.md`

Files are viewable and manageable from the GUI (open/delete/generate ATA from transcript, etc.).

## Configuration

- `config.json`: main app settings (language, Ollama URL/model, auto-generate ATA)
- `src/config_pkg/config.py`: timing and audio constants
- Ollama settings can be edited in the GUI (Ollama tab)

## Dependencies (selected)

- tkinter (bundled with Python)
- sounddevice
- SpeechRecognition
- numpy
- requests (for Ollama service)

## Internationalization

- Default language is pt-BR; UI strings come from the i18n subsystem. Switch language in the GUI.

## License

MIT License © 2025 Cleudeir. Permits use, modification, distribution, and private/commercial use, provided that the copyright and permission notice are included in copies or substantial portions of the software. See the `LICENSE` file for full text.

## Recomendação (Windows): usar "Stereo Mix" como segundo microfone

O dispositivo "Stereo Mix" (também chamado de "Mixagem Estéreo") captura o áudio que está saindo do seu PC (sistema/alto-falantes). Ele é útil como segundo microfone quando você quer transcrever o que a reunião está tocando no computador enquanto usa seu microfone físico para sua voz.

### Como ativar o Stereo Mix

No Windows 10/11:

1) Clique com o botão direito no ícone de som na bandeja do sistema e abra Configurações de som.

2) Role até “Configurações relacionadas” e clique em “Mais configurações de som”.

3) Na janela “Som”, vá até a aba “Gravação”.

4) Clique com o botão direito na lista e marque “Mostrar Dispositivos Desabilitados”.

5) Encontre “Stereo Mix” (ou “Mixagem Estéreo”), clique com o botão direito e escolha “Habilitar”.

6) (Opcional) Defina como dispositivo padrão de gravação e ajuste os níveis em Propriedades.

Alternativa (caminho clássico): Painel de Controle → Hardware e Sons → Som → aba Gravação → habilite “Stereo Mix”.

Se “Stereo Mix” não aparecer, veja “Solução de problemas” abaixo.

### Como usar no aplicativo

1) Abra o app e vá até a aba de Microfones.

2) Clique em “Atualizar” para recarregar a lista.

3) Selecione seu microfone físico como Microfone 1.

4) Selecione “Stereo Mix” como Microfone 2.

5) (Opcional) Clique em “Salvar Preferências” para lembrar essa escolha.

6) Inicie a gravação contínua. O app vai transcrever sua voz (mic físico) e o áudio do sistema (Stereo Mix) em paralelo.

### Dicas e cuidados

- Para evitar eco/realimentação, prefira usar fones de ouvido.
- Ajuste o volume do sistema para não saturar o “Stereo Mix”.
- Feche apps desnecessários que emitem som, se não quiser que apareçam na transcrição do Stereo Mix.

### Solução de problemas

- “Stereo Mix” não aparece: habilite “Mostrar Dispositivos Desabilitados” (aba Gravação); atualize o driver de áudio (ex.: Realtek); verifique Configurações → Privacidade e segurança → Microfone → permita acesso.
- Alguns notebooks não oferecem “Stereo Mix”: como alternativa, você pode usar ferramentas como “Virtual Audio Cable”/“VB-Audio/Voicemeeter” para criar um dispositivo virtual que capture o áudio do sistema.
