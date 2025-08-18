import sys

print("Python", sys.version)

try:
    import src.gui.app as app

    print("Imported GUI:", hasattr(app, "MicrophoneTranscriberGUI"))
except Exception as e:
    print("Import failed:", repr(e))
    raise
