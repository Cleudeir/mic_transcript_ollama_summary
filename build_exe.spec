# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Define the main script
main_script = 'main.py'

# Define additional data files and directories to include
datas = [
    ('config.json', '.'),
    ('src', 'src'),
]

# Define hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'sounddevice',
    'speech_recognition',
    'numpy',
    'requests',
    'ollama',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'threading',
    'json',
    'os',
    'datetime',
    'src.capture_audio',
    'src.gui',
    'src.ollama_service',
    'src.transcribe_text',
    'src.translations',
]

a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MicrophoneTranscriber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI applications
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file path here if you have one
)
